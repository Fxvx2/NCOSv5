// src/app/supabaseClient.ts
// Utility to initialize and export a Supabase client for the frontend
// Reads credentials from NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Create a single Supabase client for the app
export const supabase = createClient(supabaseUrl, supabaseAnonKey); 