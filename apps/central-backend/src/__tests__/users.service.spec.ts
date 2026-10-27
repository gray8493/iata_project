import { ConflictException, ForbiddenException, NotFoundException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { UsersService } from '../modules/users/users.service';
import { PrismaService } from '../prisma/prisma.service';
import { REPORTS_OVERVIEW_CACHE_KEY } from '../common/redis.service';

jest.mock('bcrypt');

describe('UsersService (Web Admin Unit Tests)', () => {
  let service: UsersService;
  let prisma: any;

  const mockAdmin = {
    id: 'admin-uuid-1',
    username: 'admin',
    passwordHash: 'hashed_admin',
    fullName: 'Quản Trị Viên',
    email: 'admin@aita.edu.vn',
    role: 'ADMIN',
    isActive: true,
    isDeleted: false,
    createdAt: new Date('2026-09-01T00:00:00.000Z'),
    updatedAt: new Date('2026-09-01T00:00:00.000Z'),
  };

  const mockInstructor = {
    id: 'instructor-uuid-1',
    username: 'instructor1',
    passwordHash: 'hashed_pw',
    fullName: 'Thầy Nguyễn Văn An',
    email: 'instructor1@aita.edu.vn',
    role: 'INSTRUCTOR',
    isActive: true,
    isDeleted: false,
    createdAt: new Date('2026-09-10T00:00:00.000Z'),
    updatedAt: new Date('2026-09-10T00:00:00.000Z'),
  };

  beforeEach(() => {
    prisma = {
      user: {
        findMany: jest.fn(),
        count: jest.fn(),
        findFirst: jest.fn(),
        create: jest.fn(),
        update: jest.fn(),
      },
      aiQuotaConfig: {
        create: jest.fn(),
        upsert: jest.fn(),
        updateMany: jest.fn(),
      },
      refreshToken: {
        updateMany: jest.fn(),
      },
      $transaction: jest.fn((callback) => {
        if (typeof callback === 'function') {
          return callback(prisma);
        }
        return Promise.all(callback);
      }),
    };

    service = new UsersService(prisma as unknown as PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('UT02_Users_TC001: Lấy danh sách tài khoản phân trang', () => {
    it('trả về danh sách người dùng kèm phân trang chính xác', async () => {
      prisma.user.findMany.mockResolvedValue([mockAdmin, mockInstructor]);
      prisma.user.count.mockResolvedValue(2);

      const result = await service.list({ page: 1, page_size: 10, search: 'admin' });

      expect(result.message).toBe('Lấy danh sách người dùng thành công');
      expect(result.data.items).toHaveLength(2);
      expect(result.data.pagination.total_items).toBe(2);
      expect(result.data.pagination.page).toBe(1);
    });
  });

  describe('UT02_Users_TC002: Tạo mới tài khoản Giảng viên thành công', () => {
    it('tạo người dùng kèm mật khẩu băm và cấu hình hạn mức AI', async () => {
      (bcrypt.hash as jest.Mock).mockResolvedValue('new_hashed_password');
      prisma.user.create.mockResolvedValue(mockInstructor);
      prisma.aiQuotaConfig.create.mockResolvedValue({ id: 'quota-1' });

      const result = await service.create({
        username: 'instructor1',
        password: 'Password123@',
        full_name: 'Thầy Nguyễn Văn An',
        email: 'instructor1@aita.edu.vn',
        role: 'INSTRUCTOR',
        daily_token_quota: 50000,
      });

      expect(result.message).toBe('Tạo tài khoản người dùng mới thành công');
      expect(result.data.username).toBe('instructor1');
      expect(prisma.aiQuotaConfig.create).toHaveBeenCalled();
    });
  });

  describe('UT02_Users_TC003: Xem chi tiết tài khoản theo ID', () => {
    it('trả về thông tin người dùng và quota khi ID tồn tại', async () => {
      prisma.user.findFirst.mockResolvedValue({
        ...mockInstructor,
        quotaConfig: { dailyTokenLimit: 50000 },
      });

      const result = await service.get(mockInstructor.id);

      expect(result.message).toBe('Lấy thông tin tài khoản thành công');
      expect(result.data.id).toBe(mockInstructor.id);
      expect(result.data.daily_token_quota).toBe(50000);
    });

    it('ném NotFoundException khi không tìm thấy người dùng', async () => {
      prisma.user.findFirst.mockResolvedValue(null);

      await expect(service.get('nonexistent-uuid')).rejects.toThrow(NotFoundException);
    });
  });

  describe('UT02_Users_TC004: Cập nhật thông tin tài khoản', () => {
    it('cập nhật thành công tên hiển thị và hạn ngạch AI', async () => {
      prisma.user.findFirst.mockResolvedValue(mockInstructor);
      prisma.user.update.mockResolvedValue({
        ...mockInstructor,
        fullName: 'Thầy Nguyễn Văn An (Updated)',
        updatedAt: new Date(),
      });

      const result = await service.update(
        mockInstructor.id,
        { full_name: 'Thầy Nguyễn Văn An (Updated)', daily_token_quota: 80000 },
        mockAdmin.id,
      );

      expect(result.message).toBe('Cập nhật tài khoản thành công');
      expect(result.data.full_name).toBe('Thầy Nguyễn Văn An (Updated)');
      expect(prisma.aiQuotaConfig.upsert).toHaveBeenCalled();
    });

    it('ngăn chặn người dùng tự khóa tài khoản của chính mình', async () => {
      prisma.user.findFirst.mockResolvedValue(mockAdmin);

      await expect(
        service.update(mockAdmin.id, { is_active: false }, mockAdmin.id),
      ).rejects.toThrow(ForbiddenException);
    });
  });

  describe('UT02_Users_TC005: Xóa mềm tài khoản người dùng', () => {
    it('đánh dấu isDeleted=true và thu hồi refresh token của người dùng', async () => {
      prisma.user.findFirst.mockResolvedValue(mockInstructor);
      prisma.user.update.mockResolvedValue({ ...mockInstructor, isDeleted: true });

      const result = await service.delete(mockInstructor.id, mockAdmin.id);

      expect(result.message).toBe('Xóa người dùng thành công');
      expect(prisma.user.update).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { id: mockInstructor.id },
          data: expect.objectContaining({ isDeleted: true, isActive: false }),
        }),
      );
    });

    it('ngăn chặn người dùng tự xóa tài khoản của chính mình', async () => {
      prisma.user.findFirst.mockResolvedValue(mockAdmin);

      await expect(service.delete(mockAdmin.id, mockAdmin.id)).rejects.toThrow(ForbiddenException);
    });
  });

  describe('UT02_Users_TC006: response quota mới + xóa cache báo cáo tổng quan', () => {
    it('create trả daily_token_quota theo yêu cầu và xóa cache overview', async () => {
      const redis = { del: jest.fn().mockResolvedValue(undefined) };
      const withCache = new UsersService(prisma as unknown as PrismaService, redis as any);
      (bcrypt.hash as jest.Mock).mockResolvedValue('new_hashed_password');
      prisma.user.create.mockResolvedValue(mockInstructor);

      const result = await withCache.create({
        username: 'teacher_binh',
        password: 'Abc12345',
        full_name: 'Thầy Bình',
        email: 'binh@aita.edu.vn',
        role: 'INSTRUCTOR',
        daily_token_quota: 7777,
      });

      expect(result.data.daily_token_quota).toBe(7777);
      expect(result.data.used_tokens_today).toBe(0);
      expect(redis.del).toHaveBeenCalledWith(REPORTS_OVERVIEW_CACHE_KEY);
    });

    it('update trả quota vừa lưu thay vì snapshot cũ trước khi upsert', async () => {
      const redis = { del: jest.fn().mockResolvedValue(undefined) };
      const withCache = new UsersService(prisma as unknown as PrismaService, redis as any);
      prisma.user.findFirst.mockResolvedValue(mockInstructor);
      prisma.user.update.mockResolvedValue({
        ...mockInstructor,
        fullName: 'Thầy Nguyễn Văn An (Updated)',
        quotaConfig: { dailyTokenLimit: 50000, usedTokensToday: 12000 },
        updatedAt: new Date(),
      });

      const result = await withCache.update(mockInstructor.id, { daily_token_quota: 80000 } as any, mockAdmin.id);

      expect(result.data.daily_token_quota).toBe(80000);
      expect(result.data.used_tokens_today).toBe(12000);
      expect(redis.del).toHaveBeenCalledWith(REPORTS_OVERVIEW_CACHE_KEY);
    });

    it('delete cũng xóa cache overview', async () => {
      const redis = { del: jest.fn().mockResolvedValue(undefined) };
      const withCache = new UsersService(prisma as unknown as PrismaService, redis as any);
      prisma.user.findFirst.mockResolvedValue(mockInstructor);
      prisma.user.update.mockResolvedValue({ ...mockInstructor, isDeleted: true });
      prisma.aiQuotaConfig.updateMany.mockResolvedValue({ count: 1 });
      prisma.refreshToken.updateMany.mockResolvedValue({ count: 1 });

      const result = await withCache.delete(mockInstructor.id, mockAdmin.id);

      expect(result.message).toBe('Xóa người dùng thành công');
      expect(redis.del).toHaveBeenCalledWith(REPORTS_OVERVIEW_CACHE_KEY);
    });
  });
});
