import { Global, Logger, Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { ThrottlerGuard, ThrottlerModule } from '@nestjs/throttler';
import { AdaptiveThrottlerGuard } from './guards/adaptive-throttler.guard';
import { createClient } from 'redis';
import { RedisThrottlerStorage } from './redis-throttler.storage';

@Global()
@Module({
  imports: [ThrottlerModule.forRootAsync({
    imports: [ConfigModule],
    inject: [ConfigService],
    useFactory: async (config: ConfigService) => {
      const redisUrl = config.get<string>('REDIS_URL');
      if (!redisUrl) return { throttlers: [{ name: 'default', ttl: 60_000, limit: 80 }] };
      const client = createClient({ url: redisUrl });
      client.on('error', () => new Logger('RateLimitModule').error('Redis rate-limit storage connection error.'));
      await client.connect();
      return { throttlers: [{ name: 'default', ttl: 60_000, limit: 80 }], storage: new RedisThrottlerStorage(client) };
    },
  })],
  providers: [AdaptiveThrottlerGuard, ThrottlerGuard],
  exports: [AdaptiveThrottlerGuard, ThrottlerGuard],
})
export class RateLimitModule {}
