import { ArgumentsHost, HttpException, UnauthorizedException, UnprocessableEntityException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { AuthService } from '../modules/auth/auth.service';
import { LoginDto } from '../modules/auth/dto/login.dto';
import { RefreshTokenDto } from '../modules/auth/dto/refresh-token.dto';
import { JwtAuthGuard } from '../modules/auth/guards/jwt-auth.guard';
import { JwtStrategy } from '../modules/auth/strategies/jwt.strategy';
import { PrismaService } from '../prisma/prisma.service';
import { createValidationPipe } from '../common/validation/validation-pipe.factory';
import { ApiExceptionFilter } from '../common/filters/api-exception.filter';

jest.mock('bcrypt');

describe('AuthService / DTOs / guards (docs: docs/testcases/1-unit/Auth/Auth_testcase.md)', () => {
  let service: AuthService;
  let prisma: any;
  let jwt: any;
  let config: any;

  const activeUser = {
    id: '550e8400-e29b-41d4-a716-446655440000',
    username: 'admin',
    passwordHash: 'hashed_password',
    fullName: 'Quản Trị Viên',
    email: 'admin@fe.edu.vn',
    role: 'ADMIN',
    isActive: true,
    isDeleted: false,
    createdAt: new Date('2026-09-01T00:00:00.000Z'),
  };

  beforeEach(() => {
    prisma = {
      user: { findFirst: jest.fn() },
      refreshToken: { create: jest.fn(), findFirst: jest.fn(), updateMany: jest.fn() },
      $transaction: jest.fn((arg: any) => (typeof arg === 'function' ? arg(prisma) : Promise.all(arg))),
    };
    jwt = {
      signAsync: jest.fn((payload: { token_type?: string }) => Promise.resolve(`jwt_token_${payload.token_type}`)),
      verifyAsync: jest.fn(),
      decode: jest.fn().mockReturnValue({ exp: Math.floor(Date.now() / 1000) + 900 }),
    };
    config = {
      get: jest.fn((_key: string, def?: string) => def),
      getOrThrow: jest.fn((key: string) => `secret_for_${key}`),
    };
    service = new AuthService(prisma as unknown as PrismaService, jwt as unknown as JwtService, config as unknown as ConfigService);
  });

  afterEach(() => jest.clearAllMocks());

  async function validateBody(metatype: any, value: unknown): Promise<unknown> {
    return createValidationPipe().transform(value, { type: 'body', metatype, data: '' });
  }

  async function validationError(metatype: any, value: unknown): Promise<UnprocessableEntityException> {
    try {
      await validateBody(metatype, value);
    } catch (error) {
      if (error instanceof UnprocessableEntityException) return error;
      throw error;
    }
    throw new Error('Expected ValidationPipe to reject the payload');
  }

  function expectValidationDetail(error: UnprocessableEntityException, field: string, issue: string): void {
    const body = error.getResponse() as any;
    expect(body.error_code).toBe('VALIDATION_FAILED');
    expect(body.message).toBe('Dữ liệu gửi lên không đúng định dạng.');
    const detail = body.details.find((d: any) => d.field === field);
    expect(detail).toBeDefined();
    expect(detail.issues).toContain(issue);
  }

  function makeHost(): { host: ArgumentsHost; status: jest.Mock; json: jest.Mock } {
    const json = jest.fn();
    const status = jest.fn().mockReturnValue({ json });
    const host = {
      switchToHttp: () => ({
        getRequest: () => ({ method: 'POST', url: '/api/v1/auth/login' }),
        getResponse: () => ({ status }),
      }),
    } as unknown as ArgumentsHost;
    return { host, status, json };
  }

  async function expectInternalServerError(promise: Promise<unknown>): Promise<void> {
    const error = await promise.catch((e) => e);
    const { host, status, json } = makeHost();
    new ApiExceptionFilter().catch(error, host);
    expect(status).toHaveBeenCalledWith(500);
    expect(json).toHaveBeenCalledWith(expect.objectContaining({ error_code: 'INTERNAL_SERVER_ERROR', message: 'Đã xảy ra lỗi hệ thống.' }));
  }

  // -------------------------------------------------------------------------
  // PHẦN 1: POST /api/v1/auth/login
  // -------------------------------------------------------------------------

  describe('UT01_AuthLogin_TC001: Đăng nhập thành công với ADMIN', () => {
    it('cấp token và lưu refresh token', async () => {
      prisma.user.findFirst.mockResolvedValue(activeUser);
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);
      prisma.refreshToken.create.mockResolvedValue({ id: 'rt' });

      const result = await service.login({ username: 'admin', password: 'AdminPassword2026@' } as LoginDto);

      expect(result.message).toBe('Đăng nhập thành công');
      expect(result.data.access_token).toBeDefined();
      expect(result.data.refresh_token).toBeDefined();
      expect(result.data.token_type).toBe('Bearer');
      expect(result.data.expires_in).toBe(900);
      expect(result.data.user.role).toBe('ADMIN');
      expect(result.data.user.is_active).toBe(true);
      expect(prisma.refreshToken.create).toHaveBeenCalled();
    });
  });

  describe('UT01_AuthLogin_TC002: Đăng nhập thành công với INSTRUCTOR', () => {
    it('trả role INSTRUCTOR', async () => {
      prisma.user.findFirst.mockResolvedValue({ ...activeUser, username: 'teacher_hung', role: 'INSTRUCTOR' });
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);
      const result = await service.login({ username: 'teacher_hung', password: 'Password123@' } as LoginDto);
      expect(result.data.user.role).toBe('INSTRUCTOR');
    });
  });

  describe('UT01_AuthLogin_TC003: Sai mật khẩu', () => {
    it('trả 401 AUTH_INVALID_CREDENTIALS', async () => {
      prisma.user.findFirst.mockResolvedValue(activeUser);
      (bcrypt.compare as jest.Mock).mockResolvedValue(false);
      const error = await service.login({ username: 'teacher_hung', password: 'WrongPassword999@' } as LoginDto).catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_CREDENTIALS', message: 'Tên đăng nhập hoặc mật khẩu không chính xác.', details: null });
    });
  });

  describe('UT01_AuthLogin_TC004: Username không tồn tại', () => {
    it('trả 401 AUTH_INVALID_CREDENTIALS', async () => {
      prisma.user.findFirst.mockResolvedValue(null);
      const error = await service.login({ username: 'nonexistent_user', password: 'Password123@' } as LoginDto).catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_CREDENTIALS');
    });
  });

  describe('UT01_AuthLogin_TC005: Tài khoản bị khóa, mật khẩu đúng', () => {
    it('trả 403 AUTH_ACCOUNT_DISABLED', async () => {
      prisma.user.findFirst.mockResolvedValue({ ...activeUser, isActive: false });
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);
      const error = await service.login({ username: 'teacher_locked', password: 'CorrectPassword123@' } as LoginDto).catch((e) => e);
      expect(error).toBeInstanceOf(HttpException);
      expect(error.getStatus()).toBe(403);
      expect((error.getResponse() as any).error_code).toBe('AUTH_ACCOUNT_DISABLED');
    });
  });

  describe('UT01_AuthLogin_TC006: Tài khoản bị khóa, mật khẩu sai', () => {
    it('trả 401 AUTH_INVALID_CREDENTIALS (kiểm tra mật khẩu trước)', async () => {
      prisma.user.findFirst.mockResolvedValue({ ...activeUser, isActive: false });
      (bcrypt.compare as jest.Mock).mockResolvedValue(false);
      const error = await service.login({ username: 'teacher_locked', password: 'WrongPassword999@' } as LoginDto).catch((e) => e);
      expect(error.getStatus()).toBe(401);
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_CREDENTIALS');
    });
  });

  describe('UT01_AuthLogin_TC007: Lỗi CSDL khi đăng nhập', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      prisma.user.findFirst.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.login({ username: 'teacher_hung', password: 'Password123@' } as LoginDto));
    });
  });

  describe('UT01_AuthLogin_TC008: Body rỗng', () => {
    it('trả 422 cho cả username và password', async () => {
      const error = await validationError(LoginDto, {});
      expectValidationDetail(error, 'username', 'username must be a string');
      expectValidationDetail(error, 'password', 'password must be a string');
    });
  });

  describe('UT01_AuthLogin_TC009: Thiếu username', () => {
    it('trả 422 field username', async () => {
      const error = await validationError(LoginDto, { password: 'Password123@' });
      expectValidationDetail(error, 'username', 'username must be a string');
    });
  });

  describe('UT01_AuthLogin_TC010: Thiếu password', () => {
    it('trả 422 field password', async () => {
      const error = await validationError(LoginDto, { username: 'teacher_hung' });
      expectValidationDetail(error, 'password', 'password must be a string');
    });
  });

  describe('UT01_AuthLogin_TC011: username sai kiểu (số)', () => {
    it('trả 422 field username', async () => {
      const error = await validationError(LoginDto, { username: 123456, password: 'Password123@' });
      expectValidationDetail(error, 'username', 'username must be a string');
    });
  });

  describe('UT01_AuthLogin_TC012: password sai kiểu (mảng)', () => {
    it('trả 422 field password', async () => {
      const error = await validationError(LoginDto, { username: 'teacher_hung', password: ['Pass123', 'Secret'] });
      expectValidationDetail(error, 'password', 'password must be a string');
    });
  });

  describe('UT01_AuthLogin_TC013: username 2 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(LoginDto, { username: 'th', password: 'Password123@' });
      expectValidationDetail(error, 'username', 'username must be longer than or equal to 3 characters');
    });
  });

  describe('UT01_AuthLogin_TC014: username 3 ký tự (biên dưới hợp lệ)', () => {
    it('không ném lỗi validation và đăng nhập thành công', async () => {
      await expect(validateBody(LoginDto, { username: 'adm', password: 'Adm12@' })).resolves.toBeDefined();
      prisma.user.findFirst.mockResolvedValue({ ...activeUser, username: 'adm' });
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);
      const result = await service.login({ username: 'adm', password: 'Adm12@' } as LoginDto);
      expect(result.data.user.username).toBe('adm');
    });
  });

  describe('UT01_AuthLogin_TC015: username 50 ký tự (biên trên hợp lệ)', () => {
    it('không ném lỗi validation', async () => {
      await expect(validateBody(LoginDto, { username: 'a'.repeat(50), password: 'Password123@' })).resolves.toBeDefined();
    });
  });

  describe('UT01_AuthLogin_TC016: username 51 ký tự', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(LoginDto, { username: 'a'.repeat(51), password: 'Password123@' });
      expectValidationDetail(error, 'username', 'username must be shorter than or equal to 50 characters');
    });
  });

  describe('UT01_AuthLogin_TC017: password 5 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(LoginDto, { username: 'teacher_hung', password: '12345' });
      expectValidationDetail(error, 'password', 'password must be longer than or equal to 6 characters');
    });
  });

  describe('UT01_AuthLogin_TC018: password 6 ký tự (biên dưới hợp lệ)', () => {
    it('không ném lỗi validation', async () => {
      await expect(validateBody(LoginDto, { username: 'adm', password: 'Adm12@' })).resolves.toBeDefined();
    });
  });

  describe('UT01_AuthLogin_TC019: password 100 ký tự (biên trên hợp lệ)', () => {
    it('không ném lỗi validation', async () => {
      await expect(validateBody(LoginDto, { username: 'teacher_hung', password: 'P'.repeat(100) })).resolves.toBeDefined();
    });
  });

  describe('UT01_AuthLogin_TC020: password 101 ký tự', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(LoginDto, { username: 'teacher_hung', password: 'P'.repeat(101) });
      expectValidationDetail(error, 'password', 'password must be shorter than or equal to 100 characters');
    });
  });

  // -------------------------------------------------------------------------
  // PHẦN 2: GET /api/v1/auth/me
  // -------------------------------------------------------------------------

  describe('UT01_AuthMe_TC001: Không gửi Header Authorization', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, undefined); } catch (e) { return e; } })() as UnauthorizedException;
      expect(error.getStatus()).toBe(401);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
    });
  });

  describe('UT01_AuthMe_TC002: Token hết hạn', () => {
    it('trả 401 AUTH_TOKEN_EXPIRED', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, { name: 'TokenExpiredError' }); } catch (e) { return e; } })() as UnauthorizedException;
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_TOKEN_EXPIRED', message: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.', details: null });
    });
  });

  describe('UT01_AuthMe_TC003: Token sai chữ ký', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, { name: 'JsonWebTokenError' }); } catch (e) { return e; } })() as UnauthorizedException;
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
    });
  });

  describe('UT01_AuthMe_TC004: Sai Scheme (Basic)', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => {
      const guard = new JwtAuthGuard();
      const error = (() => { try { guard.handleRequest(null, false, undefined); } catch (e) { return e; } })() as UnauthorizedException;
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_TOKEN');
    });
  });

  describe('UT01_AuthMe_TC005: Refresh token dùng làm access', () => {
    it('JwtStrategy.validate ném 401 AUTH_INVALID_TOKEN', async () => {
      const strategy = new JwtStrategy(config as unknown as ConfigService, { user: { findFirst: jest.fn() } } as any);
      const error = await strategy.validate({ id: 'u1', username: 'admin', role: 'ADMIN', token_type: 'refresh' } as any).catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_TOKEN');
    });
  });

  describe('UT01_AuthMe_TC006: Tài khoản bị xóa/vô hiệu hóa', () => {
    it('JwtStrategy.validate ném 401 AUTH_ACCOUNT_DISABLED', async () => {
      const strategy = new JwtStrategy(config as unknown as ConfigService, { user: { findFirst: jest.fn().mockResolvedValue(null) } } as any);
      const error = await strategy.validate({ id: 'gone', username: 'x', role: 'ADMIN', token_type: 'access' } as any).catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản không còn hoạt động.' });
    });
  });

  describe('UT01_AuthMe_TC007: Lỗi CSDL khi lấy hồ sơ', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      prisma.user.findFirst.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.me('u1'));
    });
  });

  describe('UT01_AuthMe_TC008: me thành công với INSTRUCTOR', () => {
    it('trả đúng các trường hồ sơ', async () => {
      prisma.user.findFirst.mockResolvedValue({ ...activeUser, username: 'teacher_hung', role: 'INSTRUCTOR' });
      const result = await service.me(activeUser.id);
      expect(result.message).toBe('Lấy thông tin tài khoản thành công');
      expect(result.data).toEqual(expect.objectContaining({
        username: 'teacher_hung', role: 'INSTRUCTOR', is_active: true,
        full_name: 'Quản Trị Viên', email: 'admin@fe.edu.vn',
      }));
      expect(result.data.created_at).toBe(activeUser.createdAt.toISOString());
    });
  });

  describe('UT01_AuthMe_TC009: me thành công với ADMIN', () => {
    it('trả role ADMIN', async () => {
      prisma.user.findFirst.mockResolvedValue(activeUser);
      const result = await service.me(activeUser.id);
      expect(result.data.role).toBe('ADMIN');
      expect(result.data.username).toBe('admin');
    });
  });

  describe('UT01_AuthMe_TC010: vai trò không được hỗ trợ trong CSDL', () => {
    it('trả 500 INTERNAL_SERVER_ERROR do toAppRole ném lỗi', async () => {
      prisma.user.findFirst.mockResolvedValue({ ...activeUser, role: 'SUPERADMIN' });
      await expectInternalServerError(service.me(activeUser.id));
    });
  });

  // -------------------------------------------------------------------------
  // PHẦN 3: POST /api/v1/auth/refresh
  // -------------------------------------------------------------------------

  function stubRefreshSuccess(user: any): void {
    jwt.verifyAsync.mockResolvedValue({ id: user.id, username: user.username, role: user.role, token_type: 'refresh', jti: 'token-uuid' });
    prisma.refreshToken.findFirst.mockResolvedValue({ id: 'token-uuid', tokenHash: 'hash', userId: user.id, user });
    prisma.refreshToken.updateMany.mockResolvedValue({ count: 1 });
    prisma.refreshToken.create.mockResolvedValue({ id: 'new' });
  }

  describe('UT01_AuthRefresh_TC001: Gia hạn thành công (INSTRUCTOR)', () => {
    it('rotate refresh token và cấp token mới', async () => {
      stubRefreshSuccess({ ...activeUser, role: 'INSTRUCTOR' });
      const result = await service.refresh('raw_refresh_token');
      expect(result.message).toBe('Gia hạn mã truy cập thành công');
      expect(result.data.access_token).toBeDefined();
      expect(result.data.token_type).toBe('Bearer');
      expect(prisma.refreshToken.updateMany).toHaveBeenCalled();
    });
  });

  describe('UT01_AuthRefresh_TC002: Gia hạn thành công (ADMIN)', () => {
    it('cấp token mới cho ADMIN', async () => {
      stubRefreshSuccess(activeUser);
      const result = await service.refresh('raw_refresh_token');
      expect(result.data.access_token).toBeDefined();
      expect(result.data.refresh_token).toBeDefined();
    });
  });

  describe('UT01_AuthRefresh_TC003: Token sai chữ ký/hết hạn', () => {
    it('trả 401 AUTH_INVALID_REFRESH_TOKEN', async () => {
      jwt.verifyAsync.mockRejectedValue(new Error('invalid signature'));
      const error = await service.refresh('bad').catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_REFRESH_TOKEN', message: 'Mã refresh token không hợp lệ hoặc đã hết hạn.', details: null });
    });
  });

  describe('UT01_AuthRefresh_TC004: Access token dùng cho refresh', () => {
    it('trả 401 AUTH_INVALID_REFRESH_TOKEN', async () => {
      jwt.verifyAsync.mockResolvedValue({ id: activeUser.id, token_type: 'access', jti: 'x' });
      const error = await service.refresh('access').catch((e) => e);
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_REFRESH_TOKEN');
    });
  });

  describe('UT01_AuthRefresh_TC005: Token không tồn tại trong kho phiên', () => {
    it('trả 401 AUTH_INVALID_REFRESH_TOKEN', async () => {
      jwt.verifyAsync.mockResolvedValue({ id: activeUser.id, username: 'admin', role: 'ADMIN', token_type: 'refresh', jti: 'token-uuid' });
      prisma.refreshToken.findFirst.mockResolvedValue(null);
      const error = await service.refresh('unknown').catch((e) => e);
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_REFRESH_TOKEN');
    });
  });

  describe('UT01_AuthRefresh_TC006: Token đã bị thu hồi (count = 0)', () => {
    it('trả 401 AUTH_INVALID_REFRESH_TOKEN', async () => {
      jwt.verifyAsync.mockResolvedValue({ id: activeUser.id, username: 'admin', role: 'ADMIN', token_type: 'refresh', jti: 'token-uuid' });
      prisma.refreshToken.findFirst.mockResolvedValue({ id: 'token-uuid', tokenHash: 'hash', userId: activeUser.id, user: activeUser });
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 0 });
      const error = await service.refresh('rotated').catch((e) => e);
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_REFRESH_TOKEN');
    });
  });

  describe('UT01_AuthRefresh_TC007: Tài khoản gắn token bị khóa/xóa', () => {
    it('trả 401 AUTH_INVALID_REFRESH_TOKEN (không phải AUTH_ACCOUNT_DISABLED)', async () => {
      jwt.verifyAsync.mockResolvedValue({ id: activeUser.id, username: 'admin', role: 'ADMIN', token_type: 'refresh', jti: 'token-uuid' });
      prisma.refreshToken.findFirst.mockResolvedValue({ id: 'token-uuid', tokenHash: 'hash', userId: activeUser.id, user: { ...activeUser, isActive: false } });
      const error = await service.refresh('token').catch((e) => e);
      expect((error.getResponse() as any).error_code).toBe('AUTH_INVALID_REFRESH_TOKEN');
    });
  });

  describe('UT01_AuthRefresh_TC008: Lỗi CSDL khi gia hạn', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      jwt.verifyAsync.mockResolvedValue({ id: activeUser.id, username: 'admin', role: 'ADMIN', token_type: 'refresh', jti: 'token-uuid' });
      prisma.$transaction.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.refresh('token'));
    });
  });

  describe('UT01_AuthRefresh_TC009: Thiếu refresh_token', () => {
    it('trả 422 field refresh_token', async () => {
      const error = await validationError(RefreshTokenDto, {});
      expectValidationDetail(error, 'refresh_token', 'refresh_token must be a jwt string');
    });
  });

  describe('UT01_AuthRefresh_TC010: refresh_token chỉ chứa khoảng trắng', () => {
    it('trả 422 field refresh_token', async () => {
      const error = await validationError(RefreshTokenDto, { refresh_token: '   ' });
      expectValidationDetail(error, 'refresh_token', 'refresh_token must be a jwt string');
    });
  });

  describe('UT01_AuthRefresh_TC011: refresh_token sai kiểu (số)', () => {
    it('trả 422 field refresh_token', async () => {
      const error = await validationError(RefreshTokenDto, { refresh_token: 987654321 });
      expectValidationDetail(error, 'refresh_token', 'refresh_token must be a jwt string');
    });
  });

  describe('UT01_AuthRefresh_TC012: refresh_token là chuỗi ngẫu nhiên không phải JWT', () => {
    it('trả 422 field refresh_token', async () => {
      const error = await validationError(RefreshTokenDto, { refresh_token: 'random_fake_token_not_jwt' });
      expectValidationDetail(error, 'refresh_token', 'refresh_token must be a jwt string');
    });
  });
});
