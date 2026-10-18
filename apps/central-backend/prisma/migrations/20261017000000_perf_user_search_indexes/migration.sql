-- Performance indexes for admin user listing and search.

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE INDEX "idx_users_role_created" ON "users"("role", "created_at" DESC, "id");

CREATE INDEX "idx_users_full_name_trgm" ON "users" USING GIN ("full_name" gin_trgm_ops);
CREATE INDEX "idx_users_email_trgm" ON "users" USING GIN ("email" gin_trgm_ops);
CREATE INDEX "idx_users_username_trgm" ON "users" USING GIN ("username" gin_trgm_ops);
