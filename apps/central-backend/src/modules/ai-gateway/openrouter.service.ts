import { BadGatewayException, HttpException, Injectable, ServiceUnavailableException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { AiFeature, AiQuotaService, QuotaReservation } from './ai-quota.service';

export type JsonSchemaDefinition = Record<string, unknown>;
export interface OpenRouterResult<T> { data: T; tokensConsumed: number; }
export interface ProviderImage { mimeType: string; base64: string; }

type FailureKind = 'rate' | 'exhausted' | 'transient' | 'fatal';

class ProviderFailure extends Error {
  constructor(
    readonly kind: FailureKind,
    readonly status: number | undefined,
    readonly detail: string,
    readonly retryAfterMs: number | undefined = undefined,
    readonly structuredFormatUnsupported = false,
  ) { super(detail); this.name = 'ProviderFailure'; }
}

export class ProviderHttpError extends Error {
  constructor(readonly status: number | undefined, readonly rawBody: string, readonly detail: string, readonly retryAfterMs?: number) {
    super(detail);
    this.name = 'ProviderHttpError';
  }
}

interface ChatMessagePart { type: 'text' | 'image_url'; text?: string; image_url?: { url: string }; }
interface ChatMessage { role: 'system' | 'user'; content: string | ChatMessagePart[]; }
interface ChatCompletionResponse {
  choices?: Array<{ message?: { content?: string | null } }>;
  usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number };
}

interface GenerateJsonArgs {
  userId: string;
  feature: AiFeature;
  prompt: string;
  schema: JsonSchemaDefinition;
  maxOutputTokens: number;
  image?: ProviderImage;
}

const DEFAULT_BASE_URL = 'https://openrouter.ai/api/v1';
const DEFAULT_MODEL = 'openrouter/free';
const DEFAULT_TIMEOUT_MS = 60_000;
const DEFAULT_KEY_COOLDOWN_MS = 60_000;
const TRANSIENT_COOLDOWN_MS = 5_000;
const EXHAUSTED_KEY_COOLDOWN_MS = 30 * 60_000;

@Injectable()
export class OpenRouterService {
  private readonly apiKeys: string[];
  private readonly baseUrl: string;
  private readonly model: string;
  private readonly timeoutMs: number;
  private readonly keyCooldownMs: number;
  private rotationIndex = 0;
  private readonly cooldownUntil = new Map<string, number>();
  private structuredUnsupported = false;

  constructor(private readonly config: ConfigService, private readonly quota: AiQuotaService) {
    this.apiKeys = String(config.get<string>('OPENROUTER_API_KEYS', '')).split(',').map((key) => key.trim()).filter(Boolean);
    this.baseUrl = (config.get<string>('OPENROUTER_BASE_URL') || DEFAULT_BASE_URL).replace(/\/+$/, '');
    this.model = config.get<string>('OPENROUTER_MODEL') || DEFAULT_MODEL;
    this.timeoutMs = this.readNumber(config.get('OPENROUTER_TIMEOUT_MS'), DEFAULT_TIMEOUT_MS, 1);
    this.keyCooldownMs = this.readNumber(config.get('OPENROUTER_KEY_COOLDOWN_MS'), DEFAULT_KEY_COOLDOWN_MS, 0);
  }

