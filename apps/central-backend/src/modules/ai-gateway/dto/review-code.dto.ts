import { Type } from 'class-transformer';
import { ApiProperty } from '@nestjs/swagger';
import { IsIn, IsObject, IsString, MaxLength, MinLength, ValidateNested } from 'class-validator';

class FailedTestcaseDto {
  @IsString() @MaxLength(10000) input!: string;
  @IsString() @MaxLength(10000) expected_output!: string;
  @IsString() @MaxLength(10000) actual_output!: string;
}

export class ReviewCodeDto {
  @ApiProperty({ minLength: 10, maxLength: 10000 })
  @IsString() @MinLength(10) @MaxLength(10000)
  source_code!: string;

  @ApiProperty({ enum: ['C', 'JAVA', 'PYTHON', 'PHP'] })
  @IsIn(['C', 'JAVA', 'PYTHON', 'PHP'])
  language!: 'C' | 'JAVA' | 'PYTHON' | 'PHP';

  @ApiProperty({ maxLength: 3000 })
  @IsString() @MinLength(1) @MaxLength(3000)
  problem_statement!: string;

  @ApiProperty({ type: FailedTestcaseDto })
  @IsObject() @ValidateNested() @Type(() => FailedTestcaseDto)
  failed_testcase!: FailedTestcaseDto;
}
