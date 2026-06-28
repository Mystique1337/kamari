---
name: kamari-frontend
description: Build and modify the Kámárí web/PWA/mobile client. Use for any work in apps/kamari_app - Ionic React + TypeScript + Capacitor + Vite PWA, camera capture, consent/result screens, API client, i18n.
---

# Kámárí Frontend (Ionic React + Capacitor + PWA)

One codebase ships as web app, installable PWA, Android, and iOS. Do **not** introduce Flutter or a second frontend framework.

## Stack (locked by master plan §11)
- Vite + React + TypeScript (`react-ts` template)
- `@ionic/react`, `@ionic/react-router`, `ionicons`
- `@capacitor/core`, `@capacitor/cli`, `@capacitor/android`, `@capacitor/ios`, `@capacitor/camera`, `@capacitor/preferences`, `@capacitor/filesystem`
- `@supabase/supabase-js` (auth), `@tanstack/react-query` (data), `zod` (validation)
- `vite-plugin-pwa` (service worker / offline shell), `react-router-dom`
- App id: `com.kamari.app`, name `Kamari`

## Directory contract
`src/pages/`, `src/components/`, `src/lib/{api.ts,supabase.ts,validators.ts,camera.ts}`, `src/routes.tsx`, `capacitor.config.ts`, `vite.config.ts`.

## MVP screens (build these first)
Welcome → Consent/privacy → CameraCapture → AgeResult → DeveloperDashboard → ApiKeys. Defer Login, Liveness, SecondaryCheck, UsageLogs, Settings, LanguageSelector.

## Rules
- **Camera**: browser `getUserMedia` for web/PWA; `@capacitor/camera` on native. Abstract behind `lib/camera.ts`.
- **API**: all calls go through `lib/api.ts` to the Railway gateway; validate every response with `zod` against the `/v1/age/estimate` contract (§20). Always surface `request_id`, `model_version`, and `retention`.
- **Result screen** must handle all decisions: `allow / block / secondary_check / recapture`.
- **Privacy copy is mandatory** on consent + result screens - show retention (`image_not_stored` by default).
- **Tokens** stored via `@capacitor/preferences` on native (never localStorage on native).
- **i18n** (later): en, sw, yo, ha, am, fr, ar - Arabic needs RTL handling.

## Build / sync
```bash
npm run build && npx cap sync
npx cap open android   # Android Studio
npx cap open ios       # Xcode (macOS only - required for App Store)
```

## Acceptance (§11.8): web build, PWA install, Android build, iOS project, camera, consent screen, age-endpoint integration, all decision states, API-key dashboard, visible privacy copy.
