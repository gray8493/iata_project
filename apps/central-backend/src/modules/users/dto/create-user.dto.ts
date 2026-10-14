import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsIn, IsInt, IsOptional, IsString, Matches, Max, MaxLength, Min, MinLength } from 'class-validator';

export class CreateUserDto {
  @ApiProperty({ minLength: 3, maxLength: 30, example: 'teacher_lan' })
  @IsString() @MinLength(3) @MaxLength(30) @Matches(/^[a-z0-9_]+$/)
  username!: string;

  @ApiProperty({ minLength: 8, maxLength: 100, writeOnly: true })
  @IsString() @MinLength(8) @MaxLength(100) @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/)
  password!: string;

  @ApiProperty({ minLength: 2, maxLength: 100 })
  @IsString() @MinLength(2) @MaxLength(100)
  full_name!: string;

  @ApiProperty({ maxLength: 120 })
  @IsEmail() @MaxLength(120)
  email!: string;

  @ApiProperty({ enum: ['ADMIN', 'INSTRUCTOR'] })
  @IsIn(['ADMIN', 'INSTRUCTOR'])
  role!: 'ADMIN' | 'INSTRUCTOR';

  @ApiProperty({ required: false, minimum: 1000, maximum: 1000000, default: 50000 })
  @IsOptional() @IsInt() @Min(1000) @Max(1000000)
  daily_token_quota?: number;
}
