import { ArgumentsHost, HttpException, UnauthorizedException, UnprocessableEntityException } from '@nestjs/common';
import { AuditLogsService } from '../modules/audit-logs/audit-logs.service';
import { ListAiUsageDto } from '../modules/audit-logs/dto/list-ai-usage.dto';
import { PrismaService } from '../prisma/prisma.service';
import { RedisService, REPORTS_OVERVIEW_CACHE_KEY } from '../common/redis.service';
import { createValidationPipe } from '../common/validation/validation-pipe.factory';
import { ApiExceptionFilter } from '../common/filters/api-exception.filter';
import { RolesGuard } from '../common/guards/roles.guard';
import { JwtAuthGuard } from '../modules/auth/guards/jwt-auth.guard';
import { JwtStrategy } from '../modules/auth/strategies/jwt.strategy';

describe('AuditLogsService / guards (docs: docs/testcases/1-unit/Reports/Reports_testcase.md)', () => {
  let service: AuditLogsService;
  let prisma: any;
  let redis: any;

  beforeEach(() => {
    prisma = {
      user: { count: jest.fn() },
      aiQuotaConfig: { aggregate: jest.fn() },
      aiQuotaLog: { aggregate: jest.fn(), groupBy: jest.fn(), findMany: jest.fn(), count: jest.fn() },
      $transaction: jest.fn((operations: Promise<unknown>[]) => Promise.all(operations)),
    };
    redis = {
      getJson: jest.fn().mockResolvedValue(null),
      setJson: jest.fn().mockResolvedValue(undefined),
    };
    service = new AuditLogsService(prisma as unknown as PrismaService, redis as unknown as RedisService);
  });

  afterEach(() => jest.clearAllMocks());

  function expectedDaysInMonth(): number {
    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 0)).getUTCDate();
  }

  async function validateQuery(value: unknown): Promise<unknown> {
    const pipe = createValidationPipe();
    return pipe.transform(value, { type: 'query', metatype: ListAiUsageDto, data: '' });
  }

  async function validationError(value: unknown): Promise<UnprocessableEntityException> {
    try {
      await validateQuery(value);
    } catch (error) {
      if (error instanceof UnprocessableEntityException) return error;
      throw error;
    }
    throw new Error('Expected ValidationPipe to reject the payload');
  }

  function makeHost(): { host: ArgumentsHost; status: jest.Mock; json: jest.Mock } {
    const json = jest.fn();
    const status = jest.fn().mockReturnValue({ json });
    const host = {
      switchToHttp: () => ({
        getRequest: () => ({ method: 'GET', url: '/api/v1/admin/reports/overview' }),
        getResponse: () => ({ status }),
      }),
    } as unknown as ArgumentsHost;
    return { host, status, json };
  }

  // -------------------------------------------------------------------------
  // PHẦN 1: GET /api/v1/admin/reports/overview
  // -------------------------------------------------------------------------

  describe('UT04_ReportsOverview_TC001: Báo cáo tổng quan khi có dữ liệu', () => {
    it('trả về số giảng viên, token tiêu thụ và tính năng dùng nhiều nhất', async () => {
      prisma.user.count.mockResolvedValue(24);
      prisma.aiQuotaConfig.aggregate.mockResolvedValue({ _sum: { dailyTokenLimit: 200000 } });
      prisma.aiQuotaLog.aggregate.mockResolvedValue({ _sum: { totalTokens: 1285000 } });
      prisma.aiQuotaLog.groupBy.mockResolvedValue([{ featureType: 'TESTCASE_GEN', _sum: { totalTokens: 750000 } }]);

      const result = await service.overview();

      expect(result.message).toBe('Lấy số liệu thống kê tổng quan thành công');
      expect(result.data.total_instructors).toBe(24);
      expect(result.data.ai_token_usage.total_tokens_consumed_month).toBe(1285000);
      expect(result.data.ai_token_usage.top_consuming_feature).toBe('TESTCASE_GEN');
      expect(result.data.ai_token_usage.total_budget_limit).toBe(200000 * expectedDaysInMonth());
      expect(redis.setJson).toHaveBeenCalledWith(REPORTS_OVERVIEW_CACHE_KEY, result, 45);
    });
  });

  describe('UT04_ReportsOverview_TC002: CSDL rỗng (Biên 0)', () => {
    it('quy các giá trị null/rỗng về 0 và top_consuming_feature = null', async () => {
      prisma.user.count.mockResolvedValue(0);
      prisma.aiQuotaConfig.aggregate.mockResolvedValue({ _sum: { dailyTokenLimit: null } });
      prisma.aiQuotaLog.aggregate.mockResolvedValue({ _sum: { totalTokens: null } });
      prisma.aiQuotaLog.groupBy.mockResolvedValue([]);

      const result = await service.overview();

      expect(result.data.total_instructors).toBe(0);
      expect(result.data.ai_token_usage.total_tokens_consumed_month).toBe(0);
      expect(result.data.ai_token_usage.total_budget_limit).toBe(0);
      expect(result.data.ai_token_usage.top_consuming_feature).toBeNull();
    });
  });

  describe('UT04_ReportsOverview_TC003: Hạn mức tháng chỉ tính Instructor đang hoạt động', () => {
    it('lọc quota theo role INSTRUCTOR, isActive true, isDeleted false', async () => {
      prisma.user.count.mockResolvedValue(0);
      prisma.aiQuotaConfig.aggregate.mockResolvedValue({ _sum: { dailyTokenLimit: 0 } });
      prisma.aiQuotaLog.aggregate.mockResolvedValue({ _sum: { totalTokens: 0 } });
      prisma.aiQuotaLog.groupBy.mockResolvedValue([]);

      await service.overview();

      expect(prisma.aiQuotaConfig.aggregate).toHaveBeenCalledWith(expect.objectContaining({
        where: { isDeleted: false, user: { role: 'INSTRUCTOR', isActive: true, isDeleted: false } },
      }));
    });
  });

  describe('UT04_ReportsOverview_TC004: Trả kết quả từ cache Redis', () => {
    it('không truy vấn CSDL khi cache còn hiệu lực', async () => {
      const cached = {
        message: 'Lấy số liệu thống kê tổng quan thành công',
        data: { total_instructors: 5, ai_token_usage: { total_tokens_consumed_month: 10, total_budget_limit: 100, top_consuming_feature: 'CODE_REVIEW' } },
      };
      redis.getJson.mockResolvedValue(cached);

      const result = await service.overview();

      expect(result).toBe(cached);
      expect(prisma.user.count).not.toHaveBeenCalled();
      expect(prisma.aiQuotaLog.aggregate).not.toHaveBeenCalled();
      expect(prisma.aiQuotaConfig.aggregate).not.toHaveBeenCalled();
    });
  });

  describe('UT04_ReportsOverview_TC005: Lỗi máy chủ nội bộ khi CSDL ngắt kết nối', () => {
    it('ApiExceptionFilter ánh xạ lỗi không phải HttpException thành 500 INTERNAL_SERVER_ERROR', async () => {
      prisma.user.count.mockRejectedValue(new Error('Connection refused'));

      await expect(service.overview()).rejects.toThrow('Connection refused');

      const { host, status, json } = makeHost();
      const error = await service.overview().catch((e) => e);
      new ApiExceptionFilter().catch(error, host);

      expect(status).toHaveBeenCalledWith(500);
      expect(json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        status_code: 500,
        error_code: 'INTERNAL_SERVER_ERROR',
        message: 'Đã xảy ra lỗi hệ thống.',
        details: null,
      }));
    });
  });

  describe('UT04_ReportsOverview_TC006: Không cung cấp Token xác thực', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, undefined); } catch (e) { return e; } })() as UnauthorizedException;
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getStatus()).toBe(401);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
    });
  });

  describe('UT04_ReportsOverview_TC007: Token đã hết hạn', () => {
    it('trả 401 AUTH_TOKEN_EXPIRED', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, { name: 'TokenExpiredError' }); } catch (e) { return e; } })() as UnauthorizedException;
      expect(error.getStatus()).toBe(401);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_TOKEN_EXPIRED', message: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.', details: null });
    });
  });

  describe('UT04_ReportsOverview_TC008: Token sai chữ ký', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, { name: 'JsonWebTokenError' }); } catch (e) { return e; } })() as UnauthorizedException;
      expect(error.getStatus()).toBe(401);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
    });
  });

  describe('UT04_ReportsOverview_TC009: Dùng Refresh Token làm Access Token', () => {
    it('JwtStrategy.validate ném 401 AUTH_INVALID_TOKEN khi token_type != access', async () => {
      const strategy = new JwtStrategy({ getOrThrow: () => 'x'.repeat(32) } as any, { user: { findFirst: jest.fn() } } as any);
      const error = await strategy.validate({ id: 'u1', username: 'admin', role: 'ADMIN', token_type: 'refresh' } as any).catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.' });
    });
  });

  describe('UT04_ReportsOverview_TC010: Tài khoản không còn hoạt động', () => {
    it('JwtStrategy.validate ném 401 AUTH_ACCOUNT_DISABLED khi user không tồn tại', async () => {
      const strategy = new JwtStrategy({ getOrThrow: () => 'x'.repeat(32) } as any, { user: { findFirst: jest.fn().mockResolvedValue(null) } } as any);
      const error = await strategy.validate({ id: 'deleted', username: 'admin', role: 'ADMIN', token_type: 'access' } as any).catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản không còn hoạt động.' });
    });
  });

  describe('UT04_ReportsOverview_TC011: Giảng viên không có quyền xem báo cáo', () => {
    it('RolesGuard ném 403 FORBIDDEN_ADMIN_ONLY với role INSTRUCTOR', () => {
      const reflector = { getAllAndOverride: jest.fn().mockReturnValue(['ADMIN']) } as any;
      const guard = new RolesGuard(reflector);
      const context = {
        getHandler: () => ({}), getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => ({ user: { id: '1', username: 'teacher_hung', role: 'INSTRUCTOR' } }) }),
      } as any;

      const error = (() => { try { guard.canActivate(context); } catch (e) { return e; } })() as HttpException;
      expect(error.getStatus()).toBe(403);
      expect(error.getResponse()).toEqual({ error_code: 'FORBIDDEN_ADMIN_ONLY', message: 'Bạn không có quyền thực hiện thao tác này.', details: null });
    });
  });

  // -------------------------------------------------------------------------
  // PHẦN 2: GET /api/v1/admin/reports/ai-usage
  // -------------------------------------------------------------------------

  describe('UT04_ReportsAiUsage_TC001: Nhật ký với tham số mặc định', () => {
    it('trả về items và pagination đúng định dạng', async () => {
      const log = {
        id: 'log-1', userId: 'u1', featureType: 'TESTCASE_GEN', modelName: 'gemini-3.8-flash',
        promptTokens: 500, completionTokens: 200, totalTokens: 700, createdAt: new Date('2026-10-14T10:00:00.000Z'),
        user: { username: 'instructor1', fullName: 'Thầy An' },
      };
      prisma.aiQuotaLog.findMany.mockResolvedValue([log]);
      prisma.aiQuotaLog.count.mockResolvedValue(1);

      const result = await service.listAiUsage({ page: 1, page_size: 20 });

      expect(result.message).toBe('Lấy nhật ký sử dụng AI thành công');
      expect(result.data.items[0]).toEqual(expect.objectContaining({
        id: 'log-1', user_id: 'u1', username: 'instructor1', full_name: 'Thầy An',
        feature_type: 'TESTCASE_GEN', model_name: 'gemini-3.8-flash',
        prompt_tokens: 500, completion_tokens: 200, total_tokens: 700,
        created_at: '2026-10-14T10:00:00.000Z',
      }));
      expect(result.data.pagination).toEqual({ page: 1, page_size: 20, total_items: 1, total_pages: 1 });
    });
  });

  describe('UT04_ReportsAiUsage_TC002: Lọc theo giảng viên', () => {
    it('đưa userId vào điều kiện where', async () => {
      prisma.aiQuotaLog.findMany.mockResolvedValue([]);
      prisma.aiQuotaLog.count.mockResolvedValue(0);

      await service.listAiUsage({ page: 1, page_size: 20, user_id: '550e8400-e29b-41d4-a716-446655440000' });

      expect(prisma.aiQuotaLog.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: expect.objectContaining({ isDeleted: false, userId: '550e8400-e29b-41d4-a716-446655440000' }),
      }));
    });
  });

  describe('UT04_ReportsAiUsage_TC003: Lọc theo khoảng thời gian (gte/lte)', () => {
    it('đưa from/to vào createdAt dạng bao gồm hai mốc', async () => {
      prisma.aiQuotaLog.findMany.mockResolvedValue([]);
      prisma.aiQuotaLog.count.mockResolvedValue(0);

      await service.listAiUsage({ page: 1, page_size: 20, from: '2026-10-01T00:00:00.000Z', to: '2026-10-31T23:59:59.000Z' });

      expect(prisma.aiQuotaLog.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: expect.objectContaining({
          createdAt: { gte: new Date('2026-10-01T00:00:00.000Z'), lte: new Date('2026-10-31T23:59:59.000Z') },
        }),
      }));
    });
  });

  describe('UT04_ReportsAiUsage_TC004: page_size = 100 (biên trên hợp lệ)', () => {
    it('tính skip và take chính xác, không ném lỗi validation', async () => {
      prisma.aiQuotaLog.findMany.mockResolvedValue([]);
      prisma.aiQuotaLog.count.mockResolvedValue(0);

      const result = await service.listAiUsage({ page: 1, page_size: 100 });

      expect(prisma.aiQuotaLog.findMany).toHaveBeenCalledWith(expect.objectContaining({ skip: 0, take: 100 }));
      expect(result.data.pagination.page_size).toBe(100);
    });
  });

  describe('UT04_ReportsAiUsage_TC005: Không có bản ghi khớp bộ lọc', () => {
    it('trả items rỗng và total_pages = 0', async () => {
      prisma.aiQuotaLog.findMany.mockResolvedValue([]);
      prisma.aiQuotaLog.count.mockResolvedValue(0);

      const result = await service.listAiUsage({ page: 1, page_size: 20 });

      expect(result.data.items).toEqual([]);
      expect(result.data.pagination).toEqual({ page: 1, page_size: 20, total_items: 0, total_pages: 0 });
    });
  });

  describe('UT04_ReportsAiUsage_TC006: page_size = 101 vượt biên trên', () => {
    it('ValidationPipe ném 422 VALIDATION_FAILED với field page_size', async () => {
      const error = await validationError({ page: 1, page_size: 101 });
      expect(error).toBeInstanceOf(UnprocessableEntityException);
      const body = error.getResponse() as any;
      expect(body.error_code).toBe('VALIDATION_FAILED');
      expect(body.message).toBe('Dữ liệu gửi lên không đúng định dạng.');
      expect(body.details[0].field).toBe('page_size');
      expect(body.details[0].issues.length).toBeGreaterThan(0);
    });
  });

  describe('UT04_ReportsAiUsage_TC007: page = 0 vi phạm biên dưới', () => {
    it('ValidationPipe ném 422 VALIDATION_FAILED với field page', async () => {
      const error = await validationError({ page: 0, page_size: 20 });
      expect(error).toBeInstanceOf(UnprocessableEntityException);
      const body = error.getResponse() as any;
      expect(body.error_code).toBe('VALIDATION_FAILED');
      expect(body.details[0].field).toBe('page');
    });
  });

  describe('UT04_ReportsAiUsage_TC008: from > to', () => {
    it('ném 400 INVALID_DATE_RANGE', async () => {
      const error = await service.listAiUsage({ page: 1, page_size: 20, from: '2026-10-20', to: '2026-10-10' }).catch((e) => e);
      expect(error).toBeInstanceOf(HttpException);
      expect(error.getStatus()).toBe(400);
      expect(error.getResponse()).toEqual({
        error_code: 'INVALID_DATE_RANGE',
        message: 'Thời điểm bắt đầu phải nhỏ hơn hoặc bằng thời điểm kết thúc.',
        details: null,
      });
    });
  });

  describe('UT04_ReportsAiUsage_TC009: user_id không phải UUID', () => {
    it('ValidationPipe ném 422 VALIDATION_FAILED với field user_id', async () => {
      const error = await validationError({ page: 1, page_size: 20, user_id: 'not-a-uuid' });
      expect(error).toBeInstanceOf(UnprocessableEntityException);
      expect((error.getResponse() as any).details[0].field).toBe('user_id');
    });
  });

  describe('UT04_ReportsAiUsage_TC010: from sai định dạng ISO', () => {
    it('ValidationPipe ném 422 VALIDATION_FAILED với field from', async () => {
      const error = await validationError({ page: 1, page_size: 20, from: '31-10-2026' });
      expect(error).toBeInstanceOf(UnprocessableEntityException);
      expect((error.getResponse() as any).details[0].field).toBe('from');
    });
  });

  describe('UT04_ReportsAiUsage_TC011: Không cung cấp Token xác thực', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, undefined); } catch (e) { return e; } })() as UnauthorizedException;
      expect(error.getStatus()).toBe(401);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
    });
  });

  describe('UT04_ReportsAiUsage_TC012: Giảng viên không có quyền tra cứu nhật ký', () => {
    it('RolesGuard ném 403 FORBIDDEN_ADMIN_ONLY', () => {
      const reflector = { getAllAndOverride: jest.fn().mockReturnValue(['ADMIN']) } as any;
      const guard = new RolesGuard(reflector);
      const context = {
        getHandler: () => ({}), getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => ({ user: { id: '1', username: 'teacher_hung', role: 'INSTRUCTOR' } }) }),
      } as any;
      const error = (() => { try { guard.canActivate(context); } catch (e) { return e; } })() as HttpException;
      expect(error.getStatus()).toBe(403);
      expect(error.getResponse()).toEqual({ error_code: 'FORBIDDEN_ADMIN_ONLY', message: 'Bạn không có quyền thực hiện thao tác này.', details: null });
    });
  });
});
