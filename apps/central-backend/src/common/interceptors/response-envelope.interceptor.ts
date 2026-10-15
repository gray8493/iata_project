import { CallHandler, ExecutionContext, Injectable, NestInterceptor } from '@nestjs/common';
import { Response } from 'express';
import { map, Observable } from 'rxjs';

@Injectable()
export class ResponseEnvelopeInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const httpResponse = context.switchToHttp().getResponse<Response>();
    return next.handle().pipe(
      map((result: { message?: string; data?: unknown } | unknown) => {
        const payload = result as { message?: string; data?: unknown };
        return {
          success: true,
          status_code: httpResponse.statusCode,
          message: payload?.message ?? 'Thao tác thành công',
          data: payload && Object.prototype.hasOwnProperty.call(payload, 'data') ? payload.data : result ?? null,
          timestamp: new Date().toISOString(),
        };
      }),
    );
  }
}
