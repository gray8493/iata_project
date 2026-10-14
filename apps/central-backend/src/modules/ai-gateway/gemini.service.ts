import { BadGatewayException, HttpException, Injectable, ServiceUnavailableException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { GoogleGenAI, Schema } from '@google/genai';
import { AiFeature, AiQuotaService, QuotaReservation } from './ai-quota.service';

export interface GeminiResult<T> { data: T; tokensConsumed: number; }

@Injectable()
export class GeminiService {
  private client?: GoogleGenAI;
  private readonly model: string;

  constructor(private readonly config: ConfigService, private readonly quota: AiQuotaService) {
    this.model = config.get<string>('GEMINI_MODEL', 'gemini-3.8-flash');
  }

  async generateJson<T>(args: {
    userId: string;
    feature: AiFeature;
    prompt: string;
    schema: Schema;
    maxOutputTokens: number;
    image?: { mimeType: string; base64: string };
  }): Promise<GeminiResult<T>> {
    const client = this.getClient();
    const estimatedInput = Math.ceil(args.prompt.length / 4) + (args.image ? 1000 : 0);
    const reservation = await this.quota.reserve(args.userId, estimatedInput + args.maxOutputTokens);
    let response;
    try {
      const contents = args.image
        ? [{ text: args.prompt }, { inlineData: { mimeType: args.image.mimeType, data: args.image.base64 } }]
        : args.prompt;
      response = await client.models.generateContent({
        model: this.model,
        contents,
        config: {
          responseMimeType: 'application/json',
          responseSchema: args.schema,
          temperature: 0.2,
          maxOutputTokens: args.maxOutputTokens,
        },
      });
    } catch (error) {
      await this.releaseQuietly(reservation);
      const status = this.providerStatus(error);
      if (status === 429) {
        throw new HttpException({ error_code: 'AI_PROVIDER_RATE_LIMITED', message: 'Dịch vụ AI đang giới hạn số yêu cầu. Vui lòng thử lại sau.', details: null }, 429);
      }
      throw new BadGatewayException({ error_code: 'AI_PROVIDER_ERROR', message: 'Không thể nhận phản hồi từ dịch vụ AI.', details: null });
    }

    const promptTokens = response.usageMetadata?.promptTokenCount ?? estimatedInput;
    const completionTokens = response.usageMetadata?.candidatesTokenCount ?? Math.ceil((response.text ?? '').length / 4);
    const totalTokens = response.usageMetadata?.totalTokenCount ?? promptTokens + completionTokens;
    await this.quota.settle(args.userId, reservation, { promptTokens, completionTokens, totalTokens }, args.feature, this.model);

    if (!response.text) throw new BadGatewayException({ error_code: 'AI_INVALID_RESPONSE', message: 'Dịch vụ AI trả về nội dung rỗng.', details: null });
    try {
      return { data: JSON.parse(response.text) as T, tokensConsumed: totalTokens };
    } catch {
      throw new BadGatewayException({ error_code: 'AI_INVALID_RESPONSE', message: 'Dịch vụ AI trả về dữ liệu không đúng định dạng.', details: null });
    }
  }

  private getClient(): GoogleGenAI {
    const apiKey = this.config.get<string>('GEMINI_API_KEY');
    if (!apiKey) throw new ServiceUnavailableException({ error_code: 'AI_NOT_CONFIGURED', message: 'Dịch vụ AI chưa được cấu hình trên máy chủ.', details: null });
    this.client ??= new GoogleGenAI({ apiKey, httpOptions: { timeout: 30000 } });
    return this.client;
  }

  private providerStatus(error: unknown): number | undefined {
    if (typeof error !== 'object' || error === null) return undefined;
    const status = (error as { status?: unknown; statusCode?: unknown }).status ?? (error as { statusCode?: unknown }).statusCode;
    return typeof status === 'number' ? status : undefined;
  }

  private async releaseQuietly(reservation: QuotaReservation): Promise<void> {
    try { await this.quota.release(reservation); } catch { /* Keep provider errors sanitized; quota reconciliation can be retried operationally. */ }
  }
}
