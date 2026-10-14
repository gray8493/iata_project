CREATE TABLE "users" (
    "id" UUID NOT NULL,
    "username" VARCHAR(50) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "full_name" VARCHAR(100) NOT NULL,
    "email" VARCHAR(120) NOT NULL,
    "role" VARCHAR(20) NOT NULL DEFAULT 'INSTRUCTOR',
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "is_deleted" BOOLEAN NOT NULL DEFAULT false,
    "deleted_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ai_quota_configs" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "daily_token_limit" INTEGER NOT NULL DEFAULT 50000,
    "used_tokens_today" INTEGER NOT NULL DEFAULT 0,
    "last_reset_date" DATE NOT NULL DEFAULT CURRENT_DATE,
    "is_deleted" BOOLEAN NOT NULL DEFAULT false,
    "deleted_at" TIMESTAMPTZ(6),
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "ai_quota_configs_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "ai_quota_logs" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "feature_type" VARCHAR(30) NOT NULL,
    "model_name" VARCHAR(50) NOT NULL DEFAULT 'gemini-3.8-flash',
    "prompt_tokens" INTEGER NOT NULL DEFAULT 0,
    "completion_tokens" INTEGER NOT NULL DEFAULT 0,
    "total_tokens" INTEGER NOT NULL DEFAULT 0,
    "is_deleted" BOOLEAN NOT NULL DEFAULT false,
    "deleted_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "ai_quota_logs_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "refresh_tokens" (
    "id" UUID NOT NULL,
    "token_hash" CHAR(64) NOT NULL,
    "user_id" UUID NOT NULL,
    "expires_at" TIMESTAMPTZ(6) NOT NULL,
    "revoked_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "users_username_key" ON "users"("username");
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");
CREATE INDEX "idx_users_role" ON "users"("role");
CREATE UNIQUE INDEX "ai_quota_configs_user_id_key" ON "ai_quota_configs"("user_id");
CREATE INDEX "idx_ai_quota_logs_user_created" ON "ai_quota_logs"("user_id", "created_at");
CREATE INDEX "idx_ai_quota_logs_created_feature" ON "ai_quota_logs"("created_at", "feature_type");
CREATE UNIQUE INDEX "refresh_tokens_token_hash_key" ON "refresh_tokens"("token_hash");
CREATE INDEX "idx_refresh_tokens_user_expires" ON "refresh_tokens"("user_id", "expires_at");

ALTER TABLE "ai_quota_configs" ADD CONSTRAINT "ai_quota_configs_user_id_fkey"
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "ai_quota_logs" ADD CONSTRAINT "ai_quota_logs_user_id_fkey"
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "refresh_tokens" ADD CONSTRAINT "refresh_tokens_user_id_fkey"
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
