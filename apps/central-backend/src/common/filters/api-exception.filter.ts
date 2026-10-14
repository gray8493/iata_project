import { ArgumentsHost, Catch, ExceptionFilter, HttpException, HttpStatus, Logger } from '@nestjs/common';
import { Request, Response } from 'express';

@Catch()
export class ApiExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(ApiExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const context = host.switchToHttp();
    const request = context.getRequest<Request>();
    const response = context.getResponse<Response>();
    const status = exception instanceof HttpException ? exception.getStatus() : HttpStatus.INTERNAL_SERVER_ERROR;
    const payload = exception instanceof HttpException ? exception.getResponse() : null;

    if (!(exception instanceof HttpException) || status >= 500) {
      this.logger.error(`Request failed: ${request.method} ${request.url}`, exception instanceof Error ? exception.stack : undefined);
    }

    const body = typeof payload === 'object' && payload !== null ? payload as Record<string, unknown> : {};
    const validationMessages = Array.isArray(body.message) ? body.message : undefined;
    response.status(status).json({
      success: false,
      status_code: status,
      error_code: typeof body.error_code === 'string' ? body.error_code : this.errorCodeFor(status),
      message: typeof body.message === 'string' ? body.message : status >= 500 ? 'Đã xảy ra lỗi hệ thống.' : 'Yêu cầu không hợp lệ.',
      details: body.details ?? validationMessages ?? null,
      timestamp: new Date().toISOString(),
    });
  }

  private errorCodeFor(status: number): string {
    if (status === 400) return 'BAD_REQUEST';
    if (status === 401) return 'AUTH_UNAUTHORIZED';
    if (status === 403) return 'FORBIDDEN';
    if (status === 404) return 'NOT_FOUND';
    if (status === 409) return 'CONFLICT';
    if (status === 422) return 'VALIDATION_FAILED';
    if (status === 429) return 'RATE_LIMIT_EXCEEDED';
    if (status === 502) return 'UPSTREAM_SERVICE_ERROR';
    return 'INTERNAL_SERVER_ERROR';
  }
}
