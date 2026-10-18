import { Module } from '@nestjs/common';
import { AiGatewayController } from './ai-gateway.controller';
import { AiGatewayService } from './ai-gateway.service';
import { AiQuotaService } from './ai-quota.service';
import { OpenRouterService } from './openrouter.service';

@Module({ controllers: [AiGatewayController], providers: [AiGatewayService, AiQuotaService, OpenRouterService] })
export class AiGatewayModule {}
