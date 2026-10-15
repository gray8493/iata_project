import { ApiProperty } from '@nestjs/swagger';
import { ArrayMaxSize, ArrayMinSize, IsArray, IsString, MaxLength } from 'class-validator';

export class EvaluateWebUiDto {
  @ApiProperty({ description: 'PNG or JPEG base64, with or without a data URL prefix.' })
  @IsString() @MaxLength(7000000)
  screenshot_base64!: string;

  @ApiProperty({ type: [String], minItems: 1, maxItems: 20 })
  @IsArray() @ArrayMinSize(1) @ArrayMaxSize(20)
  @IsString({ each: true }) @MaxLength(500, { each: true })
  rubric_requirements!: string[];
}
