import { Controller, Get, UseGuards } from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';
import { AdaptiveThrottlerGuard } from '../../common/guards/adaptive-throttler.guard';
import { SystemService } from './system.service';

@ApiTags('System')
@Controller('system')
@UseGuards(AdaptiveThrottlerGuard)
export class SystemController {
  constructor(private readonly system: SystemService) {}

  @Get('version')
  @ApiOperation({
    summary: 'Lấy phiên bản mới nhất của Desktop Client (Auto-Update)',
    description:
      'Manifest tự lấy từ release mới nhất trên GitHub (APP_UPDATE_SOURCE=github); ' +
      'fallback về các biến APP_UPDATE_* khi GitHub lỗi hoặc chưa cấu hình.',
  })
  async version() {
    return {
      message: 'Lấy thông tin phiên bản thành công',
      data: await this.system.getVersionManifest(),
    };
  }
}
