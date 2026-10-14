import { Module } from '@nestjs/common';
import { AiGatewayController } from './ai-gateway.controller';
import { AiGatewayService } from './ai-gateway.service';
import { AiQuotaService } from './ai-quota.service';
import { GeminiService } from './gemini.service';

@Module({ controllers: [AiGatewayController], providers: [AiGatewayService, AiQuotaService, GeminiService] })
export class AiGatewayModule {}