  async generateJson<T>(args: GenerateJsonArgs): Promise<OpenRouterResult<T>> {
    if (this.apiKeys.length === 0) {
      throw new ServiceUnavailableException({ error_code: 'AI_NOT_CONFIGURED', message: 'Dịch vụ AI chưa được cấu hình trên máy chủ.', details: null });
    }
    const estimatedInput = Math.ceil(args.prompt.length / 4) + (args.image ? 1000 : 0);
    const reservation = await this.quota.reserve(args.userId, estimatedInput + args.maxOutputTokens);
    let attempted = 0;
    let capacityOnly = true;
    let lastFailure: ProviderFailure | undefined;

    for (const apiKey of this.rotationOrder()) {
      if (this.isCoolingDown(apiKey)) continue;
      attempted += 1;
      const structured = !this.structuredUnsupported;
      let response: ChatCompletionResponse;
      try {
        response = await this.post(apiKey, this.buildBody(args, structured));
      } catch (error) {
        const failure = this.asProviderFailure(error);
        if (failure.structuredFormatUnsupported) {
          this.structuredUnsupported = true;
          try {
            response = await this.post(apiKey, this.buildBody(args, false));
          } catch (fallback) {
            lastFailure = this.applyFailure(apiKey, this.asProviderFailure(fallback));
            continue;
          }
        } else {
          lastFailure = this.applyFailure(apiKey, failure);
          if (failure.kind === 'transient' || failure.kind === 'fatal') capacityOnly = false;
          if (failure.kind === 'fatal') break;
          continue;
        }
      }

      const content = response.choices?.[0]?.message?.content ?? '';
      const fallbackPrompt = Math.ceil(args.prompt.length / 4) + (args.image ? 1000 : 0);
      const promptTokens = response.usage?.prompt_tokens ?? fallbackPrompt;
      const completionTokens = response.usage?.completion_tokens ?? Math.ceil(content.length / 4);
      const totalTokens = response.usage?.total_tokens ?? promptTokens + completionTokens;
      await this.quota.settle(args.userId, reservation, { promptTokens, completionTokens, totalTokens }, args.feature, this.model);

      if (!content) {
        throw new BadGatewayException({ error_code: 'AI_INVALID_RESPONSE', message: 'Dịch vụ AI trả về nội dung rỗng.', details: null });
      }
      return { data: this.parseJson(content) as T, tokensConsumed: totalTokens };
    }

    await this.releaseQuietly(reservation);
    if (attempted === 0 || capacityOnly) {
      throw new HttpException({ error_code: 'AI_PROVIDER_RATE_LIMITED', message: 'Dịch vụ AI đang giới hạn số yêu cầu. Vui lòng thử lại sau.', details: null }, 429);
    }
    throw new BadGatewayException({ error_code: 'AI_PROVIDER_ERROR', message: 'Không thể nhận phản hồi từ dịch vụ AI.', details: null });
  }

  providerStatus() {
    const now = Date.now();
    const accounts = this.apiKeys.map((key, index) => {
      const until = this.cooldownUntil.get(key) ?? 0;
      const cooling = now < until;
      return {
        account: `ACC-${String(index + 1).padStart(2, '0')}`,
        key_hint: `${key.slice(0, 9)}…${key.slice(-4)}`,
        state: cooling ? 'COOLDOWN' : 'READY',
        cooldown_remaining_seconds: cooling ? Math.ceil((until - now) / 1000) : 0,
      };
    });
    return {
      provider: 'openrouter',
      model: this.model,
      accounts_configured: this.apiKeys.length,
      structured_outputs_supported: !this.structuredUnsupported,
      accounts,
    };
  }

