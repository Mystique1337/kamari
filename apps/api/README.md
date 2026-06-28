# Kámárí API Gateway

FastAPI orchestration gateway. Validates requests, runs the **policy/decision engine**,
calls the Modal CNN + Gemma endpoints, and returns the app contract. No heavy ML here;
no raw images stored. Deployed on Railway.

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
| POST | `/v1/age/estimate` | image → CNN → policy → (Gemma) message |
| POST | `/v1/age/explain` | re-render explanation for a known decision |
| POST | `/v1/auth/jwt/login`, `/v1/auth/register`, `/v1/users/me` | human auth (fastapi-users JWT) — **mounts only when `DATABASE_URL` is set** |

Humans authenticate via fastapi-users JWT over Postgres (`kamari.app_users`, argon2);
machines use hashed API keys. Set `JWT_SECRET` + `DATABASE_URL` to enable auth.

## Env (see infra/railway)
`MODAL_AGE_ENDPOINT`, `MODAL_GEMMA_ENDPOINT`, `SUPABASE_URL`,
`SUPABASE_SERVICE_ROLE_KEY`, `API_KEY_PEPPER`, `REQUIRE_API_KEY`, `RETENTION_DEFAULT`.

## Policy engine (`app/policy.py`, plan §10.4)
Conservative near the boundary — borderline cases are never auto-approved. Decision codes
come from the fixed enum (§21); the same rules seed the Gemma SFT data.

## Test
```bash
cd apps/api && pip install -r requirements.txt pytest && PYTHONPATH=. pytest -q
```

## Wire the app
Set the app's `VITE_KAMARI_API_URL` to this gateway's URL and `VITE_USE_MOCK=0`.
