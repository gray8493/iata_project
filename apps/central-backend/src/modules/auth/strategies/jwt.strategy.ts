import { Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { PrismaService } from '../../../prisma/prisma.service';
import { toAppRole } from '../../../common/decorators/roles.decorator';
import { AuthUser } from '../decorators/current-user.decorator';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(config: ConfigService, private readonly prisma: PrismaService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.getOrThrow<string>('JWT_ACCESS_SECRET'),
    });
  }

  async validate(payload: AuthUser & { token_type?: string }): Promise<AuthUser> {
    if (payload.token_type !== 'access' || !payload.id) {
      throw new UnauthorizedException({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.' });
    }
    const user = await this.prisma.user.findFirst({
      where: { id: payload.id, isActive: true, isDeleted: false },
      select: { id: true, username: true, role: true },
    });
    if (!user) throw new UnauthorizedException({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản không còn hoạt động.' });
    return { ...user, role: toAppRole(user.role) };
  }
}
