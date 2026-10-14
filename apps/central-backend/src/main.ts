import 'reflect-metadata';
import { json } from 'express';
import { UnprocessableEntityException, ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { ApiExceptionFilter } from './common/filters/api-exception.filter';
import { ResponseEnvelopeInterceptor } from './common/interceptors/response-envelope.interceptor';

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule, { bufferLogs: true, bodyParser: false });
  app.use(json({ limit: '7mb' }));
  app.setGlobalPrefix('api/v1');
  const config = app.get(ConfigService);
  app.getHttpAdapter().getInstance().set('trust proxy', config.get<number>('TRUST_PROXY_HOPS', 0));
  app.enableCors({
    origin: config.getOrThrow<string>('WEB_ADMIN_ORIGINS').split(',').map((origin) => origin.trim()).filter(Boolean),
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Authorization', 'Content-Type'],
  });
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
    exceptionFactory: (errors) => new UnprocessableEntityException({
      error_code: 'VALIDATION_FAILED',
      message: 'Dữ liệu gửi lên không đúng định dạng.',
      details: errors.map((error) => ({ field: error.property, issues: Object.values(error.constraints ?? {}) })),
    }),
  }));
  app.useGlobalFilters(new ApiExceptionFilter());
  app.useGlobalInterceptors(new ResponseEnvelopeInterceptor());

  const swaggerConfig = new DocumentBuilder()
    .setTitle('AITA System API')
    .setDescription('Central API for authentication, administration, and AI services.')
    .setVersion('1.0.0')
    .addBearerAuth()
    .build();
  SwaggerModule.setup('api/docs', app, SwaggerModule.createDocument(app, swaggerConfig));

  await app.listen(process.env.PORT ? Number(process.env.PORT) : 3000);
}

void bootstrap();
