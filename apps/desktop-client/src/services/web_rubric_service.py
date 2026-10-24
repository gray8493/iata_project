"""
AITA Desktop Client - Web Assignment Rubric Engine
==================================================
Implements UC-19 / IT11: real automated grading of web assignments using the
4-component rubric (weights: HTML 2.0, CSS 2.0, JS 3.0, UI/UX 3.0 -> total 10.0).

Pipeline per submission:
  1. Render the deployed page (or a local `index.html`) in a Headless Chromium
     via Playwright; capture the DOM HTML, extracted CSS, interaction metrics
     and a full-page screenshot.
  2. DOM structure scoring   -> BeautifulSoup4 (semantic tags, alt, headings).
  3. CSS standards scoring   -> TinyCSS2 W3C syntax lint + responsive media queries.
  4. Functional scoring      -> Playwright/DOM interaction metrics (scripts,
     event listeners, interactive controls).
  5. UI/UX scoring           -> AI Vision (OpenRouter) via the Central AI Gateway
     (`POST /api/v1/ai/evaluate-web-ui`) using the base64 screenshot.

When Playwright/Chromium is unavailable the engine degrades gracefully to a
static-file analysis (DOM/CSS/JS) and records the reason in the rubric log.
"""

import base64
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SEMANTIC_TAGS = ("header", "nav", "main", "footer", "section", "article", "aside", "form")
WEIGHTS = {"dom": 0.2, "lint": 0.2, "func": 0.3, "ui": 0.3}
GITHUB_HOST = "github.com"


def classify_url(raw_url: str) -> Tuple[Optional[str], str, str]:
    """
    Classifies a single link.
    Returns (kind, normalized, error) where kind is "repo", "live" or None.
    A github.com/<user>/<repo> link is normalized (drops /tree/..., .git and trailing "/").
    """
    from urllib.parse import urlparse
    url = (raw_url or "").strip().rstrip(".,;:!?)\"]'")
    if not (url.startswith("http://") or url.startswith("https://")):
        return None, url, "Link không đúng định dạng http:// hoặc https://"
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host == GITHUB_HOST or host.endswith("." + GITHUB_HOST):
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2:
            user, repo = parts[0], parts[1]
            if repo.lower().endswith(".git"):
                repo = repo[:-4]
            return "repo", f"https://{GITHUB_HOST}/{user}/{repo}", ""
        return None, url, "Link GitHub không đúng dạng github.com/<user>/<repo>"
    if host:
        return "live", url, ""
    return None, url, "Link không đúng định dạng http:// hoặc https://"


_JS_PROBE = """
() => {
  const onclick = document.querySelectorAll('[onclick]').length;
  const interactive = document.querySelectorAll('button, a[href], form, input, select, textarea').length;
  const scripts = document.querySelectorAll('script').length;
  const evt = (document.documentElement.innerHTML.match(/addEventListener/g) || []).length;
  return { onclick, interactive, scripts, evt };
}
"""


