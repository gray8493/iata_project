import { ApiProperty } from '@nestjs/swagger';
import { IsString, MaxLength, MinLength } from 'class-validator';

export class LoginDto {
  @ApiProperty({ minLength: 3, maxLength: 50, example: 'teacher_hung' })
  @IsString()
  @MinLength(3)
  @MaxLength(50)
  username!: string;

  @ApiProperty({ minLength: 6, maxLength: 100, writeOnly: true })
  @IsString()
  @MinLength(6)
  @MaxLength(100)
  password!: string;
}
