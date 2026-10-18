import { UnprocessableEntityException, ValidationPipe } from '@nestjs/common';

export function createValidationPipe(): ValidationPipe {
  return new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
    exceptionFactory: (errors) => new UnprocessableEntityException({
      error_code: 'VALIDATION_FAILED',
      message: 'Dữ liệu gửi lên không đúng định dạng.',
      details: errors.map((error) => ({ field: error.property, issues: Object.values(error.constraints ?? {}) })),
    }),
  });
}
