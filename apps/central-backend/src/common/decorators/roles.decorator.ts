import { SetMetadata } from '@nestjs/common';

export const ROLES_KEY = 'aita:roles';
export type AppRole = 'ADMIN' | 'INSTRUCTOR';
export const Roles = (...roles: AppRole[]) => SetMetadata(ROLES_KEY, roles);

export function toAppRole(role: string): AppRole {
  if (role === 'ADMIN' || role === 'INSTRUCTOR') return role;
  throw new Error('Database contains an unsupported user role.');
}
