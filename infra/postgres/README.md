# Kámárí - Postgres (self-hosted, with pgvector)

Kámárí uses a plain self-hosted **Postgres + pgvector** (Supabase is no longer required).
Everything lives in a dedicated `kamari` schema, so it can share an existing database.

## Apply
```bash
psql "$DATABASE_URL" -f infra/postgres/schema.sql
```
Creates schema `kamari`, the `pgcrypto` + `vector` extensions, all tables, and a pgvector
index on `face_embeddings`.

## Connect the gateway
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
SUPABASE_DB_SCHEMA=kamari        # (env name kept; it's just the schema)
```

## Auth
Since Supabase Auth is gone, the gateway owns authentication:
- **Humans** (developer dashboard): email + password in `kamari.app_users`
  (`hashed_password` = argon2) issuing JWTs. Recommended via `fastapi-users`.
- **Machines** (API product): hashed API keys in `kamari.api_keys` (sha256 + pepper) -
  already in `apps/api/app/security/api_keys.py`.

## pgvector / verification
`kamari.face_embeddings` stores opt-in face embeddings (`vector(512)`) for **1:1
verification only** - never 1:N search; queries must be scoped to `subject_ref`.
Embeddings are not stored by default and should be encrypted at rest.

## Privacy
Only request **metadata** is stored (decision, reason code, model version, request id) -
never raw images. See `inference_requests.retention_policy`.

Full setup flow: `docs/SETUP.md` (Tier 2).
