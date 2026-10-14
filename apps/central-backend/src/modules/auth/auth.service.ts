import { createHash, randomUUID } from 'node:crypto';
import { ForbiddenException, Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { User } from '@prisma/client';
import * as bcrypt from 'bcrypt';
import { PrismaService } from '../../prisma/prisma.service';
import { AuthUser } from './decorators/current-user.decorator';
import { LoginDto } from './dto/login.dto';
import { toAppRole } from '../../common/decorators/roles.decorator';

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
  ) {}

  async login(input: LoginDto) {
    const user = await this.prisma.user.findFirst({
      where: { username: input.username, isDeleted: false },
    });
    if (!user || !(await bcrypt.compare(input.password, user.passwordHash))) {
      throw new UnauthorizedException({ error_code: 'AUTH_INVALID_CREDENTIALS', message: 'Tên đăng nhập hoặc mật khẩu không chính xác.', details: null });
    }
    if (!user.isActive) {
      throw new ForbiddenException({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản của bạn đã bị vô hiệu hóa.', details: null });
    }
    return { message: 'Đăng nhập thành công', data: await this.issueTokens(user) };
  }

  async refresh(rawToken: string) {
    let payload: AuthUser & { token_type?: string; jti?: string };
    try {
      payload = await this.jwt.verifyAsync(rawToken, { secret: this.config.getOrThrow('JWT_REFRESH_SECRET') });
    } catch {
      throw this.invalidRefreshToken();
    }
    if (payload.token_type !== 'refresh' || !payload.jti || !payload.id) throw this.invalidRefreshToken();

    const tokenHash = this.hashToken(rawToken);
    const user = await this.prisma.$transaction(async (tx) => {
      const stored = await tx.refreshToken.findFirst({
        where: { id: payload.jti, tokenHash, userId: payload.id, revokedAt: null, expiresAt: { gt: new Date() } },
        include: { user: true },
      });
      if (!stored || !stored.user.isActive || stored.user.isDeleted) return null;
      const revoked = await tx.refreshToken.updateMany({
        where: { id: stored.id, revokedAt: null, expiresAt: { gt: new Date() } },
        data: { revokedAt: new Date() },
      });
      if (revoked.count !== 1) return null;
      return stored.user;
    });
    if (!user) throw this.invalidRefreshToken();
    return { message: 'Gia hạn mã truy cập thành công', data: await this.issueTokens(user) };
  }

  async me(userId: string) {
    const user = await this.prisma.user.findFirst({
      where: { id: userId, isActive: true, isDeleted: false },
      select: { id: true, username: true, fullName: true, email: true, role: true, isActive: true, createdAt: true },
    });
    if (!user) throw new UnauthorizedException({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản không còn hoạt động.', details: null });
    return { message: 'Lấy thông tin tài khoản thành công', data: {
      id: user.id, username: user.username, full_name: user.fullName, email: user.email,
      role: toAppRole(user.role), is_active: user.isActive, created_at: user.createdAt.toISOString(),
    } };
  }

  private async issueTokens(user: User) {
    const accessExpiresIn = this.config.get<string>('JWT_ACCESS_EXPIRES_IN', '15m');
    const refreshExpiresIn = this.config.get<string>('JWT_REFRESH_EXPIRES_IN', '7d');
    const refreshId = randomUUID();
    const identity = { id: user.id, username: user.username, role: toAppRole(user.role) };
    const [accessToken, refreshToken] = await Promise.all([
      this.jwt.signAsync({ ...identity, token_type: 'access' }, {
        secret: this.config.getOrThrow('JWT_ACCESS_SECRET'), expiresIn: accessExpiresIn,
      }),
      this.jwt.signAsync({ ...identity, token_type: 'refresh', jti: refreshId }, {
        secret: this.config.getOrThrow('JWT_REFRESH_SECRET'), expiresIn: refreshExpiresIn, jwtid: refreshId,
      }),
    ]);
    const decoded = this.jwt.decode(refreshToken) as { exp?: number } | null;
    if (!decoded?.exp) throw new Error('Refresh token missing expiry');
    await this.prisma.refreshToken.create({ data: {
      id: refreshId, tokenHash: this.hashToken(refreshToken), userId: user.id,
      expiresAt: new Date(decoded.exp * 1000),
    } });
    return {
      access_token: accessToken, refresh_token: refreshToken, token_type: 'Bearer',
      expires_in: this.durationSeconds(accessExpiresIn),
      user: { id: user.id, username: user.username, full_name: user.fullName, email: user.email, role: toAppRole(user.role), is_active: user.isActive },
    };
  }

  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  private durationSeconds(value: string): number {
    const match = /^([1-9]\d*)(s|m|h|d)$/.exec(value);
    if (!match) throw new Error('JWT expiration must use a duration such as 15m or 7d');
    const factors: Record<string, number> = { s: 1, m: 60, h: 3600, d: 86400 };
    return Number(match[1]) * factors[match[2]];
  }

  private invalidRefreshToken(): UnauthorizedException {
    return new UnauthorizedException({ error_code: 'AUTH_INVALID_REFRESH_TOKEN', message: 'Mã refresh token không hợp lệ hoặc đã hết hạn.', details: null });
  }
}
