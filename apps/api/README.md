# Kámárí API Gateway

![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) ![Railway](https://img.shields.io/badge/deploy-Railway-0B0D0E?logo=railway&logoColor=white) [![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](../../LICENSE)

*Part of the [Kámárí](../../README.md) monorepo.*

FastAPI orchestration gateway. Validates requests, runs the **policy/decision engine**,
calls the Modal CNN + Gemma endpoints, and returns the app contract. No heavy ML here;
no raw images stored. Deployed on Railway at **https://kamari-api.shinzii.tech**.

## Run
```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000/docs
```
Runs standalone with a **built-in mock** when `MODAL_AGE_ENDPOINT` is unset, so the app
can call it live without the models. Set the Modal URLs to go fully live.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/health` | status + which endpoints are configured |
| GET | `/v1/models` | model registry summary |
| POST | `/v1/age/estimate` | image → CNN → policy → (Gemma) message; org-scoped logging |
| POST | `/v1/age/explain` | re-render explanation for a known decision |
| GET | `/v1/me` | current user (GoTrue) |
| POST/GET/DELETE | `/v1/keys` | API key create / list / revoke (emails on create + revoke) |
| GET | `/v1/usage/summary`, `/v1/usage/logs` | org-scoped usage analytics |
| POST | `/v1/account/welcome` | send the welcome email after signup (public, rate-limited) |
| GET | `/v1/account/plans` | public pricing catalogue |
| GET/POST | `/v1/account/plan` | current plan + usage / switch plan (demo) |
| POST | `/v1/guardian/request`, `/v1/guardian/verify`, `GET /v1/guardian/status/{id}` | guardian consent (public) |

Humans authenticate via **Supabase GoTrue** JWTs, which the gateway verifies with the project
JWT secret (`SUPABASE_JWT_SECRET`); data goes through Supabase REST. Machines use hashed API keys.
The auth-protected routes mount only when `SUPABASE_JWT_SECRET` is set.

## Email (n8n)
Transactional email is delivered by the live n8n "Dynamic Email Template Sender" workflow. The
gateway POSTs `{template, variables}` with the `EMAIL_SECRET` header; templates live in
`app/email_templates.py` (welcome, API key created/revoked, guardian consent). Best effort: a mail
failure never breaks a request.

## Env
See **`.env.example`**. Key vars: `MODAL_AGE_ENDPOINT`, `MODAL_GEMMA_ENDPOINT`, `SUPABASE_URL`,
`SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`, `SUPABASE_DB_SCHEMA`,
`API_KEY_PEPPER`, `REQUIRE_API_KEY`, `N8N_EMAIL_WEBHOOK_URL`, `N8N_EMAIL_HEADER_NAME`,
`N8N_EMAIL_HEADER_SECRET`, `APP_PUBLIC_URL`, `RETENTION_DEFAULT`.

## Pricing tiers (demo, enforced)
Plans Free / Growth / Scale (`app/plans.py`) set a per-minute rate limit and a monthly quota.
`app/billing.py` enforces both on keyed requests (429 on exceed) and resolves the plan from the org
owner's Supabase user metadata. Switching plans is a demo (no payment); wire a provider into
`POST /v1/account/plan` to charge.

## Database
Run `infra/postgres/schema_public.sql` (public schema, no PostgREST reconfig). The dedicated-schema
variant `schema.sql` is optional. Set `SUPABASE_DB_SCHEMA` to match (default `public`).

## Policy engine (`app/policy.py`, plan §10.4)
Conservative near the boundary - borderline cases are never auto-approved. Decision codes
come from the fixed enum (§21); the same rules seed the Gemma SFT data.

## Test
```bash
cd apps/api && pip install -r requirements.txt pytest && PYTHONPATH=. pytest -q
```

## Wire the app
Set the app's `VITE_KAMARI_API_URL` to this gateway's URL and `VITE_USE_MOCK=0`.
