# Kámárí App

Web-first, mobile-style age-verification client. One Ionic React + TypeScript codebase →
web, PWA, Android, and iOS (via Capacitor). Themed as an African product: **Adire indigo**
base with terracotta / gold / palm-green accents and Adinkra-inspired motifs.

## Run

```bash
npm install
cp .env.example .env.local   # leave VITE_KAMARI_API_URL empty to use the mock
npm run dev                  # http://localhost:5173
```

The app ships with a **realistic mock** of `POST /v1/age/estimate`, so the whole flow -
Welcome → Consent → Camera → Result - works today. When the ML side is ready, set
`VITE_KAMARI_API_URL` to the Railway gateway URL and `VITE_USE_MOCK=0`; nothing else changes.

## Screens (MVP)
`Welcome` · `Consent` (privacy/retention) · `CameraCapture` (web `getUserMedia` / native
Capacitor camera) · `AgeResult` (handles allow / block / secondary_check / recapture) ·
`DeveloperDashboard` · `ApiKeys`.

## Architecture
- `src/lib/api.ts` - the single API seam (mock ↔ live gateway). Validates responses with Zod.
- `src/lib/types.ts` - API contract types/enums, kept in sync with `apps/api` and the plan §20/§21.
- `src/lib/camera.ts` - web frame capture + native Capacitor selfie (front camera, never saved).
- `src/lib/state.tsx` - in-memory flow state; the selfie is never persisted (privacy posture).
- `src/theme/` - design tokens (`variables.css`) + Adinkra pattern system (`kamari.css`).

## PWA / native
- PWA: configured via `vite-plugin-pwa` (`npm run build` emits the manifest + service worker).
- Native: `npx cap add android` / `npx cap add ios`, then `npm run build && npx cap sync`.
  iOS App Store builds require macOS + Xcode.

## Privacy
Photo is processed once and never stored; only the decision + model version are kept
server-side. Every result is framed as an estimate, not a legal age determination.
