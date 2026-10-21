import { Injectable, Optional } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { GitHubReleaseInfo, GitHubReleaseService } from './github-release.service';

export interface WindowsArtifact {
  artifact_type: 'exe' | 'zip';
  url: string;
  sha256: string;
  size_bytes: number;
  entrypoint: string;
}

export interface VersionManifest {
  latest_version: string;
  min_supported_version: string;
  mandatory: boolean;
  notes: string;
  published_at: string;
  platforms: { windows: WindowsArtifact };
}

@Injectable()
export class SystemService {
  constructor(
    private readonly config: ConfigService,
    @Optional() private readonly github?: GitHubReleaseService,
  ) {}

  /**
   * Manifest auto-update cho Desktop Client.
   *
   * Nguồn ưu tiên là **release mới nhất trên GitHub** (`APP_UPDATE_SOURCE=github`, mặc định)
   * để mỗi bản phát hành chỉ cần tạo release, không phải sửa `APP_UPDATE_*` rồi redeploy.
   * Khi tắt nguồn đó, chưa cấu hình repo, hoặc GitHub lỗi → dựng manifest từ env như cũ;
   * nhờ vậy endpoint auto-update không bao giờ trả 500 chỉ vì GitHub.
   */
  async getVersionManifest(): Promise<VersionManifest> {
    const base = this.fromEnv();
    const release = await this.latestRelease();
    if (!release) return base;

    return {
      ...base,
      latest_version: release.version,
      notes: base.notes || release.notes,
      published_at: release.publishedAt || base.published_at,
      platforms: {
        windows: {
          ...base.platforms.windows,
          artifact_type: 'zip',
          url: release.url || base.platforms.windows.url,
          sha256: release.sha256 || base.platforms.windows.sha256,
          size_bytes: release.sizeBytes || base.platforms.windows.size_bytes,
        },
      },
    };
  }

  /** Release mới nhất từ GitHub; `null` khi tắt nguồn github, chưa cấu hình hoặc gọi lỗi. */
  private async latestRelease(): Promise<GitHubReleaseInfo | null> {
    const source = (this.read('APP_UPDATE_SOURCE') || 'github').toLowerCase();
    if (source !== 'github' || !this.github) return null;
    try {
      return await this.github.getLatestRelease();
    } catch {
      return null;
    }
  }

  /** Dựng manifest thuần từ biến môi trường (đường dự phòng khi không dùng được GitHub). */
  private fromEnv(): VersionManifest {
    const artifactType = this.read('APP_UPDATE_ARTIFACT_TYPE', 'zip').toLowerCase() === 'exe' ? 'exe' : 'zip';
    const sizeRaw = Number(this.read('APP_UPDATE_SIZE_WINDOWS', '0'));

    return {
      latest_version: this.read('APP_LATEST_VERSION', '0.0.0'),
      min_supported_version: this.read('APP_MIN_SUPPORTED_VERSION', '0.0.0'),
      mandatory: this.read('APP_UPDATE_MANDATORY', 'false').toLowerCase() === 'true',
      notes: this.read('APP_UPDATE_NOTES'),
      published_at: this.read('APP_UPDATE_PUBLISHED_AT'),
      platforms: {
        windows: {
          artifact_type: artifactType,
          url: this.read('APP_UPDATE_URL_WINDOWS'),
          sha256: this.read('APP_UPDATE_SHA256_WINDOWS').toLowerCase(),
          size_bytes: Number.isFinite(sizeRaw) && sizeRaw > 0 ? Math.floor(sizeRaw) : 0,
          entrypoint: this.read('APP_UPDATE_ENTRYPOINT', 'AITA_Grader_v1.exe'),
        },
      },
    };
  }

  /**
   * Lưu ý: Joi trong `app.module.ts` đã ép kiểu sẵn, nên ConfigService.get() trả về
   * `boolean` (APP_UPDATE_MANDATORY) hoặc `number` (APP_UPDATE_SIZE_WINDOWS) — không
   * phải chuỗi. Phải ép về chuỗi trước khi trim, nếu không endpoint sẽ ném TypeError 500.
   */
  private read(key: string, fallback = ''): string {
    return String(this.config.get(key) ?? fallback).trim();
  }
}
