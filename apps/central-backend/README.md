# AITA Central Backend

Central REST API for authentication, account administration, AI quota and Gemini services, and audit reporting. The implementation follows the NestJS + Prisma + PostgreSQL stack in `docs/architecture/tech-stack.md`.

## Requirements

- Node.js 20 or newer
- PostgreSQL 14 or newer

## Local setup

1. Install dependencies with `npm install`.
2. Copy `.env.example` to `.env`; set `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, and two different random JWT secrets of at least 32 characters. Neon uses the pooled URL (`DATABASE_URL`) for application traffic and the direct URL (`DATABASE_URL_UNPOOLED`) for Prisma migrations.
3. Create the PostgreSQL database named in `DATABASE_URL`.
4. Run `npm run db:generate` and `npm run db:deploy`.
5. Set `BOOTSTRAP_ADMIN_USERNAME`, `BOOTSTRAP_ADMIN_PASSWORD` (at least 12 characters), `BOOTSTRAP_ADMIN_FULL_NAME`, and `BOOTSTRAP_ADMIN_EMAIL`, then run `npm run db:seed` once to create the first Admin.
6. Start the development server with `npm run start:dev`.

The API is served under `/api/v1`. Swagger UI is available at `/api/docs`.
The browser-based Web Admin origin is controlled by the comma-separated `WEB_ADMIN_ORIGINS` setting; local development defaults to `http://localhost:3001`. Readiness can be checked at `GET /api/v1/health` (PostgreSQL and configured Redis storage).

Rate limits: authenticated non-AI routes allow 80 requests/minute per user; AI generation routes allow 15 requests/minute per user. Login is limited to 10/minute and refresh to 30/minute per client IP. Set `REDIS_URL` for shared rate-limit storage; it is required in production and optional in local development (which falls back to in-memory storage). Set `TRUST_PROXY_HOPS` to the number of trusted reverse proxies in front of the API so IP-based limits use the client IP safely.

## Implemented endpoints

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`
- `GET|POST /api/v1/admin/users`
- `GET|PUT|DELETE /api/v1/admin/users/:id`
- `GET /api/v1/ai/quota`
- `POST /api/v1/ai/generate-testcases`
- `POST /api/v1/ai/review-code`
- `POST /api/v1/ai/verify-plagiarism`
- `POST /api/v1/ai/evaluate-web-ui`
- `GET /api/v1/admin/reports/overview`
- `GET /api/v1/admin/reports/ai-usage`

Refresh tokens are stored as SHA-256 hashes and rotated on use. The one-time bootstrap command never prints or stores the supplied password and refuses to run when an active Admin already exists. Public sign-up is intentionally not provided by the API contract.

## Database changes

Update `prisma/schema.prisma`, then create and review a migration before deployment. Production deployments should run `npm run db:deploy`; do not use `prisma db push` against production.

For Neon, run `neon deploy` from the repository root to provision the declared services and pull the branch variables. Then run `neon env pull --file apps/central-backend/.env` so NestJS and Prisma can read the connection URLs from the backend package directory. Both root `.env.local` and backend `.env` are ignored by Git.
