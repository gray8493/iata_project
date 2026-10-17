import { ForbiddenException, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { AuthService } from '../modules/auth/auth.service';
import { PrismaService } from '../prisma/prisma.service';

jest.mock('bcrypt');

describe('AuthService (Web Admin Unit Tests)', () => {
  let service: AuthService;
  let prisma: any;
  let jwt: any;
  let config: any;

  const mockUser = {
    id: '550e8400-e29b-41d4-a716-446655440000',
    username: 'admin',
    passwordHash: 'hashed_password',
    fullName: 'Quản Trị Viên',
    email: 'admin@aita.edu.vn',
    role: 'ADMIN',
    isActive: true,
    isDeleted: false,
    createdAt: new Date('2026-09-01T00:00:00.000Z'),
    updatedAt: new Date('2026-09-01T00:00:00.000Z'),
  };

  beforeEach(() => {
    prisma = {
      user: {
        findFirst: jest.fn(),
      },
      refreshToken: {
        create: jest.fn(),
        findFirst: jest.fn(),
        updateMany: jest.fn(),
      },
      $transaction: jest.fn((callback) => callback(prisma)),
    };

    jwt = {
      signAsync: jest.fn().mockImplementation((payload) => Promise.resolve(`jwt_token_${payload.token_type}`)),
      verifyAsync: jest.fn(),
      decode: jest.fn().mockReturnValue({ exp: Math.floor(Date.now() / 1000) + 3600 }),
    };

    config = {
      get: jest.fn((key, def) => def || '15m'),
      getOrThrow: jest.fn((key) => `secret_for_${key}`),
    };

    service = new AuthService(prisma as unknown as PrismaService, jwt as unknown as JwtService, config as unknown as ConfigService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('UT01_Auth_TC001: Đăng nhập thành công với tài khoản Admin hợp lệ', () => {
    it('trả về JWT access token, refresh token và thông tin người dùng', async () => {
      prisma.user.findFirst.mockResolvedValue(mockUser);
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);

      const result = await service.login({ username: 'admin', password: 'ValidPassword123' });

      expect(result.message).toBe('Đăng nhập thành công');
      expect(result.data.access_token).toBeDefined();
      expect(result.data.refresh_token).toBeDefined();
      expect(result.data.user.username).toBe('admin');
      expect(result.data.user.role).toBe('ADMIN');
      expect(prisma.refreshToken.create).toHaveBeenCalled();
    });
  });

  describe('UT01_Auth_TC002: Đăng nhập thất bại do sai mật khẩu', () => {
    it('ném UnauthorizedException khi mật khẩu không khớp', async () => {
      prisma.user.findFirst.mockResolvedValue(mockUser);
      (bcrypt.compare as jest.Mock).mockResolvedValue(false);

      await expect(service.login({ username: 'admin', password: 'WrongPassword' }))
        .rejects.toThrow(UnauthorizedException);
    });
  });

  describe('UT01_Auth_TC003: Đăng nhập thất bại do tài khoản không tồn tại', () => {
    it('ném UnauthorizedException khi không tìm thấy username', async () => {
      prisma.user.findFirst.mockResolvedValue(null);

      await expect(service.login({ username: 'nonexistent', password: 'Password123' }))
        .rejects.toThrow(UnauthorizedException);
    });
  });

  describe('UT01_Auth_TC004: Đăng nhập thất bại khi tài khoản bị khóa', () => {
    it('ném ForbiddenException khi isActive = false', async () => {
      prisma.user.findFirst.mockResolvedValue({ ...mockUser, isActive: false });
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);

      await expect(service.login({ username: 'admin', password: 'ValidPassword123' }))
        .rejects.toThrow(ForbiddenException);
    });
  });

  describe('UT01_Auth_TC005: Lấy thông tin tài khoản hiện tại (me)', () => {
    it('trả về chi tiết người dùng khi token hợp lệ', async () => {
      prisma.user.findFirst.mockResolvedValue(mockUser);

      const result = await service.me(mockUser.id);

      expect(result.message).toBe('Lấy thông tin tài khoản thành công');
      expect(result.data.username).toBe('admin');
      expect(result.data.email).toBe('admin@aita.edu.vn');
    });

    it('ném UnauthorizedException nếu tài khoản bị khóa hoặc xóa', async () => {
      prisma.user.findFirst.mockResolvedValue(null);

      await expect(service.me(mockUser.id))
        .rejects.toThrow(UnauthorizedException);
    });
  });

  describe('UT01_Auth_TC006: Gia hạn Access Token với Refresh Token hợp lệ', () => {
    it('cấp cặp token mới và xoay vòng refresh token', async () => {
      const validPayload = { id: mockUser.id, username: 'admin', role: 'ADMIN', token_type: 'refresh', jti: 'token-uuid' };
      jwt.verifyAsync.mockResolvedValue(validPayload);
      prisma.refreshToken.findFirst.mockResolvedValue({
        id: 'token-uuid',
        tokenHash: 'somehash',
        userId: mockUser.id,
        user: mockUser,
      });
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.refresh('raw_refresh_token_string');

      expect(result.message).toBe('Gia hạn mã truy cập thành công');
      expect(result.data.access_token).toBeDefined();
      expect(result.data.refresh_token).toBeDefined();
    });
  });

  describe('UT01_Auth_TC007: Gia hạn thất bại khi Refresh Token không hợp lệ', () => {
    it('ném UnauthorizedException khi token sai chữ ký hoặc hết hạn', async () => {
      jwt.verifyAsync.mockRejectedValue(new Error('Invalid token'));

      await expect(service.refresh('invalid_token'))
        .rejects.toThrow(UnauthorizedException);
    });
  });
});
