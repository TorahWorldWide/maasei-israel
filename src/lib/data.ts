import seedEntries from "@/data/entries.json";

export type MediaType = "video_embed" | "video_upload" | "image";
export type Category = "חסד" | "המצאה מדעית" | "תרומה לעולם" | "היסטורי";
export type Status = "pending" | "approved";

// One picture's paper trail, as the enrichment passes wrote it into
// audit.image_provenance. Field names drifted between passes, so the site
// reads every spelling that reached the table.
export interface ImageProvenance {
  url: string;
  group?: string | null;
  group_en?: string | null;
  caption_he?: string | null;
  caption_en?: string | null;
  // The long "what is in the frame" note. The thumbnail shows the short caption
  // (rule 147); the enlarged view shows this beneath it, so a disclosure written
  // here stays visible to the reader (rule 153).
  caption_long_he?: string | null;
  caption_long_en?: string | null;
  credit?: string | null;
  credit_en?: string | null;
  credit_line?: string | null;
  photographer?: string | null;
  source?: string | null;
  source_url?: string | null;
  shot_when?: string | null;
  shot_when_en?: string | null;
  date?: string | null;
  year?: string | number | null;
  license?: string | null;
}

// A verbatim quote from an authoritative source that proves the deed happened.
// The UI turns `quote` into a link that jumps to the EXACT spot in the source
// (browser Text Fragment for web pages, #page=N for PDFs).
export interface Citation {
  quote: string; // verbatim text from the source — never paraphrased
  source_label: string; // who/what it's from (shown as the attribution)
  source_url: string; // the source document/page
  locator?: string; // optional: page number for PDFs (e.g. "12"), or a section hint
  // English rendering. quote_en is a faithful translation shown BENEATH the
  // original quote when the site is in English AND the original quote is Hebrew
  // (empty when the quote is already English — we keep the verbatim original).
  quote_en?: string;
  source_label_en?: string;
  locator_en?: string;
}

export interface Entry {
  id: string;
  title: string;
  description: string;
  category: Category;
  // Optional multiple tags. When present, the UI filters/badges by these;
  // when absent it falls back to the single `category`. The first element
  // mirrors `category` (the primary tag).
  categories?: Category[];
  year: number | null;
  media_type: MediaType;
  media_url: string;
  // Optional gallery of image URLs (for image entries with several pictures).
  // When media_type === "image" and this is non-empty, the UI shows all of
  // them; otherwise it falls back to the single media_url. Video entries ignore
  // this. Populated by the autonomous company only when no video exists.
  media_urls?: string[];
  source_url: string;
  source_label: string;
  submitted_by?: string;
  // Optional poetic two-part split shown flanking the theater screen.
  // act = חלק א׳ · הניצוץ (the deed); ripple = חלק ב׳ · האור (its light in the world).
  // When absent, the UI falls back to title (spark) and description (light).
  act?: string;
  ripple?: string;
  // Rule 130: the 3–10 sentence opener, written last and read first. The page
  // leads with it and keeps the full text behind a "read more" button (rule 131).
  summary_short?: string;
  // The four sections rules 64–67 of the standard require: how the deed came to
  // be, what happened next, what the doer got for it, and the honors in their name.
  origin_story?: string;
  aftermath?: string;
  recognition?: string;
  honors?: { what: string; year?: number | null; source?: string }[];
  // Verbatim quotes from authoritative sources — the hard proof. Each is clickable
  // and jumps to the exact spot in its source.
  citations?: Citation[];
  // The documented reasoning behind the chosen title (for review + future automation).
  // See docs/title-methodology.md. Not shown on the public site.
  title_reasoning?: string;
  // English translations (populated once; the UI shows them when lang === "en"
  // and falls back to the Hebrew field when a translation is missing).
  title_en?: string;
  description_en?: string;
  summary_short_en?: string;
  act_en?: string;
  ripple_en?: string;
  origin_story_en?: string;
  aftermath_en?: string;
  recognition_en?: string;
  source_label_en?: string;
  // Normalized identity signals for duplicate detection (people + keywords),
  // mirroring deed_registry. No DB column yet — always undefined until the
  // `dedup` jsonb column is added; src/lib/dedup.ts degrades gracefully.
  dedup?: { people?: string[]; keywords?: string[] };
  // The enrichment record. Only image_provenance is read by the public site —
  // it carries the caption and group heading every picture is shown with
  // (rules 44–46) plus its credit and usage basis (rules 12, 137).
  audit?: { image_provenance?: ImageProvenance[] };
  status: Status;
  created_at: string;
}

