import { INestApplication } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { json } from 'express';
import compression = require('compression');
import { ApiExceptionFilter } from './common/filters/api-exception.filter';
import { ResponseEnvelopeInterceptor } from './common/interceptors/response-envelope.interceptor';
import { createValidationPipe } from './common/validation/validation-pipe.factory';

export function configureApp(app: INestApplication): void {
  app.use(compression({ threshold: 1024 }));
  app.use(json({ limit: '7mb' }));
  app.setGlobalPrefix('api/v1');
  const config = app.get(ConfigService);
  app.getHttpAdapter().getInstance().set('trust proxy', config.get<number>('TRUST_PROXY_HOPS', 0));
  app.enableCors({
    origin: config
      .getOrThrow<string>('CORS_ORIGINS')
      .split(',')
      .map((origin) => origin.trim())
      .filter(Boolean),
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Authorization', 'Content-Type', 'X-Requested-With'],
    exposedHeaders: ['X-Total-Count'],
    credentials: true,
    maxAge: 86400,
  });
  app.useGlobalPipes(createValidationPipe());
  app.useGlobalFilters(new ApiExceptionFilter());
  app.useGlobalInterceptors(new ResponseEnvelopeInterceptor());

  const swaggerConfig = new DocumentBuilder()
    .setTitle('AITA System API')
    .setDescription('Central API for authentication, administration, and AI services.')
    .setVersion('1.0.0')
    .addBearerAuth()
    .build();
  SwaggerModule.setup('api/docs', app, SwaggerModule.createDocument(app, swaggerConfig));
}
