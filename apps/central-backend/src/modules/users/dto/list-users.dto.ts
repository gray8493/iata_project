import { Type } from 'class-transformer';
import { IsIn, IsInt, IsOptional, IsString, Max, MaxLength, Min } from 'class-validator';

export class ListUsersDto {
  @IsOptional() @Type(() => Number) @IsInt() @Min(1)
  page = 1;

  @IsOptional() @Type(() => Number) @IsInt() @Min(1) @Max(100)
  page_size = 10;

  @IsOptional() @IsIn(['ADMIN', 'INSTRUCTOR'])
  role?: 'ADMIN' | 'INSTRUCTOR';

  @IsOptional() @IsString() @MaxLength(50)
  search?: string;
}
