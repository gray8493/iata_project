import { ConfigService } from '@nestjs/config';
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
    it('trả version 0.0.0, artifact zip và entrypoint AITA.exe', () => {
      const manifest = makeService({}).getVersionManifest();
      expect(manifest.latest_version).toBe('0.0.0');
      expect(manifest.min_supported_version).toBe('0.0.0');
      expect(manifest.mandatory).toBe(false);
      expect(manifest.platforms.windows.artifact_type).toBe('zip');
      expect(manifest.platforms.windows.entrypoint).toBe('AITA.exe');
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
});