export type SubmissionInput = Omit<Entry, "id" | "status" | "created_at">;

// The tags to filter/badge an entry by: the explicit `categories` array when
// present, otherwise the single `category`.
export function entryCategories(e: Entry): Category[] {
  return e.categories && e.categories.length ? e.categories : [e.category];
}

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

export async function getEntryById(id: string): Promise<Entry | null> {
  if (!hasSupabase()) {
    return (
      (seedEntries as Entry[]).find(
        (e) => e.id === id && e.status === "approved"
      ) ?? null
    );
  }
  try {
    const client = await getAnonClient();
    const { data, error } = await client
      .from("entries")
      .select("*")
      .eq("id", id)
      .eq("status", "approved")
      .single();
    if (error) throw error;
    return data as Entry;
  } catch {
    return (
      (seedEntries as Entry[]).find(
        (e) => e.id === id && e.status === "approved"
      ) ?? null
    );
  }
}

// ─── Admin: image order (rule 132) ──────────────────────────────────────────
export interface MediaEntry {
  id: string;
  title: string;
  media_type: MediaType;
  media_url: string;
  media_urls: string[];
}

export async function listEntriesWithMedia(): Promise<MediaEntry[]> {
  const client = await getServiceClient();
  const { data, error } = await client
    .from("entries")
    .select("id, title, media_type, media_url, media_urls")
    .eq("status", "approved")
    .order("title");
  if (error) throw error;
  return ((data ?? []) as MediaEntry[]).filter(
    (e) => (e.media_urls?.length ?? 0) > 1
  );
}

export const NOT_A_REORDER = "not a reordering of the stored images";

export async function reorderEntryMedia(
  id: string,
  urls: string[]
): Promise<string[]> {
  const client = await getServiceClient();
  const { data: row, error } = await client
    .from("entries")
    .select("media_type, media_urls")
    .eq("id", id)
    .single();
  if (error) throw error;

  // A reorder may only permute what is stored — this route never adds,
  // removes or rewrites a url.
  const stored = (row.media_urls ?? []) as string[];
  const key = (a: string[]) => [...a].sort().join(" ");
  if (stored.length !== urls.length || key(stored) !== key(urls)) {
    throw new Error(NOT_A_REORDER);
  }

  const patch: { media_urls: string[]; media_url?: string } = {
    media_urls: urls,
  };
  // The card and the stage read media_url, so an image deed's lead moves too.
  if (row.media_type === "image") patch.media_url = urls[0];

  const { data: written, error: writeErr } = await client
    .from("entries")
    .update(patch)
    .eq("id", id)
    .select("media_urls")
    .single();
  if (writeErr) throw writeErr;
  return (written.media_urls ?? []) as string[];
}

// ─── Overview (the historian's "state of the nation" summary) ───────────────
export interface Overview {
  headline: string;
  narrative: string;
  headline_en?: string;
  narrative_en?: string;
  stats: Record<string, string | number>;
  date_range: string;
  revision: number;
}

export async function getOverview(): Promise<Overview | null> {
  if (!hasSupabase()) return null;
  try {
    const client = await getAnonClient();
    const { data, error } = await client
      .from("overview")
      .select("headline, narrative, headline_en, narrative_en, stats, date_range, revision")
      .eq("id", 1)
      .single();
    if (error) throw error;
    // Only show it once the historian has actually written something.
    if (!data || !data.headline) return null;
    return data as Overview;
  } catch {
    return null;
  }
}
