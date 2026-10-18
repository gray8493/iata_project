import { ConflictException, ForbiddenException, HttpException, UnauthorizedException } from '@nestjs/common';
import { Prisma } from '@prisma/client';
import * as bcrypt from 'bcrypt';
import { UsersService } from '../modules/users/users.service';
import { AuthService } from '../modules/auth/auth.service';
import { AuditLogsService } from '../modules/audit-logs/audit-logs.service';
import { AiQuotaService } from '../modules/ai-gateway/ai-quota.service';
import { OpenRouterService } from '../modules/ai-gateway/openrouter.service';
import { PrismaService } from '../prisma/prisma.service';
import { RedisService, REPORTS_OVERVIEW_CACHE_KEY } from '../common/redis.service';
import { RolesGuard } from '../common/guards/roles.guard';
import { JwtStrategy } from '../modules/auth/strategies/jwt.strategy';

describe('Integration (docs: docs/testcases/2-integration/Testcase_integration.md)', () => {
  let prisma: any;
  let redis: any;
  let users: UsersService;
  let auth: AuthService;
  let reports: AuditLogsService;
  const jwtMock = { signAsync: jest.fn(), verifyAsync: jest.fn(), decode: jest.fn() };
  const configMock = {
    get: jest.fn((_key: string, def?: string) => def),
    getOrThrow: jest.fn((key: string) => `secret_for_${key}`),
  };

  function todayUtc(): Date {
    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  }

  beforeEach(() => {
    prisma = {
      user: { findFirst: jest.fn(), findMany: jest.fn(), create: jest.fn(), update: jest.fn(), count: jest.fn() },
      aiQuotaConfig: { create: jest.fn(), upsert: jest.fn(), findFirst: jest.fn(), findUnique: jest.fn(), updateMany: jest.fn(), update: jest.fn(), aggregate: jest.fn() },
      aiQuotaLog: { create: jest.fn(), findMany: jest.fn(), count: jest.fn(), aggregate: jest.fn(), groupBy: jest.fn() },
      refreshToken: { findFirst: jest.fn(), updateMany: jest.fn(), create: jest.fn() },
      $transaction: jest.fn((arg: any) => (typeof arg === 'function' ? arg(prisma) : Promise.all(arg))),
    };
    redis = { getJson: jest.fn().mockResolvedValue(null), setJson: jest.fn().mockResolvedValue(undefined), del: jest.fn().mockResolvedValue(undefined) };
    users = new UsersService(prisma as unknown as PrismaService);
    auth = new AuthService(prisma as unknown as PrismaService, jwtMock as any, configMock as any);
    reports = new AuditLogsService(prisma as unknown as PrismaService, redis as unknown as RedisService);
    jest.spyOn(bcrypt, 'hash').mockResolvedValue('hashed-password' as never);
    jest.spyOn(bcrypt, 'compare').mockResolvedValue(true as never);
  });

  afterEach(() => jest.restoreAllMocks());

  // -------------------------------------------------------------------------
  // IT01 - Vòng đời người dùng + cấu hình hạn ngạch
  // -------------------------------------------------------------------------

  describe('IT01_UserLifecycle_TC001: Tạo tài khoản Giảng viên kèm cấu hình hạn ngạch', () => {
    it('tạo user và aiQuotaConfig trong cùng một transaction', async () => {
      prisma.user.create.mockResolvedValue({
        id: 'u-new', username: 'teacher_an', fullName: 'Nguyễn An', email: 'an@example.com', role: 'INSTRUCTOR',
        isActive: true, createdAt: new Date('2026-10-17T00:00:00.000Z'), quotaConfig: { dailyTokenLimit: 80000, usedTokensToday: 0 },
      });
      prisma.aiQuotaConfig.create.mockResolvedValue({ id: 'q-new' });

      const result = await users.create({
        username: 'teacher_an', password: 'Abc12345', full_name: 'Nguyễn An', email: 'AN@example.com', role: 'INSTRUCTOR', daily_token_quota: 80000,
      } as any);

      expect(prisma.$transaction).toHaveBeenCalled();
      expect(prisma.user.create).toHaveBeenCalledWith(expect.objectContaining({
        data: expect.objectContaining({ username: 'teacher_an', email: 'an@example.com', role: 'INSTRUCTOR' }),
      }));
      expect(prisma.aiQuotaConfig.create).toHaveBeenCalledWith(expect.objectContaining({
        data: expect.objectContaining({ userId: 'u-new', dailyTokenLimit: 80000 }),
      }));
      expect(result.message).toBe('Tạo tài khoản người dùng mới thành công');
      expect(result.data.role).toBe('INSTRUCTOR');
      expect(result.data.daily_token_quota).toBe(80000);
    });
  });

  describe('IT01_UserLifecycle_TC002: Tạo tài khoản trùng username/email (rollback)', () => {
    it('ánh xạ lỗi P2002 thành 409 USER_ALREADY_EXISTS', async () => {
      prisma.user.create.mockRejectedValue(new Prisma.PrismaClientKnownRequestError('Unique constraint failed', { code: 'P2002', clientVersion: '5.22.0' }));

      const error = await users.create({ username: 'teacher_an', password: 'Abc12345', full_name: 'Nguyễn An', email: 'an@example.com', role: 'INSTRUCTOR' } as any).catch((e) => e);

      expect(error).toBeInstanceOf(ConflictException);
      expect(error.getStatus()).toBe(409);
      expect(error.getResponse()).toEqual({ error_code: 'USER_ALREADY_EXISTS', message: 'Tên đăng nhập hoặc email đã tồn tại.', details: null });
    });
  });

  // -------------------------------------------------------------------------
  // IT02 - Khóa tài khoản + thu hồi token
  // -------------------------------------------------------------------------

  describe('IT02_DisableRevoke_TC001: Khóa tài khoản thì vô hiệu hóa refresh token', () => {
    it('set isActive=false và thu hồi toàn bộ refresh token chưa bị thu hồi', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: 'u1', role: 'INSTRUCTOR', isActive: true });
      prisma.user.update.mockResolvedValue({ id: 'u1', username: 'teacher_an', fullName: 'Nguyễn An', email: 'an@example.com', role: 'INSTRUCTOR', isActive: false, createdAt: new Date(), updatedAt: new Date(), quotaConfig: null });
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 2 });

      await users.update('u1', { is_active: false } as any, 'admin-1');

      expect(prisma.user.update).toHaveBeenCalledWith(expect.objectContaining({
        where: { id: 'u1' }, data: expect.objectContaining({ isActive: false }),
      }));
      expect(prisma.refreshToken.updateMany).toHaveBeenCalledWith(expect.objectContaining({
        where: { userId: 'u1', revokedAt: null }, data: expect.objectContaining({ revokedAt: expect.any(Date) }),
      }));
    });
  });

  describe('IT02_DisableRevoke_TC002: Access token của tài khoản đã khóa bị từ chối', () => {
    it('JwtStrategy.validate ném 401 AUTH_ACCOUNT_DISABLED', async () => {
      const strategy = new JwtStrategy({ getOrThrow: () => 'x'.repeat(32) } as any, { user: { findFirst: jest.fn().mockResolvedValue(null) } } as any);
      const error = await strategy.validate({ id: 'u1', username: 'teacher_an', role: 'INSTRUCTOR', token_type: 'access' } as any).catch((e) => e);

      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getStatus()).toBe(401);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản không còn hoạt động.' });
    });
  });

  // -------------------------------------------------------------------------
  // IT03 - Cấp hạn ngạch qua cập nhật người dùng
  // -------------------------------------------------------------------------

  describe('IT03_QuotaAllocation_TC001: Admin cấp/đổi hạn ngạch qua PUT users/:id', () => {
    it('upsert cấu hình hạn ngạch trong transaction cập nhật', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: 'u1', role: 'INSTRUCTOR', isActive: true });
      prisma.user.update.mockResolvedValue({ id: 'u1', username: 'teacher_an', fullName: 'Nguyễn An', email: 'an@example.com', role: 'INSTRUCTOR', isActive: true, createdAt: new Date(), updatedAt: new Date(), quotaConfig: { dailyTokenLimit: 120000, usedTokensToday: 0 } });
      prisma.aiQuotaConfig.upsert.mockResolvedValue({ id: 'q1' });

      const result = await users.update('u1', { daily_token_quota: 120000 } as any, 'admin-1');

      expect(prisma.aiQuotaConfig.upsert).toHaveBeenCalledWith(expect.objectContaining({
        where: { userId: 'u1' },
        create: expect.objectContaining({ userId: 'u1', dailyTokenLimit: 120000 }),
        update: expect.objectContaining({ dailyTokenLimit: 120000, isDeleted: false }),
      }));
      expect(result.data.daily_token_quota).toBe(120000);
    });
  });

  // -------------------------------------------------------------------------
  // IT04 - Đăng nhập + đồng bộ hạn ngạch
  // -------------------------------------------------------------------------

  describe('IT04_AuthQuotaSync_TC001: Đăng nhập rồi truy vấn hạn ngạch còn lại', () => {
    it('login trả tokens và quota snapshot khớp remaining', async () => {
      const user = { id: 'u1', username: 'teacher_an', fullName: 'Nguyễn An', email: 'an@example.com', role: 'INSTRUCTOR', isActive: true, isDeleted: false, passwordHash: 'hashed-password' };
      prisma.user.findFirst.mockResolvedValue(user);
      jwtMock.signAsync.mockResolvedValue('signed-token');
      jwtMock.decode.mockReturnValue({ exp: Math.floor(Date.now() / 1000) + 604800 });
      prisma.refreshToken.create.mockResolvedValue({});

      const login = await auth.login({ username: 'teacher_an', password: 'Abc12345' } as any);
      expect(login.data.expires_in).toBe(900);
      expect(login.data.user.role).toBe('INSTRUCTOR');

      const quota = new AiQuotaService(prisma as unknown as PrismaService, redis as unknown as RedisService);
      prisma.aiQuotaConfig.findFirst.mockResolvedValue({ id: 'q1', userId: 'u1', dailyTokenLimit: 50000, usedTokensToday: 12000, lastResetDate: todayUtc(), isDeleted: false });
      prisma.aiQuotaConfig.findUnique.mockResolvedValue({ id: 'q1', dailyTokenLimit: 50000, usedTokensToday: 12000, lastResetDate: todayUtc(), isDeleted: false });

      const snapshot = await quota.snapshot('u1');
      expect(snapshot).toEqual(expect.objectContaining({ daily_limit_tokens: 50000, used_tokens_today: 12000, remaining_tokens: 38000 }));
    });
  });

  // -------------------------------------------------------------------------
  // IT15 - Báo cáo Admin
  // -------------------------------------------------------------------------

  describe('IT15_ReportOverview_TC001: Báo cáo tổng quan tổng hợp nhiều bảng', () => {
    it('tính tổng ngân sách tháng từ daily limit và ghi cache Redis', async () => {
      prisma.user.count.mockResolvedValue(12);
      prisma.aiQuotaConfig.aggregate.mockResolvedValue({ _sum: { dailyTokenLimit: 200000 } });
      prisma.aiQuotaLog.aggregate.mockResolvedValue({ _sum: { totalTokens: 1285000 } });
      prisma.aiQuotaLog.groupBy.mockResolvedValue([{ featureType: 'TESTCASE_GEN', _sum: { totalTokens: 750000 } }]);

      const result = await reports.overview();
      const now = new Date();
      const daysInMonth = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 0)).getUTCDate();

      expect(result.data.total_instructors).toBe(12);
      expect(result.data.ai_token_usage.total_tokens_consumed_month).toBe(1285000);
      expect(result.data.ai_token_usage.total_budget_limit).toBe(200000 * daysInMonth);
      expect(result.data.ai_token_usage.top_consuming_feature).toBe('TESTCASE_GEN');
      expect(redis.setJson).toHaveBeenCalledWith(REPORTS_OVERVIEW_CACHE_KEY, result, 45);
    });
  });

  describe('IT15_ReportAiUsage_TC002: Lọc nhật ký theo giảng viên và khoảng ngày', () => {
    it('đưa userId và createdAt(gte/lte) vào where, tính pagination', async () => {
      prisma.aiQuotaLog.findMany.mockResolvedValue([{
        id: 'log-1', userId: 'u1', featureType: 'TESTCASE_GEN', modelName: 'gemini-3.8-flash',
        promptTokens: 500, completionTokens: 200, totalTokens: 700, createdAt: new Date('2026-10-14T10:00:00.000Z'),
        user: { username: 'teacher_an', fullName: 'Nguyễn An' },
      }]);
      prisma.aiQuotaLog.count.mockResolvedValue(21);

      const result = await reports.listAiUsage({ page: 1, page_size: 20, user_id: '550e8400-e29b-41d4-a716-446655440000', from: '2026-10-01T00:00:00.000Z', to: '2026-10-31T23:59:59.000Z' } as any);

      expect(prisma.aiQuotaLog.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: expect.objectContaining({ isDeleted: false, userId: '550e8400-e29b-41d4-a716-446655440000', createdAt: { gte: new Date('2026-10-01T00:00:00.000Z'), lte: new Date('2026-10-31T23:59:59.000Z') } }),
      }));
      expect(result.data.pagination).toEqual({ page: 1, page_size: 20, total_items: 21, total_pages: 2 });
    });
  });

  describe('IT15_ReportAiUsage_TC003: Khoảng ngày không hợp lệ', () => {
    it('ném 400 INVALID_DATE_RANGE khi from > to', async () => {
      const error = await reports.listAiUsage({ page: 1, page_size: 20, from: '2026-10-20', to: '2026-10-10' } as any).catch((e) => e);
      expect(error).toBeInstanceOf(HttpException);
      expect(error.getStatus()).toBe(400);
      expect(error.getResponse()).toEqual({ error_code: 'INVALID_DATE_RANGE', message: 'Thời điểm bắt đầu phải nhỏ hơn hoặc bằng thời điểm kết thúc.', details: null });
    });
  });

  // -------------------------------------------------------------------------
  // IT16 - Khả năng chịu lỗi của nhà cung cấp AI
  // -------------------------------------------------------------------------

  describe('IT16_AiResilience_TC001: Lỗi nhà cung cấp AI được hoàn hạn ngạch', () => {
    it('ném 502 AI_PROVIDER_ERROR và release phần đã giữ chỗ', async () => {
      const quota = { reserve: jest.fn().mockResolvedValue({ configId: 'q1', reserved: 600, date: todayUtc() }), release: jest.fn().mockResolvedValue(undefined), settle: jest.fn() };
      const aiConfig = { get: jest.fn((key: string, def?: string) => (key === 'OPENROUTER_API_KEYS' ? 'test-key' : def)), getOrThrow: jest.fn() };
      const provider = new OpenRouterService(aiConfig as any, quota as unknown as AiQuotaService);
      (provider as any).post = jest.fn().mockRejectedValue({ status: 503 });

      const error = await provider.generateJson({ userId: 'u1', feature: 'TESTCASE_GEN', prompt: 'p'.repeat(40), schema: {} as any, maxOutputTokens: 100 }).catch((e) => e);

      expect(error).toBeInstanceOf(HttpException);
      expect(error.getStatus()).toBe(502);
      expect(error.getResponse()).toEqual({ error_code: 'AI_PROVIDER_ERROR', message: 'Không thể nhận phản hồi từ dịch vụ AI.', details: null });
      expect(quota.release).toHaveBeenCalledWith(expect.objectContaining({ configId: 'q1' }));
    });
  });

  // -------------------------------------------------------------------------
  // IT17 - Chặn khi vượt hạn ngạch
  // -------------------------------------------------------------------------

  describe('IT17_QuotaGuard_TC001: Chặn khi vượt hạn ngạch trong ngày', () => {
    it('ném 429 AI_QUOTA_EXCEEDED khi usedTokensToday vượt trần', async () => {
      prisma.aiQuotaConfig.findFirst.mockResolvedValue({ id: 'q1', userId: 'u1', dailyTokenLimit: 1000, usedTokensToday: 900, lastResetDate: todayUtc(), isDeleted: false });
      prisma.aiQuotaConfig.findUnique.mockResolvedValue({ id: 'q1', dailyTokenLimit: 1000, usedTokensToday: 900, lastResetDate: todayUtc(), isDeleted: false });
      prisma.aiQuotaConfig.updateMany.mockResolvedValue({ count: 0 });
      const quota = new AiQuotaService(prisma as unknown as PrismaService, redis as unknown as RedisService);

      const error = await quota.reserve('u1', 200).catch((e) => e);

      expect(error).toBeInstanceOf(HttpException);
      expect(error.getStatus()).toBe(429);
      expect(error.getResponse()).toEqual({ error_code: 'AI_QUOTA_EXCEEDED', message: 'Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.', details: null });
    });
  });

  // -------------------------------------------------------------------------
  // IT21 - Phân quyền chéo module
  // -------------------------------------------------------------------------

  describe('IT21_RbacBlock_TC001: Phân quyền chéo module', () => {
    function forbiddenFor(requiredRoles: string[], userRole: string) {
      const reflector = { getAllAndOverride: jest.fn().mockReturnValue(requiredRoles) } as any;
      const context = {
        getHandler: () => ({}), getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => ({ user: { id: '1', username: 'someone', role: userRole } }) }),
      } as any;
      return (() => { try { new RolesGuard(reflector).canActivate(context); } catch (e) { return e as any; } })();
    }

    it('INSTRUCTOR gọi endpoint ADMIN và ADMIN gọi endpoint INSTRUCTOR đều bị 403', () => {
      const instructorError = forbiddenFor(['ADMIN'], 'INSTRUCTOR');
      const adminError = forbiddenFor(['INSTRUCTOR'], 'ADMIN');
      for (const error of [instructorError, adminError]) {
        expect(error).toBeInstanceOf(ForbiddenException);
        expect(error.getStatus()).toBe(403);
        expect(error.getResponse()).toEqual({ error_code: 'FORBIDDEN_ADMIN_ONLY', message: 'Bạn không có quyền thực hiện thao tác này.', details: null });
      }
    });
  });

  // -------------------------------------------------------------------------
  // IT22 - Luân chuyển refresh token
  // -------------------------------------------------------------------------

  describe('IT22_RefreshRotation_TC001: Luân chuyển refresh token', () => {
    it('thu hồi token cũ và cấp cặp token mới', async () => {
      jwtMock.verifyAsync.mockResolvedValue({ id: 'u1', username: 'teacher_an', role: 'INSTRUCTOR', token_type: 'refresh', jti: 'jti-1' });
      jwtMock.signAsync.mockResolvedValue('new-signed-token');
      jwtMock.decode.mockReturnValue({ exp: Math.floor(Date.now() / 1000) + 604800 });
      prisma.refreshToken.findFirst.mockResolvedValue({ id: 'jti-1', tokenHash: 'hash', userId: 'u1', revokedAt: null, expiresAt: new Date(Date.now() + 3600_000), user: { id: 'u1', username: 'teacher_an', fullName: 'Nguyễn An', email: 'an@example.com', role: 'INSTRUCTOR', isActive: true, isDeleted: false } });
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 1 });
      prisma.refreshToken.create.mockResolvedValue({});

      const result = await auth.refresh('valid.refresh.token');

      expect(prisma.refreshToken.updateMany).toHaveBeenCalledWith(expect.objectContaining({ data: expect.objectContaining({ revokedAt: expect.any(Date) }) }));
      expect(result.message).toBe('Gia hạn mã truy cập thành công');
      expect(result.data.token_type).toBe('Bearer');
    });
  });

  describe('IT22_RefreshRotation_TC002: Refresh token không hợp lệ/hết hạn', () => {
    it('ném 401 AUTH_INVALID_REFRESH_TOKEN', async () => {
      jwtMock.verifyAsync.mockRejectedValue(new Error('jwt expired'));

      const error = await auth.refresh('expired.refresh.token').catch((e) => e);

      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getStatus()).toBe(401);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_REFRESH_TOKEN', message: 'Mã refresh token không hợp lệ hoặc đã hết hạn.', details: null });
    });
  });

  // -------------------------------------------------------------------------
  // IT23 - Xóa mềm và loại trừ khỏi danh sách
  // -------------------------------------------------------------------------

  describe('IT23_SoftDeleteExclusion_TC001: Xóa mềm và loại khỏi danh sách', () => {
    it('set cờ xóa mềm + thu hồi token, và list luôn lọc isDeleted=false', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: 'u2', role: 'INSTRUCTOR', isActive: true });
      prisma.user.update.mockResolvedValue({ id: 'u2' });
      prisma.aiQuotaConfig.updateMany.mockResolvedValue({ count: 1 });
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 1 });

      const result = await users.delete('u2', 'admin-1');

      expect(prisma.user.update).toHaveBeenCalledWith(expect.objectContaining({
        where: { id: 'u2' }, data: expect.objectContaining({ isDeleted: true, isActive: false, deletedAt: expect.any(Date) }),
      }));
      expect(prisma.aiQuotaConfig.updateMany).toHaveBeenCalledWith(expect.objectContaining({ where: { userId: 'u2', isDeleted: false } }));
      expect(prisma.refreshToken.updateMany).toHaveBeenCalledWith(expect.objectContaining({ where: { userId: 'u2', revokedAt: null } }));
      expect(result.message).toBe('Xóa người dùng thành công');

      prisma.user.findMany.mockResolvedValue([]);
      prisma.user.count.mockResolvedValue(0);
      await users.list({ page: 1, page_size: 20 } as any);
      expect(prisma.user.findMany).toHaveBeenCalledWith(expect.objectContaining({ where: expect.objectContaining({ isDeleted: false }) }));
    });
  });

  describe('IT23_SoftDeleteExclusion_TC002: Không thể xóa chính mình', () => {
    it('ném 403 USER_CANNOT_DELETE_SELF', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: 'admin-1', role: 'ADMIN', isActive: true });

      const error = await users.delete('admin-1', 'admin-1').catch((e) => e);

      expect(error).toBeInstanceOf(ForbiddenException);
      expect(error.getStatus()).toBe(403);
      expect(error.getResponse()).toEqual({ error_code: 'USER_CANNOT_DELETE_SELF', message: 'Bạn không thể xóa tài khoản đang sử dụng.', details: null });
    });
  });
});
