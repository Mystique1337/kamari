import { AgeEstimateResponse, type EstimateOptions } from './types';

// The base URL of the Kamari gateway (Railway), which calls the Modal CNN/Gemma endpoints.
// While empty (or VITE_USE_MOCK=1) a realistic mock is used so the flow is demoable offline.
const API_URL = (import.meta.env.VITE_KAMARI_API_URL as string | undefined)?.replace(/\/$/, '');
const USE_MOCK = import.meta.env.VITE_USE_MOCK === '1' || !API_URL;

export const apiMode = USE_MOCK ? 'mock' : 'live';
export const apiBase = API_URL ?? '';

function dataUrlToBlob(dataUrl: string): Blob {
  const [head, b64] = dataUrl.split(',');
  const mime = /data:(.*?);/.exec(head)?.[1] ?? 'image/jpeg';
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new Blob([bytes], { type: mime });
}

function authHeaders(token?: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ---------------- consumer age check ----------------
/** POST /v1/age/estimate. Multipart image upload. Returns a validated response. */
export async function estimateAge(
  imageDataUrl: string,
  opts: EstimateOptions = {},
): Promise<AgeEstimateResponse> {
  if (USE_MOCK) return mockEstimate();

  const form = new FormData();
  form.append('image', dataUrlToBlob(imageDataUrl), 'selfie.jpg');
  form.append('language', opts.language ?? 'en');
  form.append('country', opts.country ?? 'NG');

  const res = await fetch(`${API_URL}/v1/age/estimate`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(`Age estimate failed (${res.status})`);
  return AgeEstimateResponse.parse(await res.json());
}

// ---------------- developer: API keys ----------------
export interface ApiKeyRow {
  id: string; name: string; status: string;
  rate_limit_per_minute: number; created_at: string; last_used_at: string | null;
}

export async function listKeys(token: string): Promise<ApiKeyRow[]> {
  const res = await fetch(`${API_URL}/v1/keys`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(`Could not load keys (${res.status})`);
  return res.json();
}

export async function createKey(token: string, name: string): Promise<{ name: string; api_key: string }> {
  const res = await fetch(`${API_URL}/v1/keys?name=${encodeURIComponent(name)}`, {
    method: 'POST', headers: authHeaders(token),
  });
  if (!res.ok) throw new Error(`Could not create key (${res.status})`);
  return res.json();
}

export async function revokeKey(token: string, id: string): Promise<void> {
  const res = await fetch(`${API_URL}/v1/keys/${id}`, { method: 'DELETE', headers: authHeaders(token) });
  if (!res.ok) throw new Error(`Could not revoke key (${res.status})`);
}

// ---------------- developer: usage ----------------
export interface UsageSummary {
  total: number; allow: number; block: number;
  secondary_check: number; recapture: number; allow_rate: number; last_24h: number;
}
export interface UsageLog {
  request_id: string; endpoint: string; decision: string;
  reason_code: string; estimated_age: number | null; created_at: string;
}

export async function usageSummary(token: string): Promise<UsageSummary> {
  const res = await fetch(`${API_URL}/v1/usage/summary`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(`Could not load usage (${res.status})`);
  return res.json();
}

export async function usageLogs(token: string, limit = 50): Promise<UsageLog[]> {
  const res = await fetch(`${API_URL}/v1/usage/logs?limit=${limit}`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error(`Could not load logs (${res.status})`);
  return res.json();
}

export async function sendWelcome(token: string): Promise<void> {
  try {
    await fetch(`${API_URL}/v1/account/welcome`, { method: 'POST', headers: authHeaders(token) });
  } catch { /* best effort */ }
}

// ---------------- guardian consent (public) ----------------
export async function guardianRequest(
  guardianEmail: string, appName = 'Kamari', guardianName = '',
): Promise<{ session_id: string; expires_in: number }> {
  const res = await fetch(`${API_URL}/v1/guardian/request`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ guardian_email: guardianEmail, app_name: appName, guardian_name: guardianName }),
  });
  if (!res.ok) throw new Error(`Could not start guardian check (${res.status})`);
  return res.json();
}

export async function guardianVerify(sessionId: string, code: string): Promise<{ approved: boolean }> {
  const res = await fetch(`${API_URL}/v1/guardian/verify`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, code }),
  });
  if (res.status === 401) throw new Error('That code is not correct.');
  if (!res.ok) throw new Error(`Verification failed (${res.status})`);
  return res.json();
}

// --- Mock: samples a plausible borderline result so every decision path is reachable ---
function mockEstimate(): Promise<AgeEstimateResponse> {
  const age = +(13 + Math.random() * 14).toFixed(1); // 13-27
  const pUnder = +Math.max(0, Math.min(1, (19 - age) / 8 + Math.random() * 0.1)).toFixed(2);
  const quality = +(0.7 + Math.random() * 0.3).toFixed(2);
  const uncertainty = +(0.1 + Math.random() * 0.25).toFixed(2);

  let decision: AgeEstimateResponse['decision'] = 'allow';
  let reason: AgeEstimateResponse['reason_code'] = 'ALLOW';
  let message = 'You are verified. Welcome in.';
  if (quality < 0.72) {
    decision = 'recapture'; reason = 'RECAPTURE_LOW_QUALITY';
    message = 'The photo was a little unclear. Let us try once more in better light.';
  } else if (pUnder >= 0.7) {
    decision = 'block'; reason = 'BLOCK_LIKELY_MINOR';
    message = 'We cannot confirm you meet the age requirement. A guardian check is needed.';
  } else if (age < 21) {
    decision = 'secondary_check'; reason = 'SECONDARY_CHECK_NEAR_THRESHOLD';
    message = 'You are close to the limit, so we need one more quick check.';
  } else if (uncertainty > 0.28) {
    decision = 'secondary_check'; reason = 'SECONDARY_CHECK_LOW_CONFIDENCE';
    message = 'We would like a second check to be sure.';
  }

  const body: AgeEstimateResponse = {
    request_id: `req_mock_${Math.random().toString(36).slice(2, 10)}`,
    model_version: 'cnn_v0-mock',
    estimated_age: age,
    age_band: age < 18 ? '16-17' : age < 21 ? '18-20' : '21-25',
    p_under_18: pUnder,
    uncertainty,
    face_quality: quality,
    decision,
    reason_code: reason,
    message,
    retention: 'image_not_stored',
  };
  return new Promise((r) => setTimeout(() => r(body), 900));
}
