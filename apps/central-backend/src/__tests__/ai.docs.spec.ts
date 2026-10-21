import { ArgumentsHost, BadGatewayException, ForbiddenException, HttpException, UnauthorizedException, UnprocessableEntityException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Reflector } from '@nestjs/core';
import { AiGatewayService } from '../modules/ai-gateway/ai-gateway.service';
import { AiQuotaService } from '../modules/ai-gateway/ai-quota.service';
import { OpenRouterService } from '../modules/ai-gateway/openrouter.service';
import { GenerateTestcasesDto } from '../modules/ai-gateway/dto/generate-testcases.dto';
import { ReviewCodeDto } from '../modules/ai-gateway/dto/review-code.dto';
import { VerifyPlagiarismDto } from '../modules/ai-gateway/dto/verify-plagiarism.dto';
import { EvaluateWebUiDto } from '../modules/ai-gateway/dto/evaluate-web-ui.dto';
import { EvaluatePeCodeDto } from '../modules/ai-gateway/dto/evaluate-pe-code.dto';
import { PrismaService } from '../prisma/prisma.service';
import { RolesGuard } from '../common/guards/roles.guard';
import { AdaptiveThrottlerGuard } from '../common/guards/adaptive-throttler.guard';
import { JwtAuthGuard } from '../modules/auth/guards/jwt-auth.guard';
import { JwtStrategy } from '../modules/auth/strategies/jwt.strategy';
import { createValidationPipe } from '../common/validation/validation-pipe.factory';
import { ApiExceptionFilter } from '../common/filters/api-exception.filter';

