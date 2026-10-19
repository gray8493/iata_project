import { Body, Controller, Get, Post, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { Throttle } from '@nestjs/throttler';
import { Roles } from '../../common/decorators/roles.decorator';
import { AdaptiveThrottlerGuard } from '../../common/guards/adaptive-throttler.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { AuthUser, CurrentUser } from '../auth/decorators/current-user.decorator';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { AiGatewayService } from './ai-gateway.service';
import { AiQuotaService } from './ai-quota.service';
import { OpenRouterService } from './openrouter.service';
import { EvaluateWebUiDto } from './dto/evaluate-web-ui.dto';
import { GenerateTestcasesDto } from './dto/generate-testcases.dto';
import { ReviewCodeDto } from './dto/review-code.dto';
import { VerifyPlagiarismDto } from './dto/verify-plagiarism.dto';
import { EvaluatePeCodeDto } from './dto/evaluate-pe-code.dto';

@ApiTags('AI Hub')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard, AdaptiveThrottlerGuard)
@Roles('INSTRUCTOR')
@Controller('ai')
export class AiGatewayController {
  constructor(private readonly ai: AiGatewayService, private readonly quota: AiQuotaService, private readonly openrouter: OpenRouterService) {}

  @Get('quota')
  @ApiOperation({ summary: 'Lấy hạn ngạch AI trong ngày' })
  async getQuota(@CurrentUser() user: AuthUser) {
    return { message: 'Lấy thông tin hạn ngạch AI thành công', data: await this.quota.snapshot(user.id) };
  }

  @Get('provider-status')
  @Roles('ADMIN')
  @ApiOperation({ summary: 'Lấy trạng thái AI Hub (OpenRouter) — chỉ ADMIN' })
  getProviderStatus() {
    return { message: 'Lấy trạng thái AI Hub thành công', data: this.openrouter.providerStatus() };
  }

  @Post('generate-testcases')
  @Throttle({ default: { limit: 15, ttl: 60_000 } })
  generateTestcases(@CurrentUser() user: AuthUser, @Body() dto: GenerateTestcasesDto) { return this.ai.generateTestcases(user.id, dto); }

  @Post('review-code')
  @Throttle({ default: { limit: 15, ttl: 60_000 } })
  reviewCode(@CurrentUser() user: AuthUser, @Body() dto: ReviewCodeDto) { return this.ai.reviewCode(user.id, dto); }

  @Post('verify-plagiarism')
  @Throttle({ default: { limit: 15, ttl: 60_000 } })
  verifyPlagiarism(@CurrentUser() user: AuthUser, @Body() dto: VerifyPlagiarismDto) { return this.ai.verifyPlagiarism(user.id, dto); }

  @Post('evaluate-web-ui')
  @Throttle({ default: { limit: 15, ttl: 60_000 } })
  evaluateWebUi(@CurrentUser() user: AuthUser, @Body() dto: EvaluateWebUiDto) { return this.ai.evaluateWebUi(user.id, dto); }

  @Post('evaluate-pe-code')
  @Throttle({ default: { limit: 15, ttl: 60_000 } })
  evaluatePeCode(@CurrentUser() user: AuthUser, @Body() dto: EvaluatePeCodeDto) { return this.ai.evaluatePeCode(user.id, dto); }
}
