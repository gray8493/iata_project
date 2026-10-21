import { HttpException, UnprocessableEntityException } from '@nestjs/common';
import { AiGatewayService } from '../modules/ai-gateway/ai-gateway.service';
import { OpenRouterService } from '../modules/ai-gateway/openrouter.service';
import { AiQuotaService } from '../modules/ai-gateway/ai-quota.service';
import { GenerateTestcasesDto } from '../modules/ai-gateway/dto/generate-testcases.dto';
import { VerifyPlagiarismDto } from '../modules/ai-gateway/dto/verify-plagiarism.dto';
import { createValidationPipe } from '../common/validation/validation-pipe.factory';

describe('System (docs: docs/testcases/3-system/system-test-specification.md)', () => {
  let provider: { generateJson: jest.Mock };
  let ai: AiGatewayService;

  beforeEach(() => {
    provider = { generateJson: jest.fn() };
    ai = new AiGatewayService(provider as unknown as OpenRouterService);
  });

  afterEach(() => jest.clearAllMocks());

  async function validate(metatype: any, value: unknown): Promise<unknown> {
    return createValidationPipe().transform(value, { type: 'body', metatype, data: '' } as any);
  }

  describe('ST02_AITestcaseGen_TC001: Sinh bộ testcase bằng AI OpenRouter thành công', () => {
    it('trả về đúng số lượng testcase hợp lệ và token tiêu thụ', async () => {
      const testcases = [
        { input: '-5', expected_output: 'NO', explanation: 'số âm', is_boundary: true },
        { input: '2', expected_output: 'YES', explanation: 'số nguyên tố chẵn', is_boundary: true },
        { input: '1000000', expected_output: 'NO', explanation: 'giá trị cực đại', is_boundary: true },
      ];
      provider.generateJson.mockResolvedValue({ data: { testcases }, tokensConsumed: 1234 });

      const result = await ai.generateTestcases('u1', { problem_description: 'Viết chương trình kiểm tra số nguyên tố N', language: 'C', count: 3, include_boundary: true } as any);

      expect(result.message).toBe('Sinh testcase tự động bằng AI thành công');
      expect(result.data.tokens_consumed).toBe(1234);
      expect(result.data.testcases).toHaveLength(3);
      expect(provider.generateJson).toHaveBeenCalledWith(expect.objectContaining({ feature: 'TESTCASE_GEN', userId: 'u1' }));
    });
  });

  describe('ST02_AITestcaseGen_TC002: Chặn khi hết hạn ngạch AI trong ngày', () => {
    it('ném 429 AI_QUOTA_EXCEEDED và không gọi nhà cung cấp', async () => {
      const quota = {
        reserve: jest.fn().mockRejectedValue(new HttpException({ error_code: 'AI_QUOTA_EXCEEDED', message: 'Tài khoản của bạn đã sử dụng hết hạn ngạch Token AI trong ngày.', details: null }, 429)),
        release: jest.fn(),
        settle: jest.fn(),
      };
      const aiConfig = { get: jest.fn((key: string, def?: string) => (key === 'OPENROUTER_API_KEYS' ? 'test-key' : def)), getOrThrow: jest.fn() };
      const service = new OpenRouterService(aiConfig as any, quota as unknown as AiQuotaService);

      const error = await service.generateJson({ userId: 'u1', feature: 'TESTCASE_GEN', prompt: 'p'.repeat(40), schema: {} as any, maxOutputTokens: 100 }).catch((e) => e);

      expect(error).toBeInstanceOf(HttpException);
      expect(error.getStatus()).toBe(429);
      expect(error.getResponse()).toEqual(expect.objectContaining({ error_code: 'AI_QUOTA_EXCEEDED' }));
    });
  });

  describe('ST03_PlagiarismVong2_TC001: AI phân tích ngữ nghĩa cặp bài nghi vấn (Vòng 2)', () => {
    it('trả về bằng chứng sao chép đúng cấu trúc', async () => {
      provider.generateJson.mockResolvedValue({
        data: {
          ket_luan: 'Hai bài có dấu hiệu tương đồng về cấu trúc.',
          do_tin_cay: 86,
          bang_chung: [{ mo_ta: 'Cùng cấu trúc xử lý.', dong_a: [1, 1], dong_b: [1, 1] }],
          khac_biet: ['Tên biến khác nhau.'],
          de_xuat: ['Trao đổi với sinh viên về cách xây dựng lời giải.'],
        },
        tokensConsumed: 900,
      });

      const result = await ai.verifyPlagiarism('u1', { student_a_code: 'a'.repeat(20), student_b_code: 'b'.repeat(20), ast_similarity_percentage: 86, language: 'C' } as any);

      expect(result.message).toBe('Đối soát đạo văn bằng AI hoàn tất');
      expect(result.data.tokens_consumed).toBe(900);
      expect((result.data as any).do_tin_cay).toBe(86);
      expect((result.data as any).bang_chung).toHaveLength(1);
    });
  });

  describe('ST03_PlagiarismVong2_TC002: Giá trị biên ngưỡng tương đồng AST', () => {
    const base = { student_a_code: 'a'.repeat(20), student_b_code: 'b'.repeat(20), language: 'C' };

    it('80 và 100 hợp lệ, 79 bị từ chối 422', async () => {
      await expect(validate(VerifyPlagiarismDto, { ...base, ast_similarity_percentage: 80 })).resolves.toBeDefined();
      await expect(validate(VerifyPlagiarismDto, { ...base, ast_similarity_percentage: 100 })).resolves.toBeDefined();

      const error = (await validate(VerifyPlagiarismDto, { ...base, ast_similarity_percentage: 79 }).catch((e) => e)) as any;
      expect(error).toBeInstanceOf(UnprocessableEntityException);
      const body = error.getResponse() as any;
      expect(body.error_code).toBe('VALIDATION_FAILED');
      expect(body.details.some((d: any) => d.field === 'ast_similarity_percentage')).toBe(true);
    });
  });
});
