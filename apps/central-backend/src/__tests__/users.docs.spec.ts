import { ArgumentsHost, BadRequestException, UnauthorizedException, UnprocessableEntityException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Reflector } from '@nestjs/core';
import { ParseUUIDPipe } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { Prisma } from '@prisma/client';
import { UsersService } from '../modules/users/users.service';
import { CreateUserDto } from '../modules/users/dto/create-user.dto';
import { UpdateUserDto } from '../modules/users/dto/update-user.dto';
import { ListUsersDto } from '../modules/users/dto/list-users.dto';
import { PrismaService } from '../prisma/prisma.service';
import { RolesGuard } from '../common/guards/roles.guard';
import { JwtAuthGuard } from '../modules/auth/guards/jwt-auth.guard';
import { JwtStrategy } from '../modules/auth/strategies/jwt.strategy';
import { createValidationPipe } from '../common/validation/validation-pipe.factory';
import { ApiExceptionFilter } from '../common/filters/api-exception.filter';

jest.mock('bcrypt');

describe('UsersService / DTOs / guards (docs: docs/testcases/1-unit/Users/Users_testcase.md)', () => {
  let service: UsersService;
  let prisma: any;
  let config: any;

  const userId = '550e8400-e29b-41d4-a716-446655440001';
  const actorId = '550e8400-e29b-41d4-a716-446655440099';

  function makeUser(overrides: Record<string, unknown> = {}) {
    return {
      id: userId,
      username: 'teacher_lan',
      fullName: 'Thầy An',
      email: 'lan@fe.edu.vn',
      role: 'INSTRUCTOR',
      isActive: true,
      createdAt: new Date('2026-09-01T00:00:00.000Z'),
      quotaConfig: { dailyTokenLimit: 50000, usedTokensToday: 0 },
      ...overrides,
    };
  }

  beforeEach(() => {
    prisma = {
      user: {
        findFirst: jest.fn(),
        findMany: jest.fn(),
        count: jest.fn(),
        create: jest.fn(),
        update: jest.fn(),
      },
      aiQuotaConfig: { create: jest.fn(), upsert: jest.fn(), updateMany: jest.fn() },
      refreshToken: { updateMany: jest.fn() },
      $transaction: jest.fn((arg: any) => (typeof arg === 'function' ? arg(prisma) : Promise.all(arg))),
    };
    config = {
      get: jest.fn((_key: string, def?: string) => def),
      getOrThrow: jest.fn((key: string) => `secret_for_${key}`),
    };
    service = new UsersService(prisma as unknown as PrismaService);
  });

  afterEach(() => jest.clearAllMocks());

  async function validate(metatype: any, value: unknown, type: 'body' | 'query' = 'body'): Promise<unknown> {
    return createValidationPipe().transform(value, { type, metatype, data: '' } as any);
  }

  async function validationError(metatype: any, value: unknown, type: 'body' | 'query' = 'body'): Promise<UnprocessableEntityException> {
    try {
      await validate(metatype, value, type);
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
        getRequest: () => ({ method: 'GET', url: '/api/v1/admin/users' }),
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

  function expectUnauthorizedNoToken(): void {
    const guard = new JwtAuthGuard();
    const error = (() => {
      try {
        guard.handleRequest(null, false, undefined);
      } catch (e) {
        return e;
      }
    })() as UnauthorizedException;
    expect(error.getStatus()).toBe(401);
    expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
  }

  function expectForbiddenForInstructor(): void {
    const reflector = { getAllAndOverride: jest.fn().mockReturnValue(['ADMIN']) } as unknown as Reflector;
    const context = {
      getHandler: () => ({}),
      getClass: () => ({}),
      switchToHttp: () => ({ getRequest: () => ({ user: { id: actorId, username: 'teacher_hung', role: 'INSTRUCTOR' } }) }),
    } as any;
    const error = (() => {
      try {
        new RolesGuard(reflector).canActivate(context);
      } catch (e) {
        return e;
      }
    })() as any;
    expect(error.getStatus()).toBe(403);
    expect(error.getResponse()).toEqual({ error_code: 'FORBIDDEN_ADMIN_ONLY', message: 'Bạn không có quyền thực hiện thao tác này.', details: null });
  }

  function p2002(): Prisma.PrismaClientKnownRequestError {
    return new Prisma.PrismaClientKnownRequestError('Unique constraint failed on the fields: (`email`)', {
      code: 'P2002',
      clientVersion: '5.22.0',
    });
  }

  // =========================================================================
  // PHẦN 1: GET /api/v1/admin/users (DANH SÁCH TÀI KHOẢN)
  // =========================================================================

  describe('UT02_UsersList_TC001: Người gọi chưa đăng nhập', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT02_UsersList_TC002: Token đã hết hạn sử dụng', () => {
    it('trả 401 AUTH_TOKEN_EXPIRED', () => {
      const guard = new JwtAuthGuard();
      const error = (() => {
        try {
          guard.handleRequest(null, false, { name: 'TokenExpiredError' });
        } catch (e) {
          return e;
        }
      })() as UnauthorizedException;
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_TOKEN_EXPIRED', message: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.', details: null });
    });
  });

  describe('UT02_UsersList_TC003: Giảng viên (INSTRUCTOR) không có quyền xem danh sách', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForInstructor());
  });

  describe('UT02_UsersList_TC004: Tài khoản trong Token đã bị vô hiệu hóa', () => {
    it('JwtStrategy.validate ném 401 AUTH_ACCOUNT_DISABLED', async () => {
      const strategy = new JwtStrategy(config as unknown as ConfigService, { user: { findFirst: jest.fn().mockResolvedValue(null) } } as any);
      const error = await strategy.validate({ id: 'gone', username: 'x', role: 'ADMIN', token_type: 'access' } as any).catch((e) => e);
      expect(error).toBeInstanceOf(UnauthorizedException);
      expect(error.getResponse()).toEqual({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản không còn hoạt động.' });
    });
  });

  describe('UT02_UsersList_TC005: Tham số page vi phạm biên dưới (page = 0)', () => {
    it('trả 422 field page', async () => {
      const error = await validationError(ListUsersDto, { page: 0, page_size: 10 }, 'query');
      expectValidationDetail(error, 'page', 'page must not be less than 1');
    });
  });

  describe('UT02_UsersList_TC006: Tham số page_size vượt biên trên (page_size = 101)', () => {
    it('trả 422 field page_size', async () => {
      const error = await validationError(ListUsersDto, { page: 1, page_size: 101 }, 'query');
      expectValidationDetail(error, 'page_size', 'page_size must not be greater than 100');
    });
  });

  describe('UT02_UsersList_TC007: Tham số role không thuộc enum hợp lệ', () => {
    it('trả 422 field role', async () => {
      const error = await validationError(ListUsersDto, { role: 'STUDENT' }, 'query');
      expectValidationDetail(error, 'role', 'role must be one of the following values: ADMIN, INSTRUCTOR');
    });
  });

  describe('UT02_UsersList_TC008: Từ khóa search vượt quá 50 ký tự', () => {
    it('trả 422 field search', async () => {
      const error = await validationError(ListUsersDto, { search: 'a'.repeat(51) }, 'query');
      expectValidationDetail(error, 'search', 'search must be shorter than or equal to 50 characters');
    });
  });

  describe('UT02_UsersList_TC009: Lỗi máy chủ khi truy vấn danh sách', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      prisma.$transaction.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.list({ page: 1, page_size: 10 } as ListUsersDto));
    });
  });

  describe('UT02_UsersList_TC010: Danh sách rỗng / trang không có dữ liệu', () => {
    it('trả items rỗng và total_pages = 0', async () => {
      prisma.user.findMany.mockResolvedValue([]);
      prisma.user.count.mockResolvedValue(0);
      const result = await service.list({ page: 1, page_size: 10 } as ListUsersDto);
      expect(result.data.items).toEqual([]);
      expect(result.data.pagination).toEqual({ page: 1, page_size: 10, total_items: 0, total_pages: 0 });
    });
  });

  describe('UT02_UsersList_TC011: Lấy danh sách với tham số phân trang mặc định', () => {
    it('trả đúng các trường và phân trang', async () => {
      prisma.user.findMany.mockResolvedValue([
        makeUser(),
        makeUser({ id: 'id-2', username: 'admin2', fullName: 'Quản Trị 2', email: 'admin2@fe.edu.vn', role: 'ADMIN', quotaConfig: null }),
      ]);
      prisma.user.count.mockResolvedValue(2);
      const result = await service.list({ page: 1, page_size: 10 } as ListUsersDto);
      expect(result.message).toBe('Lấy danh sách người dùng thành công');
      expect(result.data.items[0]).toEqual(
        expect.objectContaining({
          id: userId,
          username: 'teacher_lan',
          full_name: 'Thầy An',
          email: 'lan@fe.edu.vn',
          role: 'INSTRUCTOR',
          is_active: true,
          created_at: new Date('2026-09-01T00:00:00.000Z').toISOString(),
          daily_token_quota: 50000,
          used_tokens_today: 0,
        }),
      );
      expect(result.data.items[1].daily_token_quota).toBe(50000);
      expect(result.data.pagination).toEqual({ page: 1, page_size: 10, total_items: 2, total_pages: 1 });
    });
  });

  describe('UT02_UsersList_TC012: Lấy danh sách kèm bộ lọc vai trò', () => {
    it('where chứa isDeleted: false và role INSTRUCTOR', async () => {
      prisma.user.findMany.mockResolvedValue([]);
      prisma.user.count.mockResolvedValue(0);
      await service.list({ page: 1, page_size: 10, role: 'INSTRUCTOR' } as ListUsersDto);
      const where = prisma.user.findMany.mock.calls[0][0].where;
      expect(where.isDeleted).toBe(false);
      expect(where.role).toBe('INSTRUCTOR');
    });
  });

  describe('UT02_UsersList_TC013: Tìm kiếm theo từ khóa', () => {
    it('where.OR chứa 3 nhánh contains không phân biệt hoa thường', async () => {
      prisma.user.findMany.mockResolvedValue([]);
      prisma.user.count.mockResolvedValue(0);
      await service.list({ page: 1, page_size: 10, search: 'hung' } as ListUsersDto);
      const where = prisma.user.findMany.mock.calls[0][0].where;
      expect(where.OR).toEqual([
        { username: { contains: 'hung', mode: 'insensitive' } },
        { fullName: { contains: 'hung', mode: 'insensitive' } },
        { email: { contains: 'hung', mode: 'insensitive' } },
      ]);
    });
  });

  // =========================================================================
  // PHẦN 2: POST /api/v1/admin/users (TẠO TÀI KHOẢN)
  // =========================================================================

  const validCreate = {
    username: 'teacher_lan',
    password: 'Password1',
    full_name: 'Thầy An',
    email: 'lan@fe.edu.vn',
    role: 'INSTRUCTOR' as const,
  };

  describe('UT02_UsersCreate_TC001: Người gọi chưa đăng nhập', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT02_UsersCreate_TC002: Giảng viên không có quyền tạo tài khoản', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForInstructor());
  });

  describe('UT02_UsersCreate_TC003: Request Body rỗng thiếu toàn bộ trường bắt buộc', () => {
    it('trả 422 cho tất cả các trường bắt buộc', async () => {
      const error = await validationError(CreateUserDto, {});
      for (const field of ['username', 'password', 'full_name', 'email', 'role']) {
        const body = error.getResponse() as any;
        expect(body.details.find((d: any) => d.field === field)).toBeDefined();
      }
    });
  });

  describe('UT02_UsersCreate_TC004: username dài 2 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, username: 'ab' });
      expectValidationDetail(error, 'username', 'username must be longer than or equal to 3 characters');
    });
  });

  describe('UT02_UsersCreate_TC005: username dài đúng 3 ký tự (biên dưới hợp lệ)', () => {
    it('hợp lệ và tạo tài khoản thành công', async () => {
      await expect(validate(CreateUserDto, { ...validCreate, username: 'abc' })).resolves.toBeDefined();
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashed');
      prisma.user.create.mockResolvedValue(makeUser({ username: 'abc' }));
      prisma.aiQuotaConfig.create.mockResolvedValue({});
      const result = await service.create({ ...validCreate, username: 'abc' } as CreateUserDto);
      expect(result.message).toBe('Tạo tài khoản người dùng mới thành công');
    });
  });

  describe('UT02_UsersCreate_TC006: username dài đúng 30 ký tự (biên trên hợp lệ)', () => {
    it('không ném lỗi validation', async () => {
      await expect(validate(CreateUserDto, { ...validCreate, username: 'a'.repeat(30) })).resolves.toBeDefined();
    });
  });

  describe('UT02_UsersCreate_TC007: username dài 31 ký tự', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, username: 'a'.repeat(31) });
      expectValidationDetail(error, 'username', 'username must be shorter than or equal to 30 characters');
    });
  });

  describe('UT02_UsersCreate_TC008: username chứa ký tự không hợp lệ', () => {
    it('trả 422 vi phạm regex', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, username: 'Teacher Hung!' });
      const body = error.getResponse() as any;
      const detail = body.details.find((d: any) => d.field === 'username');
      expect(detail).toBeDefined();
      expect(detail.issues.some((issue: string) => issue.includes('^[a-z0-9_]+$'))).toBe(true);
    });
  });

  describe('UT02_UsersCreate_TC009: password dài 7 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, password: 'Pass12a' });
      expectValidationDetail(error, 'password', 'password must be longer than or equal to 8 characters');
    });
  });

  describe('UT02_UsersCreate_TC010: password không đủ độ phức tạp', () => {
    it('trả 422 vi phạm regex', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, password: 'password' });
      const body = error.getResponse() as any;
      const detail = body.details.find((d: any) => d.field === 'password');
      expect(detail).toBeDefined();
      expect(detail.issues.some((issue: string) => issue.includes('(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$'))).toBe(true);
    });
  });

  describe('UT02_UsersCreate_TC011: password dài đúng 8 ký tự và đủ độ phức tạp', () => {
    it('không ném lỗi validation', async () => {
      await expect(validate(CreateUserDto, { ...validCreate, password: 'Passw0rd' })).resolves.toBeDefined();
    });
  });

  describe('UT02_UsersCreate_TC012: full_name dài 1 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, full_name: 'A' });
      expectValidationDetail(error, 'full_name', 'full_name must be longer than or equal to 2 characters');
    });
  });

  describe('UT02_UsersCreate_TC013: full_name dài đúng 2 ký tự', () => {
    it('không ném lỗi validation', async () => {
      await expect(validate(CreateUserDto, { ...validCreate, full_name: 'An' })).resolves.toBeDefined();
    });
  });

  describe('UT02_UsersCreate_TC014: email sai định dạng', () => {
    it('trả 422 field email', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, email: 'not-an-email' });
      expectValidationDetail(error, 'email', 'email must be an email');
    });
  });

  describe('UT02_UsersCreate_TC015: role sai giá trị ngoài enum', () => {
    it('trả 422 field role', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, role: 'STUDENT' });
      expectValidationDetail(error, 'role', 'role must be one of the following values: ADMIN, INSTRUCTOR');
    });
  });

  describe('UT02_UsersCreate_TC016: daily_token_quota mang giá trị số âm', () => {
    it('trả 422 field daily_token_quota', async () => {
      const error = await validationError(CreateUserDto, { ...validCreate, daily_token_quota: -1 });
      expectValidationDetail(error, 'daily_token_quota', 'daily_token_quota must not be less than 0');
    });
  });

  describe('UT02_UsersCreate_TC017: daily_token_quota bằng 0 và bỏ trống', () => {
    it('0 hợp lệ; bỏ trống dùng mặc định 50000', async () => {
      await expect(validate(CreateUserDto, { ...validCreate, daily_token_quota: 0 })).resolves.toBeDefined();
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashed');
      prisma.user.create.mockResolvedValue(makeUser());
      prisma.aiQuotaConfig.create.mockResolvedValue({});
      await service.create({ ...validCreate } as CreateUserDto);
      expect(prisma.aiQuotaConfig.create.mock.calls[0][0].data.dailyTokenLimit).toBe(50000);
    });
  });

  describe('UT02_UsersCreate_TC018: Trùng tên đăng nhập hoặc email (P2002)', () => {
    it('trả 409 USER_ALREADY_EXISTS', async () => {
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashed');
      prisma.$transaction.mockRejectedValue(p2002());
      const error = await service.create({ ...validCreate } as CreateUserDto).catch((e) => e);
      expect(error.getStatus()).toBe(409);
      expect(error.getResponse()).toEqual({ error_code: 'USER_ALREADY_EXISTS', message: 'Tên đăng nhập hoặc email đã tồn tại.', details: null });
    });
  });

  describe('UT02_UsersCreate_TC019: Lỗi máy chủ khi tạo người dùng mới', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashed');
      prisma.$transaction.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.create({ ...validCreate } as CreateUserDto));
    });
  });

  describe('UT02_UsersCreate_TC020: Tạo mới thành công tài khoản Giảng viên', () => {
    it('băm mật khẩu, hạ chữ thường email, tạo kèm quota trong transaction', async () => {
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashed_pwd');
      prisma.user.create.mockResolvedValue(makeUser());
      prisma.aiQuotaConfig.create.mockResolvedValue({});
      const result = await service.create({ ...validCreate, email: 'LAN@FE.EDU.VN' } as CreateUserDto);
      expect(result.message).toBe('Tạo tài khoản người dùng mới thành công');
      expect(bcrypt.hash).toHaveBeenCalledWith('Password1', 12);
      expect(prisma.user.create.mock.calls[0][0].data.email).toBe('lan@fe.edu.vn');
      expect(prisma.aiQuotaConfig.create).toHaveBeenCalled();
      expect(result.data.role).toBe('INSTRUCTOR');
    });
  });

  describe('UT02_UsersCreate_TC021: Tạo mới thành công tài khoản ADMIN', () => {
    it('trả data.role ADMIN', async () => {
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashed');
      prisma.user.create.mockResolvedValue(makeUser({ role: 'ADMIN' }));
      prisma.aiQuotaConfig.create.mockResolvedValue({});
      const result = await service.create({ ...validCreate, role: 'ADMIN' } as CreateUserDto);
      expect(result.data.role).toBe('ADMIN');
    });
  });

  describe('UT02_UsersCreate_TC022: Tạo thành công và tự sinh hạn mức AI mặc định', () => {
    it('aiQuotaConfig.create nhận dailyTokenLimit 50000 và lastResetDate đầu ngày UTC', async () => {
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashed');
      prisma.user.create.mockResolvedValue(makeUser());
      prisma.aiQuotaConfig.create.mockResolvedValue({});
      await service.create({ ...validCreate } as CreateUserDto);
      const data = prisma.aiQuotaConfig.create.mock.calls[0][0].data;
      expect(data.dailyTokenLimit).toBe(50000);
      const reset: Date = data.lastResetDate;
      expect(reset.getUTCHours()).toBe(0);
      expect(reset.getUTCMinutes()).toBe(0);
      expect(reset.getUTCSeconds()).toBe(0);
    });
  });

  // =========================================================================
  // PHẦN 3: GET /api/v1/admin/users/:id (CHI TIẾT TÀI KHOẢN)
  // =========================================================================

  describe('UT02_UsersGetDetail_TC001: Người gọi chưa đăng nhập', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT02_UsersGetDetail_TC002: Giảng viên không có quyền xem chi tiết', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForInstructor());
  });

  describe('UT02_UsersGetDetail_TC003: Tham số id không đúng định dạng UUID', () => {
    it('ParseUUIDPipe trả 400 BAD_REQUEST', async () => {
      const error = await new ParseUUIDPipe().transform('abc', { type: 'param', data: 'id' } as any).catch((e) => e);
      expect(error).toBeInstanceOf(BadRequestException);
      expect(error.getStatus()).toBe(400);
      expect(error.message).toBe('Validation failed (uuid is expected)');
    });
  });

  describe('UT02_UsersGetDetail_TC004: Không tìm thấy người dùng với ID đã chỉ định', () => {
    it('trả 404 USER_NOT_FOUND', async () => {
      prisma.user.findFirst.mockResolvedValue(null);
      const error = await service.get(userId).catch((e) => e);
      expect(error.getStatus()).toBe(404);
      expect(error.getResponse()).toEqual({ error_code: 'USER_NOT_FOUND', message: 'Không tìm thấy người dùng với ID đã chỉ định.', details: null });
    });
  });

  describe('UT02_UsersGetDetail_TC005: Lỗi máy chủ khi truy vấn chi tiết', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      prisma.user.findFirst.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.get(userId));
    });
  });

  describe('UT02_UsersGetDetail_TC006: Xem chi tiết thành công tài khoản Giảng viên', () => {
    it('trả role INSTRUCTOR và quota 50000', async () => {
      prisma.user.findFirst.mockResolvedValue(makeUser());
      const result = await service.get(userId);
      expect(result.message).toBe('Lấy thông tin tài khoản thành công');
      expect(result.data.role).toBe('INSTRUCTOR');
      expect(result.data.daily_token_quota).toBe(50000);
    });
  });

  describe('UT02_UsersGetDetail_TC007: Xem chi tiết thành công tài khoản Quản trị viên', () => {
    it('trả role ADMIN', async () => {
      prisma.user.findFirst.mockResolvedValue(makeUser({ role: 'ADMIN' }));
      const result = await service.get(userId);
      expect(result.data.role).toBe('ADMIN');
    });
  });

  // =========================================================================
  // PHẦN 4: PUT /api/v1/admin/users/:id (CẬP NHẬT TÀI KHOẢN)
  // =========================================================================

  describe('UT02_UsersUpdate_TC001: Người gọi chưa đăng nhập', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT02_UsersUpdate_TC002: Giảng viên không có quyền cập nhật', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForInstructor());
  });

  describe('UT02_UsersUpdate_TC003: Cập nhật tài khoản không tồn tại', () => {
    it('trả 404 USER_NOT_FOUND', async () => {
      prisma.user.findFirst.mockResolvedValue(null);
      const error = await service.update(userId, { full_name: 'X' } as UpdateUserDto, actorId).catch((e) => e);
      expect(error.getStatus()).toBe(404);
      expect((error.getResponse() as any).error_code).toBe('USER_NOT_FOUND');
    });
  });

  describe('UT02_UsersUpdate_TC004: Quản trị viên tự khóa tài khoản của chính mình', () => {
    it('trả 403 USER_CANNOT_DISABLE_SELF', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'ADMIN', isActive: true });
      const error = await service.update(userId, { is_active: false } as UpdateUserDto, userId).catch((e) => e);
      expect(error.getStatus()).toBe(403);
      expect(error.getResponse()).toEqual({ error_code: 'USER_CANNOT_DISABLE_SELF', message: 'Bạn không thể tự vô hiệu hóa tài khoản đang sử dụng.', details: null });
    });
  });

  describe('UT02_UsersUpdate_TC005: Tham số id trên đường dẫn không hợp lệ (id = 0)', () => {
    it('ParseUUIDPipe trả 400 BAD_REQUEST', async () => {
      const error = await new ParseUUIDPipe().transform('0', { type: 'param', data: 'id' } as any).catch((e) => e);
      expect(error.getStatus()).toBe(400);
      expect(error.message).toBe('Validation failed (uuid is expected)');
    });
  });

  describe('UT02_UsersUpdate_TC006: Cập nhật email sai định dạng', () => {
    it('trả 422 field email', async () => {
      const error = await validationError(UpdateUserDto, { email: 'invalid-email' });
      expectValidationDetail(error, 'email', 'email must be an email');
    });
  });

  describe('UT02_UsersUpdate_TC007: Cập nhật role sai giá trị ngoài ADMIN/INSTRUCTOR', () => {
    it('trả 422 field role', async () => {
      const error = await validationError(UpdateUserDto, { role: 'SUPERADMIN' });
      expectValidationDetail(error, 'role', 'role must be one of the following values: ADMIN, INSTRUCTOR');
    });
  });

  describe('UT02_UsersUpdate_TC008: Cập nhật daily_token_quota mang giá trị số âm', () => {
    it('trả 422 field daily_token_quota', async () => {
      const error = await validationError(UpdateUserDto, { daily_token_quota: -1 });
      expectValidationDetail(error, 'daily_token_quota', 'daily_token_quota must not be less than 0');
    });
  });

  describe('UT02_UsersUpdate_TC009: is_active sai kiểu dữ liệu', () => {
    it('trả 422 field is_active', async () => {
      const error = await validationError(UpdateUserDto, { is_active: 'false' });
      expectValidationDetail(error, 'is_active', 'is_active must be a boolean value');
    });
  });

  describe('UT02_UsersUpdate_TC010: Cập nhật email bị trùng (P2002)', () => {
    it('trả 409 USER_ALREADY_EXISTS', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'INSTRUCTOR', isActive: true });
      prisma.$transaction.mockRejectedValue(p2002());
      const error = await service.update(userId, { email: 'taken@fe.edu.vn' } as UpdateUserDto, actorId).catch((e) => e);
      expect(error.getStatus()).toBe(409);
      expect((error.getResponse() as any).error_code).toBe('USER_ALREADY_EXISTS');
    });
  });

  describe('UT02_UsersUpdate_TC011: Vô hiệu hóa Admin hoạt động cuối cùng', () => {
    it('trả 409 LAST_ACTIVE_ADMIN', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'ADMIN', isActive: true });
      prisma.user.count.mockResolvedValue(1);
      const error = await service.update(userId, { is_active: false } as UpdateUserDto, actorId).catch((e) => e);
      expect(error.getStatus()).toBe(409);
      expect(error.getResponse()).toEqual({ error_code: 'LAST_ACTIVE_ADMIN', message: 'Không thể vô hiệu hóa hoặc hạ quyền Admin hoạt động cuối cùng.', details: null });
    });
  });

  describe('UT02_UsersUpdate_TC012: Lỗi máy chủ khi cập nhật tài khoản', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'INSTRUCTOR', isActive: true });
      prisma.$transaction.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.update(userId, { full_name: 'X' } as UpdateUserDto, actorId));
    });
  });

  describe('UT02_UsersUpdate_TC013: Cập nhật thành công hồ sơ và hạn mức AI', () => {
    it('upsert quota với dailyTokenLimit 80000', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'INSTRUCTOR', isActive: true });
      prisma.user.update.mockResolvedValue(makeUser({ fullName: 'Thầy An (Updated)', updatedAt: new Date('2026-10-17T00:00:00.000Z') }));
      prisma.aiQuotaConfig.upsert.mockResolvedValue({});
      const result = await service.update(userId, { full_name: 'Thầy An (Updated)', daily_token_quota: 80000 } as UpdateUserDto, actorId);
      expect(result.message).toBe('Cập nhật tài khoản thành công');
      expect(result.data.full_name).toBe('Thầy An (Updated)');
      expect(prisma.aiQuotaConfig.upsert.mock.calls[0][0].update.dailyTokenLimit).toBe(80000);
    });
  });

  describe('UT02_UsersUpdate_TC014: Khóa tài khoản Giảng viên thành công', () => {
    it('trả is_active false và thu hồi refresh token', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'INSTRUCTOR', isActive: true });
      prisma.user.update.mockResolvedValue(makeUser({ isActive: false, updatedAt: new Date('2026-10-17T00:00:00.000Z') }));
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 1 });
      const result = await service.update(userId, { is_active: false } as UpdateUserDto, actorId);
      expect(result.data.is_active).toBe(false);
      expect(prisma.refreshToken.updateMany).toHaveBeenCalledWith(expect.objectContaining({ where: { userId, revokedAt: null } }));
    });
  });

  describe('UT02_UsersUpdate_TC015: Mở khóa tài khoản Giảng viên thành công', () => {
    it('trả is_active true và không thu hồi refresh token', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'INSTRUCTOR', isActive: false });
      prisma.user.update.mockResolvedValue(makeUser({ isActive: true, updatedAt: new Date('2026-10-17T00:00:00.000Z') }));
      const result = await service.update(userId, { is_active: true } as UpdateUserDto, actorId);
      expect(result.data.is_active).toBe(true);
      expect(prisma.refreshToken.updateMany).not.toHaveBeenCalled();
    });
  });

  // =========================================================================
  // PHẦN 5: DELETE /api/v1/admin/users/:id (XÓA MỀM TÀI KHOẢN)
  // =========================================================================

  describe('UT02_UsersDelete_TC001: Người gọi chưa đăng nhập', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT02_UsersDelete_TC002: Giảng viên không có quyền xóa tài khoản', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForInstructor());
  });

  describe('UT02_UsersDelete_TC003: Tham số id không hợp lệ (id = 0)', () => {
    it('ParseUUIDPipe trả 400 BAD_REQUEST', async () => {
      const error = await new ParseUUIDPipe().transform('0', { type: 'param', data: 'id' } as any).catch((e) => e);
      expect(error.getStatus()).toBe(400);
    });
  });

  describe('UT02_UsersDelete_TC004: Xóa tài khoản không tồn tại', () => {
    it('trả 404 USER_NOT_FOUND', async () => {
      prisma.user.findFirst.mockResolvedValue(null);
      const error = await service.delete(userId, actorId).catch((e) => e);
      expect(error.getStatus()).toBe(404);
      expect((error.getResponse() as any).error_code).toBe('USER_NOT_FOUND');
    });
  });

  describe('UT02_UsersDelete_TC005: Quản trị viên tự xóa tài khoản của chính mình', () => {
    it('trả 403 USER_CANNOT_DELETE_SELF', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'ADMIN', isActive: true });
      const error = await service.delete(userId, userId).catch((e) => e);
      expect(error.getStatus()).toBe(403);
      expect(error.getResponse()).toEqual({ error_code: 'USER_CANNOT_DELETE_SELF', message: 'Bạn không thể xóa tài khoản đang sử dụng.', details: null });
    });
  });

  describe('UT02_UsersDelete_TC006: Xóa Admin hoạt động cuối cùng', () => {
    it('trả 409 LAST_ACTIVE_ADMIN', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'ADMIN', isActive: true });
      prisma.user.count.mockResolvedValue(1);
      const error = await service.delete(userId, actorId).catch((e) => e);
      expect(error.getStatus()).toBe(409);
      expect(error.getResponse()).toEqual({ error_code: 'LAST_ACTIVE_ADMIN', message: 'Không thể xóa Admin hoạt động cuối cùng.', details: null });
    });
  });

  describe('UT02_UsersDelete_TC007: Lỗi máy chủ khi xóa người dùng', () => {
    it('trả 500 INTERNAL_SERVER_ERROR', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'INSTRUCTOR', isActive: true });
      prisma.$transaction.mockRejectedValue(new Error('Connection refused'));
      await expectInternalServerError(service.delete(userId, actorId));
    });
  });

  describe('UT02_UsersDelete_TC008: Xóa mềm tài khoản Giảng viên thành công', () => {
    it('đặt cờ xóa, xóa mềm quota và thu hồi token', async () => {
      prisma.user.findFirst.mockResolvedValue({ id: userId, role: 'INSTRUCTOR', isActive: true });
      prisma.user.update.mockResolvedValue({});
      prisma.aiQuotaConfig.updateMany.mockResolvedValue({ count: 1 });
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 1 });
      const result = await service.delete(userId, actorId);
      expect(result.message).toBe('Xóa người dùng thành công');
      expect(result.data).toBeNull();
      expect(prisma.user.update.mock.calls[0][0].data).toEqual(expect.objectContaining({ isDeleted: true, isActive: false }));
      expect(prisma.aiQuotaConfig.updateMany).toHaveBeenCalled();
      expect(prisma.refreshToken.updateMany).toHaveBeenCalled();
    });
  });
});
