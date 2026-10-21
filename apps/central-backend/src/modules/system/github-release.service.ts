import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

/** Thông tin một bản phát hành lấy từ GitHub Releases API (đã rút gọn cho manifest). */
export interface GitHubReleaseInfo {
  version: string;
  url: string;
  sha256: string;
  sizeBytes: number;
  publishedAt: string;
  notes: string;
}

interface GitHubAsset {
  name?: string;
  browser_download_url?: string;
  size?: number;
  digest?: string | null;
}

export interface GitHubReleasePayload {
  tag_name?: string;
  name?: string;
  published_at?: string;
  assets?: GitHubAsset[];
}

const API_ROOT = 'https://api.github.com';
const TAG_VERSION = /^v?(\d+(?:\.\d+)*)/i;
const ZIP_NAME = /^AITA_Grader.*\.zip$/i;

/** `v1.2.3-portable` -> `1.2.3`; trả '' nếu tag không có phần số phiên bản. */
export function versionFromTag(tag: string | undefined): string {
  const match = TAG_VERSION.exec(String(tag ?? '').trim());
  return match ? match[1] : '';
}

/** Chỉ lấy asset ZIP của AITA, bỏ qua file phụ (.exe, aita_selftest.txt…). */
export function pickZipAsset(assets: GitHubAsset[] | undefined): GitHubAsset | null {
  const zips = (assets ?? []).filter((asset) => ZIP_NAME.test(String(asset?.name ?? '')));
  return zips.length > 0 ? zips[0] : null;
}

/** Payload GitHub -> thông tin manifest; null nếu thiếu tag hoặc thiếu asset ZIP. */
export function releaseToInfo(payload: GitHubReleasePayload | null | undefined): GitHubReleaseInfo | null {
  const version = versionFromTag(payload?.tag_name);
  const asset = pickZipAsset(payload?.assets);
  const url = String(asset?.browser_download_url ?? '').trim();
  if (!version || !asset || !url) return null;
  return {
    version,
    url,
    sha256: String(asset.digest ?? '')
      .replace(/^sha256:/i, '')
      .toLowerCase(),
    sizeBytes: Number(asset.size ?? 0) || 0,
    publishedAt: String(payload?.published_at ?? '').trim(),
    notes: String(payload?.name ?? '').trim(),
  };
}

/**
 * Đọc release mới nhất từ GitHub Releases để backend tự dựng manifest auto-update,
 * nhờ vậy mỗi bản phát hành chỉ cần tạo release — không phải sửa `APP_UPDATE_*` trên Render.
 *
 * Kết quả được cache `APP_UPDATE_GITHUB_TTL_SECONDS` (mặc định 300s) để không gọi
 * GitHub ở mọi request và tránh vượt rate-limit 60 request/giờ của IP chưa xác thực.
 * Mọi lỗi (mạng, 401 do thiếu `GITHUB_TOKEN` với repo private, 404…) đều trả `null`
 * để `SystemService` quay về cấu hình env.
 */
@Injectable()
export class GitHubReleaseService {
  private readonly logger = new Logger(GitHubReleaseService.name);
  private cached: { at: number; value: GitHubReleaseInfo | null } | null = null;

  constructor(private readonly config: ConfigService) {}

  async getLatestRelease(): Promise<GitHubReleaseInfo | null> {
    const repo = this.text('APP_UPDATE_GITHUB_REPO');
    if (!repo) return null;

    const ttlMs = this.number('APP_UPDATE_GITHUB_TTL_SECONDS', 300) * 1000;
    const now = Date.now();
    if (this.cached && now - this.cached.at < ttlMs) return this.cached.value;

    const fresh = await this.fetchLatest(repo);
    // Gọi lỗi tạm thời thì giữ kết quả lần trước, tránh manifest nhảy qua lại.
    this.cached = { at: now, value: fresh ?? this.cached?.value ?? null };
    return this.cached.value;
  }

  private async fetchLatest(repo: string): Promise<GitHubReleaseInfo | null> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.number('APP_UPDATE_GITHUB_TIMEOUT_MS', 5000));
    try {
      const headers: Record<string, string> = {
        Accept: 'application/vnd.github+json',
        'User-Agent': 'AITA-Backend',
        'X-GitHub-Api-Version': '2022-11-28',
      };
      const token = this.text('GITHUB_TOKEN');
      if (token) headers.Authorization = `Bearer ${token}`;

      const response = await fetch(`${API_ROOT}/repos/${repo}/releases/latest`, {
        headers,
        signal: controller.signal,
      });
      if (!response.ok) {
        this.logger.warn(`GitHub Releases trả HTTP ${response.status} cho ${repo} - dùng cấu hình env.`);
        return null;
      }
      return releaseToInfo((await response.json()) as GitHubReleasePayload);
    } catch (error) {
      this.logger.warn(`Không gọi được GitHub Releases (${repo}): ${(error as Error).message}`);
      return null;
    } finally {
      clearTimeout(timer);
    }
  }

  private text(key: string, fallback = ''): string {
    return String(this.config.get(key) ?? fallback).trim();
  }

  private number(key: string, fallback: number): number {
    const value = Number(this.text(key, String(fallback)));
    return Number.isFinite(value) && value >= 0 ? value : fallback;
  }
}
