import { Body, Controller, Delete, Get, HttpCode, Param, ParseUUIDPipe, Post, Put, Query, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { Roles } from '../../common/decorators/roles.decorator';
import { RolesGuard } from '../../common/guards/roles.guard';
import { AdaptiveThrottlerGuard } from '../../common/guards/adaptive-throttler.guard';
import { AuthUser, CurrentUser } from '../auth/decorators/current-user.decorator';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CreateUserDto } from './dto/create-user.dto';
import { ListUsersDto } from './dto/list-users.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { UsersService } from './users.service';

@ApiTags('Admin Users')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard, AdaptiveThrottlerGuard)
@Roles('ADMIN')
@Controller('admin/users')
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  @ApiOperation({ summary: 'Lấy danh sách tài khoản có phân trang' })
  list(@Query() query: ListUsersDto) { return this.users.list(query); }

  @Post()
  @ApiOperation({ summary: 'Tạo tài khoản' })
  create(@Body() dto: CreateUserDto) { return this.users.create(dto); }

  @Get(':id')
  @ApiOperation({ summary: 'Lấy chi tiết tài khoản' })
  get(@Param('id', new ParseUUIDPipe()) id: string) { return this.users.get(id); }

  @Put(':id')
  @ApiOperation({ summary: 'Cập nhật tài khoản' })
  update(@Param('id', new ParseUUIDPipe()) id: string, @Body() dto: UpdateUserDto, @CurrentUser() actor: AuthUser) {
    return this.users.update(id, dto, actor.id);
  }

  @Delete(':id')
  @HttpCode(200)
  @ApiOperation({ summary: 'Xóa mềm tài khoản' })
  delete(@Param('id', new ParseUUIDPipe()) id: string, @CurrentUser() actor: AuthUser) {
    return this.users.delete(id, actor.id);
  }
}
