import { ApiPropertyOptional } from '@nestjs/swagger';
import { IsBoolean, IsEmail, IsIn, IsInt, IsOptional, IsString, Matches, Max, MaxLength, Min, MinLength } from 'class-validator';

export class UpdateUserDto {
  @ApiPropertyOptional({ minLength: 3, maxLength: 30 })
  @IsOptional() @IsString() @MinLength(3) @MaxLength(30) @Matches(/^[a-z0-9_]+$/)
  username?: string;

  @ApiPropertyOptional({ minLength: 8, maxLength: 100, writeOnly: true })
  @IsOptional() @IsString() @MinLength(8) @MaxLength(100) @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/)
  password?: string;

  @ApiPropertyOptional({ minLength: 2, maxLength: 100 })
  @IsOptional() @IsString() @MinLength(2) @MaxLength(100)
  full_name?: string;

  @ApiPropertyOptional({ maxLength: 120 })
  @IsOptional() @IsEmail() @MaxLength(120)
  email?: string;

  @ApiPropertyOptional({ enum: ['ADMIN', 'INSTRUCTOR'] })
  @IsOptional() @IsIn(['ADMIN', 'INSTRUCTOR'])
  role?: 'ADMIN' | 'INSTRUCTOR';

  @ApiPropertyOptional()
  @IsOptional() @IsBoolean()
  is_active?: boolean;

  @ApiPropertyOptional({ minimum: 1000, maximum: 1000000 })
  @IsOptional() @IsInt() @Min(1000) @Max(1000000)
  daily_token_quota?: number;
}
