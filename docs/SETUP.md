# Kámárí Setup Guide

How to run and deploy Kámárí, tier by tier. Do the tiers in order; stop wherever you have enough.

```
Tier 0  App on mock ........... 0 setup, runs today
Tier 1  App <-> local gateway . no accounts
Tier 2  Supabase (auth + data)  GoTrue + REST, public schema
Tier 3  Modal (real models) ... Modal account + trained model
Tier 4  Railway (deploy) ...... web + API, custom domains
Tier 5  Android APK ........... GitHub Actions artifact
```

---

## Tier 0 - Run the app (mock)
```bash
cd apps/kamari_app
npm install
npm run dev            # http://localhost:5173
```
The app ships a realistic mock of the age API, so the full flow works with no backend.

---

## Tier 1 - App and local gateway (no accounts)
Run the FastAPI gateway (it has its own mock for the ML calls) and point the app at it.

```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000      # docs at http://localhost:8000/docs
```
Create `apps/kamari_app/.env.local`:
```
VITE_KAMARI_API_URL=http://localhost:8000
VITE_USE_MOCK=0
```
The Developer screen shows API mode: live, and every age check is a real call to the gateway.

---

## Tier 2 - Supabase (auth + data)
Kámárí uses Supabase **GoTrue** for human auth and Supabase **REST** for data, on the **public**
schema (PostgREST exposes it by default, so no reconfiguration).

1. In the Supabase SQL editor, run **`infra/postgres/schema_public.sql`** (creates
   `organizations`, `api_keys`, `inference_requests` and grants `service_role`).
2. Set on the gateway (see `apps/api/.env.example`):
   ```
   SUPABASE_URL=...
   SUPABASE_SERVICE_ROLE_KEY=...
   SUPABASE_ANON_KEY=...
   SUPABASE_JWT_SECRET=...        # verifies GoTrue access tokens
   SUPABASE_DB_SCHEMA=public
   ```
3. Set on the app build: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
4. If you want signups usable immediately, set `GOTRUE_MAILER_AUTOCONFIRM=true` (or disable "Enable
   email confirmations") on the auth service, since Kámárí sends its own welcome email via n8n.

The gateway logs request metadata only (decision, model version, request id, organization), never
the image. See `infra/postgres/README.md` for the optional dedicated-`kamari`-schema variant and
`pgvector` for future 1:1 verification.

---

## Tier 3 - Modal (real models)
```bash
pip install modal
modal setup                         # authorize in browser
modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=Shinzmann WANDB_API_KEY=... WANDB_PROJECT=kamari
```
Train (after the data notebook has published `kamari-faces-v0`), then deploy serving:
```bash
modal run    services/modal_age/train_cnn.py
modal run    services/modal_gemma/train_gemma.py --n 8000
modal deploy services/modal_age/serve_cnn.py     # -> MODAL_AGE_ENDPOINT
modal deploy services/modal_gemma/serve_gemma.py # -> MODAL_GEMMA_ENDPOINT
```
Both serve always-on (`min_containers=1`). Set the two URLs in the gateway env.

---

## Tier 4 - Railway (deploy web + API)
Two services in one project, each built from its Dockerfile.

```bash
npm i -g @railway/cli && railway login
railway init --name kamari
railway add --service api && railway add --service web
# set variables (see apps/api/.env.example for api; VITE_* for web), then:
cd apps/api        && railway up --service api --ci
cd apps/kamari_app && railway up --service web --ci
railway domain --service api    # and --service web, to generate URLs
```
Custom domains in production: web `kamari.shinzii.tech`, api `kamari-api.shinzii.tech`. Set the web
build var `VITE_KAMARI_API_URL` to the API URL and `APP_PUBLIC_URL` on the api to the web URL.

CI/CD: `.github/workflows/` runs tests + app build, auto-deploys to Railway (set repo secret
`RAILWAY_TOKEN`), and builds the Android APK.

---

## Tier 5 - Android APK
The Capacitor `android/` project is committed. CI builds the APK:
- Push to `main` or run Actions -> Build Android APK -> Run workflow.
- Download `kamari-android-debug` from the run's Artifacts.
- Set repo secrets `VITE_KAMARI_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` for a live
  build. Locally (with Android Studio): `npm run build && npx cap sync android && npx cap open android`.

---

## Fully live checklist
```
[x] Data notebook run -> kamari-faces-v0 on HF
[x] CNN trained + serve_cnn deployed -> MODAL_AGE_ENDPOINT
[x] Gemma trained + serve_gemma deployed -> MODAL_GEMMA_ENDPOINT
[x] Supabase schema_public.sql applied; GoTrue + REST configured
[x] Gateway + web on Railway with custom domains
[x] App VITE_KAMARI_API_URL -> API domain, VITE_USE_MOCK=0
```
