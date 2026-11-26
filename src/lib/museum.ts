// Types for the museum deed page. The single source of truth is
// data/museum/schema/museum-page.schema.json; keep the two in step.

export type MuseumSentence = { text: string; claims: string[] };
export type MuseumParagraph = MuseumSentence[];

export type MuseumStation = {
  id: string;
  title: string;
  kind?: "story" | "hard";
  paragraphs: MuseumParagraph[];
  media?: string[];
  disagreements?: string[];
};

export type MuseumDisagreement = {
  id: string;
  question: string;
  versions: { says: string; claims: string[] }[];
};

export type MuseumClaim = {
  id: string;
  text: string;
  source: string;
  quote: string;
  locator?: string;
  status: "confirmed" | "contradicted" | "unverifiable" | "unchecked";
  checker_note?: string;
};

export type MuseumSource = {
  id: string;
  label: string;
  url: string;
  archive_url?: string;
  date?: string;
  kind: string;
};

export type MuseumMedia = {
  id: string;
  kind: "image" | "video";
  url: string;
  youtube_id?: string;
  source_page: string;
  source_name: string;
  credit: string;
  licence: string;
  licence_url?: string;
  hosting: "embed" | "hotlink" | "rehost";
  caption: string;
  date?: string;
  width?: number;
  height?: number;
  illustrates?: string[];
  role?: "deed" | "related";
  spoken?: string;
  audio_tracks?: string[];
};

export type MuseumPageData = {
  schema: "maasei-museum/1";
  slug: string;
  deed: string;
  canonical_type?: string;
  year?: string | null;
  title: string;
  trailer: MuseumParagraph;
  hero_media?: string[];
  glance?: { label: string; value: string; claims: string[] }[];
  stations: MuseumStation[];
  disagreements?: MuseumDisagreement[];
  unknowns?: MuseumSentence[];
  claims: MuseumClaim[];
  sources: MuseumSource[];
  media: MuseumMedia[];
  check: {
    passed: boolean;
    checker?: string;
    checked_at?: string;
    counts: Record<string, number>;
    note?: string;
  };
  lang?: "he" | "en";
  translation?: { passed?: boolean; quote_translations?: Record<string, string>; [k: string]: unknown };
};

/** The sources a list of claims rests on, in first-use order. */
export function sourcesOf(page: MuseumPageData, claimIds: string[]): MuseumSource[] {
  const claims = new Map(page.claims.map((c) => [c.id, c]));
  const sources = new Map(page.sources.map((s) => [s.id, s]));
  const out: MuseumSource[] = [];
  for (const id of claimIds) {
    const c = claims.get(id);
    const s = c ? sources.get(c.source) : undefined;
    if (s && !out.includes(s)) out.push(s);
  }
  return out;
}

/** A thumbnail of a Commons hot-link at a given width (Special:FilePath honours ?width=). */
export function sized(url: string, width: number): string {
  return url.includes("Special:FilePath") ? url.replace(/\?width=\d+/, "") + `?width=${width}` : url;
}

// Two images are "the same shot" when their file names match once crop
// markers, the extension and filler words are dropped, e.g.
// "Ruth Handler 1961 (cropped).jpg" and "Ruth Handler in 1961.jpg".
// Numbered series such as "… Arrives (1).jpg" / "… Arrives (2).jpg" stay
// distinct: those are different photographs of one event.
const SHOT_FILLER = new Set(["in", "of", "the", "at", "dr", "a", "and", "cropped", "crop", "jpg", "jpeg", "png", "tif", "tiff", "webp"]);
export function shotKey(m: MuseumMedia): string {
  const raw = (m.source_page || m.url).split(/[/:]/).pop() ?? "";
  let name = raw;
  try { name = decodeURIComponent(raw); } catch { /* keep raw */ }
  return name
    .toLowerCase()
    .replace(/\.[a-z0-9]{2,4}$/, "")
    .split(/[^\p{L}\p{N}]+/u)
    .filter((w) => w && !SHOT_FILLER.has(w))
    .sort()
    .join(" ");
}
/** Keep the first image of each shot, in order. */
export function distinctShots(images: MuseumMedia[]): MuseumMedia[] {
  const seen = new Set<string>();
  return images.filter((m) => { const k = shotKey(m); if (seen.has(k)) return false; seen.add(k); return true; });
}
