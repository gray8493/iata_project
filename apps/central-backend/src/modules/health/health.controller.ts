import { Controller, Get, Inject, ServiceUnavailableException, UseGuards } from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';
import { AdaptiveThrottlerGuard } from '../../common/guards/adaptive-throttler.guard';
import { ThrottlerStorage } from '@nestjs/throttler';
import { PrismaService } from '../../prisma/prisma.service';

@ApiTags('Health')
@Controller('health')
@UseGuards(AdaptiveThrottlerGuard)
export class HealthController {
  constructor(private readonly prisma: PrismaService, @Inject(ThrottlerStorage) private readonly rateLimitStorage: ThrottlerStorage) {}

  @Get()
  @ApiOperation({ summary: 'Kiểm tra trạng thái API và PostgreSQL' })
  async health() {
    await this.prisma.$queryRaw`SELECT 1`;
    const storage = this.rateLimitStorage as ThrottlerStorage & { isRedisStorage?: boolean; isHealthy?: boolean };
    if (storage.isRedisStorage && !storage.isHealthy) {
      throw new ServiceUnavailableException({ error_code: 'RATE_LIMIT_STORAGE_UNAVAILABLE', message: 'Kho rate limit hiện không khả dụng.', details: null });
    }
    return { message: 'Dịch vụ đang hoạt động', data: {
      status: 'ok', database: 'ok', rate_limit_storage: storage.isRedisStorage ? 'redis' : 'memory',
    } };
  }
}
