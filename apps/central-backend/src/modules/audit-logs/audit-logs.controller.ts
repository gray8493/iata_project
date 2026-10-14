import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiQuery, ApiTags } from '@nestjs/swagger';
import { Roles } from '../../common/decorators/roles.decorator';
import { RolesGuard } from '../../common/guards/roles.guard';
import { AdaptiveThrottlerGuard } from '../../common/guards/adaptive-throttler.guard';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { ListAiUsageDto } from './dto/list-ai-usage.dto';
import { AuditLogsService } from './audit-logs.service';

@ApiTags('Admin Reports')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard, AdaptiveThrottlerGuard)
@Roles('ADMIN')
@Controller('admin/reports')
export class AuditLogsController {
  constructor(private readonly reports: AuditLogsService) {}

  @Get('ai-usage')
  @ApiOperation({ summary: 'Tra cứu nhật ký sử dụng AI có phân trang và bộ lọc' })
  @ApiQuery({ name: 'page', required: false, type: Number, description: 'Trang hiện tại, mặc định 1' })
  @ApiQuery({ name: 'page_size', required: false, type: Number, description: 'Số bản ghi mỗi trang, mặc định 20, tối đa 100' })
  @ApiQuery({ name: 'user_id', required: false, type: String, description: 'UUID của giảng viên cần lọc' })
  @ApiQuery({ name: 'from', required: false, type: String, description: 'Thời điểm bắt đầu ISO-8601, bao gồm mốc này' })
  @ApiQuery({ name: 'to', required: false, type: String, description: 'Thời điểm kết thúc ISO-8601, bao gồm mốc này' })
  listAiUsage(@Query() query: ListAiUsageDto) { return this.reports.listAiUsage(query); }

  @Get('overview')
  @ApiOperation({ summary: 'Lấy báo cáo tổng quan và sử dụng AI trong tháng' })
  overview() { return this.reports.overview(); }
}
