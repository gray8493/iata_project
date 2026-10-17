import { Injectable, Logger, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { createClient, type RedisClientType } from 'redis';

export const REPORTS_OVERVIEW_CACHE_KEY = 'reports:overview:v1';

@Injectable()
export class RedisService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(RedisService.name);
  private client: RedisClientType | null = null;

  constructor(private readonly config: ConfigService) {}

  async onModuleInit(): Promise<void> {
    const url = this.config.get<string>('REDIS_URL');
    if (!url) return;
    try {
      const client = createClient({ url }) as RedisClientType;
      client.on('error', () => this.logger.error('Redis cache connection error.'));
      await client.connect();
      this.client = client;
    } catch {
      this.logger.warn('Redis cache unavailable; falling back to direct queries.');
      this.client = null;
    }
  }

  async onModuleDestroy(): Promise<void> {
    if (this.client?.isOpen) await this.client.quit();
  }

  async getJson<T>(key: string): Promise<T | null> {
    if (!this.client?.isReady) return null;
    try {
      const raw = await this.client.get(key);
      return raw ? (JSON.parse(raw) as T) : null;
    } catch {
      return null;
    }
  }

  async setJson(key: string, value: unknown, ttlSeconds: number): Promise<void> {
    if (!this.client?.isReady) return;
    try {
      await this.client.set(key, JSON.stringify(value), { EX: ttlSeconds });
    } catch {
      this.logger.warn(`Redis SET failed for key ${key}.`);
    }
  }

  async del(key: string): Promise<void> {
    if (!this.client?.isReady) return;
    try {
      await this.client.del(key);
    } catch {
      this.logger.warn(`Redis DEL failed for key ${key}.`);
    }
  }
}
