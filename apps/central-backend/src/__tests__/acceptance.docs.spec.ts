import { ForbiddenException } from '@nestjs/common';
import { AiGatewayService } from '../modules/ai-gateway/ai-gateway.service';
import { GeminiService } from '../modules/ai-gateway/gemini.service';
import { AuditLogsService } from '../modules/audit-logs/audit-logs.service';
import { UsersService } from '../modules/users/users.service';
import { PrismaService } from '../prisma/prisma.service';
import { RedisService } from '../common/redis.service';
import { RolesGuard } from '../common/guards/roles.guard';

describe('Acceptance (docs: docs/testcases/4-acceptance/acceptance-test-specification.md)', () => {
  let prisma: any;
  let redis: any;

  beforeEach(() => {
    prisma = {
      user: { count: jest.fn(), findMany: jest.fn() },
      aiQuotaConfig: { aggregate: jest.fn() },
      aiQuotaLog: { aggregate: jest.fn(), groupBy: jest.fn() },
      $transaction: jest.fn((arg: any) => (typeof arg === 'function' ? arg(prisma) : Promise.all(arg))),
    };
    redis = { getJson: jest.fn().mockResolvedValue(null), setJson: jest.fn().mockResolvedValue(undefined), del: jest.fn() };
  });

  afterEach(() => jest.clearAllMocks());

  describe('AT03_PedagogicalAIReview_TC001: AI sinh nhận xét sư phạm cho bài sai logic', () => {
    it('trả về nhận xét và dòng lỗi nghi vấn, không trả lời giải hoàn chỉnh', async () => {
      const gemini = {
        generateJson: jest.fn().mockResolvedValue({
          data: { suspected_error_line: 18, issue_summary: 'Biến đếm không được cập nhật trong vòng lặp', pedagogical_feedback: 'Em hãy kiểm tra lại điều kiện cập nhật biến đếm?', bug_category: 'LOGIC_ERROR' },
          tokensConsumed: 500,
        }),
      };
      const ai = new AiGatewayService(gemini as unknown as GeminiService);

      const result = await ai.reviewCode('u1', {
        source_code: 'int main() { return 0; }'.repeat(2), language: 'C', problem_statement: 'Đếm số nguyên tố',
        failed_testcase: { input: '5', expected_output: 'YES', actual_output: 'NO' },
      } as any);

      expect(result.message).toBe('Phân tích mã nguồn bằng AI thành công');
      expect(result.data.tokens_consumed).toBe(500);
      expect((result.data as any).suspected_error_line).toBe(18);
      expect((result.data as any).bug_category).toBe('LOGIC_ERROR');
      expect(gemini.generateJson).toHaveBeenCalledWith(expect.objectContaining({ feature: 'CODE_REVIEW' }));
    });
  });

  describe('AT04_AdminOverview_TC001: Dashboard thống kê và giám sát quota AI', () => {
    it('overview trả số liệu tổng hợp và list người dùng kèm quota', async () => {
      const reports = new AuditLogsService(prisma as unknown as PrismaService, redis as unknown as RedisService);
      const users = new UsersService(prisma as unknown as PrismaService);

      prisma.user.count.mockResolvedValue(8);
      prisma.aiQuotaConfig.aggregate.mockResolvedValue({ _sum: { dailyTokenLimit: 400000 } });
      prisma.aiQuotaLog.aggregate.mockResolvedValue({ _sum: { totalTokens: 990000 } });
      prisma.aiQuotaLog.groupBy.mockResolvedValue([{ featureType: 'CODE_REVIEW', _sum: { totalTokens: 600000 } }]);

      const overview = await reports.overview();
      expect(overview.data.total_instructors).toBe(8);
      expect(overview.data.ai_token_usage.total_tokens_consumed_month).toBe(990000);
      expect(overview.data.ai_token_usage.top_consuming_feature).toBe('CODE_REVIEW');

      prisma.user.findMany.mockResolvedValue([{
        id: 'u1', username: 'teacher_an', fullName: 'Nguyễn An', email: 'an@example.com', role: 'INSTRUCTOR',
        isActive: true, createdAt: new Date('2026-10-01T00:00:00.000Z'), quotaConfig: { dailyTokenLimit: 50000, usedTokensToday: 12000 },
      }]);
      prisma.user.count.mockResolvedValue(1);

      const list = await users.list({ page: 1, page_size: 20 } as any);
      expect(list.data.items[0]).toEqual(expect.objectContaining({ daily_token_quota: 50000, used_tokens_today: 12000 }));
    });
  });

  describe('AT04_AdminSecurityRBAC_TC001: Giảng viên truy cập API Admin bị từ chối', () => {
    it('RolesGuard ném 403 FORBIDDEN_ADMIN_ONLY với role INSTRUCTOR', () => {
      const reflector = { getAllAndOverride: jest.fn().mockReturnValue(['ADMIN']) } as any;
      const context = {
        getHandler: () => ({}), getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => ({ user: { id: '1', username: 'teacher_an', role: 'INSTRUCTOR' } }) }),
      } as any;

      const error = (() => { try { new RolesGuard(reflector).canActivate(context); } catch (e) { return e as any; } })();

      expect(error).toBeInstanceOf(ForbiddenException);
      expect(error.getStatus()).toBe(403);
      expect(error.getResponse()).toEqual({ error_code: 'FORBIDDEN_ADMIN_ONLY', message: 'Bạn không có quyền thực hiện thao tác này.', details: null });
    });
  });
});
