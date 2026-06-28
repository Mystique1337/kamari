import { AgeEstimateResponse, type EstimateOptions } from './types';

// The ONLY thing the app waits on from the ML side: this base URL.
// Point it at the Railway gateway (which calls the Modal CNN/Gemma endpoints).
// While that's empty (or VITE_USE_MOCK=1), a realistic mock is used so the whole
// flow is demoable today.
const API_URL = (import.meta.env.VITE_KAMARI_API_URL as string | undefined)?.replace(/\/$/, '');
const USE_MOCK = import.meta.env.VITE_USE_MOCK === '1' || !API_URL;

export const apiMode = USE_MOCK ? 'mock' : 'live';

function dataUrlToBlob(dataUrl: string): Blob {
  const [head, b64] = dataUrl.split(',');
  const mime = /data:(.*?);/.exec(head)?.[1] ?? 'image/jpeg';
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new Blob([bytes], { type: mime });
}

/** POST /v1/age/estimate — multipart image upload. Returns a validated response. */
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

// --- Mock: samples a plausible borderline result so every decision path is reachable ---
function mockEstimate(): Promise<AgeEstimateResponse> {
  const age = +(13 + Math.random() * 14).toFixed(1); // 13–27
  const pUnder = +Math.max(0, Math.min(1, (19 - age) / 8 + Math.random() * 0.1)).toFixed(2);
  const quality = +(0.7 + Math.random() * 0.3).toFixed(2);
  const uncertainty = +(0.1 + Math.random() * 0.25).toFixed(2);

  let decision: AgeEstimateResponse['decision'] = 'allow';
  let reason: AgeEstimateResponse['reason_code'] = 'ALLOW';
  let message = 'You are verified. Welcome in.';
  if (quality < 0.72) {
    decision = 'recapture'; reason = 'RECAPTURE_LOW_QUALITY';
    message = 'The photo was a little unclear — let’s try once more in better light.';
  } else if (pUnder >= 0.7) {
    decision = 'block'; reason = 'BLOCK_LIKELY_MINOR';
    message = 'We can’t confirm you meet the age requirement. A guardian check is needed.';
  } else if (age < 21) {
    decision = 'secondary_check'; reason = 'SECONDARY_CHECK_NEAR_THRESHOLD';
    message = 'You’re close to the limit, so we need one more quick check.';
  } else if (uncertainty > 0.28) {
    decision = 'secondary_check'; reason = 'SECONDARY_CHECK_LOW_CONFIDENCE';
    message = 'We’d like a second check to be sure.';
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
