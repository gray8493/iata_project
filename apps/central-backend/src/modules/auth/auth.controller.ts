import { Body, Controller, Get, Post, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { Throttle } from '@nestjs/throttler';
import { AdaptiveThrottlerGuard } from '../../common/guards/adaptive-throttler.guard';
import { AuthService } from './auth.service';
import { CurrentUser, AuthUser } from './decorators/current-user.decorator';
import { LoginDto } from './dto/login.dto';
import { RefreshTokenDto } from './dto/refresh-token.dto';
import { JwtAuthGuard } from './guards/jwt-auth.guard';

@ApiTags('Auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly auth: AuthService) {}

  @Post('login')
  @UseGuards(AdaptiveThrottlerGuard)
  @Throttle({ default: { limit: 10, ttl: 60_000 } })
  @ApiOperation({ summary: 'Đăng nhập hệ thống' })
  login(@Body() dto: LoginDto) { return this.auth.login(dto); }

  @Get('me')
  @UseGuards(JwtAuthGuard, AdaptiveThrottlerGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Lấy hồ sơ tài khoản hiện tại' })
  me(@CurrentUser() user: AuthUser) { return this.auth.me(user.id); }

  @Post('refresh')
  @UseGuards(AdaptiveThrottlerGuard)
  @Throttle({ default: { limit: 30, ttl: 60_000 } })
  @ApiOperation({ summary: 'Gia hạn access token và xoay refresh token' })
  refresh(@Body() dto: RefreshTokenDto) { return this.auth.refresh(dto.refresh_token); }
}
