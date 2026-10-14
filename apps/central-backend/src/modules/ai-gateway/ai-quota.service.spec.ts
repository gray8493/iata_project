import { ForbiddenException, HttpException } from '@nestjs/common';
import { AiQuotaService } from './ai-quota.service';
import { PrismaService } from '../../prisma/prisma.service';

describe('AiQuotaService (Web Admin AI Quota Unit Tests)', () => {
  let service: AiQuotaService;
  let prisma: any;

  const mockConfig = {
    id: 'quota-config-1',
    userId: 'user-uuid-1',
    dailyTokenLimit: 50000,
    usedTokensToday: 15000,
    lastResetDate: new Date('2026-10-14T00:00:00.000Z'),
    isDeleted: false,
  };

  beforeEach(() => {
    prisma = {
      aiQuotaConfig: {
        findFirst: jest.fn(),
        findUnique: jest.fn(),
        update: jest.fn(),
        updateMany: jest.fn(),
      },
      aiQuotaLog: {
        create: jest.fn(),
      },
      $transaction: jest.fn((callback) => {
        if (typeof callback === 'function') {
          return callback(prisma);
        }
        return Promise.all(callback);
      }),
    };

    service = new AiQuotaService(prisma as unknown as PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('UT04_AiQuota_TC001: Lấy snapshot hạn mức AI trong ngày của người dùng', () => {
    it('trả về daily limit, used tokens và remaining tokens', async () => {
      prisma.aiQuotaConfig.findFirst.mockResolvedValue(mockConfig);
      prisma.aiQuotaConfig.findUnique.mockResolvedValue(mockConfig);

      const result = await service.snapshot('user-uuid-1');

      expect(result.daily_limit_tokens).toBe(50000);
      expect(result.used_tokens_today).toBe(15000);
      expect(result.remaining_tokens).toBe(35000);
      expect(result.reset_at_utc).toBeDefined();
    });

    it('ném ForbiddenException nếu tài khoản chưa được cấu hình hạn ngạch', async () => {
      prisma.aiQuotaConfig.findFirst.mockResolvedValue(null);

      await expect(service.snapshot('user-without-quota')).rejects.toThrow(ForbiddenException);
    });
  });

  describe('UT04_AiQuota_TC002: Đặt trước (reserve) token AI khi số token còn lại đủ', () => {
    it('đặt trước thành công và tăng usedTokensToday', async () => {
      prisma.aiQuotaConfig.findFirst.mockResolvedValue(mockConfig);
      prisma.aiQuotaConfig.findUnique.mockResolvedValue(mockConfig);
      prisma.aiQuotaConfig.updateMany.mockResolvedValue({ count: 1 });

      const reservation = await service.reserve('user-uuid-1', 5000);

      expect(reservation.configId).toBe('quota-config-1');
      expect(reservation.reserved).toBe(5000);
    });

    it('ném HttpException 429 khi vượt quá hạn ngạch trong ngày', async () => {
      prisma.aiQuotaConfig.findFirst.mockResolvedValue(mockConfig);
      prisma.aiQuotaConfig.findUnique.mockResolvedValue(mockConfig);
      // updateMany count = 0 biểu thị không thỏa mãn điều kiện usedTokensToday <= limit - amount
      prisma.aiQuotaConfig.updateMany.mockResolvedValue({ count: 0 });

      await expect(service.reserve('user-uuid-1', 40000)).rejects.toThrow(HttpException);
    });
  });

  describe('UT04_AiQuota_TC003: Quyết toán (settle) token và ghi nhật ký ai_quota_logs', () => {
    it('ghi log sử dụng AI và điều chỉnh số token thực tế', async () => {
      prisma.aiQuotaConfig.findUnique.mockResolvedValue(mockConfig);
      prisma.aiQuotaConfig.update.mockResolvedValue(mockConfig);
      prisma.aiQuotaLog.create.mockResolvedValue({ id: 'log-1' });

      const reservation = {
        configId: 'quota-config-1',
        reserved: 5000,
        date: mockConfig.lastResetDate,
      };

      await service.settle(
        'user-uuid-1',
        reservation,
        { promptTokens: 3000, completionTokens: 1500, totalTokens: 4500 },
        'TESTCASE_GEN',
        'gemini-3.8-flash',
      );

      expect(prisma.aiQuotaLog.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            userId: 'user-uuid-1',
            featureType: 'TESTCASE_GEN',
            totalTokens: 4500,
          }),
        }),
      );
    });
  });
});
