import { ExecutionContext, Injectable, UnauthorizedException } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  handleRequest<TUser = unknown>(error: unknown, user: TUser, info: { name?: string } | undefined): TUser {
    if (info?.name === 'TokenExpiredError') {
      throw new UnauthorizedException({ error_code: 'AUTH_TOKEN_EXPIRED', message: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.', details: null });
    }
    if (error || !user) {
      throw new UnauthorizedException({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
    }
    return user;
  }
}
