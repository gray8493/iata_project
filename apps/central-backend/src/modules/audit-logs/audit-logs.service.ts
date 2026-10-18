import { BadRequestException, Injectable, Optional } from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { PrismaService } from '../../prisma/prisma.service';
import { RedisService, REPORTS_OVERVIEW_CACHE_KEY } from '../../common/redis.service';
import { ListAiUsageDto } from './dto/list-ai-usage.dto';

export interface OverviewResult {
  message: string;
  data: {
    total_instructors: number;
    ai_token_usage: {
      total_tokens_consumed_month: number;
      total_budget_limit: number;
      top_consuming_feature: string | null;
    };
  };
}

@Injectable()
export class AuditLogsService {
  constructor(
    private readonly prisma: PrismaService,
    @Optional() private readonly redis?: RedisService,
  ) {}

  async listAiUsage(query: ListAiUsageDto) {
    const from = query.from ? new Date(query.from) : undefined;
    const to = query.to ? new Date(query.to) : undefined;
    if (from && to && from > to) {
      throw new BadRequestException({ error_code: 'INVALID_DATE_RANGE', message: 'Thời điểm bắt đầu phải nhỏ hơn hoặc bằng thời điểm kết thúc.', details: null });
    }
    const where: Prisma.AiQuotaLogWhereInput = {
      isDeleted: false,
      ...(query.user_id ? { userId: query.user_id } : {}),
      ...(from || to ? { createdAt: { ...(from ? { gte: from } : {}), ...(to ? { lte: to } : {}) } } : {}),
    };
    const skip = (query.page - 1) * query.page_size;
    const [logs, totalItems] = await this.prisma.$transaction([
      this.prisma.aiQuotaLog.findMany({
        where, skip, take: query.page_size,
        orderBy: [{ createdAt: 'desc' }, { id: 'asc' }],
        select: {
          id: true, userId: true, featureType: true, modelName: true,
          promptTokens: true, completionTokens: true, totalTokens: true, createdAt: true,
          user: { select: { username: true, fullName: true } },
        },
      }),
      this.prisma.aiQuotaLog.count({ where }),
    ]);
    return { message: 'Lấy nhật ký sử dụng AI thành công', data: {
      items: logs.map((log) => ({
        id: log.id, user_id: log.userId, username: log.user.username, full_name: log.user.fullName,
        feature_type: log.featureType, model_name: log.modelName,
        prompt_tokens: log.promptTokens, completion_tokens: log.completionTokens, total_tokens: log.totalTokens,
        created_at: log.createdAt.toISOString(),
      })),
      pagination: { page: query.page, page_size: query.page_size, total_items: totalItems, total_pages: Math.ceil(totalItems / query.page_size) },
    } };
  }

  async overview(): Promise<OverviewResult> {
    const cached = await this.redis?.getJson<OverviewResult>(REPORTS_OVERVIEW_CACHE_KEY);
    if (cached) return cached;

    const now = new Date();
    const monthStart = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1));
    const daysInMonth = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 0)).getUTCDate();
    const [totalInstructors, quota, usage, topFeature] = await Promise.all([
      this.prisma.user.count({ where: { role: 'INSTRUCTOR', isDeleted: false } }),
      this.prisma.aiQuotaConfig.aggregate({
        where: { isDeleted: false, user: { role: 'INSTRUCTOR', isActive: true, isDeleted: false } },
        _sum: { dailyTokenLimit: true },
      }),
      this.prisma.aiQuotaLog.aggregate({ where: { isDeleted: false, createdAt: { gte: monthStart } }, _sum: { totalTokens: true } }),
      this.prisma.aiQuotaLog.groupBy({
        by: ['featureType'], where: { isDeleted: false, createdAt: { gte: monthStart } },
        _sum: { totalTokens: true }, orderBy: { _sum: { totalTokens: 'desc' } }, take: 1,
      }),
    ]);
    const result: OverviewResult = { message: 'Lấy số liệu thống kê tổng quan thành công', data: {
      total_instructors: totalInstructors,
      ai_token_usage: {
        total_tokens_consumed_month: usage._sum.totalTokens ?? 0,
        total_budget_limit: (quota._sum.dailyTokenLimit ?? 0) * daysInMonth,
        top_consuming_feature: topFeature[0]?.featureType ?? null,
      },
    } };
    await this.redis?.setJson(REPORTS_OVERVIEW_CACHE_KEY, result, 45);
    return result;
  }
}
