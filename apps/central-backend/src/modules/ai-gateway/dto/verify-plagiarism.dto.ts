import { ApiProperty } from '@nestjs/swagger';
import { IsIn, IsNumber, IsString, Max, MaxLength, Min, MinLength } from 'class-validator';

export class VerifyPlagiarismDto {
  @ApiProperty({ minLength: 10, maxLength: 10000 })
  @IsString() @MinLength(10) @MaxLength(10000)
  student_a_code!: string;

  @ApiProperty({ minLength: 10, maxLength: 10000 })
  @IsString() @MinLength(10) @MaxLength(10000)
  student_b_code!: string;

  @ApiProperty({ minimum: 80, maximum: 100 })
  @IsNumber() @Min(80) @Max(100)
  ast_similarity_percentage!: number;

  @ApiProperty({ enum: ['C', 'JAVA', 'PYTHON', 'PHP'] })
  @IsIn(['C', 'JAVA', 'PYTHON', 'PHP'])
  language!: 'C' | 'JAVA' | 'PYTHON' | 'PHP';
}
