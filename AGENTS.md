\


# AGENTS.md

AITA — desktop tool for instructors to auto-grade C/Java/Python (and web) student submissions, plus a central admin backend. This repo is a course deliverable (SWD392); `docs/` and `rules/` are in Vietnamese and are graded artifacts. Keep that language in docs; code identifiers/comments mix English + Vietnamese.

## Monorepo layout

- `apps/desktop-client` — PyQt6/Python grader. Implemented. Entry `main.py`; all code under `src/`.
- `apps/central-backend` — NestJS 10 + Prisma 5 + PostgreSQL REST API. Implemented.
- `apps/web-admin` — Next.js 14 admin SPA (Tailwind, port 3001). Implemented. Backend base URL comes from `NEXT_PUBLIC_API_URL` (inlined at build; see `apps/web-admin/.env.example`, fallback `http://localhost:3000/api/v1` only in dev).
- `docs/` — architecture, OpenAPI specs (`docs/apis/*.yaml`), testcases, PlantUML diagrams.
- `rules/` — mandatory Git branch rules and testcase ID/format rules (authoritative).
- `tests/` — pytest root chia theo level: `unit/` (pure logic), `integration/` (dịch vụ + HTTP mock), `system/` (Qt offscreen), `acceptance/` (luồng nghiệp vụ), `e2e/` (toolchain thật GCC/JDK/Python, tự skip nếu thiếu), `performance/` (ngân sách thời gian), `fixtures/` (bài nộp mẫu). Các test mới gắn marker `unit|integration|system|acceptance|e2e|performance` (đăng ký trong `pytest.ini`). `apps/desktop-client/tests/` — pytest root thứ hai (20+ module test dịch vụ/lõi).
- `submissions/`, `data/`, `*.db`, `results.csv` — generated/fixture data, gitignored. `AITA.spec` is gitignored by `*.spec` and must be force-added if changed.

## Desktop client (Python 3.11)

- **Import root is `apps/desktop-client/src`**: modules use `from core...`, `from ui...`, `from services...`, `from database...`. `python apps/desktop-client/main.py` works (`main.py` prepends `src` to `sys.path`). For pytest/pyright run with `PYTHONPATH=apps/desktop-client/src` (both `pyrightconfig.json` files already add that extra path).
- Run: `python apps/desktop-client/main.py`
- Deps: `pip install -r apps/desktop-client/requirements.txt`
- Tests: `python -m pytest tests/ apps/desktop-client/tests/ -v` (`pytest.ini` sets `-p no:cacheprovider`). Chạy theo level: `python -m pytest tests/e2e -m e2e`; hoặc `test.bat` chạy tuần tự 6 nhóm và xuất JUnit + coverage vào `reports/`.

## Central backend (`apps/central-backend`, Node 20)

- `npm install` then `npm run db:generate` and `npm run db:deploy` (use `db:migrate` for new migrations).
- `npm run db:seed` is a one-time admin bootstrap: needs `BOOTSTRAP_ADMIN_USERNAME/PASSWORD/FULL_NAME/EMAIL` and refuses to run if an active Admin exists.
- `npm run start:dev` → API at `http://localhost:3000/api/v1`, Swagger at `/api/docs`.
- Test `npm test`; build `npm run build`. No lint script / no ESLint config exists (CI calls `npm run lint --if-present`, a no-op).
- `.env` is Joi-validated and required to boot: `DATABASE_URL`, both JWT secrets ≥32 chars. Copy `.env.example`.
- Prisma uses pooled `DATABASE_URL` for app traffic and direct `DATABASE_URL_UNPOOLED` for migrations. Never `prisma db push` against production.

## Neon DB

- `neon deploy` from repo root (config in `neon.ts`), then `neon env pull --file apps/central-backend/.env`. Neon skills are installed under `.agents/skills/`.

## CI (`.github/workflows/ci.yml`, on push/PR to `master`)

- flake8 limited to critical errors `E9,F63,F7,F82` (excludes venv/node_modules/build/dist); `python -m compileall apps tests`; OpenAPI YAML parse; backend `lint/test/build --if-present`; web-admin `npm ci`/`lint`/`build` on `apps/web-admin`; desktop client chạy 2 job pytest: `desktop-client-test-ubuntu` (unit+integration nhanh trên ubuntu-latest) và `desktop-client-ci` (full suite trên windows-latest: Qt offscreen, GCC + JDK 17 qua setup-java, coverage + JUnit XML upload artifact `reports/`).

## Conventions

- **Never commit to `master`.** Branch names are lowercase, hyphen-separated, ASCII: `docs-<api>-<name>`, `code-<feature>-<name>`, `test-<unit|integration|system|acceptance|e2e|perf>-<name>`; then open a PR. See `rules/git-rules.md`.
- Testcase IDs: `<UT|IT|ST|AT><NN>_<ModulePascalCase>_TC<nnn>`; each level needs Normal/Boundary/Exception cases. Format and template in `rules/testcase-rules.md` and `docs/testcases/`. Rules chưa định nghĩa prefix cho level e2e/performance — các test đó dùng `E2E<NN>` / `PF<NN>` theo cùng khuôn mẫu.
- Exactly 3 design patterns are graded and live in `apps/desktop-client/src/core/`: RunnerFactory (Factory, `factories/`), matching strategies (Strategy, `strategies/`), CompilerAdapter (Adapter, expected in `adapters/` — currently empty). Keep `docs/architecture/design-patterns.md` in sync when touching these.

## Domain facts

- Input CSV `students.csv` = 2 columns `MSSV,File`; output `results.csv` = 7 columns (adds score, passed/testcase, verdict, avg time, AI comment).
- Verdicts: `AC, WA, TLE, MLE, CE, RE`.
- Grading is black-box: run the student's `main()` with stdin and diff stdout. Do not wrap or rewrite student code.
- Local SQLite DB at `apps/desktop-client/data/local_grading.db` (created by `database/db_manager.py`, WAL mode).
- The AI API key stays server-side only. Desktop client resolves backend via `AITA_BACKEND_URL`, else probes localhost:3000, else `https://iata-project-o4z6.onrender.com/api/v1`. Backend CORS origins are configured via `CORS_ORIGINS` env var (comma-separated, default `http://localhost:3001`).
