# Kámárí — Supabase (self-hosted, sub-schema)

Kámárí does **not** need its own Supabase project. It lives in a dedicated `kamari`
sub-schema inside your existing self-hosted Postgres.

## Apply
```bash
psql "$DATABASE_URL" -f infra/supabase/schema.sql
```
This creates schema `kamari` and all tables (organizations, app_users, api_keys,
model_versions, inference_requests, age_decisions, verification_sessions, benchmark_runs,
benchmark_metrics, audit_events, feedback, n8n_events).

## Connect the gateway
The gateway connects directly to Postgres (no PostgREST schema exposure required):
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
SUPABASE_DB_SCHEMA=kamari
```

## Privacy
Only request **metadata** is stored (decision, reason code, model version, request id) —
never raw images or embeddings. See `inference_requests.retention_policy`.

Full setup flow: `docs/SETUP.md` (Tier 2).
