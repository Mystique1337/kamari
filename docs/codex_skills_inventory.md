# Codex Skills Inventory

Date checked: 2026-06-28

Source plan: `kamari_web_first_master_plan (2).md`

This document tracks the Codex skills installed for the Kamari web-first build and the project skill areas that still need normal engineering work rather than a Codex skill install.

## Installed Codex Skills

Installed into `~/.codex/skills` from the curated `openai/skills` repository:

| Skill | Project use |
| --- | --- |
| `playwright` | Validate the Ionic React/PWA app across desktop and mobile viewports, test camera/result flows where browser automation is possible. |
| `playwright-interactive` | Debug interactive frontend behavior during app integration and manual browser checks. |
| `screenshot` | Capture and inspect UI states for frontend quality review. |
| `jupyter-notebook` | Support dataset exploration, benchmark analysis, model experiment notebooks, and report generation. |
| `gh-fix-ci` | Diagnose and fix GitHub Actions failures for app, API, model, and benchmark workflows. |
| `gh-address-comments` | Help address GitHub review comments cleanly during feature work. |
| `security-best-practices` | Review auth, API keys, secrets, retention, and privacy-sensitive implementation choices. |
| `security-threat-model` | Threat-model biometric age-gating, 1:1 verification, liveness checks, and minor-data handling. |
| `security-ownership-map` | Track ownership boundaries for app, API, ML services, data, infra, and operations. |

## Skill Areas From The Master Plan

These are the main engineering skill areas required by the plan:

| Area | Required skills |
| --- | --- |
| Frontend | Ionic React, TypeScript, Vite, Capacitor, PWA/service worker setup, browser camera APIs, responsive mobile UI, API integration, React Query, Zod, Supabase client usage. |
| API/backend | FastAPI, Pydantic schemas, multipart uploads, Railway deployment, Supabase auth/RLS/API keys, Modal integration, n8n webhooks, rate limiting, structured errors, audit logging. |
| ML/CV | PyTorch CNN training, face detection/alignment, age regression/classification, uncertainty calibration, ONNX/TFLite export, benchmark metrics, liveness and 1:1 verification evaluation. |
| LLM/Gemma | LoRA/QLoRA fine-tuning, structured SFT JSONL, JSON-schema-constrained output, multilingual policy explanations, hallucination/policy evals. |
| Data/benchmarking | Dataset adapters, manifest validation, Parquet/YAML, license tracking, dataset cards, benchmark cards, subgroup reporting. |
| DevOps | GitHub Actions, versioned releases, Docker, Railway, Modal, Supabase self-hosting, secrets management, n8n workflow exports. |
| Security/privacy | No default face image storage, no default embedding storage, consent flows, retention visibility, auditability, conservative age-gating policy. |

## Relevant Gaps

No curated Codex skill was found for these plan-specific technologies, so they remain normal implementation and documentation responsibilities:

- Ionic React
- Capacitor
- Vite PWA plugin
- FastAPI
- Railway
- Supabase
- Modal
- n8n
- Hugging Face model and dataset cards
- PyTorch / ONNX / TFLite
- Gemma LoRA tuning

## Available But Not Installed

The curated list also included skills that do not match the current master plan or duplicate already available connector/system capabilities:

- Non-plan deployment targets: `cloudflare-deploy`, `netlify-deploy`, `render-deploy`, `vercel-deploy`
- Unused application stacks: `aspnet-core`, `winui-app`, `chatgpt-apps`
- Design-only Figma skills: `figma`, `figma-use`, `figma-implement-design`, `figma-generate-design`, `figma-generate-library`, `figma-create-new-file`, `figma-code-connect-components`, `figma-create-design-system-rules`
- Project-management connectors already available through installed plugins or not requested for this repo: `notion-*`, `linear`
- Other non-core skills: `cli-creator`, `define-goal`, `migrate-to-codex`, `pdf`, `sentry`, `speech`, `transcribe`

## Notes

- The upstream experimental skills path `skills/.experimental` was checked but was not available.
- Restart Codex to pick up newly installed skills.
