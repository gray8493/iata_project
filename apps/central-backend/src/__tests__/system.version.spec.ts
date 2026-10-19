import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { NestFactory } from '@nestjs/core';
import * as Joi from 'joi';
import 'reflect-metadata';
import { SystemController } from '../modules/system/system.controller';
import { SystemService } from '../modules/system/system.service';

describe('System Version (docs: docs/testcases/1-unit/System/System_testcase.md)', () => {
  function makeService(env: Record<string, string>): SystemService {
    const config = { get: (key: string) => env[key] } as unknown as ConfigService;
    return new SystemService(config);
  }

  describe('UT06_System_TC001: Dựng manifest auto-update từ cấu hình đầy đủ', () => {
    it('trả đúng version, artifact và checksum', () => {
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

      const manifest = service.getVersionManifest();
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
    it('trả version 0.0.0, artifact zip và entrypoint AITA_Grader_v1.exe', () => {
      const manifest = makeService({}).getVersionManifest();
      expect(manifest.latest_version).toBe('0.0.0');
      expect(manifest.min_supported_version).toBe('0.0.0');
      expect(manifest.mandatory).toBe(false);
      expect(manifest.platforms.windows.artifact_type).toBe('zip');
      expect(manifest.platforms.windows.entrypoint).toBe('AITA_Grader_v1.exe');
      expect(manifest.platforms.windows.size_bytes).toBe(0);
    });
  });

  describe('UT06_System_TC003: Cấu hình không hợp lệ được chuẩn hóa an toàn', () => {
    it('artifact_type lạ quy về zip và size âm quy về 0', () => {
      const manifest = makeService({
        APP_UPDATE_ARTIFACT_TYPE: 'msi',
        APP_UPDATE_SIZE_WINDOWS: '-100',
      }).getVersionManifest();
      expect(manifest.platforms.windows.artifact_type).toBe('zip');
      expect(manifest.platforms.windows.size_bytes).toBe(0);
    });
  });

  describe('UT06_System_TC004: Controller bọc manifest trong envelope chuẩn', () => {
    it('trả message tiếng Việt và data là manifest', () => {
      const controller = new SystemController(makeService({ APP_LATEST_VERSION: '2.6.0' }));
      const result = controller.version();
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
    });

    /** Dựng ConfigService THẬT (qua ConfigModule.forRoot + validationSchema), như lúc chạy. */
    async function withRealConfig<T>(
      env: Record<string, string>,
      run: (config: ConfigService) => T,
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
        return run(app.get(ConfigService));
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
        (config) => {
          // Đúng cái bẫy của production: giá trị đọc ra KHÔNG phải chuỗi.
          expect(typeof config.get('APP_UPDATE_MANDATORY')).toBe('boolean');
          expect(typeof config.get('APP_UPDATE_SIZE_WINDOWS')).toBe('number');

          const manifest = new SystemService(config).getVersionManifest();
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
      await withRealConfig({ APP_UPDATE_MANDATORY: 'false' }, (config) => {
        const manifest = new SystemService(config).getVersionManifest();
        expect(manifest.mandatory).toBe(false);
        expect(manifest.platforms.windows.artifact_type).toBe('zip');
        expect(manifest.platforms.windows.size_bytes).toBe(0);
      });
    });
  });
});
