import { ApiProperty } from '@nestjs/swagger';
import { IsBoolean, IsIn, IsInt, IsOptional, IsString, Max, MaxLength, Min, MinLength } from 'class-validator';

export class GenerateTestcasesDto {
  @ApiProperty({ minLength: 20, maxLength: 5000 })
  @IsString() @MinLength(20) @MaxLength(5000)
  problem_description!: string;

  @ApiProperty({ enum: ['C', 'JAVA', 'PYTHON', 'WEB'] })
  @IsIn(['C', 'JAVA', 'PYTHON', 'WEB'])
  language!: 'C' | 'JAVA' | 'PYTHON' | 'WEB';

  @ApiProperty({ required: false, minimum: 1, maximum: 10, default: 3 })
  @IsOptional() @IsInt() @Min(1) @Max(10)
  count = 3;

  @ApiProperty({ required: false, default: true })
  @IsOptional() @IsBoolean()
  include_boundary = true;
}
