import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { NestFactory } from '@nestjs/core';
import * as Joi from 'joi';
import 'reflect-metadata';
import {
  GitHubReleaseInfo,
  GitHubReleaseService,
  pickZipAsset,
  releaseToInfo,
  versionFromTag,
} from '../modules/system/github-release.service';
import { SystemController } from '../modules/system/system.controller';
import { SystemService } from '../modules/system/system.service';

describe('System Version (docs: docs/testcases/1-unit/System/System_testcase.md)', () => {
  function makeService(env: Record<string, string>, github?: GitHubReleaseService): SystemService {
    const config = { get: (key: string) => env[key] } as unknown as ConfigService;
    return new SystemService(config, github);
  }

  /** Giả lập GitHubReleaseService: trả release cho trước, hoặc ném lỗi để test nhánh fallback. */
  function stubGithub(release: GitHubReleaseInfo | Error | null): GitHubReleaseService {
    return {
      getLatestRelease: async () => {
        if (release instanceof Error) throw release;
        return release;
      },
    } as unknown as GitHubReleaseService;
  }

  const sampleRelease: GitHubReleaseInfo = {
    version: '1.1.0',
    url: 'https://github.com/x/y/releases/download/v1.1.0-portable/AITA_Grader_v1_portable.zip',
    sha256: 'd'.repeat(64),
    sizeBytes: 123,
    publishedAt: '2026-10-21T00:00:00Z',
    notes: 'AITA Grader v1.1.0',
  };

  describe('UT06_System_TC001: Dựng manifest auto-update từ cấu hình đầy đủ', () => {
    it('trả đúng version, artifact và checksum', async () => {
      const service = makeService({
        APP_LATEST_VERSION: '2.5.0',
        APP_MIN_SUPPORTED_VERSION: '2.0.0',
        APP_UPDATE_MANDATORY: 'true',
        APP_UPDATE_NOTES: '- Sửa lỗi chấm Java',
        APP_UPDATE_PUBLISHED_AT: '2026-10-19T00:00:00Z',
        APP_UPDATE_ARTIFACT_TYPE: 'exe',
        APP_UPDATE_ENTRYPOINT: 'AITA.exe',
        APP_UPDATE_URL_WINDOWS: 'https://github.com/aita/releases/download/v2.5.0/AITA.exe',
        APP_UPDATE_SHA256_WINDOWS: 'A'.repeat(64),
        APP_UPDATE_SIZE_WINDOWS: '10485760',
      });

      const manifest = await service.getVersionManifest();
      expect(manifest.latest_version).toBe('2.5.0');
      expect(manifest.min_supported_version).toBe('2.0.0');
      expect(manifest.mandatory).toBe(true);
      expect(manifest.platforms.windows).toEqual({
        artifact_type: 'exe',
        url: 'https://github.com/aita/releases/download/v2.5.0/AITA.exe',
        sha256: 'a'.repeat(64),
        size_bytes: 10485760,
        entrypoint: 'AITA.exe',
      });
    });
  });

  describe('UT06_System_TC002: Giá trị mặc định khi thiếu cấu hình (biên)', () => {
    it('trả version 0.0.0, artifact zip và entrypoint AITA_Grader_v1.exe', async () => {
      const manifest = await makeService({}).getVersionManifest();
      expect(manifest.latest_version).toBe('0.0.0');
      expect(manifest.min_supported_version).toBe('0.0.0');
      expect(manifest.mandatory).toBe(false);
      expect(manifest.platforms.windows.artifact_type).toBe('zip');
      expect(manifest.platforms.windows.entrypoint).toBe('AITA_Grader_v1.exe');
      expect(manifest.platforms.windows.size_bytes).toBe(0);
    });
  });

  describe('UT06_System_TC003: Cấu hình không hợp lệ được chuẩn hóa an toàn', () => {
    it('artifact_type lạ quy về zip và size âm quy về 0', async () => {
      const manifest = await makeService({
        APP_UPDATE_ARTIFACT_TYPE: 'msi',
        APP_UPDATE_SIZE_WINDOWS: '-100',
      }).getVersionManifest();
      expect(manifest.platforms.windows.artifact_type).toBe('zip');
      expect(manifest.platforms.windows.size_bytes).toBe(0);
    });
  });

  describe('UT06_System_TC004: Controller bọc manifest trong envelope chuẩn', () => {
    it('trả message tiếng Việt và data là manifest', async () => {
      const controller = new SystemController(makeService({ APP_LATEST_VERSION: '2.6.0' }));
      const result = await controller.version();
      expect(result.message).toBe('Lấy thông tin phiên bản thành công');
      expect(result.data.latest_version).toBe('2.6.0');
    });
  });

  describe('UT06_System_TC005: Giá trị đã qua Joi (boolean/number) vẫn dựng được manifest', () => {
    // Lỗi thật đã xảy ra trên production: Joi ép APP_UPDATE_MANDATORY -> boolean và
    // APP_UPDATE_SIZE_WINDOWS -> number, mà ConfigService.get() trả về bản đã ép kiểu
    // trước cả process.env, nên `read()` cũ gọi .trim() thẳng -> TypeError -> GET
    // /system/version trả 500 và tính năng Auto-Update ở Desktop Client im lặng không chạy.
    const schema = Joi.object({
      APP_LATEST_VERSION: Joi.string().optional().allow(''),
      APP_MIN_SUPPORTED_VERSION: Joi.string().optional().allow(''),
      APP_UPDATE_MANDATORY: Joi.boolean().truthy('true').falsy('false').default(false),
      APP_UPDATE_NOTES: Joi.string().optional().allow(''),
      APP_UPDATE_PUBLISHED_AT: Joi.string().optional().allow(''),
      APP_UPDATE_ARTIFACT_TYPE: Joi.string().valid('exe', 'zip').default('zip'),
      APP_UPDATE_ENTRYPOINT: Joi.string().optional().allow(''),
      APP_UPDATE_URL_WINDOWS: Joi.string().uri().optional().allow(''),
      APP_UPDATE_SHA256_WINDOWS: Joi.string().pattern(/^[a-fA-F0-9]{64}$/).optional().allow(''),
      APP_UPDATE_SIZE_WINDOWS: Joi.number().integer().min(0).optional().allow(''),
      APP_UPDATE_SOURCE: Joi.string().valid('github', 'env').allow('').default('env'),
    });

    /** Dựng ConfigService THẬT (qua ConfigModule.forRoot + validationSchema), như lúc chạy. */
    async function withRealConfig<T>(
      env: Record<string, string>,
      run: (config: ConfigService) => T | Promise<T>,
    ): Promise<T> {
      const saved = new Map<string, string | undefined>();
      for (const [key, value] of Object.entries(env)) {
        saved.set(key, process.env[key]);
        process.env[key] = value;
      }

      const dynamicModule = ConfigModule.forRoot({
        isGlobal: true,
        ignoreEnvFile: true,
        validationSchema: schema,
      });
      class ProbeModule {}
      Module({ imports: [dynamicModule] })(ProbeModule);

      const app = await NestFactory.createApplicationContext(ProbeModule, { logger: false });
      try {
        return await run(app.get(ConfigService));
      } finally {
        await app.close();
        for (const [key, value] of saved) {
          if (value === undefined) delete process.env[key];
          else process.env[key] = value;
        }
      }
    }

    it('ConfigService trả boolean/number nhưng manifest vẫn đúng, không ném lỗi', async () => {
      await withRealConfig(
        {
          APP_LATEST_VERSION: '2.6.0',
          APP_UPDATE_MANDATORY: 'true',
          APP_UPDATE_ARTIFACT_TYPE: 'zip',
          APP_UPDATE_ENTRYPOINT: 'AITA_Grader_v1.exe',
          APP_UPDATE_SIZE_WINDOWS: '10485760',
          APP_UPDATE_SHA256_WINDOWS: 'B'.repeat(64),
        },
        async (config) => {
          // Đúng cái bẫy của production: giá trị đọc ra KHÔNG phải chuỗi.
          expect(typeof config.get('APP_UPDATE_MANDATORY')).toBe('boolean');
          expect(typeof config.get('APP_UPDATE_SIZE_WINDOWS')).toBe('number');

          const manifest = await new SystemService(config).getVersionManifest();
          expect(manifest.latest_version).toBe('2.6.0');
          expect(manifest.mandatory).toBe(true);
          expect(manifest.platforms.windows.artifact_type).toBe('zip');
          expect(manifest.platforms.windows.entrypoint).toBe('AITA_Grader_v1.exe');
          expect(manifest.platforms.windows.size_bytes).toBe(10485760);
          expect(manifest.platforms.windows.sha256).toBe('b'.repeat(64));
        },
      );
    });

    it('thiếu cấu hình chỉ còn mặc định Joi (mandatory boolean) vẫn trả false thay vì ném lỗi', async () => {
      await withRealConfig({ APP_UPDATE_MANDATORY: 'false' }, async (config) => {
        const manifest = await new SystemService(config).getVersionManifest();
        expect(manifest.mandatory).toBe(false);
        expect(manifest.platforms.windows.artifact_type).toBe('zip');
        expect(manifest.platforms.windows.size_bytes).toBe(0);
      });
    });
  });

  describe('UT06_System_TC006: Chuyển payload GitHub Releases thành thông tin manifest', () => {
    const payload = {
      tag_name: 'v1.1.0-portable',
      name: 'AITA Grader v1.1.0 (portable)',
      published_at: '2026-10-21T00:00:00Z',
      assets: [
        { name: 'aita_selftest.txt', size: 10, browser_download_url: 'https://example.com/aita_selftest.txt' },
        {
          name: 'AITA_Grader_v1_portable.zip',
          size: 215437452,
          digest: 'sha256:' + 'C'.repeat(64),
          browser_download_url:
            'https://github.com/x/y/releases/download/v1.1.0-portable/AITA_Grader_v1_portable.zip',
        },
      ],
    };

    it('tách version từ tag, ưu tiên asset ZIP và chuẩn hóa digest', () => {
      const info = releaseToInfo(payload);
      expect(info).not.toBeNull();
      expect(info?.version).toBe('1.1.0');
      expect(info?.url).toBe(
        'https://github.com/x/y/releases/download/v1.1.0-portable/AITA_Grader_v1_portable.zip',
      );
      expect(info?.sha256).toBe('c'.repeat(64));
      expect(info?.sizeBytes).toBe(215437452);
      expect(info?.publishedAt).toBe('2026-10-21T00:00:00Z');
      expect(info?.notes).toBe('AITA Grader v1.1.0 (portable)');
    });

    it('tag không có số phiên bản hoặc release thiếu asset ZIP thì trả null', () => {
      expect(versionFromTag('nightly')).toBe('');
      expect(versionFromTag('v2.5.0')).toBe('2.5.0');
      expect(pickZipAsset([{ name: 'AITA_Grader_v1.exe', size: 1 }])).toBeNull();
      expect(releaseToInfo({ tag_name: 'nightly', assets: payload.assets })).toBeNull();
      expect(releaseToInfo({ tag_name: 'v1.0.1', assets: [] })).toBeNull();
    });
  });

  describe('UT06_System_TC007: Manifest tự lấy từ GitHub Release (không cần sửa env)', () => {
    it('dùng version/url/sha256/size của release, giữ entrypoint và min_supported_version của env', async () => {
      const service = makeService(
        {
          APP_UPDATE_SOURCE: 'github',
          APP_MIN_SUPPORTED_VERSION: '1.0.0',
          APP_UPDATE_ENTRYPOINT: 'AITA_Grader_v1.exe',
          APP_LATEST_VERSION: '1.0.0',
          APP_UPDATE_URL_WINDOWS: 'https://example.com/cu.zip',
        },
        stubGithub(sampleRelease),
      );

      const manifest = await service.getVersionManifest();
      expect(manifest.latest_version).toBe('1.1.0');
      expect(manifest.min_supported_version).toBe('1.0.0');
      expect(manifest.notes).toBe('AITA Grader v1.1.0');
      expect(manifest.published_at).toBe('2026-10-21T00:00:00Z');
      expect(manifest.platforms.windows).toEqual({
        artifact_type: 'zip',
        url: sampleRelease.url,
        sha256: sampleRelease.sha256,
        size_bytes: 123,
        entrypoint: 'AITA_Grader_v1.exe',
      });
    });
  });

  describe('UT06_System_TC008: GitHub lỗi hoặc tắt nguồn github thì quay về env', () => {
    it('APP_UPDATE_SOURCE=env thì bỏ qua release, dùng APP_LATEST_VERSION', async () => {
      const service = makeService(
        { APP_UPDATE_SOURCE: 'env', APP_LATEST_VERSION: '9.9.9' },
        stubGithub(sampleRelease),
      );
      expect((await service.getVersionManifest()).latest_version).toBe('9.9.9');
    });

    it('GitHub ném lỗi thì manifest vẫn dựng được từ env (endpoint không 500)', async () => {
      const service = makeService(
        {
          APP_LATEST_VERSION: '1.0.0',
          APP_UPDATE_URL_WINDOWS: 'https://example.com/AITA_Grader_v1_portable.zip',
        },
        stubGithub(new Error('rate limit')),
      );
      const manifest = await service.getVersionManifest();
      expect(manifest.latest_version).toBe('1.0.0');
      expect(manifest.platforms.windows.url).toBe('https://example.com/AITA_Grader_v1_portable.zip');
    });

    it('chưa cấu hình APP_UPDATE_GITHUB_REPO thì không gọi mạng, dùng env', async () => {
      const github = new GitHubReleaseService({ get: () => '' } as unknown as ConfigService);
      const service = makeService({ APP_LATEST_VERSION: '1.2.3' }, github);
      expect((await service.getVersionManifest()).latest_version).toBe('1.2.3');
    });
  });

  describe('UT06_System_TC009: Cache TTL của GitHubReleaseService', () => {
    it('chỉ gọi GitHub một lần trong thời gian TTL', async () => {
      const spy = jest.spyOn(globalThis, 'fetch').mockResolvedValue({
        ok: true,
        json: async () => ({
          tag_name: 'v1.1.0',
          name: 'AITA Grader v1.1.0',
          published_at: '2026-10-21T00:00:00Z',
          assets: [
            {
              name: 'AITA_Grader_v1_portable.zip',
              size: 123,
              digest: 'sha256:' + 'E'.repeat(64),
              browser_download_url: 'https://example.com/AITA_Grader_v1_portable.zip',
            },
          ],
        }),
      } as unknown as Response);

      try {
        const env: Record<string, string> = {
          APP_UPDATE_GITHUB_REPO: 'x/y',
          APP_UPDATE_GITHUB_TTL_SECONDS: '300',
        };
        const service = new GitHubReleaseService({ get: (key: string) => env[key] } as unknown as ConfigService);

        const first = await service.getLatestRelease();
        const second = await service.getLatestRelease();

        expect(first?.version).toBe('1.1.0');
        expect(second?.version).toBe('1.1.0');
        expect(spy).toHaveBeenCalledTimes(1);
      } finally {
        spy.mockRestore();
      }
    });
  });
});
