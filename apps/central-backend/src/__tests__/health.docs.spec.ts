import { ArgumentsHost, ServiceUnavailableException } from '@nestjs/common';
import { ThrottlerStorage } from '@nestjs/throttler';
import { ApiExceptionFilter } from '../common/filters/api-exception.filter';
import { HealthController } from '../modules/health/health.controller';
import { PrismaService } from '../prisma/prisma.service';

describe('Health (docs: docs/testcases/1-unit/Health/Health_testcase.md)', () => {
  function makeController(prisma: any, storage: any): HealthController {
    return new HealthController(prisma as PrismaService, storage as ThrottlerStorage);
  }

  function makeHost(): { host: ArgumentsHost; status: jest.Mock; json: jest.Mock } {
    const json = jest.fn();
    const status = jest.fn().mockReturnValue({ json });
    const host = {
      switchToHttp: () => ({
        getRequest: () => ({ method: 'GET', url: '/api/v1/health' }),
        getResponse: () => ({ status }),
      }),
    } as unknown as ArgumentsHost;
    return { host, status, json };
  }

  describe('UT05_Health_TC001: Kho rate-limit mặc định (in-memory)', () => {
    it('trả 200 với database ok và rate_limit_storage memory', async () => {
      const prisma = { $queryRaw: jest.fn().mockResolvedValue([{ ok: 1 }]) };
      const controller = makeController(prisma, {});
      const result = await controller.health();
      expect(prisma.$queryRaw).toHaveBeenCalled();
      expect(result).toEqual({ message: 'Dịch vụ đang hoạt động', data: { status: 'ok', database: 'ok', rate_limit_storage: 'memory' } });
    });
  });

  describe('UT05_Health_TC002: Lỗi kết nối cơ sở dữ liệu PostgreSQL', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      const prisma = { $queryRaw: jest.fn().mockRejectedValue(new Error('Connection refused')) };
      const controller = makeController(prisma, {});
      const error = await controller.health().catch((e) => e);
      const { host, status, json } = makeHost();
      new ApiExceptionFilter().catch(error, host);
      expect(status).toHaveBeenCalledWith(500);
      expect(json).toHaveBeenCalledWith(expect.objectContaining({ error_code: 'INTERNAL_SERVER_ERROR', message: 'Đã xảy ra lỗi hệ thống.' }));
    });
  });

  describe('UT05_Health_TC003: Kho rate-limit Redis không khả dụng', () => {
    it('trả 503 RATE_LIMIT_STORAGE_UNAVAILABLE', async () => {
      const prisma = { $queryRaw: jest.fn().mockResolvedValue([]) };
      const controller = makeController(prisma, { isRedisStorage: true, isHealthy: false });
      const error = await controller.health().catch((e) => e);
      expect(error).toBeInstanceOf(ServiceUnavailableException);
      expect(error.getStatus()).toBe(503);
      expect(error.getResponse()).toEqual({ error_code: 'RATE_LIMIT_STORAGE_UNAVAILABLE', message: 'Kho rate limit hiện không khả dụng.', details: null });
    });
  });

  describe('UT05_Health_TC004: Kho rate-limit Redis khả dụng (biên)', () => {
    it('trả 200 với rate_limit_storage = redis', async () => {
      const prisma = { $queryRaw: jest.fn().mockResolvedValue([]) };
      const controller = makeController(prisma, { isRedisStorage: true, isHealthy: true });
      const result = await controller.health();
      expect(result.data.rate_limit_storage).toBe('redis');
    });
  });
});