  private async post(apiKey: string, body: unknown): Promise<ChatCompletionResponse> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      let response: Response;
      let rawBody: string;
      try {
        response = await fetch(`${this.baseUrl}/chat/completions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}`, 'X-Title': 'AITA' },
          body: JSON.stringify(body),
          signal: controller.signal,
        });
        rawBody = await response.text();
      } catch (error) {
        return this.rethrowAsHttpError(error, undefined, 'Không thể kết nối tới nhà cung cấp AI.');
      }
      if (!response.ok) {
        throw new ProviderHttpError(response.status, rawBody, this.providerMessage(rawBody, rawBody || `HTTP ${response.status}`), this.retryAfterMs(response.headers));
      }
      try {
        return JSON.parse(rawBody) as ChatCompletionResponse;
      } catch {
        throw new ProviderHttpError(response.status, rawBody, 'Dịch vụ AI trả về dữ liệu không đúng định dạng.');
      }
    } finally {
      clearTimeout(timer);
    }
  }

  private buildBody(args: GenerateJsonArgs, structured: boolean) {
    const requirement = structured
      ? 'Respond with a single JSON object only, without markdown fences or commentary.'
      : `Respond with a single JSON object only, without markdown fences or commentary. Your response must conform to this JSON Schema:\n${JSON.stringify(args.schema)}`;
    const messages: ChatMessage[] = [
      { role: 'system', content: requirement },
      {
        role: 'user', content: args.image
          ? [
            { type: 'text', text: args.prompt },
            { type: 'image_url', image_url: { url: `data:${args.image.mimeType};base64,${args.image.base64}` } },
          ]
          : args.prompt,
      },
    ];
    const body: Record<string, unknown> = { model: this.model, messages, temperature: 0.2, max_tokens: args.maxOutputTokens };
    if (structured) body.response_format = { type: 'json_schema', json_schema: { name: 'aita_response', strict: false, schema: args.schema } };
    return body;
  }

  private asProviderFailure(error: unknown): ProviderFailure {
    const status = this.statusOf(error);
    const kind: FailureKind = status === 429 ? 'rate'
      : status === 401 || status === 402 || status === 403 ? 'exhausted'
      : status === undefined || status >= 500 ? 'transient'
      : 'fatal';
    const detail = typeof error === 'object' && error !== null && typeof (error as { message?: unknown }).message === 'string'
      ? (error as { message: string }).message
      : 'HTTP ' + status;
    const retryAfterMs = error instanceof ProviderHttpError ? error.retryAfterMs : undefined;
    const structuredFormatUnsupported = status === 400 && /response_format|json_schema|structured|json_object/i.test(detail);
    return new ProviderFailure(kind, status, detail, retryAfterMs, structuredFormatUnsupported);
  }

  private applyFailure(apiKey: string, failure: ProviderFailure): ProviderFailure {
    const current = this.cooldownUntil.get(apiKey) ?? 0;
    const now = Date.now();
    if (failure.kind === 'rate') {
      this.cooldownUntil.set(apiKey, Math.max(current, now + Math.min(failure.retryAfterMs ?? this.keyCooldownMs, EXHAUSTED_KEY_COOLDOWN_MS)));
    } else if (failure.kind === 'exhausted') {
      this.cooldownUntil.set(apiKey, Math.max(current, now + EXHAUSTED_KEY_COOLDOWN_MS));
    } else if (failure.kind === 'transient') {
      this.cooldownUntil.set(apiKey, Math.max(current, now + TRANSIENT_COOLDOWN_MS));
    }
    return failure;
  }

  private parseJson(content: string): unknown {
    const trimmed = content.trim();
    const fenced = /^```[A-Za-z]*\s*([\s\S]*?)\s*```$/.exec(trimmed);
    const candidate = (fenced ? fenced[1] : trimmed).trim();
    const direct = this.tryParse(candidate);
    if (direct !== undefined) return direct;
    const embedded = /[[{][\s\S]*[\]}]/.exec(candidate);
    if (embedded) {
      const parsed = this.tryParse(embedded[0]);
      if (parsed !== undefined) return parsed;
    }
    throw new BadGatewayException({ error_code: 'AI_INVALID_RESPONSE', message: 'Dịch vụ AI trả về dữ liệu không đúng định dạng.', details: null });
  }

  private tryParse(text: string): unknown | undefined {
    try { return JSON.parse(text); } catch { return undefined; }
  }

  private rethrowAsHttpError(error: unknown, status: number | undefined, message: string): never {
    if (error instanceof ProviderHttpError) throw error;
    throw new ProviderHttpError(status, '', error instanceof Error && error.name === 'AbortError' ? `${message} (timeout ${this.timeoutMs} ms).` : message);
  }

  private providerMessage(rawBody: string, fallback: string): string {
    const parsed = this.tryParse(rawBody);
    if (typeof parsed === 'object' && parsed !== null) {
      const nest = parsed as { error?: { message?: string } | string; message?: string };
      if (typeof nest.error === 'object' && nest.error?.message) return nest.error.message;
      if (typeof nest.message === 'string') return nest.message;
    }
    return fallback;
  }

  private retryAfterMs(headers: Headers): number | undefined {
    const raw = headers.get('retry-after');
    if (!raw) return undefined;
    const seconds = Number(raw);
    return Number.isFinite(seconds) && seconds >= 0 ? Math.min(seconds * 1000, EXHAUSTED_KEY_COOLDOWN_MS) : undefined;
  }

  private statusOf(error: unknown): number | undefined {
    if (typeof error !== 'object' || error === null) return undefined;
    const status = (error as { status?: unknown }).status ?? (error as { statusCode?: unknown }).statusCode;
    return typeof status === 'number' ? status : undefined;
  }

  private rotationOrder(): string[] {
    const count = this.apiKeys.length;
    const start = this.rotationIndex;
    this.rotationIndex = (this.rotationIndex + 1) % count;
    return Array.from({ length: count }, (_, index) => this.apiKeys[(start + index) % count]);
  }

  private isCoolingDown(apiKey: string): boolean { return Date.now() < (this.cooldownUntil.get(apiKey) ?? 0); }

  private async releaseQuietly(reservation: QuotaReservation): Promise<void> {
    try { await this.quota.release(reservation); } catch { /* quota reconciliation can be retried operationally. */ }
  }

  private readNumber(raw: unknown, fallback: number, minimum: number): number {
    const parsed = typeof raw === 'string' ? Number(raw) : typeof raw === 'number' ? raw : NaN;
    return Number.isFinite(parsed) && parsed >= minimum ? parsed : fallback;
  }
}