describe('AI Gateway (docs: docs/testcases/1-unit/AI/AI_testcase.md)', () => {
  let ai: AiGatewayService;
  let provider: { generateJson: jest.Mock };
  const instructorId = '550e8400-e29b-41d4-a716-446655440001';

  const configMock = {
    get: jest.fn((_key: string, def?: string) => def),
    getOrThrow: jest.fn((key: string) => `secret_for_${key}`),
  };

  function todayUtc(): Date {
    const now = new Date();
    return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  }

  function makeTestcase(index: number) {
    return { input: `in_${index}`, expected_output: `out_${index}`, explanation: 'because', is_boundary: false };
  }

  function makeTestcases(count: number) {
    return Array.from({ length: count }, (_, i) => makeTestcase(i));
  }

  beforeEach(() => {
    provider = { generateJson: jest.fn() };
    ai = new AiGatewayService(provider as unknown as OpenRouterService);
  });

  afterEach(() => jest.clearAllMocks());

  async function validate(metatype: any, value: unknown): Promise<unknown> {
    return createValidationPipe().transform(value, { type: 'body', metatype, data: '' } as any);
  }

  async function validationError(metatype: any, value: unknown): Promise<UnprocessableEntityException> {
    try {
      await validate(metatype, value);
    } catch (error) {
      if (error instanceof UnprocessableEntityException) return error;
      throw error;
    }
    throw new Error('Expected ValidationPipe to reject the payload');
  }

  function expectValidationDetail(error: UnprocessableEntityException, field: string, issue: string): void {
    const body = error.getResponse() as any;
    expect(body.error_code).toBe('VALIDATION_FAILED');
    expect(body.message).toBe('Dữ liệu gửi lên không đúng định dạng.');
    const detail = body.details.find((d: any) => d.field === field);
    expect(detail).toBeDefined();
    expect(detail.issues).toContain(issue);
  }

  function expectValidationField(error: UnprocessableEntityException, field: string): void {
    const body = error.getResponse() as any;
    expect(body.error_code).toBe('VALIDATION_FAILED');
    expect(body.details.some((d: any) => d.field === field)).toBe(true);
  }

  function makeHost(): { host: ArgumentsHost; status: jest.Mock; json: jest.Mock } {
    const json = jest.fn();
    const status = jest.fn().mockReturnValue({ json });
    const host = {
      switchToHttp: () => ({
        getRequest: () => ({ method: 'POST', url: '/api/v1/ai/generate-testcases' }),
        getResponse: () => ({ status }),
      }),
    } as unknown as ArgumentsHost;
    return { host, status, json };
  }

  async function expectInternalServerError(promise: Promise<unknown>): Promise<void> {
    const error = await promise.catch((e) => e);
    const { host, status, json } = makeHost();
    new ApiExceptionFilter().catch(error, host);
    expect(status).toHaveBeenCalledWith(500);
    expect(json).toHaveBeenCalledWith(expect.objectContaining({ error_code: 'INTERNAL_SERVER_ERROR', message: 'Đã xảy ra lỗi hệ thống.' }));
  }

  function expectUnauthorizedNoToken(): void {
    const guard = new JwtAuthGuard();
    const error = (() => {
      try {
        guard.handleRequest(null, false, undefined);
      } catch (e) {
        return e;
      }
    })() as UnauthorizedException;
    expect(error.getStatus()).toBe(401);
    expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
  }

  function expectForbiddenForAdmin(): void {
    const reflector = { getAllAndOverride: jest.fn().mockReturnValue(['INSTRUCTOR']) } as unknown as Reflector;
    const context = {
      getHandler: () => ({}),
      getClass: () => ({}),
      switchToHttp: () => ({ getRequest: () => ({ user: { id: instructorId, username: 'admin', role: 'ADMIN' } }) }),
    } as any;
    const error = (() => {
      try {
        new RolesGuard(reflector).canActivate(context);
      } catch (e) {
        return e;
      }
    })() as any;
    expect(error.getStatus()).toBe(403);
    expect(error.getResponse()).toEqual({ error_code: 'FORBIDDEN_ADMIN_ONLY', message: 'Bạn không có quyền thực hiện thao tác này.', details: null });
  }

  function quotaExceeded(): HttpException {
    return new HttpException({ error_code: 'AI_QUOTA_EXCEEDED', message: 'Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.', details: null }, 429);
  }

  function providerError(): BadGatewayException {
    return new BadGatewayException({ error_code: 'AI_PROVIDER_ERROR', message: 'Không thể nhận phản hồi từ dịch vụ AI.', details: null });
  }

  // =========================================================================
  // PHẦN 1: GET /api/v1/ai/quota
  // =========================================================================

  describe('UT03_AiQuota (AiQuotaService)', () => {
    let prisma: any;
    let quota: AiQuotaService;

    beforeEach(() => {
      prisma = {
        aiQuotaConfig: { findFirst: jest.fn(), findUnique: jest.fn(), update: jest.fn(), updateMany: jest.fn() },
        aiQuotaLog: { create: jest.fn() },
        $transaction: jest.fn((arg: any) => (typeof arg === 'function' ? arg(prisma) : Promise.all(arg))),
      };
      quota = new AiQuotaService(prisma as unknown as PrismaService);
    });

    describe('UT03_AiQuota_TC001: Không gửi Header Authorization', () => {
      it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
    });

    describe('UT03_AiQuota_TC002: Token không hợp lệ/sai chữ ký', () => {
      it('trả 401 AUTH_INVALID_TOKEN', () => {
        const error = (() => {
          try {
            new JwtAuthGuard().handleRequest(null, false, { name: 'JsonWebTokenError' });
          } catch (e) {
            return e;
          }
        })() as UnauthorizedException;
        expect(error.getResponse()).toEqual({ error_code: 'AUTH_INVALID_TOKEN', message: 'Token không hợp lệ.', details: null });
      });
    });

    describe('UT03_AiQuota_TC003: Token đã hết hạn', () => {
      it('trả 401 AUTH_TOKEN_EXPIRED', () => {
        const error = (() => {
          try {
            new JwtAuthGuard().handleRequest(null, false, { name: 'TokenExpiredError' });
          } catch (e) {
            return e;
          }
        })() as UnauthorizedException;
        expect(error.getResponse()).toEqual({ error_code: 'AUTH_TOKEN_EXPIRED', message: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.', details: null });
      });
    });

    describe('UT03_AiQuota_TC004: Tài khoản trong Token đã bị vô hiệu hóa', () => {
      it('JwtStrategy.validate ném 401 AUTH_ACCOUNT_DISABLED', async () => {
        const strategy = new JwtStrategy(configMock as unknown as ConfigService, { user: { findFirst: jest.fn().mockResolvedValue(null) } } as any);
        const error = await strategy.validate({ id: 'gone', username: 'x', role: 'INSTRUCTOR', token_type: 'access' } as any).catch((e) => e);
        expect(error).toBeInstanceOf(UnauthorizedException);
        expect(error.getResponse()).toEqual({ error_code: 'AUTH_ACCOUNT_DISABLED', message: 'Tài khoản không còn hoạt động.' });
      });
    });

    describe('UT03_AiQuota_TC005: Lỗi CSDL khi truy vấn hạn ngạch', () => {
      it('trả 500 INTERNAL_SERVER_ERROR', async () => {
        prisma.$transaction.mockRejectedValue(new Error('Connection refused'));
        await expectInternalServerError(quota.snapshot(instructorId));
      });
    });

    describe('UT03_AiQuota_TC006: Lấy hạn ngạch thành công khi còn hạn mức', () => {
      it('trả daily/used/remaining/reset', async () => {
        const config = { id: 'q1', userId: instructorId, dailyTokenLimit: 50000, usedTokensToday: 15000, lastResetDate: todayUtc(), isDeleted: false };
        prisma.aiQuotaConfig.findFirst.mockResolvedValue(config);
        prisma.aiQuotaConfig.findUnique.mockResolvedValue(config);
        const result = await quota.snapshot(instructorId);
        expect(result.daily_limit_tokens).toBe(50000);
        expect(result.used_tokens_today).toBe(15000);
        expect(result.remaining_tokens).toBe(35000);
        expect(result.reset_at_utc).toBeDefined();
      });
    });

    describe('UT03_AiQuota_TC007: Lấy hạn ngạch khi đã dùng hết (Biên 0)', () => {
      it('remaining_tokens = 0', async () => {
        const config = { id: 'q1', userId: instructorId, dailyTokenLimit: 50000, usedTokensToday: 50000, lastResetDate: todayUtc(), isDeleted: false };
        prisma.aiQuotaConfig.findFirst.mockResolvedValue(config);
        prisma.aiQuotaConfig.findUnique.mockResolvedValue(config);
      const result = await quota.snapshot(instructorId);
      expect(result.remaining_tokens).toBe(0);
    });
  });

    describe('UT03_AiQuota_TC008: Giảng viên chưa được cấu hình hạn ngạch', () => {
      it('trả 403 AI_QUOTA_NOT_CONFIGURED', async () => {
        prisma.aiQuotaConfig.findFirst.mockResolvedValue(null);
        const error = await quota.snapshot(instructorId).catch((e) => e);
        expect(error).toBeInstanceOf(ForbiddenException);
        expect(error.getStatus()).toBe(403);
        expect(error.getResponse()).toEqual({ error_code: 'AI_QUOTA_NOT_CONFIGURED', message: 'Tài khoản chưa được cấu hình hạn ngạch AI.', details: null });
      });
    });

    describe('UT03_AiQuota_TC009: Tự động đặt lại hạn ngạch khi sang ngày UTC mới', () => {
      it('reset usedTokensToday về 0 khi lastResetDate là ngày hôm qua', async () => {
        const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
        const stale = { id: 'q1', userId: instructorId, dailyTokenLimit: 50000, usedTokensToday: 40000, lastResetDate: yesterday, isDeleted: false };
        prisma.aiQuotaConfig.findFirst.mockResolvedValue(stale);
        prisma.aiQuotaConfig.updateMany.mockResolvedValue({ count: 1 });
        prisma.aiQuotaConfig.findUnique.mockResolvedValue({ ...stale, usedTokensToday: 0, lastResetDate: todayUtc() });
        const result = await quota.snapshot(instructorId);
        expect(prisma.aiQuotaConfig.updateMany).toHaveBeenCalled();
        expect(result.used_tokens_today).toBe(0);
        expect(result.remaining_tokens).toBe(50000);
      });
    });
  });

  // =========================================================================
  // PHẦN 2: POST /api/v1/ai/generate-testcases
  // =========================================================================

  const validGenerate = {
    problem_description: 'Read two integers and print their sum.',
    language: 'C' as const,
    count: 3,
    include_boundary: true,
  };

  describe('UT03_AiGenerateTestcases_TC001: Không gửi Header Authorization', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT03_AiGenerateTestcases_TC002: ADMIN không có quyền', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForAdmin());
  });

  describe('UT03_AiGenerateTestcases_TC003: Giảng viên đã hết hạn ngạch', () => {
    it('trả 429 AI_QUOTA_EXCEEDED', async () => {
      provider.generateJson.mockRejectedValue(quotaExceeded());
      const error = await ai.generateTestcases(instructorId, { ...validGenerate } as GenerateTestcasesDto).catch((e) => e);
      expect(error.getStatus()).toBe(429);
      expect((error.getResponse() as any).error_code).toBe('AI_QUOTA_EXCEEDED');
    });
  });

  describe('UT03_AiGenerateTestcases_TC004: Thiếu problem_description', () => {
    it('trả 422 field problem_description', async () => {
      const error = await validationError(GenerateTestcasesDto, { language: 'C' });
      expectValidationDetail(error, 'problem_description', 'problem_description must be a string');
    });
  });

  describe('UT03_AiGenerateTestcases_TC005: problem_description dưới 20 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(GenerateTestcasesDto, { ...validGenerate, problem_description: 'Too short' });
      expectValidationDetail(error, 'problem_description', 'problem_description must be longer than or equal to 20 characters');
    });
  });

  describe('UT03_AiGenerateTestcases_TC006: problem_description vượt 5000 ký tự', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(GenerateTestcasesDto, { ...validGenerate, problem_description: 'a'.repeat(5001) });
      expectValidationDetail(error, 'problem_description', 'problem_description must be shorter than or equal to 5000 characters');
    });
  });

  describe('UT03_AiGenerateTestcases_TC007: Thiếu language', () => {
    it('trả 422 field language', async () => {
      const error = await validationError(GenerateTestcasesDto, { problem_description: validGenerate.problem_description });
      expectValidationField(error, 'language');
    });
  });

  describe('UT03_AiGenerateTestcases_TC008: language không thuộc enum', () => {
    it('trả 422 enum message', async () => {
      const error = await validationError(GenerateTestcasesDto, { ...validGenerate, language: 'JAVASCRIPT' });
      expectValidationDetail(error, 'language', 'language must be one of the following values: C, JAVA, PYTHON, WEB');
    });
  });

  describe('UT03_AiGenerateTestcases_TC009: count ngoài khoảng [1, 10]', () => {
    it('trả 422 min và max', async () => {
      const low = await validationError(GenerateTestcasesDto, { ...validGenerate, count: 0 });
      expectValidationDetail(low, 'count', 'count must not be less than 1');
      const high = await validationError(GenerateTestcasesDto, { ...validGenerate, count: 11 });
      expectValidationDetail(high, 'count', 'count must not be greater than 10');
    });
  });

  describe('UT03_AiGenerateTestcases_TC010: Nhà cung cấp AI gặp sự cố kết nối/quá tải', () => {
    it('OpenRouterService ném 502 AI_PROVIDER_ERROR và hoàn quota', async () => {
      const quotaMock = {
        reserve: jest.fn().mockResolvedValue({ configId: 'q1', reserved: 100, date: todayUtc() }),
        release: jest.fn().mockResolvedValue(undefined),
        settle: jest.fn(),
      };
      const config = { get: jest.fn((key: string, def?: string) => (key === 'OPENROUTER_API_KEYS' ? 'test-key' : def)) };
      const service = new OpenRouterService(config as unknown as ConfigService, quotaMock as unknown as AiQuotaService);
      (service as any).post = jest.fn().mockRejectedValue({ status: 503 });
      const error = await service.generateJson({ userId: instructorId, feature: 'TESTCASE_GEN', prompt: 'p', schema: {} as any, maxOutputTokens: 100 }).catch((e) => e);
      expect(error).toBeInstanceOf(BadGatewayException);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_PROVIDER_ERROR');
      expect(quotaMock.release).toHaveBeenCalled();
    });
  });

  describe('UT03_AiGenerateTestcases_TC011: Phản hồi AI sai cấu trúc JSON', () => {
    it('trả 502 AI_INVALID_RESPONSE', async () => {
      provider.generateJson.mockResolvedValue({ data: {}, tokensConsumed: 10 });
      const error = await ai.generateTestcases(instructorId, { ...validGenerate } as GenerateTestcasesDto).catch((e) => e);
      expect(error).toBeInstanceOf(BadGatewayException);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_INVALID_RESPONSE');
    });
  });

  describe('UT03_AiGenerateTestcases_TC012: Thành công với tham số mặc định', () => {
    it('trả tokens_consumed và 3 testcase', async () => {
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(3) }, tokensConsumed: 1234 });
      const result = await ai.generateTestcases(instructorId, { ...validGenerate } as GenerateTestcasesDto);
      expect(result.message).toBe('Sinh testcase tự động bằng AI thành công');
      expect((result.data as any).tokens_consumed).toBe(1234);
      expect((result.data as any).testcases).toHaveLength(3);
    });
  });

  describe('UT03_AiGenerateTestcases_TC013: Thành công với count = 1 (biên dưới)', () => {
    it('trả đúng 1 testcase', async () => {
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(1) }, tokensConsumed: 200 });
      const result = await ai.generateTestcases(instructorId, { ...validGenerate, count: 1 } as GenerateTestcasesDto);
      expect((result.data as any).testcases).toHaveLength(1);
    });
  });

  describe('UT03_AiGenerateTestcases_TC014: Thành công với count = 10 (biên trên)', () => {
    it('trả đúng 10 testcase', async () => {
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(10) }, tokensConsumed: 5000 });
      const result = await ai.generateTestcases(instructorId, { ...validGenerate, count: 10 } as GenerateTestcasesDto);
      expect((result.data as any).testcases).toHaveLength(10);
    });
  });

  describe('UT03_AiGenerateTestcases_TC015: problem_description dài đúng 20 ký tự (biên dưới)', () => {
    it('hợp lệ và sinh thành công', async () => {
      await expect(validate(GenerateTestcasesDto, { ...validGenerate, problem_description: 'a'.repeat(20) })).resolves.toBeDefined();
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(3) }, tokensConsumed: 100 });
      const result = await ai.generateTestcases(instructorId, { ...validGenerate, problem_description: 'a'.repeat(20) } as GenerateTestcasesDto);
      expect((result.data as any).testcases).toHaveLength(3);
    });
  });

  describe('UT03_AiGenerateTestcases_TC016: Thành công PYTHON với include_boundary = false', () => {
    it('prompt không chèn cụm boundary', async () => {
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(3) }, tokensConsumed: 100 });
      await ai.generateTestcases(instructorId, { ...validGenerate, language: 'PYTHON', include_boundary: false } as GenerateTestcasesDto);
      const prompt: string = provider.generateJson.mock.calls[0][0].prompt;
      expect(prompt).toContain('PYTHON');
      expect(prompt).not.toContain('including boundary cases');
    });
  });

  describe('UT03_AiGenerateTestcases_TC017: Vượt giới hạn tần suất gọi AI (throttle)', () => {
    it('trả 429 RATE_LIMIT_EXCEEDED kèm thông tin giới hạn', async () => {
      const guard = new AdaptiveThrottlerGuard({} as any, {} as any, {} as any);
      const error = await (guard as any)
        .throwThrottlingException({} as any, { limit: 15, timeToBlockExpire: 60, timeToExpire: 60 } as any)
        .catch((e: any) => e);
      expect(error.getStatus()).toBe(429);
      expect(error.getResponse()).toEqual({ error_code: 'RATE_LIMIT_EXCEEDED', message: 'Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.', details: { limit: 15, retry_after_seconds: 60 } });
    });
  });

  describe('UT03_AiGenerateTestcases_TC018: AI trả thiếu/thừa số lượng testcase vẫn dùng được', () => {
    it('cắt phần thừa thay vì trả 502', async () => {
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(5) }, tokensConsumed: 500 });
      const result = await ai.generateTestcases(instructorId, { ...validGenerate, count: 3 } as GenerateTestcasesDto);
      expect((result.data as any).testcases).toHaveLength(3);
    });

    it('AI trả ít hơn yêu cầu thì trả về số hiện có', async () => {
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(2) }, tokensConsumed: 300 });
      const result = await ai.generateTestcases(instructorId, { ...validGenerate, count: 4 } as GenerateTestcasesDto);
      expect((result.data as any).testcases).toHaveLength(2);
    });
  });

  describe('UT03_AiGenerateTestcases_TC019: Thiếu is_boundary/explanation vẫn chuẩn hoá được', () => {
    // Lỗi thật: JSON Schema bắt buộc `is_boundary` nhưng prompt không nhắc, model free
    // bỏ trường này -> 502 AI_INVALID_RESPONSE dù các tính năng AI khác vẫn chạy.
    it('điền mặc định và bỏ item rỗng hoàn toàn', async () => {
      provider.generateJson.mockResolvedValue({
        data: {
          testcases: [
            { input: '5\n1 2 3', expected_output: '6' },
            { input: '', expected_output: '' },
            { input: '1\n2', expected_output: '2', explanation: 'biên dưới', is_boundary: 'true' },
          ],
        },
        tokensConsumed: 400,
      });
      const result = await ai.generateTestcases(instructorId, { ...validGenerate, count: 2 } as GenerateTestcasesDto);
      const testcases = (result.data as any).testcases;
      expect(testcases).toHaveLength(2);
      expect(testcases[0]).toEqual({ input: '5\n1 2 3', expected_output: '6', explanation: '', is_boundary: false });
      expect(testcases[1].is_boundary).toBe(true);
    });

    it('prompt liệt kê đủ 4 khoá để model không bỏ trường', async () => {
      provider.generateJson.mockResolvedValue({ data: { testcases: makeTestcases(3) }, tokensConsumed: 100 });
      await ai.generateTestcases(instructorId, { ...validGenerate } as GenerateTestcasesDto);
      const prompt: string = provider.generateJson.mock.calls[0][0].prompt;
      expect(prompt).toContain('is_boundary');
      expect(prompt).toContain('expected_output');
    });
  });

  // =========================================================================
  // PHẦN 3: POST /api/v1/ai/review-code
  // =========================================================================

  const validReview = {
    source_code: 'int main() { return 0; }',
    language: 'C' as const,
    problem_statement: 'Print the sum of two integers.',
    failed_testcase: { input: '1 2', expected_output: '3', actual_output: '4' },
  };

  function validReviewData(overrides: Record<string, unknown> = {}) {
    return { data: { issue_summary: 'Off-by-one in loop bound.', pedagogical_feedback: 'Check <= vs <.', bug_category: 'OFF_BY_ONE', ...overrides }, tokensConsumed: 900 };
  }

  describe('UT03_AiReviewCode_TC001: Không gửi Header Authorization', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT03_AiReviewCode_TC002: ADMIN không có quyền', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForAdmin());
  });

  describe('UT03_AiReviewCode_TC003: Giảng viên đã hết hạn ngạch', () => {
    it('trả 429 AI_QUOTA_EXCEEDED', async () => {
      provider.generateJson.mockRejectedValue(quotaExceeded());
      const error = await ai.reviewCode(instructorId, { ...validReview } as ReviewCodeDto).catch((e) => e);
      expect((error.getResponse() as any).error_code).toBe('AI_QUOTA_EXCEEDED');
    });
  });

  describe('UT03_AiReviewCode_TC004: Thiếu source_code', () => {
    it('trả 422 field source_code', async () => {
      const error = await validationError(ReviewCodeDto, { language: 'C', problem_statement: validReview.problem_statement, failed_testcase: validReview.failed_testcase });
      expectValidationDetail(error, 'source_code', 'source_code must be a string');
    });
  });

  describe('UT03_AiReviewCode_TC005: source_code dưới 10 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(ReviewCodeDto, { ...validReview, source_code: 'int a;' });
      expectValidationDetail(error, 'source_code', 'source_code must be longer than or equal to 10 characters');
    });
  });

  describe('UT03_AiReviewCode_TC006: source_code vượt 10000 ký tự', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(ReviewCodeDto, { ...validReview, source_code: 'a'.repeat(10001) });
      expectValidationDetail(error, 'source_code', 'source_code must be shorter than or equal to 10000 characters');
    });
  });

  describe('UT03_AiReviewCode_TC007: Thiếu problem_statement', () => {
    it('trả 422 field problem_statement', async () => {
      const error = await validationError(ReviewCodeDto, { source_code: validReview.source_code, language: 'C', failed_testcase: validReview.failed_testcase });
      expectValidationField(error, 'problem_statement');
    });
  });

  describe('UT03_AiReviewCode_TC008: problem_statement vượt 3000 ký tự', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(ReviewCodeDto, { ...validReview, problem_statement: 'a'.repeat(3001) });
      expectValidationDetail(error, 'problem_statement', 'problem_statement must be shorter than or equal to 3000 characters');
    });
  });

  describe('UT03_AiReviewCode_TC009: Thiếu failed_testcase', () => {
    it('trả 422 field failed_testcase', async () => {
      const error = await validationError(ReviewCodeDto, { source_code: validReview.source_code, language: 'C', problem_statement: validReview.problem_statement });
      expectValidationDetail(error, 'failed_testcase', 'failed_testcase must be an object');
    });
  });

  describe('UT03_AiReviewCode_TC010: failed_testcase thiếu expected_output', () => {
    it('trả 422 field failed_testcase (lỗi lồng)', async () => {
      const body = { ...validReview, failed_testcase: { input: '1 2', actual_output: '4' } };
      const error = await validationError(ReviewCodeDto, body);
      expectValidationField(error, 'failed_testcase');
    });
  });

  describe('UT03_AiReviewCode_TC011: Nhà cung cấp AI gặp sự cố kết nối', () => {
    it('trả 502 AI_PROVIDER_ERROR', async () => {
      provider.generateJson.mockRejectedValue(providerError());
      const error = await ai.reviewCode(instructorId, { ...validReview } as ReviewCodeDto).catch((e) => e);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_PROVIDER_ERROR');
    });
  });

  describe('UT03_AiReviewCode_TC012: Phân tích lỗi C thành công (off-by-one)', () => {
    it('trả suspected_error_line và tokens', async () => {
      provider.generateJson.mockResolvedValue(validReviewData({ suspected_error_line: 4 }));
      const result = await ai.reviewCode(instructorId, { ...validReview } as ReviewCodeDto);
      expect(result.message).toBe('Phân tích mã nguồn bằng AI thành công');
      expect((result.data as any).suspected_error_line).toBe(4);
      expect((result.data as any).tokens_consumed).toBe(900);
    });
  });

  describe('UT03_AiReviewCode_TC013: Phân tích Java thành công (không có dòng lỗi)', () => {
    it('không có suspected_error_line vẫn hợp lệ', async () => {
      provider.generateJson.mockResolvedValue(validReviewData());
      const result = await ai.reviewCode(instructorId, { ...validReview, language: 'JAVA' } as ReviewCodeDto);
      expect((result.data as any).suspected_error_line).toBeUndefined();
      expect((result.data as any).bug_category).toBe('OFF_BY_ONE');
    });
  });

  describe('UT03_AiReviewCode_TC014: source_code dài đúng 10 ký tự (biên dưới)', () => {
    it('hợp lệ và phân tích thành công', async () => {
      await expect(validate(ReviewCodeDto, { ...validReview, source_code: 'a'.repeat(10) })).resolves.toBeDefined();
      provider.generateJson.mockResolvedValue(validReviewData());
      const result = await ai.reviewCode(instructorId, { ...validReview, source_code: 'a'.repeat(10) } as ReviewCodeDto);
      expect((result.data as any).issue_summary).toBeDefined();
    });
  });

  describe('UT03_AiReviewCode_TC015: actual_output rỗng (biên)', () => {
    it('chuỗi rỗng hợp lệ và phân tích thành công', async () => {
      const body = { ...validReview, failed_testcase: { input: '1 2', expected_output: '3', actual_output: '' } };
      await expect(validate(ReviewCodeDto, body)).resolves.toBeDefined();
      provider.generateJson.mockResolvedValue(validReviewData());
      const result = await ai.reviewCode(instructorId, body as ReviewCodeDto);
      expect((result.data as any).bug_category).toBeDefined();
    });
  });

  // =========================================================================
  // PHẦN 4: POST /api/v1/ai/verify-plagiarism
  // =========================================================================

  const validPlagiarism = {
    student_a_code: 'for (int i = 0; i < n; i++) sum += a[i];',
    student_b_code: 'for (int j = 0; j < n; j++) total += arr[j];',
    ast_similarity_percentage: 85,
    language: 'C' as const,
  };

  function plagiarismData(overrides: Record<string, unknown> = {}) {
    return {
      data: {
        is_plagiarized: true,
        confidence_percentage: 92,
        evidence_summary: 'Structurally identical loops.',
        cloned_segments: [{ student_a_lines: '1-5', student_b_lines: '1-5', technique: 'rename' }],
        ...overrides,
      },
      tokensConsumed: 700,
    };
  }

  describe('UT03_AiVerifyPlagiarism_TC001: Không gửi Header Authorization', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT03_AiVerifyPlagiarism_TC002: ADMIN không có quyền', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForAdmin());
  });

  describe('UT03_AiVerifyPlagiarism_TC003: Giảng viên đã hết hạn ngạch', () => {
    it('trả 429 AI_QUOTA_EXCEEDED', async () => {
      provider.generateJson.mockRejectedValue(quotaExceeded());
      const error = await ai.verifyPlagiarism(instructorId, { ...validPlagiarism } as VerifyPlagiarismDto).catch((e) => e);
      expect((error.getResponse() as any).error_code).toBe('AI_QUOTA_EXCEEDED');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC004: Thiếu student_b_code', () => {
    it('trả 422 field student_b_code', async () => {
      const error = await validationError(VerifyPlagiarismDto, { ...validPlagiarism, student_b_code: undefined });
      expectValidationDetail(error, 'student_b_code', 'student_b_code must be a string');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC005: student_a_code dưới 10 ký tự', () => {
    it('trả 422 minLength', async () => {
      const error = await validationError(VerifyPlagiarismDto, { ...validPlagiarism, student_a_code: 'abc' });
      expectValidationDetail(error, 'student_a_code', 'student_a_code must be longer than or equal to 10 characters');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC006: student_a_code vượt 10000 ký tự', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(VerifyPlagiarismDto, { ...validPlagiarism, student_a_code: 'a'.repeat(10001) });
      expectValidationDetail(error, 'student_a_code', 'student_a_code must be shorter than or equal to 10000 characters');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC007: ast_similarity_percentage < 80', () => {
    it('trả 422 min', async () => {
      const error = await validationError(VerifyPlagiarismDto, { ...validPlagiarism, ast_similarity_percentage: 79.9 });
      expectValidationDetail(error, 'ast_similarity_percentage', 'ast_similarity_percentage must not be less than 80');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC008: ast_similarity_percentage > 100', () => {
    it('trả 422 max', async () => {
      const error = await validationError(VerifyPlagiarismDto, { ...validPlagiarism, ast_similarity_percentage: 100.1 });
      expectValidationDetail(error, 'ast_similarity_percentage', 'ast_similarity_percentage must not be greater than 100');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC009: Thiếu language', () => {
    it('trả 422 field language', async () => {
      const error = await validationError(VerifyPlagiarismDto, { student_a_code: validPlagiarism.student_a_code, student_b_code: validPlagiarism.student_b_code, ast_similarity_percentage: 85 });
      expectValidationField(error, 'language');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC010: Nhà cung cấp AI gặp sự cố kết nối', () => {
    it('trả 502 AI_PROVIDER_ERROR', async () => {
      provider.generateJson.mockRejectedValue(providerError());
      const error = await ai.verifyPlagiarism(instructorId, { ...validPlagiarism } as VerifyPlagiarismDto).catch((e) => e);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_PROVIDER_ERROR');
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC011: Xác thực thành công đạo văn tinh vi', () => {
    it('trả is_plagiarized và confidence', async () => {
      provider.generateJson.mockResolvedValue(plagiarismData());
      const result = await ai.verifyPlagiarism(instructorId, { ...validPlagiarism } as VerifyPlagiarismDto);
      expect(result.message).toBe('Phân tích bằng chứng đạo văn thành công');
      expect((result.data as any).is_plagiarized).toBe(true);
      expect((result.data as any).confidence_percentage).toBe(92);
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC012: Biên dưới 80% (trùng hợp ngẫu nhiên)', () => {
    it('hợp lệ và trả is_plagiarized false', async () => {
      await expect(validate(VerifyPlagiarismDto, { ...validPlagiarism, ast_similarity_percentage: 80 })).resolves.toBeDefined();
      provider.generateJson.mockResolvedValue(plagiarismData({ is_plagiarized: false, confidence_percentage: 30, evidence_summary: 'Common boilerplate.' }));
      const result = await ai.verifyPlagiarism(instructorId, { ...validPlagiarism, ast_similarity_percentage: 80 } as VerifyPlagiarismDto);
      expect((result.data as any).is_plagiarized).toBe(false);
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC013: Biên trên 100% (sao chép nguyên văn)', () => {
    it('hợp lệ và trả confidence 100', async () => {
      await expect(validate(VerifyPlagiarismDto, { ...validPlagiarism, ast_similarity_percentage: 100 })).resolves.toBeDefined();
      provider.generateJson.mockResolvedValue(plagiarismData({ confidence_percentage: 100 }));
      const result = await ai.verifyPlagiarism(instructorId, { ...validPlagiarism, ast_similarity_percentage: 100 } as VerifyPlagiarismDto);
      expect((result.data as any).confidence_percentage).toBe(100);
    });
  });

  describe('UT03_AiVerifyPlagiarism_TC014: Tách hàm con Java với cloned_segments rỗng', () => {
    it('mảng rỗng vẫn hợp lệ', async () => {
      provider.generateJson.mockResolvedValue(plagiarismData({ cloned_segments: [] }));
      const result = await ai.verifyPlagiarism(instructorId, { ...validPlagiarism, language: 'JAVA' } as VerifyPlagiarismDto);
      expect((result.data as any).cloned_segments).toEqual([]);
    });
  });

  // =========================================================================
  // PHẦN 5: POST /api/v1/ai/evaluate-web-ui
  // =========================================================================

  const pngBase64 = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 0]).toString('base64');
  const jpegBase64 = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 1, 2, 3, 4]).toString('base64');

  function evalData(criteria: string[], scores: number[], verdicts: string[], uiScore: number) {
    return {
      data: {
        ui_score: uiScore,
        evaluation_details: criteria.map((criterion, index) => ({ criterion, score: scores[index], verdict: verdicts[index], comment: `comment ${index}` })),
        overall_feedback: 'Overall feedback.',
      },
      tokensConsumed: 1500,
    };
  }

  describe('UT03_AiEvaluateWebUI_TC001: Không gửi Header Authorization', () => {
    it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
  });

  describe('UT03_AiEvaluateWebUI_TC002: ADMIN không có quyền', () => {
    it('trả 403 FORBIDDEN_ADMIN_ONLY', () => expectForbiddenForAdmin());
  });

  describe('UT03_AiEvaluateWebUI_TC003: Giảng viên đã hết hạn ngạch', () => {
    it('trả 429 AI_QUOTA_EXCEEDED', async () => {
      provider.generateJson.mockRejectedValue(quotaExceeded());
      const error = await ai.evaluateWebUi(instructorId, { screenshot_base64: pngBase64, rubric_requirements: ['Layout'] } as EvaluateWebUiDto).catch((e) => e);
      expect((error.getResponse() as any).error_code).toBe('AI_QUOTA_EXCEEDED');
    });
  });

  describe('UT03_AiEvaluateWebUI_TC004: Thiếu screenshot_base64', () => {
    it('trả 422 field screenshot_base64', async () => {
      const error = await validationError(EvaluateWebUiDto, { rubric_requirements: ['Layout'] });
      expectValidationDetail(error, 'screenshot_base64', 'screenshot_base64 must be a string');
    });
  });

  describe('UT03_AiEvaluateWebUI_TC005: screenshot_base64 không hợp lệ', () => {
    it('trả 400 AI_IMAGE_INVALID', async () => {
      const error = await ai.evaluateWebUi(instructorId, { screenshot_base64: 'not base64!!!', rubric_requirements: ['Layout'] } as EvaluateWebUiDto).catch((e) => e);
      expect(error.getStatus()).toBe(400);
      expect(error.getResponse()).toEqual({ error_code: 'AI_IMAGE_INVALID', message: 'Ảnh phải là dữ liệu PNG/JPEG base64 hợp lệ.', details: null });
    });
  });

  describe('UT03_AiEvaluateWebUI_TC006: Ảnh vượt quá 5MB (biên trên)', () => {
    it('trả 400 AI_IMAGE_INVALID kích thước', async () => {
      const bigBase64 = Buffer.alloc(5 * 1024 * 1024 + 1, 1).toString('base64');
      const error = await ai.evaluateWebUi(instructorId, { screenshot_base64: bigBase64, rubric_requirements: ['Layout'] } as EvaluateWebUiDto).catch((e) => e);
      expect(error.getStatus()).toBe(400);
      expect(error.getResponse()).toEqual({ error_code: 'AI_IMAGE_INVALID', message: 'Ảnh phải có kích thước tối đa 5 MB.', details: null });
    });
  });

  describe('UT03_AiEvaluateWebUI_TC007: Thiếu rubric_requirements', () => {
    it('trả 422 field rubric_requirements', async () => {
      const error = await validationError(EvaluateWebUiDto, { screenshot_base64: pngBase64 });
      expectValidationDetail(error, 'rubric_requirements', 'rubric_requirements must be an array');
    });
  });

  describe('UT03_AiEvaluateWebUI_TC008: rubric_requirements rỗng (biên dưới)', () => {
    it('trả 422 minItems', async () => {
      const error = await validationError(EvaluateWebUiDto, { screenshot_base64: pngBase64, rubric_requirements: [] });
      expectValidationDetail(error, 'rubric_requirements', 'rubric_requirements must contain at least 1 elements');
    });
  });

  describe('UT03_AiEvaluateWebUI_TC009: Nhà cung cấp AI Vision gặp sự cố', () => {
    it('trả 502 AI_PROVIDER_ERROR', async () => {
      provider.generateJson.mockRejectedValue(providerError());
      const error = await ai.evaluateWebUi(instructorId, { screenshot_base64: pngBase64, rubric_requirements: ['Layout'] } as EvaluateWebUiDto).catch((e) => e);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_PROVIDER_ERROR');
    });
  });

  describe('UT03_AiEvaluateWebUI_TC010: Đánh giá thành công với 3 tiêu chí', () => {
    it('tính ui_score trung bình = 8', async () => {
      const rubric = ['Layout', 'Color', 'Typography'];
      provider.generateJson.mockResolvedValue(evalData(rubric, [9, 8, 7], ['PASS', 'PASS', 'PARTIAL'], 8));
      const result = await ai.evaluateWebUi(instructorId, { screenshot_base64: pngBase64, rubric_requirements: rubric } as EvaluateWebUiDto);
      expect(result.message).toBe('Đánh giá giao diện Web bằng AI thành công');
      expect((result.data as any).ui_score).toBe(8);
    });
  });

  describe('UT03_AiEvaluateWebUI_TC011: Đánh giá thành công với 1 tiêu chí (biên dưới)', () => {
    it('ui_score bằng điểm tiêu chí duy nhất', async () => {
      const rubric = ['Layout'];
      provider.generateJson.mockResolvedValue(evalData(rubric, [6.5], ['PARTIAL'], 6.5));
      const result = await ai.evaluateWebUi(instructorId, { screenshot_base64: pngBase64, rubric_requirements: rubric } as EvaluateWebUiDto);
      expect((result.data as any).ui_score).toBe(6.5);
    });
  });

  describe('UT03_AiEvaluateWebUI_TC012: Đánh giá thành công với ảnh JPEG data URL', () => {
    it('chấp nhận JPEG và tính ui_score', async () => {
      const rubric = ['Layout', 'Color'];
      provider.generateJson.mockResolvedValue(evalData(rubric, [8, 9], ['PASS', 'PASS'], 8.5));
      const result = await ai.evaluateWebUi(instructorId, { screenshot_base64: `data:image/jpeg;base64,${jpegBase64}`, rubric_requirements: rubric } as EvaluateWebUiDto);
      expect((result.data as any).ui_score).toBe(8.5);
    });
  });

  describe('UT03_AiEvaluateWebUI_TC013: Bài làm vi phạm rubric (ui_score thấp)', () => {
    it('verdict FAIL và ui_score = 2', async () => {
      const rubric = ['Layout', 'Color', 'Typography'];
      provider.generateJson.mockResolvedValue(evalData(rubric, [2, 3, 1], ['FAIL', 'FAIL', 'FAIL'], 2));
      const result = await ai.evaluateWebUi(instructorId, { screenshot_base64: pngBase64, rubric_requirements: rubric } as EvaluateWebUiDto);
      expect((result.data as any).ui_score).toBe(2);
      expect((result.data as any).evaluation_details.every((d: any) => d.verdict === 'FAIL')).toBe(true);
    });
  });

  describe('UT03_AiEvaluateWebUI_TC014: rubric_requirements vượt 20 phần tử (biên trên)', () => {
    it('trả 422 maxItems', async () => {
      const rubric = Array.from({ length: 21 }, (_, i) => `Tiêu chí ${i + 1}`);
      const error = await validationError(EvaluateWebUiDto, { screenshot_base64: pngBase64, rubric_requirements: rubric });
      expectValidationDetail(error, 'rubric_requirements', 'rubric_requirements must contain no more than 20 elements');
    });
  });

  describe('UT03_AiEvaluateWebUI_TC015: phần tử rubric vượt 500 ký tự (biên trên)', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(EvaluateWebUiDto, { screenshot_base64: pngBase64, rubric_requirements: ['a'.repeat(501)] });
      expectValidationDetail(error, 'rubric_requirements', 'each value in rubric_requirements must be shorter than or equal to 500 characters');
    });
  });

  describe('UT03_AiEvaluateWebUI_TC016: screenshot_base64 vượt 7.000.000 ký tự (biên trên)', () => {
    it('trả 422 maxLength', async () => {
      const error = await validationError(EvaluateWebUiDto, { screenshot_base64: 'a'.repeat(7000001), rubric_requirements: ['Layout'] });
      expectValidationDetail(error, 'screenshot_base64', 'screenshot_base64 must be shorter than or equal to 7000000 characters');
    });
  });

  // =========================================================================
  // PHẦN 6: POST /api/v1/ai/evaluate-pe-code (UC-19 - RUBRIC CHẤT LƯỢNG MÃ PE)
  // =========================================================================

  const validPeCode = {
    source_code: 'int main(void){int a,b;scanf("%d %d",&a,&b);printf("%d\\n",a+b);return 0;}',
    language: 'C' as const,
    problem_statement: 'Tính tổng hai số nguyên.',
  };

  function peRubricData(overrides: Record<string, unknown> = {}) {
    return {
      data: {
        rubric: {
          clean_code: { passed: true, reason: 'Tên biến rõ nghĩa.' },
          complexity: { passed: true, reason: 'Độ phức tạp O(1).' },
          structure: { passed: false, reason: 'Toàn bộ logic nằm trong main.' },
          format: { passed: true, reason: 'Thụt lề chuẩn.' },
          documentation: { passed: false, reason: 'Thiếu comment giải thích.' },
        },
        overall_feedback: 'Cần tách hàm và thêm comment.',
        ...overrides,
      },
      tokensConsumed: 900,
    };
  }

  function invalidResponseError(): BadGatewayException {
    return new BadGatewayException({ error_code: 'AI_INVALID_RESPONSE', message: 'Dịch vụ AI trả về dữ liệu không đúng định dạng.', details: null });
  }

  describe('UT03_AiEvaluatePeCode_TC001: Chấm rubric PE thành công đủ 5 tiêu chí', () => {
    it('trả rubric, overall_feedback và tokens_consumed', async () => {
      provider.generateJson.mockResolvedValue(peRubricData());
      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);
      expect(result.message).toBe('Đánh giá chất lượng code PE thành công');
      expect((result.data as any).tokens_consumed).toBe(900);
      expect((result.data as any).rubric.clean_code).toEqual({ passed: true, reason: 'Tên biến rõ nghĩa.' });
      expect((result.data as any).rubric.structure.passed).toBe(false);
      expect((result.data as any).overall_feedback).toBe('Cần tách hàm và thêm comment.');
      expect(provider.generateJson).toHaveBeenCalledTimes(1);
    });
  });

  describe('UT03_AiEvaluatePeCode_TC002: Model bỏ sót overall_feedback nhưng rubric đủ 5 tiêu chí (Biên)', () => {
    it('vẫn dùng rubric và tự tổng hợp nhận xét thay vì báo sai định dạng', async () => {
      const payload = peRubricData();
      delete (payload.data as Record<string, unknown>).overall_feedback;
      provider.generateJson.mockResolvedValue(payload);

      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);

      expect((result.data as any).rubric.clean_code.passed).toBe(true);
      // Nhận xét được tổng hợp từ lý do của các tiêu chí chưa đạt.
      expect((result.data as any).overall_feedback).toContain('Toàn bộ logic nằm trong main.');
      expect((result.data as any).overall_feedback).toContain('Thiếu comment giải thích.');
      // Không cần gọi lại lần 2 vì rubric đã hợp lệ.
      expect(provider.generateJson).toHaveBeenCalledTimes(1);
    });
  });

  describe('UT03_AiEvaluatePeCode_TC003: Model bỏ sót overall_feedback và mọi tiêu chí đều đạt (Biên)', () => {
    it('dùng nhận xét mặc định khi không có tiêu chí nào chưa đạt', async () => {
      provider.generateJson.mockResolvedValue({
        data: {
          rubric: {
            clean_code: { passed: true, reason: 'ok' },
            complexity: { passed: true, reason: 'ok' },
            structure: { passed: true, reason: 'ok' },
            format: { passed: true, reason: 'ok' },
            documentation: { passed: true, reason: 'ok' },
          },
        },
        tokensConsumed: 500,
      });
      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);
      expect((result.data as any).overall_feedback).toBe('Đạt đầy đủ 5 tiêu chí chất lượng mã nguồn.');
    });
  });

  describe('UT03_AiEvaluatePeCode_TC004: Lượt 1 sai định dạng, lượt 2 hợp lệ (Retry)', () => {
    it('hướng dẫn lại prompt và trả kết quả của lượt 2', async () => {
      provider.generateJson
        .mockRejectedValueOnce(invalidResponseError())
        .mockResolvedValueOnce(peRubricData());

      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);

      expect(provider.generateJson).toHaveBeenCalledTimes(2);
      expect((result.data as any).tokens_consumed).toBe(900);
      const retryPrompt = provider.generateJson.mock.calls[1][0].prompt as string;
      expect(retryPrompt).toContain('overall_feedback');
      const firstPrompt = provider.generateJson.mock.calls[0][0].prompt as string;
      expect(firstPrompt).toContain('CẤU TRÚC JSON BẮT BUỘC');
      expect(firstPrompt).toContain('overall_feedback');
    });
  });

  describe('UT03_AiEvaluatePeCode_TC005: Cả 2 lượt đều sai định dạng (Exception)', () => {
    it('trả 502 AI_INVALID_RESPONSE', async () => {
      provider.generateJson.mockRejectedValue(invalidResponseError());
      const error = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto).catch((e) => e);
      expect(error).toBeInstanceOf(BadGatewayException);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_INVALID_RESPONSE');
      expect(provider.generateJson).toHaveBeenCalledTimes(2);
    });
  });

  describe('UT03_AiEvaluatePeCode_TC006: Provider trả JSON null (Exception)', () => {
    it('trả 502 AI_INVALID_RESPONSE chứ không phải 500 INTERNAL_SERVER_ERROR', async () => {
      provider.generateJson.mockResolvedValue({ data: null, tokensConsumed: 10 });
      const error = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto).catch((e) => e);
      expect(error).toBeInstanceOf(BadGatewayException);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_INVALID_RESPONSE');
      expect(provider.generateJson).toHaveBeenCalledTimes(2);
    });
  });

  describe('UT03_AiEvaluatePeCode_TC007: Rubric thiếu 1 tiêu chí (Exception)', () => {
    it('trả 502 AI_INVALID_RESPONSE sau khi đã retry', async () => {
      const payload = peRubricData();
      delete (payload.data.rubric as Record<string, unknown>).documentation;
      provider.generateJson.mockResolvedValue(payload);
      const error = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto).catch((e) => e);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_INVALID_RESPONSE');
    });
  });

  describe('UT03_AiEvaluatePeCode_TC008: Provider trả JSON mảng thay vì object (Exception)', () => {
    it('trả 502 AI_INVALID_RESPONSE', async () => {
      provider.generateJson.mockResolvedValue({ data: [1, 2, 3], tokensConsumed: 10 });
      const error = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto).catch((e) => e);
      expect(error.getStatus()).toBe(502);
      expect((error.getResponse() as any).error_code).toBe('AI_INVALID_RESPONSE');
    });
  });

  describe('UT03_AiEvaluatePeCode_TC009: Provider lỗi hạn ngạch (429) (Exception)', () => {
    it('giữ nguyên 429 AI_QUOTA_EXCEEDED, không retry', async () => {
      provider.generateJson.mockRejectedValue(quotaExceeded());
      const error = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto).catch((e) => e);
      expect(error.getStatus()).toBe(429);
      expect((error.getResponse() as any).error_code).toBe('AI_QUOTA_EXCEEDED');
      expect(provider.generateJson).toHaveBeenCalledTimes(1);
    });
  });

  describe('UT03_AiEvaluatePeCode_TC010: Model trả tên tiêu chí camelCase và passed dạng chuỗi (Biên)', () => {
    it('quy đổi cleanCode/PASS về đúng 5 tiêu chí', async () => {
      provider.generateJson.mockResolvedValue({
        data: {
          rubric: {
            cleanCode: { passed: 'PASS', reason: 'ok' },
            complexity: { passed: 'true', reason: 'ok' },
            structure: { passed: 'FAIL', reason: 'chưa tách hàm' },
            format: { passed: 'PASS', reason: 'ok' },
            documentation: { passed: 'false', reason: 'thiếu comment' },
          },
          overall_feedback: 'Cần tách hàm và thêm comment.',
        },
        tokensConsumed: 800,
      });

      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);

      const rubric = (result.data as any).rubric;
      expect(rubric.clean_code.passed).toBe(true);
      expect(rubric.structure.passed).toBe(false);
      expect(rubric.documentation.passed).toBe(false);
      expect(provider.generateJson).toHaveBeenCalledTimes(1);
    });
  });

  describe('UT03_AiEvaluatePeCode_TC011: Model bỏ lớp bao rubric, trả thẳng 5 tiêu chí (Biên)', () => {
    it('vẫn nhận diện được rubric ở cấp cao nhất', async () => {
      provider.generateJson.mockResolvedValue({
        data: {
          clean_code: { passed: true, reason: 'ok' },
          complexity: { passed: true, reason: 'ok' },
          structure: { passed: false, reason: 'gộp trong main' },
          format: { passed: true, reason: 'ok' },
          documentation: { passed: false, reason: 'thiếu comment' },
          overall_feedback: 'Cần tách hàm.',
        },
        tokensConsumed: 700,
      });

      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);

      expect((result.data as any).rubric.structure.passed).toBe(false);
      expect((result.data as any).overall_feedback).toBe('Cần tách hàm.');
    });
  });

  describe('UT03_AiEvaluatePeCode_TC012: Tiêu chí thiếu reason (Biên)', () => {
    it('vẫn tính passed và để reason rỗng thay vì báo sai định dạng', async () => {
      provider.generateJson.mockResolvedValue({
        data: {
          rubric: {
            clean_code: { passed: true },
            complexity: { passed: true },
            structure: { passed: true },
            format: { passed: true },
            documentation: { passed: true },
          },
        },
        tokensConsumed: 600,
      });

      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);

      expect((result.data as any).rubric.clean_code).toEqual({ passed: true, reason: '' });
      expect((result.data as any).overall_feedback).toBe('Đạt đầy đủ 5 tiêu chí chất lượng mã nguồn.');
    });
  });

  describe('UT03_AiEvaluatePeCode_TC013: Trường rubric bị trả dưới dạng chuỗi JSON (Biên)', () => {
    it('parse chuỗi đó rồi chấm bình thường', async () => {
      const rubricString = JSON.stringify({
        clean_code: { passed: true, reason: 'ok' },
        complexity: { passed: true, reason: 'ok' },
        structure: { passed: true, reason: 'ok' },
        format: { passed: true, reason: 'ok' },
        documentation: { passed: false, reason: 'thiếu comment' },
      });
      provider.generateJson.mockResolvedValue({
        data: { rubric: rubricString, overall_feedback: 'Thêm comment.' },
        tokensConsumed: 650,
      });

      const result = await ai.evaluatePeCode(instructorId, { ...validPeCode } as EvaluatePeCodeDto);

      expect((result.data as any).rubric.documentation.passed).toBe(false);
      expect((result.data as any).rubric.clean_code.passed).toBe(true);
    });
  });

  // =========================================================================
  // PHẦN 7: GET /api/v1/ai/provider-status
  // =========================================================================

  describe('UT03_AiProviderStatus (OpenRouterService.providerStatus)', () => {
    function makeProviderSvc(keys: string): OpenRouterService {
      const cfg = { get: jest.fn((key: string, def?: any) => (key === 'OPENROUTER_API_KEYS' ? keys : def)) } as unknown as ConfigService;
      return new OpenRouterService(cfg, {} as unknown as AiQuotaService);
    }

    describe('UT03_AiProviderStatus_TC001: Không gửi Header Authorization', () => {
      it('trả 401 AUTH_INVALID_TOKEN', () => expectUnauthorizedNoToken());
    });

    describe('UT03_AiProviderStatus_TC002: Bearer Token đã hết hạn', () => {
      it('trả 401 AUTH_TOKEN_EXPIRED', () => {
        const error = (() => {
          try {
            new JwtAuthGuard().handleRequest(null, false, { name: 'TokenExpiredError' });
          } catch (e) {
            return e;
          }
        })() as UnauthorizedException;
        expect(error.getStatus()).toBe(401);
        expect(error.getResponse()).toEqual({ error_code: 'AUTH_TOKEN_EXPIRED', message: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.', details: null });
      });
    });

    describe('UT03_AiProviderStatus_TC003: Giảng viên không có quyền xem trạng thái AI', () => {
      it('trả 403 FORBIDDEN_ADMIN_ONLY', () => {
        const reflector = { getAllAndOverride: jest.fn().mockReturnValue(['ADMIN']) } as unknown as Reflector;
        const context = {
          getHandler: () => ({}),
          getClass: () => ({}),
          switchToHttp: () => ({ getRequest: () => ({ user: { id: instructorId, username: 'gv', role: 'INSTRUCTOR' } }) }),
        } as any;
        const error = (() => {
          try {
            new RolesGuard(reflector).canActivate(context);
          } catch (e) {
            return e;
          }
        })() as any;
        expect(error.getStatus()).toBe(403);
        expect(error.getResponse()).toEqual({ error_code: 'FORBIDDEN_ADMIN_ONLY', message: 'Bạn không có quyền thực hiện thao tác này.', details: null });
      });
    });

    describe('UT03_AiProviderStatus_TC004: ADMIN lấy trạng thái AI Hub thành công', () => {
      it('trả danh sách key với state READY', () => {
        const svc = makeProviderSvc('key-a,key-b');
        const status = svc.providerStatus();
        expect(status.provider).toBe('openrouter');
        expect(status.accounts_configured).toBe(2);
        expect(status.structured_outputs_supported).toBe(true);
        expect(status.accounts.every((a) => a.state === 'READY' && a.cooldown_remaining_seconds === 0)).toBe(true);
      });
    });

    describe('UT03_AiProviderStatus_TC005: Trạng thái khi một key đang COOLDOWN (biên)', () => {
      it('báo COOLDOWN kèm số giây còn lại', () => {
        const svc = makeProviderSvc('key-a');
        (svc as any).cooldownUntil.set('key-a', Date.now() + 60_000);
        const status = svc.providerStatus();
        expect(status.accounts[0].state).toBe('COOLDOWN');
        expect(status.accounts[0].cooldown_remaining_seconds).toBeGreaterThan(0);
      });
    });
  });
});
