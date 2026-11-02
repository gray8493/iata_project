import { AiGatewayService } from '../modules/ai-gateway/ai-gateway.service';
import { OpenRouterService } from '../modules/ai-gateway/openrouter.service';

/**
 * Hồi quy: model suy luận (nemotron VL) dùng hết ngân sách token cho phần reasoning khi
 * max_tokens quá thấp, khiến content rỗng và trả AI_INVALID_RESPONSE (502).
 * Các chức năng dài phải có ngân sách tối thiểu 4000 token.
 */
describe('AI token budget regression', () => {
  const C_CODE = '#include <stdio.h>\nint main(){ int a,b; scanf("%d %d",&a,&b); printf("%d\n", a+b); return 0; }';
  const image = { mimeType: 'image/png', base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==' };
  const pngBase64 = `data:image/png;base64,${image.base64}`;

  let provider: { generateJson: jest.Mock };
  let ai: AiGatewayService;

  beforeEach(() => {
    provider = { generateJson: jest.fn().mockResolvedValue({ data: {}, tokensConsumed: 0 }) };
    ai = new AiGatewayService(provider as unknown as OpenRouterService);
  });

  it('evaluatePeCode dùng maxOutputTokens >= 4000', async () => {
    provider.generateJson.mockResolvedValue({ data: { rubric: {}, overall_feedback: 'x' }, tokensConsumed: 1 });
    await ai.evaluatePeCode('u1', { source_code: C_CODE, language: 'C', problem_statement: 'Tính tổng' } as any).catch(() => undefined);
    expect(provider.generateJson.mock.calls[0][0].maxOutputTokens).toBeGreaterThanOrEqual(4000);
  });

  it('verifyPlagiarism dùng maxOutputTokens >= 4000', async () => {
    await ai.verifyPlagiarism('u1', { student_a_code: C_CODE, student_b_code: C_CODE, ast_similarity_percentage: 90, language: 'C' } as any).catch(() => undefined);
    expect(provider.generateJson.mock.calls[0][0].maxOutputTokens).toBeGreaterThanOrEqual(4000);
  });

  it('evaluateWebUi dùng maxOutputTokens >= 4000', async () => {
    await ai.evaluateWebUi('u1', { screenshot_base64: pngBase64, rubric_requirements: ['Bố cục'] } as any).catch(() => undefined);
    expect(provider.generateJson.mock.calls[0][0].maxOutputTokens).toBeGreaterThanOrEqual(4000);
  });
});
