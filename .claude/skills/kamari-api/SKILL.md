---
name: kamari-api
description: Build and modify the Kámárí FastAPI gateway in apps/api. Use for API routes, schemas, API-key auth, rate limiting, the policy/decision engine, and Modal/Supabase/n8n client integration. Deployed on Railway.
---

# Kámárí API Gateway (FastAPI on Railway)

Railway hosts the **orchestration gateway only** — never the GPU models. Heavy inference and training live on Modal.

## Stack
FastAPI (async) · Pydantic v2 · httpx · Docker · Railway. Layout per §5:
`app/main.py`, `app/routes/{health,age,explain,verification,liveness,sessions,feedback}.py`, `app/clients/{supabase_client,modal_client,n8n_client}.py`, `app/schemas/{age,verification,liveness}.py`, `app/security/{api_keys,rate_limit}.py`.

## Endpoints (§10.2)
```
GET  /v1/health        GET  /v1/models
POST /v1/age/estimate  POST /v1/age/explain
POST /v1/face/verify   POST /v1/liveness/check
POST /v1/sessions      GET  /v1/sessions/{id}
POST /v1/feedback      POST /v1/webhooks/n8n/report-ready
```

## Age estimate contract (§20) — do not drift
Request: `multipart/form-data` with `image`, `language`, `country`, `Authorization: Bearer`.
Response keys: `request_id, model_version, estimated_age, age_band, p_under_18, uncertainty, face_quality, decision, reason_code, message, retention`.

## Policy/decision engine (§10.4) — be conservative near the boundary
```
quality < min            -> RECAPTURE_LOW_QUALITY
p_under_18 >= block       -> BLOCK_LIKELY_MINOR / secondary
estimated_age < challenge -> SECONDARY_CHECK_NEAR_THRESHOLD
uncertainty > threshold   -> SECONDARY_CHECK_LOW_CONFIDENCE
else                      -> ALLOW
```
Never auto-approve borderline cases. Decision codes come from the **fixed list** (§21): `ALLOW, BLOCK_LIKELY_MINOR, SECONDARY_CHECK_NEAR_THRESHOLD, SECONDARY_CHECK_LOW_CONFIDENCE, RECAPTURE_LOW_QUALITY, RECAPTURE_NO_FACE, RECAPTURE_MULTIPLE_FACES, ERROR_UNSUPPORTED_IMAGE`.

## Hard rules
- **Every response carries a `request_id`**; errors are structured.
- **Retention defaults to `no_store`** — never persist raw images/embeddings by default; log only metadata to Supabase `inference_requests`.
- API-key auth: hash keys with `API_KEY_PEPPER`; enforce scopes + per-key rate limits.
- ML calls go to Modal endpoints via `clients/modal_client.py` with graceful fallback errors on cold start/timeout.
- Env vars (§14.3): `SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY, MODAL_AGE_ENDPOINT, MODAL_GEMMA_ENDPOINT, N8N_WEBHOOK_SECRET, API_KEY_PEPPER, RETENTION_DEFAULT=no_store`.

## Acceptance (§10.5): OpenAPI docs, API-key auth, rate limiting, Supabase logging, Modal CNN+Gemma integrated, no-store default, request IDs, structured errors, Postman collection, Railway prod deploy.
