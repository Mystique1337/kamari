# Kámárí Setup Guide

How to run and deploy Kámárí, tier by tier. **None of this needs the training datasets**
except the very last step (real age numbers from the Modal CNN). Do the tiers in order;
stop wherever you have enough.

```
Tier 0  App on mock ........... 0 setup, runs today
Tier 1  App ↔ local gateway ... no accounts
Tier 2  Postgres + pgvector ... your self-hosted DB (+ app-owned auth)
Tier 3  Railway (gateway live) . Railway account
Tier 4  Modal (real models) ... Modal account + a trained model (needs datasets)
Tier 5  Native Android/iOS .... Android Studio / Xcode
```

---

## Tier 0 — Run the app (mock)

```bash
cd apps/kamari_app
npm install
npm run dev            # http://localhost:5173
```
The app ships a realistic mock of the age API, so the full flow works with no backend.
Use it from your laptop browser, or your phone on the same network with `npm run dev -- --host`.

---

## Tier 1 — App ↔ local gateway (no accounts)

Run the real FastAPI gateway (it has its own mock for the ML calls, so it works without
any model) and point the app at it. This exercises the real API contract + policy engine.

**1. Start the gateway**
```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000      # docs at http://localhost:8000/docs
```

**2. Point the app at it** — create `apps/kamari_app/.env.local`:
```
VITE_KAMARI_API_URL=http://localhost:8000
VITE_USE_MOCK=0
```
Restart `npm run dev`. The Developer screen will now show **API mode: live**, and every
age check is a real HTTP call to the gateway.

---

## Tier 2 — Postgres + pgvector (self-hosted)

Plain self-hosted Postgres with pgvector — **Supabase is no longer required**. Everything
lives in a dedicated `kamari` schema, so it can share an existing database.

**1. Apply the schema** (creates schema `kamari`, `pgcrypto` + `vector` extensions, tables):
```bash
psql "postgresql://USER:PASSWORD@HOST:5432/DBNAME" -f infra/postgres/schema.sql
```

**2. Give the gateway a connection** (direct Postgres). Set in the gateway env:
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
SUPABASE_DB_SCHEMA=kamari
```
The gateway logs request **metadata only** (decision, model version, request id) to
`kamari.inference_requests` — never the image. *(Write-path wiring is the next increment;
the schema + env are ready now.)*

**3. Auth** — since Supabase Auth is gone, the gateway owns authentication. Recommended:
`fastapi-users` (JWT over `kamari.app_users`, argon2 passwords) for humans, plus the
existing hashed API keys for machines. `pgvector` powers 1:1 face verification later.

> Because you connect with a privileged role, the gateway enforces org-scoping in code.
> RLS policies in `schema.sql` are defense-in-depth for any anon/direct access.

---

## Tier 3 — Railway (deploy the gateway)

Railway hosts the **gateway only** (no GPU). The `Dockerfile` + `railway.json` already
live in `apps/api`.

**Option A — Dashboard (easiest)**
1. railway.app → **New Project → Deploy from GitHub repo** → pick `Mystique1337/kamari`.
2. In the service **Settings → Root Directory**, set `apps/api`.
3. Railway auto-detects the Dockerfile. **Variables** → add:
   ```
   MODAL_AGE_ENDPOINT=        (leave empty for now → gateway uses its mock)
   MODAL_GEMMA_ENDPOINT=
   DATABASE_URL=postgresql://...        (from Tier 2)
   SUPABASE_DB_SCHEMA=kamari
   API_KEY_PEPPER=<random-long-string>
   REQUIRE_API_KEY=false
   RETENTION_DEFAULT=image_not_stored
   ```
4. Deploy. Health check is wired to `/v1/health`. You get a public URL like
   `https://kamari-api-prod.up.railway.app`.

**Option B — CLI**
```bash
npm i -g @railway/cli
railway login
cd apps/api && railway init && railway up
```

**Then point the app at the deployed gateway** — in `apps/kamari_app/.env.local` (or your
host's env): `VITE_KAMARI_API_URL=https://<your-railway-url>`.

---

## Tier 4 — Modal (real models)

Authorize now; the **serving endpoints only return real numbers once a model is trained**
(which needs your datasets).

```bash
pip install modal
modal setup                         # opens browser to authorize

# one secret holds HF + (optional) W&B creds:
modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=Mystique1337 WANDB_API_KEY=... WANDB_PROJECT=kamari
```

Train (after the data notebook has published `kamari-faces-v0`):
```bash
modal run services/modal_age/train_cnn.py --epochs 20
modal run services/modal_gemma/train_gemma.py --epochs 3
```

Deploy serving (gives you the URLs):
```bash
modal deploy services/modal_age/serve_cnn.py     # -> MODAL_AGE_ENDPOINT
modal deploy services/modal_gemma/serve_gemma.py # -> MODAL_GEMMA_ENDPOINT
```
Set those two URLs in the gateway env (Railway variables) → the gateway stops mocking and
returns real estimates. Nothing else in the app changes.

---

## Tier 5 — Native Android / iOS (optional)

```bash
cd apps/kamari_app
npm run build
npx cap add android        # needs Android Studio
npx cap add ios            # needs macOS + Xcode
npx cap sync
npx cap open android       # or: npx cap open ios
```
Camera permission is already handled in code (front camera, never saved). iOS App Store
builds require macOS + Xcode.

---

## "Fully live" checklist
```
[ ] Data notebook run → kamari-faces-v0 on HF
[ ] CNN trained + serve_cnn deployed → MODAL_AGE_ENDPOINT
[ ] (optional) Gemma trained + serve_gemma deployed → MODAL_GEMMA_ENDPOINT
[ ] Gateway on Railway with the two Modal URLs + DATABASE_URL
[ ] App VITE_KAMARI_API_URL → Railway URL, VITE_USE_MOCK=0
[ ] kamari schema applied to self-hosted Postgres
```
