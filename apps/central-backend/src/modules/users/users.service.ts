import { ConflictException, ForbiddenException, Injectable, NotFoundException } from '@nestjs/common';
import { Prisma } from '@prisma/client';
import * as bcrypt from 'bcrypt';
import { PrismaService } from '../../prisma/prisma.service';
import { toAppRole } from '../../common/decorators/roles.decorator';
import { CreateUserDto } from './dto/create-user.dto';
import { ListUsersDto } from './dto/list-users.dto';
import { UpdateUserDto } from './dto/update-user.dto';

const publicUserSelect = {
  id: true, username: true, fullName: true, email: true, role: true,
  isActive: true, createdAt: true,
  quotaConfig: { select: { dailyTokenLimit: true, usedTokensToday: true } },
} satisfies Prisma.UserSelect;

@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

  async list(query: ListUsersDto) {
    const where: Prisma.UserWhereInput = {
      isDeleted: false,
      ...(query.role ? { role: query.role } : {}),
      ...(query.search ? { OR: [
        { username: { contains: query.search, mode: 'insensitive' } },
        { fullName: { contains: query.search, mode: 'insensitive' } },
        { email: { contains: query.search, mode: 'insensitive' } },
      ] } : {}),
    };
    const skip = (query.page - 1) * query.page_size;
    const [items, totalItems] = await this.prisma.$transaction([
      this.prisma.user.findMany({ where, select: publicUserSelect, skip, take: query.page_size, orderBy: [{ createdAt: 'desc' }, { id: 'asc' }] }),
      this.prisma.user.count({ where }),
    ]);
    return { message: 'Lấy danh sách người dùng thành công', data: {
      items: items.map((user) => this.toPublicUser(user)),
      pagination: { page: query.page, page_size: query.page_size, total_items: totalItems, total_pages: Math.ceil(totalItems / query.page_size) },
    } };
  }

  async create(input: CreateUserDto) {
    try {
      const passwordHash = await bcrypt.hash(input.password, 12);
      const user = await this.prisma.$transaction(async (tx) => {
        const created = await tx.user.create({ data: {
          username: input.username,
          passwordHash,
          fullName: input.full_name,
          email: input.email.toLowerCase(),
          role: input.role,
        } });
        await tx.aiQuotaConfig.create({ data: {
          userId: created.id,
          dailyTokenLimit: input.daily_token_quota ?? 50000,
          lastResetDate: this.todayUtc(),
        } });
        return created;
      });
      return { message: 'Tạo tài khoản người dùng mới thành công', data: this.toPublicUser(user) };
    } catch (error) {
      this.rethrowUniqueConflict(error);
    }
  }

  async get(id: string) {
    const user = await this.prisma.user.findFirst({
      where: { id, isDeleted: false },
      select: publicUserSelect,
    });
    if (!user) throw this.notFound();
    return { message: 'Lấy thông tin tài khoản thành công', data: this.toPublicUser(user) };
  }

  async update(id: string, input: UpdateUserDto, actorId: string) {
    const current = await this.prisma.user.findFirst({ where: { id, isDeleted: false } });
    if (!current) throw this.notFound();
    if (id === actorId && input.is_active === false) {
      throw new ForbiddenException({ error_code: 'USER_CANNOT_DISABLE_SELF', message: 'Bạn không thể tự vô hiệu hóa tài khoản đang sử dụng.', details: null });
    }
    if (current.role === 'ADMIN' && current.isActive && (input.is_active === false || input.role === 'INSTRUCTOR')) {
      const activeAdmins = await this.prisma.user.count({ where: { role: 'ADMIN', isActive: true, isDeleted: false } });
      if (activeAdmins <= 1) throw new ConflictException({ error_code: 'LAST_ACTIVE_ADMIN', message: 'Không thể vô hiệu hóa hoặc hạ quyền Admin hoạt động cuối cùng.', details: null });
    }

    try {
      const data: Prisma.UserUpdateInput = {
        ...(input.username !== undefined ? { username: input.username } : {}),
        ...(input.full_name !== undefined ? { fullName: input.full_name } : {}),
        ...(input.email !== undefined ? { email: input.email.toLowerCase() } : {}),
        ...(input.role !== undefined ? { role: input.role } : {}),
        ...(input.is_active !== undefined ? { isActive: input.is_active } : {}),
        ...(input.password !== undefined ? { passwordHash: await bcrypt.hash(input.password, 12) } : {}),
      };
      const user = await this.prisma.$transaction(async (tx) => {
        const updated = await tx.user.update({ where: { id }, data, select: { ...publicUserSelect, updatedAt: true } });
        if (input.daily_token_quota !== undefined) {
          await tx.aiQuotaConfig.upsert({
            where: { userId: id },
            create: { userId: id, dailyTokenLimit: input.daily_token_quota },
            update: { dailyTokenLimit: input.daily_token_quota, isDeleted: false, deletedAt: null },
          });
        }
        if (input.is_active === false || input.role !== undefined || input.password !== undefined) {
          await tx.refreshToken.updateMany({ where: { userId: id, revokedAt: null }, data: { revokedAt: new Date() } });
        }
        return updated;
      });
      return { message: 'Cập nhật tài khoản thành công', data: { ...this.toPublicUser(user), updated_at: user.updatedAt.toISOString() } };
    } catch (error) {
      this.rethrowUniqueConflict(error);
    }
  }

  async delete(id: string, actorId: string) {
    const current = await this.prisma.user.findFirst({ where: { id, isDeleted: false } });
    if (!current) throw this.notFound();
    if (id === actorId) {
      throw new ForbiddenException({ error_code: 'USER_CANNOT_DELETE_SELF', message: 'Bạn không thể xóa tài khoản đang sử dụng.', details: null });
    }
    if (current.role === 'ADMIN' && current.isActive) {
      const activeAdmins = await this.prisma.user.count({ where: { role: 'ADMIN', isActive: true, isDeleted: false } });
      if (activeAdmins <= 1) throw new ConflictException({ error_code: 'LAST_ACTIVE_ADMIN', message: 'Không thể xóa Admin hoạt động cuối cùng.', details: null });
    }
    const now = new Date();
    await this.prisma.$transaction([
      this.prisma.user.update({ where: { id }, data: { isDeleted: true, isActive: false, deletedAt: now } }),
      this.prisma.aiQuotaConfig.updateMany({ where: { userId: id, isDeleted: false }, data: { isDeleted: true, deletedAt: now } }),
      this.prisma.refreshToken.updateMany({ where: { userId: id, revokedAt: null }, data: { revokedAt: now } }),
    ]);
    return { message: 'Xóa người dùng thành công', data: null };
  }

  private toPublicUser(user: {
    id: string; username: string; fullName: string; email: string; role: string; isActive: boolean; createdAt: Date;
    quotaConfig?: { dailyTokenLimit: number; usedTokensToday: number } | null;
  }) {
    return {
      id: user.id, username: user.username, full_name: user.fullName, email: user.email,
      role: toAppRole(user.role), is_active: user.isActive, created_at: user.createdAt.toISOString(),
      daily_token_quota: user.quotaConfig?.dailyTokenLimit ?? 50000,
      used_tokens_today: user.quotaConfig?.usedTokensToday ?? 0,
    };
  }

  private notFound(): NotFoundException {
    return new NotFoundException({ error_code: 'USER_NOT_FOUND', message: 'Không tìm thấy người dùng với ID đã chỉ định.', details: null });
  }

  private todayUtc(): Date {
    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  }

  private rethrowUniqueConflict(error: unknown): never {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2002') {
      throw new ConflictException({ error_code: 'USER_ALREADY_EXISTS', message: 'Tên đăng nhập hoặc email đã tồn tại.', details: null });
    }
    throw error;
  }
}
