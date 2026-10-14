import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import * as Joi from 'joi';
import { AuthModule } from './modules/auth/auth.module';
import { UsersModule } from './modules/users/users.module';
import { AiGatewayModule } from './modules/ai-gateway/ai-gateway.module';
import { AuditLogsModule } from './modules/audit-logs/audit-logs.module';
import { HealthModule } from './modules/health/health.module';
import { RateLimitModule } from './common/rate-limit.module';
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
        GEMINI_API_KEY: Joi.string().allow('').optional(),
        GEMINI_MODEL: Joi.string().default('gemini-3.8-flash'),
        WEB_ADMIN_ORIGINS: Joi.string().default('http://localhost:3001'),
      }),
    }),
    PrismaModule,
    AuthModule,
    UsersModule,
    AiGatewayModule,
    AuditLogsModule,
    HealthModule,
    RateLimitModule,
  ],
})
export class AppModule {}
