import { z } from 'zod';

// Mirrors the API contract in the master plan (§20/§21). Keep in sync with apps/api.
export const DECISIONS = [
  'allow',
  'block',
  'secondary_check',
  'recapture',
] as const;
export type Decision = (typeof DECISIONS)[number];

export const REASON_CODES = [
  'ALLOW',
  'BLOCK_LIKELY_MINOR',
  'SECONDARY_CHECK_NEAR_THRESHOLD',
  'SECONDARY_CHECK_LOW_CONFIDENCE',
  'RECAPTURE_LOW_QUALITY',
  'RECAPTURE_NO_FACE',
  'RECAPTURE_MULTIPLE_FACES',
  'ERROR_UNSUPPORTED_IMAGE',
] as const;
export type ReasonCode = (typeof REASON_CODES)[number];

export const Explanation = z.object({
  source: z.enum(['model', 'template']),
  model_version: z.string().nullish(),
  summary: z.string().nullish(),
  next_step: z.string().nullish(),
  safety_note: z.string().nullish(),
});
export type Explanation = z.infer<typeof Explanation>;

export const AgeEstimateResponse = z.object({
  request_id: z.string(),
  model_version: z.string(),
  estimated_age: z.number(),
  age_band: z.string(),
  p_under_18: z.number(),
  uncertainty: z.number(),
  face_quality: z.number(),
  decision: z.enum(DECISIONS),
  reason_code: z.enum(REASON_CODES),
  message: z.string(),
  explanation: Explanation.optional(),
  retention: z.string(),
});
export type AgeEstimateResponse = z.infer<typeof AgeEstimateResponse>;

export interface EstimateOptions {
  language?: string;
  country?: string;
}
