import { createClient, type SupabaseClient } from '@supabase/supabase-js';

// Supabase project (self-hosted). Set these at build time on Railway:
//   VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const anon = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

export const supabaseConfigured = Boolean(url && anon);

// A single shared client. When unconfigured we still export a typed value so the
// developer portal can show a clear "auth not configured" state instead of crashing.
export const supabase: SupabaseClient | null = supabaseConfigured
  ? createClient(url as string, anon as string, {
      auth: { persistSession: true, autoRefreshToken: true },
    })
  : null;
