import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import * as Joi from 'joi';
import { AuthModule } from './modules/auth/auth.module';
import { UsersModule } from './modules/users/users.module';
import { AiGatewayModule } from './modules/ai-gateway/ai-gateway.module';
import { AuditLogsModule } from './modules/audit-logs/audit-logs.module';
import { HealthModule } from './modules/health/health.module';
import { SystemModule } from './modules/system/system.module';
import { RateLimitModule } from './common/rate-limit.module';
import { RedisModule } from './common/redis.module';
import { PrismaModule } from './prisma/prisma.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validationSchema: Joi.object({
        NODE_ENV: Joi.string().valid('development', 'test', 'production').default('development'),
        PORT: Joi.number().port().default(3000),
        TRUST_PROXY_HOPS: Joi.number().integer().min(0).default(0),
        DATABASE_URL: Joi.string().uri({ scheme: ['postgres', 'postgresql'] }).required(),
        REDIS_URL: Joi.string().uri({ scheme: ['redis', 'rediss'] }).optional().allow(''),
        JWT_ACCESS_SECRET: Joi.string().min(32).required(),
        JWT_ACCESS_EXPIRES_IN: Joi.string().pattern(/^[1-9]\d*(s|m|h|d)$/).default('15m'),
        JWT_REFRESH_SECRET: Joi.string().min(32).required(),
        JWT_REFRESH_EXPIRES_IN: Joi.string().pattern(/^[1-9]\d*(s|m|h|d)$/).default('7d'),
        OPENROUTER_API_KEYS: Joi.string().allow('').optional(),
        OPENROUTER_MODEL: Joi.string().optional(),
        OPENROUTER_BASE_URL: Joi.string().uri().optional(),
        OPENROUTER_TIMEOUT_MS: Joi.number().integer().min(1).optional(),
        OPENROUTER_KEY_COOLDOWN_MS: Joi.number().integer().min(0).optional(),
        CORS_ORIGINS: Joi.string().default('http://localhost:3001'),
        APP_LATEST_VERSION: Joi.string().optional().allow(''),
        APP_MIN_SUPPORTED_VERSION: Joi.string().optional().allow(''),
        APP_UPDATE_MANDATORY: Joi.boolean().truthy('true').falsy('false').default(false),
        APP_UPDATE_NOTES: Joi.string().optional().allow(''),
        APP_UPDATE_PUBLISHED_AT: Joi.string().optional().allow(''),
        APP_UPDATE_ARTIFACT_TYPE: Joi.string().valid('exe', 'zip').default('zip'),
        APP_UPDATE_ENTRYPOINT: Joi.string().optional().allow(''),
        APP_UPDATE_URL_WINDOWS: Joi.string().uri().optional().allow(''),
        APP_UPDATE_SHA256_WINDOWS: Joi.string().pattern(/^[a-fA-F0-9]{64}$/).optional().allow(''),
        APP_UPDATE_SIZE_WINDOWS: Joi.number().integer().min(0).optional().allow(''),
      }),
    }),
    PrismaModule,
    RedisModule,
    AuthModule,
    UsersModule,
    AiGatewayModule,
    AuditLogsModule,
    HealthModule,
    SystemModule,
    RateLimitModule,
  ],
})
export class AppModule {}
