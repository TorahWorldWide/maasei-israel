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
  status: Status;
  created_at: string;
}

export type SubmissionInput = Omit<Entry, "id" | "status" | "created_at">;

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

function hasSupabase(): boolean {
  return !!(supabaseUrl && supabaseAnonKey);
}

async function getAnonClient() {
  const { createClient } = await import("@supabase/supabase-js");
  return createClient(supabaseUrl!, supabaseAnonKey!);
}

async function getServiceClient() {
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!serviceKey) throw new Error("SUPABASE_SERVICE_ROLE_KEY not configured");
  const { createClient } = await import("@supabase/supabase-js");
  return createClient(supabaseUrl!, serviceKey);
}

export async function getApprovedEntries(): Promise<Entry[]> {
  if (!hasSupabase()) {
    return seedEntries as Entry[];
  }
  const client = await getAnonClient();
  const { data, error } = await client
    .from("entries")
    .select("*")
    .eq("status", "approved")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return (data ?? []) as Entry[];
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
  const client = await getServiceClient();
  const { error } = await client
    .from("submissions")
    .insert([{ ...submission, status: "pending" }]);
  if (error) return { ok: false, persisted: false, message: error.message };
  return { ok: true, persisted: true };
}

export async function listPending(): Promise<{
  entries: Entry[];
  configured: boolean;
}> {
  if (!hasSupabase() || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
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
  const { error: insertErr } = await client
    .from("entries")
    .insert([{ ...sub, status: "approved" }]);
  if (insertErr) throw insertErr;
  const { error: deleteErr } = await client
    .from("submissions")
    .delete()
    .eq("id", id);
  if (deleteErr) throw deleteErr;
}

export async function rejectSubmission(id: string): Promise<void> {
  const client = await getServiceClient();
  const { error } = await client
    .from("submissions")
    .delete()
    .eq("id", id);
  if (error) throw error;
}
