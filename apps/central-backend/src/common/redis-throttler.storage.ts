import { randomUUID } from 'node:crypto';
import { createClient } from 'redis';
import { ThrottlerStorage } from '@nestjs/throttler';

interface ThrottlerStorageRecord {
  totalHits: number;
  timeToExpire: number;
  isBlocked: boolean;
  timeToBlockExpire: number;
}

const incrementScript = `
local now = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local blockDuration = tonumber(ARGV[4])
local member = ARGV[5]
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - ttl)
local total = redis.call('ZCARD', KEYS[1])
local blockedTtl = redis.call('PTTL', KEYS[2])
local oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
local timeToExpire = ttl
if #oldest > 0 then
  timeToExpire = math.max(0, ttl - (now - tonumber(oldest[2])))
end
if blockedTtl > 0 then
  return { total, timeToExpire, 1, blockedTtl }
end
if total >= limit then
  redis.call('SET', KEYS[2], '1', 'PX', blockDuration)
  return { total, timeToExpire, 1, blockDuration }
end
redis.call('ZADD', KEYS[1], now, member)
redis.call('PEXPIRE', KEYS[1], ttl)
total = total + 1
oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
timeToExpire = math.max(0, ttl - (now - tonumber(oldest[2])))
return { total, timeToExpire, 0, 0 }
`;

type RedisClient = ReturnType<typeof createClient>;

export class RedisThrottlerStorage implements ThrottlerStorage {
  constructor(private readonly client: RedisClient) {}

  get isRedisStorage(): true { return true; }
  get isHealthy(): boolean { return this.client.isReady; }

  async increment(key: string, ttl: number, limit: number, blockDuration: number, _throttlerName: string): Promise<ThrottlerStorageRecord> {
    const values = await this.client.eval(incrementScript, {
      keys: [key, `${key}:blocked`],
      arguments: [String(Date.now()), String(ttl), String(limit), String(blockDuration), randomUUID()],
    }) as number[];
    return {
      totalHits: Number(values[0]),
      timeToExpire: Math.ceil(Number(values[1]) / 1000),
      isBlocked: Number(values[2]) === 1,
      timeToBlockExpire: Math.ceil(Number(values[3]) / 1000),
    };
  }

  async onApplicationShutdown(): Promise<void> {
    if (this.client.isOpen) await this.client.quit();
  }
}
