import { ConfigService } from '@nestjs/config';
import { AiFeature, AiQuotaService } from '../modules/ai-gateway/ai-quota.service';
import { OpenRouterService } from '../modules/ai-gateway/openrouter.service';

describe('OpenRouterService (Unit AI Provider Rotation Test)', () => {
  const schema = { type: 'object', properties: { ok: { type: 'boolean' } }, required: ['ok'] };
  const validResult = { data: { ok: true }, tokensConsumed: 15 };

  function todayUtc(): Date {
    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  }

  function makeConfig(env: Record<string, string>): ConfigService {
    return { get: jest.fn((key: string, def?: string) => env[key] ?? def) } as unknown as ConfigService;
  }

  function makeQuota(): AiQuotaService {
    return {
      reserve: jest.fn().mockResolvedValue({ configId: 'q1', reserved: 100, date: todayUtc() }),
      settle: jest.fn().mockResolvedValue(undefined),
      release: jest.fn().mockResolvedValue(undefined),
    } as unknown as AiQuotaService;
  }

  function args(feature: AiFeature = 'TESTCASE_GEN') {
    return { userId: 'u1', feature, prompt: 'p'.repeat(40), schema, maxOutputTokens: 100 };
  }

  function resolvedCompletion(content: string, usage = { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 }) {
    return { choices: [{ message: { content } }], usage };
  }

  function makeService(keys: string[], env: Record<string, string> = {}): OpenRouterService {
    return new OpenRouterService(makeConfig({ OPENROUTER_API_KEYS: keys.join(','), ...env }), makeQuota());
  }

  afterEach(() => jest.clearAllMocks());

  describe('UT03_AiProvider_TC001: Gọi thành công qua tài khoản quay vòng', () => {
    it('chọn lần lượt từng key trong pool 3 tài khoản', async () => {
      const service = makeService(['key-1', 'key-2', 'key-3']);
      (service as any).post = jest.fn().mockResolvedValue(resolvedCompletion('{"ok":true}'));

      const first = await service.generateJson<{ ok: boolean }>(args());
      await service.generateJson<{ ok: boolean }>(args());
      await service.generateJson<{ ok: boolean }>(args());

      const keys = (service as any).post.mock.calls.map((c: any[]) => c[0]);
      expect(keys).toEqual(['key-1', 'key-2', 'key-3']);
      expect(first).toEqual(validResult);
    });

    it('body gửi OpenRouter chứa model, temperature và response_format json_schema', async () => {
      const service = makeService(['key-1']);
      (service as any).post = jest.fn().mockResolvedValue(resolvedCompletion('{"ok":true}'));

      await service.generateJson<{ ok: boolean }>(args());

      const body = (service as any).post.mock.calls[0][1] as any;
      expect(body.model).toBe('openrouter/free');
      expect(body.temperature).toBe(0.2);
      expect(body.max_tokens).toBe(100);
      expect(body.messages).toHaveLength(2);
      expect(body.response_format.type).toBe('json_schema');
      expect(body.response_format.json_schema.schema).toEqual(schema);
    });
  });

  describe('UT03_AiProvider_TC002: Token usage từ provider được ghi vết qua settle', () => {
    it('settle nhận prompt/completion/total tokens thực tế và release không được gọi', async () => {
      const service = makeService(['key-1']);
      (service as any).post = jest.fn().mockResolvedValue(resolvedCompletion('{"ok":true}', { prompt_tokens: 120, completion_tokens: 80, total_tokens: 200 }));

      const result = await service.generateJson<{ ok: boolean }>(args());

      expect(result.tokensConsumed).toBe(200);
      expect((service as any).quota.settle).toHaveBeenCalledWith('u1', expect.objectContaining({ configId: 'q1' }), { promptTokens: 120, completionTokens: 80, totalTokens: 200 }, 'TESTCASE_GEN', 'openrouter/free');
      expect((service as any).quota.release).not.toHaveBeenCalled();
    });
  });

  describe('UT03_AiProvider_TC003: Tài khoản bị 429 thì tự chuyển sang tài khoản kế tiếp', () => {
    it('key đầu 429, key thứ hai thành công, không hoàn quota', async () => {
      const service = makeService(['key-1', 'key-2']);
      const post = (service as any).post = jest.fn()
        .mockRejectedValueOnce({ status: 429 })
        .mockResolvedValueOnce(resolvedCompletion('{"ok":true}'));

      const result = await service.generateJson<{ ok: boolean }>(args());

      expect(result).toEqual(validResult);
      expect(post).toHaveBeenCalledTimes(2);
      expect(post.mock.calls[0][0]).toBe('key-1');
      expect(post.mock.calls[1][0]).toBe('key-2');
      expect((service as any).quota.release).not.toHaveBeenCalled();
      expect((service as any).quota.settle).toHaveBeenCalledTimes(1);
    });
  });

  describe('UT03_AiProvider_TC004: Tất cả tài khoản đều bị giới hạn', () => {
    it('ném 429 AI_PROVIDER_RATE_LIMITED và hoàn quota đã giữ chỗ', async () => {
      const service = makeService(['key-1', 'key-2', 'key-3']);
      const post = (service as any).post = jest.fn().mockRejectedValue({ status: 429 });

      const error = await service.generateJson<{ ok: boolean }>(args()).catch((e) => e);

      expect(error.getStatus()).toBe(429);
      expect(error.getResponse()).toEqual(expect.objectContaining({ error_code: 'AI_PROVIDER_RATE_LIMITED' }));
      expect(post).toHaveBeenCalledTimes(3);
      expect((service as any).quota.release).toHaveBeenCalledWith(expect.objectContaining({ configId: 'q1' }));
      expect((service as any).quota.settle).not.toHaveBeenCalled();
    });
  });

  describe('UT03_AiProvider_TC005: Tài khoản đang cooldown bị bỏ qua ở lượt gọi kế tiếp', () => {
    it('lượt gọi thứ hai ném 429 ngay mà không đốt thêm request free', async () => {
      const service = makeService(['key-1', 'key-2']);
      const post = (service as any).post = jest.fn().mockRejectedValue({ status: 429 });

      await expect(service.generateJson<{ ok: boolean }>(args())).rejects.toMatchObject({ status: 429 });
      await expect(service.generateJson<{ ok: boolean }>(args())).rejects.toMatchObject({ status: 429 });
      expect(post).toHaveBeenCalledTimes(2);
    });
  });

  describe('UT03_AiProvider_TC006: Model không hỗ trợ response_format thì fallback tự động', () => {
    it('400 báo json_schema không hỗ trợ → gọi lại không response_format và nhúng schema vào prompt', async () => {
      const service = makeService(['key-1']);
      const post = (service as any).post = jest.fn()
        .mockRejectedValueOnce({ status: 400, message: 'response_format json_schema is not supported for this model' })
        .mockResolvedValueOnce(resolvedCompletion('{"ok":true}'));

      const result = await service.generateJson<{ ok: boolean }>(args());

      expect(result).toEqual(validResult);
      expect(post).toHaveBeenCalledTimes(2);
      const firstBody = post.mock.calls[0][1] as any;
      const secondBody = post.mock.calls[1][1] as any;
      expect(firstBody.response_format).toBeDefined();
      expect(secondBody.response_format).toBeUndefined();
      expect(secondBody.messages[0].content).toContain('JSON Schema');
    });
  });

  describe('UT03_AiProvider_TC007: Phản hồi bọc markdown code fence', () => {
    it('bóc tách ```json và trả về dữ liệu JSON hợp lệ', async () => {
      const service = makeService(['key-1']);
      (service as any).post = jest.fn().mockResolvedValue(resolvedCompletion('```json\n{"ok":true}\n```'));

      const result = await service.generateJson<{ ok: boolean }>(args());

      expect(result.data).toEqual({ ok: true });
    });
  });

  describe('UT03_AiProvider_TC008: Tính năng chấm UI gửi ảnh kèm prompt', () => {
    it('image_url ở dạng data URL PNG (biên chức năng vision)', async () => {
      const service = makeService(['key-1']);
      (service as any).post = jest.fn().mockResolvedValue(resolvedCompletion('{"ok":true}'));

      await service.generateJson<{ ok: boolean }>({ ...args('UI_EVALUATION'), image: { mimeType: 'image/png', base64: 'QUJD' } });

      const body = (service as any).post.mock.calls[0][1] as any;
      expect(body.messages[1].content).toEqual([
        { type: 'text', text: expect.any(String) },
        { type: 'image_url', image_url: { url: 'data:image/png;base64,QUJD' } },
      ]);
    });
  });

  describe('UT03_AiProvider_TC009: Chưa cấu hình tài khoản AI nào', () => {
    it('trả 503 AI_NOT_CONFIGURED trước khi giữ chỗ quota', async () => {
      const service = makeService([]);
      (service as any).post = jest.fn();

      const error = await service.generateJson<{ ok: boolean }>(args()).catch((e) => e);

      expect(error.getStatus()).toBe(503);
      expect(error.getResponse()).toEqual(expect.objectContaining({ error_code: 'AI_NOT_CONFIGURED' }));
      expect((service as any).quota.reserve).not.toHaveBeenCalled();
      expect((service as any).post).not.toHaveBeenCalled();
    });
  });

  describe('UT03_AiProvider_TC010: Nhà cung cấp lỗi tạm thời chỉ có 1 tài khoản', () => {
    it('ném 502 AI_PROVIDER_ERROR và hoàn quota', async () => {
      const service = makeService(['key-1']);
      const post = (service as any).post = jest.fn().mockRejectedValue({ status: 503 });

      const error = await service.generateJson<{ ok: boolean }>(args()).catch((e) => e);

      expect(error.getStatus()).toBe(502);
      expect(error.getResponse()).toEqual({ error_code: 'AI_PROVIDER_ERROR', message: 'Không thể nhận phản hồi từ dịch vụ AI.', details: null });
      expect(post).toHaveBeenCalledTimes(1);
      expect((service as any).quota.release).toHaveBeenCalledWith(expect.objectContaining({ configId: 'q1' }));
      expect((service as any).quota.settle).not.toHaveBeenCalled();
    });
  });

  describe('UT03_AiProvider_TC011: Tài khoản hết hạn mức credits (402)', () => {
    it('402 vào nhóm capacity → 429 và không thử lại key vừa lỗi', async () => {
      const service = makeService(['key-1', 'key-2']);
      const post = (service as any).post = jest.fn().mockRejectedValue({ status: 402 });

      const error = await service.generateJson<{ ok: boolean }>(args()).catch((e) => e);

      expect(error.getStatus()).toBe(429);
      expect(error.getResponse()).toEqual(expect.objectContaining({ error_code: 'AI_PROVIDER_RATE_LIMITED' }));
      expect(post).toHaveBeenCalledTimes(2);
    });
  });

  describe('UT03_AiProvider_TC012: Trạng thái pool phục vụ Web Admin', () => {
    it('trả model và trạng thái từng tài khoản, key mật bị che, không lộ key gốc', () => {
      const service = makeService(['sk-or-v1-fedcba987654', 'sk-or-v1-0123456789ab']);

      const status = service.providerStatus();

      expect(status.provider).toBe('openrouter');
      expect(status.model).toBe('openrouter/free');
      expect(status.accounts_configured).toBe(2);
      expect(status.accounts[0]).toEqual({ account: 'ACC-01', key_hint: 'sk-or-v1-…7654', state: 'READY', cooldown_remaining_seconds: 0 });
      expect(status.accounts[1].key_hint).toBe('sk-or-v1-…89ab');
      expect(JSON.stringify(status)).not.toContain('fedcba987654');
      expect(JSON.stringify(status)).not.toContain('sk-or-v1-0123456789ab');
    });
  });

  describe('UT03_AiProvider_TC013: Nội dung rỗng thì xoay sang tài khoản kế tiếp', () => {
    it('key đầu trả content rỗng, key thứ hai trả JSON hợp lệ, không hoàn quota', async () => {
      const service = makeService(['key-1', 'key-2']);
      const post = (service as any).post = jest.fn()
        .mockResolvedValueOnce(resolvedCompletion(''))
        .mockResolvedValueOnce(resolvedCompletion('{"ok":true}'));

      const result = await service.generateJson<{ ok: boolean }>(args());

      expect(result).toEqual(validResult);
      expect(post).toHaveBeenCalledTimes(2);
      expect(post.mock.calls[0][0]).toBe('key-1');
      expect(post.mock.calls[1][0]).toBe('key-2');
      expect((service as any).quota.settle).toHaveBeenCalledTimes(2);
      expect((service as any).quota.release).not.toHaveBeenCalled();
    });
  });

  describe('UT03_AiProvider_TC015: Cấu hình model dự phòng thì gửi mảng models', () => {
    it('body chứa models gồm model chính + dự phòng và bỏ trường model', async () => {
      const service = makeService(['key-1'], {
        OPENROUTER_MODEL: 'google/gemma-4-31b-it:free',
        OPENROUTER_MODEL_FALLBACKS: 'google/gemma-4-26b-a4b-it:free,openrouter/free',
      });
      (service as any).post = jest.fn().mockResolvedValue(resolvedCompletion('{"ok":true}'));

      await service.generateJson<{ ok: boolean }>(args());

      const body = (service as any).post.mock.calls[0][1] as any;
      expect(body.model).toBeUndefined();
      expect(body.models).toEqual(['google/gemma-4-31b-it:free', 'google/gemma-4-26b-a4b-it:free', 'openrouter/free']);
      expect(service.providerStatus().fallback_models).toEqual(['google/gemma-4-26b-a4b-it:free', 'openrouter/free']);
    });
  });

  describe('UT03_AiProvider_TC014: Mọi tài khoản đều trả JSON sai định dạng', () => {
    it('ném 502 AI_INVALID_RESPONSE và hoàn quota đã giữ chỗ', async () => {
      const service = makeService(['key-1']);
      const post = (service as any).post = jest.fn().mockResolvedValue(resolvedCompletion('not-json-at-all'));

      const error = await service.generateJson<{ ok: boolean }>(args()).catch((e) => e);

      expect(error.getStatus()).toBe(502);
      expect(error.getResponse()).toEqual(expect.objectContaining({ error_code: 'AI_INVALID_RESPONSE' }));
      expect(post).toHaveBeenCalledTimes(1);
      expect((service as any).quota.release).toHaveBeenCalledWith(expect.objectContaining({ configId: 'q1' }));
    });
  });
});
