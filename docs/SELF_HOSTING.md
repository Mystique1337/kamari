# Self-hosting Kamari

Run the whole Kamari age gate on your own infrastructure with Docker. No GPU required: the CNN age
model runs on CPU from the public Hugging Face weights, and the explanation layer falls back to
approved template messages when no Gemma endpoint is configured.

```
web (PWA, nginx)  ->  api (FastAPI gateway)  ->  cnn (CPU age model, from Hugging Face)
                                              ->  gemma (optional, your GPU/Modal endpoint)
```

## Quick start
```bash
git clone https://github.com/Mystique1337/kamari
cd kamari/infra/docker
docker compose up --build
# open http://localhost:8080  (gateway on http://localhost:8000)
```
That brings up three containers and a working consumer age check. First boot downloads the CNN
weights (~100 MB) from Hugging Face.

## What runs
| Service | Image | Notes |
|---|---|---|
| `cnn` | `services/selfhost_cnn` | EfficientNetV2-S `best.pt` from `Shinzmann/cnn-age-v0`, OpenCV face detect + crop, CPU. Endpoint `POST /estimate`. |
| `api` | `apps/api` | The gateway: policy engine, decisions, optional auth/keys/usage/email. Points `MODAL_AGE_ENDPOINT` at `cnn`. |
| `web` | `apps/kamari_app` | The PWA, served by nginx. |

## Optional pieces (all off by default)
Copy `infra/docker/.env.example` to `.env` and fill in what you want, then `docker compose up`:
- **Gemma explanations** - set `MODAL_GEMMA_ENDPOINT` to a Gemma serving URL (e.g. your own
  `modal deploy services/modal_gemma/serve_gemma.py`). Without it, the gateway returns approved
  multilingual template messages, so the product still works with no GPU.
- **Developer portal + logging + pricing** - set the `SUPABASE_*` and `VITE_SUPABASE_*` vars and run
  `infra/postgres/schema_public.sql` in your Supabase project. Without Supabase, the consumer age
  check works; only the developer portal is disabled.
- **Email** - set `N8N_EMAIL_*` to use your own n8n "Dynamic Email Template Sender" workflow.
- **API keys / rate limits** - set `REQUIRE_API_KEY=true` to require a key on `/v1/age/estimate`.

## Use your own models
- CNN: the container pulls `Shinzmann/cnn-age-v0`. To serve your own, set `CNN_HF_REPO` (and
  `CNN_BACKBONE` if different) on the `cnn` service.
- Gemma: deploy `services/modal_gemma/serve_gemma.py` (or any endpoint matching the request schema in
  `services/modal_gemma/README.md`) and set `MODAL_GEMMA_ENDPOINT`.

## Without Docker
- Gateway: `cd apps/api && pip install -r requirements.txt && uvicorn app.main:app --port 8000`.
- CNN: `cd services/selfhost_cnn && pip install -r requirements.txt && uvicorn cnn_server:app --port 8001`,
  then set `MODAL_AGE_ENDPOINT=http://localhost:8001/estimate` on the gateway.
- Web: `cd apps/kamari_app && VITE_KAMARI_API_URL=http://localhost:8000 npm run build` and serve `dist/`.

## Point the app at your gateway
Set the web build variable `VITE_KAMARI_API_URL` to your gateway URL (and `VITE_USE_MOCK=0`). The
installed Android app can be rebuilt the same way (see `apps/kamari_app/README.md`).

## Privacy and licensing
Selfies are processed in memory and never stored; only decision metadata is logged (and only if you
enable Supabase). The code is Apache-2.0. The CNN weights and benchmark are on Hugging Face; the raw
training faces are not redistributed. Kamari returns an estimate, not a legal age determination.
