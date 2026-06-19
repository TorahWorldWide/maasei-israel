import seedEntries from "@/data/entries.json";

export type MediaType = "video_embed" | "video_upload" | "image";
export type Category = "חסד" | "המצאה מדעית" | "תרומה לעולם" | "היסטורי";
export type Status = "pending" | "approved";

export interface Entry {
  id: string;
  title: string;
  description: string;
  category: Category;
  year: number | null;
  media_type: MediaType;
  media_url: string;
  source_url: string;
  source_label: string;
  submitted_by?: string;
  // Optional poetic two-part split shown flanking the theater screen.
  // act = חלק א׳ · הניצוץ (the deed); ripple = חלק ב׳ · האור (its light in the world).
  // When absent, the UI falls back to title (spark) and description (light).
  act?: string;
  ripple?: string;
  status: Status;
  created_at: string;
}

export type SubmissionInput = Omit<Entry, "id" | "status" | "created_at">;

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
// Accept either the classic anon key name or the new publishable-key name.
const supabaseAnonKey =
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
// Accept either the classic service-role name or the new secret-key name.
const supabaseServiceKey =
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SECRET_KEY;

function hasSupabase(): boolean {
  return !!(supabaseUrl && supabaseAnonKey);
}

function hasServiceKey(): boolean {
  return !!(supabaseUrl && supabaseServiceKey);
}

async function getAnonClient() {
  const { createClient } = await import("@supabase/supabase-js");
  return createClient(supabaseUrl!, supabaseAnonKey!);
}

async function getServiceClient() {
  if (!supabaseServiceKey)
    throw new Error("SUPABASE service key (service role / secret) not configured");
  const { createClient } = await import("@supabase/supabase-js");
  return createClient(supabaseUrl!, supabaseServiceKey);
}

export async function getApprovedEntries(): Promise<Entry[]> {
  if (!hasSupabase()) {
    return seedEntries as Entry[];
  }
  try {
    const client = await getAnonClient();
    const { data, error } = await client
      .from("entries")
      .select("*")
      .eq("status", "approved")
      .order("created_at", { ascending: false });
    if (error) throw error;
    // If the DB is reachable but empty (e.g. schema run, no rows yet),
    // fall back to the seed so the site is never blank.
    if (!data || data.length === 0) return seedEntries as Entry[];
    return data as Entry[];
  } catch {
    // Tables missing, network error, etc. — never crash the page.
    return seedEntries as Entry[];
  }
}

export async function insertSubmission(
  submission: SubmissionInput
): Promise<{ ok: boolean; persisted: boolean; message?: string }> {
  if (!hasSupabase()) {
    return {
      ok: true,
      persisted: false,
      message: "Supabase not configured — submission not persisted to database.",
    };
  }
  try {
    // RLS allows public (anon/publishable) inserts into submissions,
    // so the public form works without the service key.
    const client = await getAnonClient();
    const { error } = await client
      .from("submissions")
      .insert([{ ...submission, status: "pending" }]);
    if (error) return { ok: false, persisted: false, message: error.message };
    return { ok: true, persisted: true };
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return { ok: false, persisted: false, message };
  }
}

export async function listPending(): Promise<{
  entries: Entry[];
  configured: boolean;
}> {
  if (!hasServiceKey()) {
    return { entries: [], configured: false };
  }
  const client = await getServiceClient();
  const { data, error } = await client
    .from("submissions")
    .select("*")
    .eq("status", "pending")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return { entries: (data ?? []) as Entry[], configured: true };
}

export async function approveSubmission(id: string): Promise<void> {
  const client = await getServiceClient();
  const { data: sub, error: fetchErr } = await client
    .from("submissions")
    .select("*")
    .eq("id", id)
    .single();
  if (fetchErr) throw fetchErr;
  // Strip identity/status columns so entries gets fresh values.
  const {
    id: _id,
    status: _status,
    created_at: _created_at,
    ...rest
  } = sub as Entry;
  void _id;
  void _status;
  void _created_at;
  const { error: insertErr } = await client
    .from("entries")
    .insert([{ ...rest, status: "approved" }]);
  if (insertErr) throw insertErr;
  const { error: deleteErr } = await client
    .from("submissions")
    .delete()
    .eq("id", id);
  if (deleteErr) throw deleteErr;
}

export async function rejectSubmission(id: string): Promise<void> {
  const client = await getServiceClient();
  const { error } = await client.from("submissions").delete().eq("id", id);
  if (error) throw error;
}
