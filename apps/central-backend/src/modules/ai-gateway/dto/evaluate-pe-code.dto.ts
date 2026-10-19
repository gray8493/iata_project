import { ApiProperty } from '@nestjs/swagger';
import { IsIn, IsString, MaxLength, MinLength } from 'class-validator';

export class EvaluatePeCodeDto {
  @ApiProperty({ minLength: 10, maxLength: 20000 })
  @IsString() @MinLength(10) @MaxLength(20000)
  source_code!: string;

  @ApiProperty({ enum: ['C', 'JAVA', 'PYTHON', 'PHP'] })
  @IsIn(['C', 'JAVA', 'PYTHON', 'PHP'])
  language!: 'C' | 'JAVA' | 'PYTHON' | 'PHP';

  @ApiProperty({ required: false, maxLength: 5000 })
  @IsString() @MaxLength(5000)
  problem_statement?: string;
}