@dataclass
class WebRubricResult:
    score_dom: Optional[float] = None
    score_lint: Optional[float] = None
    score_func: Optional[float] = None
    score_ui: Optional[float] = None
    total_score: float = 0.0
    verdict: str = "FAILED"
    screenshot_path: Optional[str] = None
    rubric_log: str = ""
    ai_feedback: str = ""
    error: Optional[str] = None
    # Mã lỗi AI Vision nếu tiêu chí UI/UX không chấm được (VD: "AUTH_INVALID_TOKEN"
    # khi phiên đăng nhập backend hết hạn) — để UI cảnh báo thay vì âm thầm 0 điểm.
    ui_error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class WebRubricEngine:
    """Automated web assignment rubric grader (DOM / CSS / JS / UI)."""

    def __init__(self, ai_service=None, screenshots_dir: Optional[Path] = None):
        self._ai_service = ai_service
        if screenshots_dir is None:
            root = Path(__file__).resolve().parent.parent.parent
            screenshots_dir = root / "data" / "web_screenshots"
        self.screenshots_dir = Path(screenshots_dir)

    @property
    def ai_service(self):
        if self._ai_service is None:
            from services.ai_service import AiService
            self._ai_service = AiService()
        return self._ai_service

    @staticmethod
    def _fetch_github_raw(repo_url: Optional[str]) -> Tuple[str, List[str]]:
        """
        Fetches index.html and stylesheets directly from GitHub raw content (0 disk footprint).
        Supports branches: main, master.
        """
        if not repo_url:
            return "", []
        import urllib.request
        from urllib.parse import urlparse

        parsed = urlparse(repo_url.strip())
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(path_parts) < 2:
            return "", []
        user, repo = path_parts[0], path_parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]

        html = ""
        branches = ["main", "master"]
        matched_branch = ""
        for br in branches:
            for file_name in ["index.html", "Index.html", "index.htm"]:
                raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{br}/{file_name}"
                try:
                    req = urllib.request.Request(raw_url, headers={"User-Agent": "AITA-Web-Grader"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        if resp.status == 200:
                            html = resp.read().decode("utf-8", errors="replace")
                            matched_branch = br
                            break
                except Exception:
                    continue
            if html:
                break

        css_texts: List[str] = []
        if matched_branch:
            for css_candidate in ["style.css", "styles.css", "css/style.css", "css/styles.css", "main.css"]:
                css_url = f"https://raw.githubusercontent.com/{user}/{repo}/{matched_branch}/{css_candidate}"
                try:
                    req = urllib.request.Request(css_url, headers={"User-Agent": "AITA-Web-Grader"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        if resp.status == 200:
                            css_texts.append(resp.read().decode("utf-8", errors="replace"))
                except Exception:
                    continue

        if html:
            for block in re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.DOTALL | re.IGNORECASE):
                css_texts.append(block)

        return html, css_texts

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def grade(
        self,
        live_url: Optional[str] = None,
        local_dir: Optional[str] = None,
        repo_url: Optional[str] = None,
        mssv: str = "",
        mode: str = "HYBRID"
    ) -> WebRubricResult:
        """
        Grades a single web submission according to its mode:
        - LIVE_ONLY: grades live website only (Playwright render -> DOM, CSS, JS, UI/UX).
        - REPO_ONLY: grades GitHub repo only (raw source -> DOM, CSS, JS; UI/UX is not applicable).
        - HYBRID: grades both live website and repository.
        """
        norm_mode = (mode or "HYBRID").upper()
        if norm_mode not in ("LIVE_ONLY", "REPO_ONLY", "HYBRID"):
            norm_mode = "HYBRID"

        log_lines: List[str] = [f"[MODE]: Chế độ chấm '{norm_mode}'."]
        html = ""
        css_texts: List[str] = []
        js_metrics: Dict[str, int] = {}
        screenshot_bytes: Optional[bytes] = None

        if norm_mode == "LIVE_ONLY":
            target_url = (live_url or "").strip()
            if not target_url:
                return WebRubricResult(
                    verdict="FAILED",
                    rubric_log=f"[ERROR]: Chế độ Live URL nhưng bài nộp chưa có link trang web.",
                    error="MISSING_LIVE_URL"
                )
            try:
                html, css_texts, js_metrics, screenshot_bytes = self._render(target_url)
                log_lines.append(f"[PLAYWRIGHT]: Render thành công '{target_url}'.")
            except Exception as ex:
                log_lines.append(f"[PLAYWRIGHT]: Không render được bằng Chromium ({self._short(ex)}).")
                return WebRubricResult(
                    verdict="FAILED",
                    rubric_log="\n".join(log_lines) + f"\n[RESULT]: Lỗi kết nối Live URL: {self._short(ex)}.",
                    error="RENDER_FAILED"
                )

        elif norm_mode == "REPO_ONLY":
            log_lines.append(f"[GITHUB]: Đọc mã nguồn từ repo '{repo_url}'...")
            html, css_texts = self._fetch_github_raw(repo_url)
            if not html and local_dir:
                log_lines.append("[STATIC]: Tải trực tiếp từ repo không thấy index.html, kiểm tra thư mục cục bộ...")
                html, css_texts = self._load_static(local_dir)
            if not html:
                return WebRubricResult(
                    verdict="FAILED",
                    rubric_log="\n".join(log_lines) + f"\n[RESULT]: Không tìm thấy index.html trên repo '{repo_url}'.",
                    error="NO_HTML_IN_REPO"
                )
            log_lines.append(f"[GITHUB]: Lấy mã nguồn thành công ({len(html)} ký tự HTML, {len(css_texts)} nguồn CSS).")

        else: # HYBRID
            target_url = self._resolve_target_url(live_url, local_dir)
            if target_url:
                try:
                    html, css_texts, js_metrics, screenshot_bytes = self._render(target_url)
                    log_lines.append(f"[PLAYWRIGHT]: Render thành công Live URL '{target_url}'.")
                except Exception as ex:
                    log_lines.append(f"[PLAYWRIGHT]: Không render được Live URL ({self._short(ex)}). Thử lấy mã nguồn từ repo.")
            if not html and repo_url:
                html, css_texts = self._fetch_github_raw(repo_url)
            if not html and local_dir:
                html, css_texts = self._load_static(local_dir)
            if not html:
                return WebRubricResult(
                    verdict="FAILED",
                    rubric_log="\n".join(log_lines) + "\n[RESULT]: Không tìm thấy mã nguồn HTML từ Live URL lẫn GitHub Repo để thẩm định.",
                    error="NO_HTML"
                )

        # 1. Chấm DOM
        dom_score, dom_log = self._score_dom(html)
        log_lines.append(f"[DOM]: {dom_log}")

        # 2. Chấm CSS Lint
        lint_score, lint_log = self._score_css(html, css_texts)
        log_lines.append(f"[CSS]: {lint_log}")

        # 3. Chấm Function JS
        func_score, func_log = self._score_func(html, js_metrics)
        log_lines.append(f"[JS]: {func_log}")

        # 4. Chấm UI/UX (chỉ áp dụng khi có ảnh chụp màn hình Playwright)
        screenshot_path = None
        ui_score: Optional[float] = None
        ai_feedback = ""
        ui_error: Optional[str] = None

        if norm_mode == "REPO_ONLY":
            log_lines.append("[UI/UX]: Không áp dụng (chế độ chỉ chấm GitHub Repo).")
        else:
            if screenshot_bytes:
                screenshot_path = self._save_screenshot(screenshot_bytes, mssv)
                raw_ui, ai_feedback, ui_log, ui_error = self._score_ui(screenshot_bytes)
                ui_score = raw_ui
                if ui_error in ("AUTH_INVALID_TOKEN", "HTTP_401"):
                    ui_log = (
                        "Token không hợp lệ — phiên đăng nhập backend đã hết hạn, "
                        "đăng nhập lại rồi chấm lại bài để có điểm UI/UX (tạm tính 0.0/10)."
                    )
                log_lines.append(f"[UI/UX]: {ui_log}")
            else:
                log_lines.append("[UI/UX]: Không có ảnh chụp màn hình để AI Vision thẩm định.")

        components: Dict[str, Optional[float]] = {
            "dom": dom_score,
            "lint": lint_score,
            "func": func_score,
        }
        if ui_score is not None:
            components["ui"] = ui_score

        total = self._weighted_total(components)
        verdict = self._verdict(total)

        log_lines.append(f"[TOTAL]: {total:.2f}/10.0 -> {verdict}")

        return WebRubricResult(
            score_dom=round(dom_score, 2),
            score_lint=round(lint_score, 2),
            score_func=round(func_score, 2),
            score_ui=round(ui_score, 2) if ui_score is not None else None,
            total_score=round(total, 2),
            verdict=verdict,
            screenshot_path=screenshot_path,
            rubric_log="\n".join(log_lines),
            ai_feedback=ai_feedback,
            ui_error=ui_error,
            details=components
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def _resolve_target_url(self, live_url: Optional[str], local_dir: Optional[str]) -> Optional[str]:
        live_url = (live_url or "").strip()
        if live_url:
            return live_url
        if local_dir:
            entry = Path(local_dir)
            if entry.is_dir():
                for candidate in ("index.html", "Index.html", "index.htm"):
                    if (entry / candidate).is_file():
                        return (entry / candidate).resolve().as_uri()
            elif entry.is_file():
                return entry.resolve().as_uri()
        return None

    def _render(self, url: str) -> Tuple[str, List[str], Dict[str, int], bytes]:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(url, wait_until="load", timeout=30000)
                page.wait_for_timeout(700)

                html = page.content()
                css_texts = page.eval_on_selector_all(
                    "style", "els => els.map(e => e.textContent || '')"
                )
                hrefs = page.eval_on_selector_all(
                    'link[rel="stylesheet"]',
                    "els => els.map(e => e.href || '')"
                )
                for href in hrefs:
                    content = self._fetch_stylesheet(page, href)
                    if content:
                        css_texts.append(content)
                js_metrics = page.evaluate(_JS_PROBE)
                screenshot = page.screenshot(full_page=True)
                return html, css_texts, js_metrics, screenshot
            finally:
                browser.close()

    @staticmethod
    def _fetch_stylesheet(page, href: str) -> str:
        """Loads an external stylesheet body: local file:// from disk, http(s) via browser context."""
        if not href:
            return ""
        try:
            if href.startswith("file:"):
                from urllib.parse import urlparse, unquote
                disk_path = unquote(urlparse(href).path)
                if re.match(r"^/[A-Za-z]:", disk_path):
                    disk_path = disk_path[1:]
                return Path(disk_path).read_text(encoding="utf-8", errors="replace")
            resp = page.request.get(href, timeout=15000)
            if resp.ok:
                return resp.text()
        except Exception:
            return ""
        return ""

    def _load_static(self, local_dir: Optional[str]) -> Tuple[str, List[str]]:
        """Fallback: read HTML/CSS directly from a local submission folder."""
        if not local_dir:
            return "", []
        root = Path(local_dir)
        if root.is_file():
            root = root.parent
        if not root.is_dir():
            return "", []

        html = ""
        for candidate in ("index.html", "Index.html", "index.htm"):
            f = root / candidate
            if f.is_file():
                html = f.read_text(encoding="utf-8", errors="replace")
                break

        css_texts: List[str] = []
        for css_file in root.rglob("*.css"):
            try:
                css_texts.append(css_file.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
        # Collect inline <style> blocks from static HTML as well
        for block in re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.DOTALL | re.IGNORECASE):
            css_texts.append(block)
        return html, css_texts

    # ------------------------------------------------------------------
    # Component scorers
    # ------------------------------------------------------------------
    def _score_dom(self, html: str) -> Tuple[float, str]:
        try:
            from bs4 import BeautifulSoup
        except Exception:
            return 0.0, "Thiếu thư viện BeautifulSoup4."

        soup = BeautifulSoup(html, "html.parser")
        score = 0.0

        present = [tag for tag in SEMANTIC_TAGS if soup.find(tag)]
        score += min(len(present), len(SEMANTIC_TAGS)) / len(SEMANTIC_TAGS) * 5.0

        if soup.find("h1"):
            score += 1.0
        if soup.find("h2") or soup.find("h3"):
            score += 1.0

        images = soup.find_all("img")
        if images:
            with_alt = sum(1 for img in images if (img.get("alt") or "").strip())
            score += (with_alt / len(images)) * 2.0
        else:
            score += 1.0

        if soup.find("form") and (soup.find("label") or soup.find("input")):
            score += 1.0

        score = min(score, 10.0)
        return score, f"{len(present)}/{len(SEMANTIC_TAGS)} thẻ ngữ nghĩa, {len(images)} ảnh -> {score:.1f}/10"

    def _score_css(self, html: str, css_texts: List[str]) -> Tuple[float, str]:
        combined = "\n".join(t for t in css_texts if t)
        has_css = bool(combined.strip()) or bool(re.search(r"<style", html, flags=re.IGNORECASE))

        if not has_css:
            return 3.0, "Không phát hiện CSS (chỉ chấm cấu trúc tối thiểu) -> 3.0/10"

        errors = 0
        blocks = 0
        try:
            import tinycss2
            for css in css_texts:
                if not css:
                    continue
                nodes = tinycss2.parse_stylesheet(css, skip_whitespace=True, skip_comments=True)
                blocks += sum(1 for n in nodes if n.type == "qualified-rule")
                errors += sum(1 for n in nodes if n.type == "error")
        except Exception:
            pass

        score = 10.0 - min(errors * 2.0, 6.0)

        inline_styles = len(re.findall(r"\sstyle\s*=", html, flags=re.IGNORECASE))
        if inline_styles > 0:
            score -= min(inline_styles * 0.1, 2.0)

        if re.search(r"@media", combined, flags=re.IGNORECASE):
            score += 1.0

        score = max(0.0, min(score, 10.0))
        return score, f"{blocks} rule CSS, {errors} lỗi cú pháp, {inline_styles} inline-style -> {score:.1f}/10"

    def _score_func(self, html: str, js_metrics: Dict[str, int]) -> Tuple[float, str]:
        scripts = int(js_metrics.get("scripts", 0)) or len(re.findall(r"<script", html, flags=re.IGNORECASE))
        onclick = int(js_metrics.get("onclick", 0)) or len(re.findall(r"onclick\s*=", html, flags=re.IGNORECASE))
        evt = int(js_metrics.get("evt", 0)) or len(re.findall(r"addEventListener", html))
        interactive = int(js_metrics.get("interactive", 0)) or len(
            re.findall(r"<(button|a\b|form|input|select|textarea)", html, flags=re.IGNORECASE)
        )

        score = 0.0
        if scripts > 0:
            score += 3.0
        score += min(evt, 4) / 4 * 4.0
        score += min(onclick, 2) / 2 * 1.0
        score += min(interactive, 5) / 5 * 2.0
        score = min(score, 10.0)
        return score, f"{scripts} script, {evt} listener, {onclick} onclick, {interactive} thành phần tương tác -> {score:.1f}/10"

    def _score_ui(self, screenshot_bytes: bytes) -> Tuple[float, str, str, Optional[str]]:
        """Returns (score, feedback, log_line, error_code); error_code rỗng khi thành công."""
        try:
            b64 = base64.b64encode(screenshot_bytes).decode("ascii")
            res = self.ai_service.evaluate_web_ui(
                screenshot_base64=b64,
                rubric_requirements=[
                    "Bố cục cân đối, phân cấp thị giác rõ ràng",
                    "Phối màu hài hòa, tương phản đạt chuẩn",
                    "Typography dễ đọc, khoảng cách nhất quán",
                    "Responsive và trải nghiệm người dùng tốt"
                ]
            )
            if res.get("success"):
                ui = float(res.get("ui_score", 0.0))
                ui = max(0.0, min(ui, 10.0))
                feedback = res.get("overall_feedback", "") or ""
                return ui, feedback, f"AI Vision đánh giá {ui:.1f}/10 ({res.get('tokens_consumed', 0)} tokens).", None
            error_code = res.get("error_code") or f"HTTP_{res.get('status_code', 0)}"
            return 0.0, "", f"AI Gateway không đánh giá được: {res.get('message', 'không rõ lý do')}", error_code
        except Exception as ex:
            return 0.0, "", f"Lỗi gọi AI Vision: {self._short(ex)}", "EXCEPTION"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _weighted_total(self, components: Dict[str, Optional[float]]) -> float:
        valid = {k: v for k, v in components.items() if v is not None and k in WEIGHTS}
        total_weight = sum(WEIGHTS[k] for k in valid)
        if total_weight <= 0:
            return 0.0
        return sum(valid[k] * WEIGHTS[k] for k in valid) / total_weight * 1.0

    @staticmethod
    def _verdict(total: float) -> str:
        if total >= 7.0:
            return "PASSED"
        if total >= 5.0:
            return "PARTIAL"
        return "FAILED"

    def _save_screenshot(self, data: bytes, mssv: str) -> Optional[str]:
        try:
            self.screenshots_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = self.screenshots_dir / f"{mssv or 'student'}_{stamp}.png"
            out.write_bytes(data)
            return str(out)
        except Exception:
            return None

    @staticmethod
    def _short(ex: Exception) -> str:
        return str(ex).splitlines()[0] if str(ex) else ex.__class__.__name__
