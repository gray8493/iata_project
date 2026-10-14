import { ExecutionContext, HttpException, HttpStatus, Injectable } from '@nestjs/common';
import { Request } from 'express';
import { ThrottlerGuard, ThrottlerLimitDetail } from '@nestjs/throttler';
import { AuthUser } from '../../modules/auth/decorators/current-user.decorator';

@Injectable()
export class AdaptiveThrottlerGuard extends ThrottlerGuard {
  protected async getTracker(request: Record<string, any>): Promise<string> {
    const req = request as Request & { user?: AuthUser };
    return req.user?.id ?? req.ip ?? 'unknown-client';
  }

  protected generateKey(context: ExecutionContext, tracker: string, throttlerName: string): string {
    const request = context.switchToHttp().getRequest<Request>();
    const controllerName = context.getClass().name;
    let bucket = 'general';
    if (controllerName === 'AiGatewayController' && request.method === 'POST') bucket = 'ai';
    if (controllerName === 'AuthController') bucket = `auth:${request.route?.path ?? request.path}`;
    return `${throttlerName}:${bucket}:${tracker}`;
  }

  protected async throwThrottlingException(_context: ExecutionContext, detail: ThrottlerLimitDetail): Promise<void> {
    throw new HttpException({
      error_code: 'RATE_LIMIT_EXCEEDED',
      message: 'Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.',
      details: { limit: detail.limit, retry_after_seconds: detail.timeToBlockExpire || detail.timeToExpire },
    }, HttpStatus.TOO_MANY_REQUESTS);
  }
}
