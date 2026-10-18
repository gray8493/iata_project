import { BadRequestException } from '@nestjs/common';
import { AuditLogsService } from '../modules/audit-logs/audit-logs.service';
import { PrismaService } from '../prisma/prisma.service';

describe('AuditLogsService (Web Admin Reports Unit Tests)', () => {
  let service: AuditLogsService;
  let prisma: any;

  beforeEach(() => {
    prisma = {
      aiQuotaLog: {
        findMany: jest.fn(),
        count: jest.fn(),
        aggregate: jest.fn(),
        groupBy: jest.fn(),
      },
      user: {
        count: jest.fn(),
      },
      aiQuotaConfig: {
        aggregate: jest.fn(),
      },
      $transaction: jest.fn((callback) => {
        if (typeof callback === 'function') {
          return callback(prisma);
        }
        return Promise.all(callback);
      }),
    };

    service = new AuditLogsService(prisma as unknown as PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('UT04_Reports_TC001: Lấy báo cáo thống kê tổng quan (overview)', () => {
    it('trả về tổng số giảng viên, hạn ngạch và tính năng AI dùng nhiều nhất', async () => {
      prisma.user.count.mockResolvedValue(10);
      prisma.aiQuotaConfig.aggregate.mockResolvedValue({ _sum: { dailyTokenLimit: 500000 } });
      prisma.aiQuotaLog.aggregate.mockResolvedValue({ _sum: { totalTokens: 125000 } });
      prisma.aiQuotaLog.groupBy.mockResolvedValue([
        { featureType: 'TESTCASE_GEN', _sum: { totalTokens: 80000 } },
      ]);

      const result = await service.overview();

      expect(result.message).toBe('Lấy số liệu thống kê tổng quan thành công');
      expect(result.data.total_instructors).toBe(10);
      expect(result.data.ai_token_usage.total_tokens_consumed_month).toBe(125000);
      expect(result.data.ai_token_usage.top_consuming_feature).toBe('TESTCASE_GEN');
    });
  });

  describe('UT04_Reports_TC002: Lấy nhật ký sử dụng AI có lọc (listAiUsage)', () => {
    it('trả về danh sách nhật ký AI kèm phân trang', async () => {
      const mockLog = {
        id: 'log-uuid-1',
        userId: 'user-uuid-1',
        featureType: 'TESTCASE_GEN',
        modelName: 'gemini-3.8-flash',
        promptTokens: 500,
        completionTokens: 200,
        totalTokens: 700,
        createdAt: new Date('2026-10-14T10:00:00.000Z'),
        user: { username: 'instructor1', fullName: 'Thầy Nguyễn Văn An' },
      };

      prisma.aiQuotaLog.findMany.mockResolvedValue([mockLog]);
      prisma.aiQuotaLog.count.mockResolvedValue(1);

      const result = await service.listAiUsage({ page: 1, page_size: 10 });

      expect(result.message).toBe('Lấy nhật ký sử dụng AI thành công');
      expect(result.data.items).toHaveLength(1);
      expect(result.data.items[0].username).toBe('instructor1');
      expect(result.data.items[0].total_tokens).toBe(700);
    });

    it('ném BadRequestException nếu khoảng ngày không hợp lệ (from > to)', async () => {
      await expect(
        service.listAiUsage({ page: 1, page_size: 10, from: '2026-10-20', to: '2026-10-10' }),
      ).rejects.toThrow(BadRequestException);
    });
  });
});
