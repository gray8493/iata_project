import { ForbiddenException, HttpException, Injectable, Optional } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { RedisService, REPORTS_OVERVIEW_CACHE_KEY } from '../../common/redis.service';

export type AiFeature = 'TESTCASE_GEN' | 'CODE_REVIEW' | 'PLAGIARISM' | 'UI_EVALUATION';
export interface QuotaReservation { configId: string; reserved: number; date: Date; }

@Injectable()
export class AiQuotaService {
  constructor(
    private readonly prisma: PrismaService,
    @Optional() private readonly redis?: RedisService,
  ) {}

  async snapshot(userId: string) {
    const config = await this.getCurrentConfig(userId);
    const now = new Date();
    const resetAt = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1));
    return {
      daily_limit_tokens: config.dailyTokenLimit,
      used_tokens_today: config.usedTokensToday,
      remaining_tokens: Math.max(0, config.dailyTokenLimit - config.usedTokensToday),
      reset_at_utc: resetAt.toISOString(),
    };
  }

  async reserve(userId: string, amount: number): Promise<QuotaReservation> {
    const date = this.todayUtc();
    return this.prisma.$transaction(async (tx) => {
      const config = await tx.aiQuotaConfig.findFirst({ where: { userId, isDeleted: false } });
      if (!config) throw new ForbiddenException({ error_code: 'AI_QUOTA_NOT_CONFIGURED', message: 'Tài khoản chưa được cấu hình hạn ngạch AI.', details: null });
      if (this.dateKey(config.lastResetDate) < this.dateKey(date)) {
        await tx.aiQuotaConfig.updateMany({
          where: { id: config.id, lastResetDate: { lt: date }, isDeleted: false },
          data: { usedTokensToday: 0, lastResetDate: date },
        });
      }
      const current = await tx.aiQuotaConfig.findUnique({ where: { id: config.id } });
      if (!current || current.isDeleted) throw new ForbiddenException({ error_code: 'AI_QUOTA_NOT_CONFIGURED', message: 'Tài khoản chưa được cấu hình hạn ngạch AI.', details: null });
      const reserved = await tx.aiQuotaConfig.updateMany({
        where: { id: current.id, isDeleted: false, usedTokensToday: { lte: current.dailyTokenLimit - amount } },
        data: { usedTokensToday: { increment: amount } },
      });
      if (reserved.count !== 1) throw new HttpException({ error_code: 'AI_QUOTA_EXCEEDED', message: 'Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.', details: null }, 429);
      return { configId: current.id, reserved: amount, date };
    });
  }

  async settle(userId: string, reservation: QuotaReservation, usage: { promptTokens: number; completionTokens: number; totalTokens: number }, feature: AiFeature, model: string): Promise<void> {
    const actual = usage.totalTokens;
    const delta = actual - reservation.reserved;
    await this.prisma.$transaction(async (tx) => {
      const current = await tx.aiQuotaConfig.findUnique({ where: { id: reservation.configId } });
      if (current && !current.isDeleted && this.dateKey(current.lastResetDate) === this.dateKey(reservation.date) && delta !== 0) {
        await tx.aiQuotaConfig.update({ where: { id: current.id }, data: { usedTokensToday: { increment: delta } } });
      }
      await tx.aiQuotaLog.create({ data: {
        userId, featureType: feature, modelName: model,
        promptTokens: usage.promptTokens,
        completionTokens: usage.completionTokens,
        totalTokens: actual,
      } });
    });
    await this.redis?.del(REPORTS_OVERVIEW_CACHE_KEY);
  }

  async release(reservation: QuotaReservation): Promise<void> {
    await this.prisma.aiQuotaConfig.updateMany({
      where: { id: reservation.configId, isDeleted: false, lastResetDate: reservation.date, usedTokensToday: { gte: reservation.reserved } },
      data: { usedTokensToday: { decrement: reservation.reserved } },
    });
  }

  private async getCurrentConfig(userId: string) {
    const date = this.todayUtc();
    return this.prisma.$transaction(async (tx) => {
      const config = await tx.aiQuotaConfig.findFirst({ where: { userId, isDeleted: false } });
      if (!config) throw new ForbiddenException({ error_code: 'AI_QUOTA_NOT_CONFIGURED', message: 'Tài khoản chưa được cấu hình hạn ngạch AI.', details: null });
      if (this.dateKey(config.lastResetDate) < this.dateKey(date)) {
        await tx.aiQuotaConfig.updateMany({ where: { id: config.id, lastResetDate: { lt: date }, isDeleted: false }, data: { usedTokensToday: 0, lastResetDate: date } });
      }
      return (await tx.aiQuotaConfig.findUnique({ where: { id: config.id } }))!;
    });
  }

  private todayUtc(): Date {
    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  }

  private dateKey(date: Date): string { return date.toISOString().slice(0, 10); }
}
