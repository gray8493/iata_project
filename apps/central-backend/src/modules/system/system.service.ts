import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

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
  constructor(private readonly config: ConfigService) {}

  getVersionManifest(): VersionManifest {
    const read = (key: string, fallback = ''): string =>
      (this.config.get<string>(key) ?? fallback).trim();

    const artifactType = read('APP_UPDATE_ARTIFACT_TYPE', 'zip').toLowerCase() === 'exe' ? 'exe' : 'zip';
    const sizeRaw = Number(read('APP_UPDATE_SIZE_WINDOWS', '0'));

    return {
      latest_version: read('APP_LATEST_VERSION', '0.0.0'),
      min_supported_version: read('APP_MIN_SUPPORTED_VERSION', '0.0.0'),
      mandatory: read('APP_UPDATE_MANDATORY', 'false').toLowerCase() === 'true',
      notes: read('APP_UPDATE_NOTES'),
      published_at: read('APP_UPDATE_PUBLISHED_AT'),
      platforms: {
        windows: {
          artifact_type: artifactType,
          url: read('APP_UPDATE_URL_WINDOWS'),
          sha256: read('APP_UPDATE_SHA256_WINDOWS').toLowerCase(),
          size_bytes: Number.isFinite(sizeRaw) && sizeRaw > 0 ? Math.floor(sizeRaw) : 0,
          entrypoint: read('APP_UPDATE_ENTRYPOINT', 'AITA.exe'),
        },
      },
    };
  }
}
