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
  @ApiOperation({ summary: 'Lấy phiên bản mới nhất của Desktop Client (Auto-Update)' })
  version() {
    return {
      message: 'Lấy thông tin phiên bản thành công',
      data: this.system.getVersionManifest(),
    };
  }
}
