# Kámárí App

![Ionic React](https://img.shields.io/badge/Ionic-React-3880FF?logo=ionic&logoColor=white) ![Capacitor](https://img.shields.io/badge/Capacitor-119EFF?logo=capacitor&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) [![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](../../LICENSE)

*Part of the [Kámárí](../../README.md) monorepo.*

Web-first, mobile-style age-verification client. One Ionic React + TypeScript codebase ships
to web, PWA, and Android (iOS too, via Capacitor). Themed as an African product: **Adire indigo**
base with terracotta / gold / palm-green accents and Adinkra-inspired motifs. No em dashes in copy.

## Run

```bash
npm install
cp .env.example .env.local   # leave VITE_KAMARI_API_URL empty to use the mock
npm run dev                  # http://localhost:5173
```

The app ships with a **realistic mock** of `POST /v1/age/estimate`, so the whole consumer flow
(Welcome, Consent, Camera, Result) works offline. To go live, set in `.env.local`:

```
VITE_KAMARI_API_URL=https://<your-gateway>.up.railway.app
VITE_USE_MOCK=0
VITE_SUPABASE_URL=https://<your-supabase-host>
VITE_SUPABASE_ANON_KEY=<anon key>
```

## Features
- **Consumer age check:** Welcome, Consent (with language + country picker), live selfie capture,
  and a Result screen handling allow / block / secondary_check / recapture.
- **Languages:** picker drives the in-language decision message (Gemma is multilingual). Pan-African
  set: English, Nigerian Pidgin, French, Swahili, Yoruba, Hausa, Igbo, Zulu, Amharic.
- **Liveness secondary check:** on-device motion challenge so a printed photo or a still screen
  cannot pass the borderline (13 to 21) case. No video is stored.
- **Guardian consent flow:** for likely-minors, email a one time code to a guardian (via n8n) and
  verify it to approve. The same page also handles the link a guardian opens from their inbox.
- **Developer portal (Supabase GoTrue auth):** sign in / sign up, manage live API keys, and see
  org-scoped usage (totals, allow rate, decision mix) and recent request logs.

Live at **https://kamari.shinzii.tech** (API at `https://kamari-api.shinzii.tech`).

## Screens
`Welcome` · `Consent` · `CameraCapture` · `AgeResult` · `SecondaryCheck` · `GuardianConsent` ·
`Login` · `DeveloperDashboard` · `ApiKeys` · `UsageLogs` · `Pricing` · `Docs`.

The developer area shows the current plan and monthly-quota usage; `Pricing` lists the tiers with
demo switching; `Docs` is an in-app API reference with curl / JavaScript / Python examples.

## Architecture
- `src/lib/api.ts` - the single API seam (mock or live gateway). Validates responses with Zod.
- `src/lib/auth.tsx` - Supabase GoTrue session context (sign in/up/out, access token).
- `src/lib/supabase.ts` - shared Supabase client (from `VITE_SUPABASE_*`).
- `src/lib/i18n.ts` - language + country lists and a small UI string table with English fallback.
- `src/lib/state.tsx` - in-memory flow state (consent, locale, last result). The selfie is never persisted.
- `src/theme/` - design tokens (`variables.css`) + Adinkra pattern system (`kamari.css`).

## PWA
`npm run build` emits the manifest + service worker (`vite-plugin-pwa`). Installable on any device.

## Android APK (downloadable)
The native project lives in `android/` (Capacitor). Building an APK needs the Android SDK, so CI
does it for you:

- Push to `main` (or run **Actions → Build Android APK → Run workflow**).
- Download the APK from the run's **Artifacts** (`kamari-android-debug`), then install it.
- For a live build, set repo secrets `VITE_KAMARI_API_URL`, `VITE_SUPABASE_URL`,
  `VITE_SUPABASE_ANON_KEY` (without them the APK runs in mock mode).

Locally (with Android Studio installed): `npm run build && npx cap sync android && npx cap open android`.

## Deploy (Railway)
`Dockerfile` builds the bundle and serves it with nginx (SPA fallback so deep links work). Set the
`VITE_*` build variables on the Railway service. The FastAPI gateway deploys from `apps/api`.

## Privacy
The photo is processed once and never stored; only the decision + model version are kept
server-side. Every result is framed as an estimate, not a legal age determination.
