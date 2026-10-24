"""AITA Desktop Client - Web Studio rubric tests.

Covers the real `WebRubricEngine` scorers (DOM / CSS / JS / weighted total /
verdict) and the folder-import recognition helpers used by
`WebFolderImportDialog` (UC-19). No Playwright/network required.
"""
from pathlib import Path

import pytest

from services.web_rubric_service import WebRubricEngine, WEIGHTS, classify_url


SEMANTIC_HTML = """
<html><body>
  <header></header><nav></nav><main>
    <section><h1>Title</h1><h2>Sub</h2>
      <img src="a.png" alt="mô tả">
      <form><label>Email</label><input type="email"></form>
    </section>
  </main><footer></footer>
</body></html>
"""


@pytest.fixture()
def engine():
    return WebRubricEngine(ai_service=None)


# ------------------------------------------------------------------------------
# Target resolution
# ------------------------------------------------------------------------------
def test_resolve_target_url_prefers_live_url(engine):
    assert engine._resolve_target_url("https://demo.dev", None) == "https://demo.dev"


def test_resolve_target_url_uses_local_index_html(engine, tmp_path):
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    resolved = engine._resolve_target_url(None, str(tmp_path))
    assert resolved is not None
    assert resolved.startswith("file:")
    assert resolved.endswith("index.html")


def test_resolve_target_url_none_when_missing(engine):
    assert engine._resolve_target_url(None, None) is None


# ------------------------------------------------------------------------------
# DOM scoring
# ------------------------------------------------------------------------------
def test_score_dom_semantic_page_scores_high(engine):
    score, log = engine._score_dom(SEMANTIC_HTML)
    assert score >= 8.0
    assert "thẻ ngữ nghĩa" in log


def test_score_dom_empty_html_keeps_baseline_point(engine):
    # No <img> found -> engine grants the "no images" +1.0 baseline, so an empty
    # document still scores 1.0 (documented engine behaviour).
    score, _ = engine._score_dom("")
    assert score == 1.0


def test_score_dom_penalizes_images_without_alt(engine):
    with_alt, _ = engine._score_dom(SEMANTIC_HTML)
    no_alt, _ = engine._score_dom(SEMANTIC_HTML.replace(' alt="mô tả"', ""))
    assert no_alt < with_alt


# ------------------------------------------------------------------------------
# CSS scoring
# ------------------------------------------------------------------------------
def test_score_css_no_css_returns_baseline(engine):
    score, _ = engine._score_css("<html><body>plain</body></html>", [])
    assert score == 3.0


def test_score_css_valid_stylesheet_scores_ten(engine):
    score, _ = engine._score_css("<html><body>x</body></html>", ["a { color: red; }"])
    assert score == 10.0


def test_score_css_syntax_errors_reduce_score(engine):
    score, log = engine._score_css("<html><body>x</body></html>", ["}", "@@@", "a { color: red; }"])
    assert score < 10.0
    assert "lỗi cú pháp" in log


def test_score_css_inline_style_penalty(engine):
    score, _ = engine._score_css(
        '<html><body><p style="color: red">x</p></body></html>',
        ["a { color: red; }"],
    )
    assert score < 10.0


# ------------------------------------------------------------------------------
# JS / functional scoring
# ------------------------------------------------------------------------------
def test_score_func_counts_scripts_and_controls(engine):
    html = (
        "<html><body><script>x</script><script>y</script>"
        "addEventListener addEventListener addEventListener addEventListener"
        '<button onclick="go()">Go</button><a href="/x">x</a></body></html>'
    )
    score, log = engine._score_func(html, {})
    assert score > 0.0
    assert "script" in log


def test_score_func_empty_html_scores_zero(engine):
    score, _ = engine._score_func("", {})
    assert score == 0.0


# ------------------------------------------------------------------------------
# Weighted total + verdict
# ------------------------------------------------------------------------------
def test_weighted_total_all_components(engine):
    total = engine._weighted_total({"dom": 10.0, "lint": 10.0, "func": 10.0, "ui": 10.0})
    assert round(total, 2) == 10.0
    assert round(sum(WEIGHTS.values()), 2) == 1.0


def test_weighted_total_redistributes_when_ui_missing(engine):
    # UI unavailable -> weights re-normalised over DOM/Lint/Func only
    total = engine._weighted_total({"dom": 10.0, "lint": 0.0, "func": 0.0})
    assert round(total, 2) == round((10.0 * 0.2) / 0.7, 2)


@pytest.mark.parametrize(
    "total,verdict",
    [(10.0, "PASSED"), (7.0, "PASSED"), (6.99, "PARTIAL"), (5.0, "PARTIAL"), (4.99, "FAILED"), (0.0, "FAILED")],
)
def test_verdict_thresholds(engine, total, verdict):
    assert engine._verdict(total) == verdict


def test_grade_without_html_returns_failed(engine):
    result = engine.grade(live_url=None, local_dir=None)
    assert result.verdict == "FAILED"
    assert result.error == "NO_HTML"


# ------------------------------------------------------------------------------
# URL classification & normalization helpers
# ------------------------------------------------------------------------------
def test_classify_url_normalizes_github_repo():
    kind, normalized, error = classify_url("https://github.com/user/repo.git/tree/main")
    assert kind == "repo"
    assert normalized == "https://github.com/user/repo"
    assert error == ""


def test_classify_url_treats_other_hosts_as_live():
    kind, normalized, error = classify_url("https://demo.vercel.app/")
    assert kind == "live"
    assert normalized == "https://demo.vercel.app/"
    assert error == ""


def test_classify_url_rejects_non_url():
    kind, _normalized, error = classify_url("just-some-text")
    assert kind is None
    assert error != ""


def test_engine_screenshots_dir_defaults_under_data():
    eng = WebRubricEngine()
    assert eng.screenshots_dir.name == "web_screenshots"
    assert isinstance(eng.screenshots_dir, Path)


def test_grade_repo_only_ui_score_is_none(monkeypatch):
    eng = WebRubricEngine()
    monkeypatch.setattr(eng, "_fetch_github_raw", lambda url: (SEMANTIC_HTML, ["body { color: red; }"]))
    res = eng.grade(repo_url="https://github.com/test/project", mode="REPO_ONLY")
    assert res.score_ui is None
    assert res.score_dom is not None
    assert res.score_lint is not None
    assert res.score_func is not None
    assert res.total_score > 0
    assert "Không áp dụng (chế độ chỉ chấm GitHub Repo)" in res.rubric_log



# ------------------------------------------------------------------------------
# UI/UX scoring: AI auth failure propagation (IT11 — "Token không hợp lệ")
# ------------------------------------------------------------------------------
class _StubAiService:
    def __init__(self, result):
        self._result = result

    def evaluate_web_ui(self, **kwargs):
        return self._result


def test_score_ui_propagates_auth_error_code(engine):
    stub = _StubAiService({
        "success": False,
        "message": "Token không hợp lệ.",
        "error_code": "AUTH_INVALID_TOKEN",
    })
    engine._ai_service = stub
    score, feedback, log, error_code = engine._score_ui(b"fake-png")
    assert error_code == "AUTH_INVALID_TOKEN"
    assert score == 0.0
    assert feedback == ""


def test_score_ui_success_returns_no_error_code(engine):
    stub = _StubAiService({
        "success": True,
        "ui_score": 8.0,
        "overall_feedback": "Bố cục tốt",
        "tokens_consumed": 10,
    })
    engine._ai_service = stub
    score, feedback, log, error_code = engine._score_ui(b"fake-png")
    assert error_code is None
    assert score == 8.0
    assert "8.0/10" in log
