# Kámárí

African-focused, privacy-first **age verification**. A user takes a selfie, Kámárí returns a
calibrated age decision and a clear, multilingual message. The photo is processed once and never
stored. Open source under **Apache-2.0**, with a managed API you can pay for by usage.

**Live:** web app at **https://kamari.shinzii.tech**, API at **https://kamari-api.shinzii.tech**.

## How it works
A small calibrated **CNN** makes the age-gate signal (estimated age, probability under-18,
uncertainty), a **policy engine** turns that into a decision, and a fine-tuned **Gemma** model
writes the human, in-language explanation as strict JSON. A FastAPI gateway orchestrates it; an
Ionic React + Capacitor client ships to web, PWA, and Android.

```
Selfie ─▶ CNN (age, p<18, uncertainty, quality)
            └─▶ Policy engine ─▶ decision (allow | secondary_check | block | recapture)
                                   └─▶ Gemma ─▶ strict-JSON, in-language message
```

## Decisions
| Decision | Meaning |
|---|---|
| `allow` | Age requirement met. |
| `secondary_check` | Borderline (near 18 to 21) or low confidence. Run liveness or a guardian check. |
| `block` | Likely under age. Hand off to the guardian consent flow. |
| `recapture` | No clear face or poor quality. Ask for a new photo. |

## Repository layout
```
apps/api          FastAPI gateway (Railway): policy, auth, keys, usage, pricing, email
apps/kamari_app   Ionic React + Capacitor client (web, PWA, Android)
services/modal_age    CNN training + CPU serving on Modal
services/modal_gemma  Gemma QLoRA training + GPU serving on Modal
notebooks         One Colab notebook: gather, clean, EDA, publish datasets to Hugging Face
data, training    Dataset registry/adapters, manifest schema, SFT builder
infra             Postgres schema (Supabase), n8n workflow export, Railway notes
docs              Master plan, setup, model cards, methodology
```

## Results (v0)

**CNN age model** (`tf_efficientnetv2_s`, 30 epochs on H200, held-out benchmark n=8,322):

| Metric | Value |
|---|---|
| MAE | **6.03 years** |
| MPTR@18 (minors passed as adults) | 0.317 |
| MPTR@18, dark + brown skin | 0.383 |
| MPTR@21 | 0.27 |
| Adult-block rate (adults wrongly blocked) | 0.01 |
| MAE by skin: dark / light | 6.58 / 5.72 |
| GPU eval latency p50 / p95 | 14.2 ms / 14.3 ms |

MAE is strong; MPTR@18 is still high, so **the CNN is not a standalone gate**. The policy engine
(conservative near the 18 to 21 boundary), uncertainty routing, liveness, and the guardian flow
provide the safety margin. Lowering MPTR needs more 13 to 17 and African-labelled data. The safety
headline is **Minor-Pass-Through Rate**, weighted 5x in model selection.

**Gemma explanation model** (`gemma-4-E4B-it`, QLoRA r=32, 3 epochs): produces strict-JSON,
in-language messages and never estimates age. The deployed model is verified returning valid JSON
live; the v0 offline eval ran through a decoding path affected by a Gemma 4 `generate()` bug and is
not representative (a corrected eval is pending). See `services/modal_gemma/README.md`.

## Dataset and benchmark (Kámárí-Safe Open v0)
Built from open, license-checked face datasets with an auto label-quality gate, MTCNN face crops,
skin-tone (ITA) banding, and a leakage-free split. Composition: ~480,828 kept rows; 24,753 exact-age
training rows; African-signal slice 10,182; 13 to 21 boundary slice 3,139. Full methodology in
[`docs/methodology.md`](docs/methodology.md). Artifacts on Hugging Face (namespace `Shinzmann`).

## Trained artifacts (Hugging Face)
| Artifact | Repo |
|---|---|
| CNN age model (weights, ONNX, reports) | `Shinzmann/cnn-age-v0` |
| Gemma explanation LoRA | `Shinzmann/gemma-explain-lora-v0` |
| Benchmark (Kámárí-Safe Open v0) | `Shinzmann/kamari-safe-open-v0` |
| Dataset registry / provenance | `Shinzmann/dataset-registry-v0` |
| Training faces (private) | `Shinzmann/kamari-faces-v0` |

## Where things run
| Workstream | Runs on |
|---|---|
| Data gather / clean / EDA / publish | Google Colab, then Hugging Face |
| CNN + Gemma training | Modal (H200) |
| CNN serving | Modal CPU, always-on, OpenCV face detect + crop |
| Gemma serving | Modal GPU L4, always-on |
| Web app + API gateway | Railway (custom domains) |
| Android APK | GitHub Actions artifact |
| Auth + data | Supabase (GoTrue + REST, public schema) |
| Email | n8n (welcome, API key, guardian) |

## Platform features
- Consumer age check with language + country picker (English, Pidgin, French, Swahili, Yoruba,
  Hausa, Igbo, Zulu, Amharic), on-device liveness, and a guardian consent flow.
- Developer portal: login, API keys, usage and logs, and pricing tiers (Free / Growth / Scale) with
  enforced rate limits and monthly quotas (demo billing, no payment yet).
- Developer docs with curl / JavaScript / Python examples at `/docs`.

## Privacy posture
No raw face images or embeddings stored by default. Metadata and audit logs only, with retention
visible in the API and UI. Verification is 1:1 only, never 1:N face search. Every age result is an
estimate, not a legal determination.

## Setup and deploy
- [`docs/SETUP.md`](docs/SETUP.md) — local run, Supabase, Modal, Railway, native build.
- [`docs/master_plan.md`](docs/master_plan.md) — the web-first product plan.
- CI/CD: GitHub Actions run tests + app build, build the Android APK, and auto-deploy to Railway
  (set `RAILWAY_TOKEN`).

## Contributing
Apache-2.0. Commit feature by feature. Keep relevant READMEs current after any major change. House
style: no em dashes anywhere.
