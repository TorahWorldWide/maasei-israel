import type { Entry } from "@/lib/data";

// ─── Duplicate detection for the admin approve flow ─────────────────────────
// Server-side only: compares a pending submission against the published
// entries and returns structured matches the admin UI can render. Three
// signals, checked per entry:
//   1. Same YouTube video ID (exact).
//   2. Title similarity — Hebrew-aware token-set overlap (≥60% of the shorter
//      title's content tokens appear in the other).
//   3. Overlap of the `dedup` jsonb (shared person, or ≥2 shared keywords).

export interface DuplicateMatch {
  id: string;
  title: string;
  reason: string;
}

// ─── YouTube ────────────────────────────────────────────────────────────────

const YT_ID = "[A-Za-z0-9_-]{11}";
const YT_PATTERNS = [
  new RegExp(`[?&]v=(${YT_ID})`),
  new RegExp(`youtu\\.be/(${YT_ID})`),
  new RegExp(`youtube\\.com/(?:embed|shorts|live|v)/(${YT_ID})`),
];

export function extractYouTubeId(url: string | undefined | null): string | null {
  if (!url) return null;
  for (const re of YT_PATTERNS) {
    const m = url.match(re);
    if (m) return m[1];
  }
  return null;
}

// ─── Hebrew-aware title normalization ───────────────────────────────────────
// The known failure mode: rephrased titles (e.g. three זק"א entries) slipping
// past naive matching. So normalization removes gershayim/geresh INSIDE words
// (זק"א → זקא, not זק + א), maps final letters to base forms, and matches
// tokens through their prefix-stripped variants (ו/ה/ב/ל/מ/ש), so
// "לחיסון" ≈ "החיסון" ≈ "חיסון".

const HEBREW_PREFIXES = new Set(["ו", "ה", "ב", "ל", "מ", "ש"]);

const FINAL_LETTERS: Record<string, string> = {
  "ך": "כ",
  "ם": "מ",
  "ן": "נ",
  "ף": "פ",
  "ץ": "צ",
};

// Generic words that carry no identity on this site (mirrors the ledger's
// stop list in company-scripts, plus common function words).
const STOPWORDS = new Set([
  "של", "את", "על", "עם", "גם", "כל", "לא", "זה", "זו", "הוא", "היא", "הם",
  "אשר", "כי", "אל", "מן", "בין", "אחד", "אחת", "שנת", "שנה", "שנים",
  "ישראל", "ישראלי", "ישראלית", "ישראלים", "מדינת",
  "מים", "ילדים", "בני", "אדם", "אנשים", "מקבלים", "עוזר", "עוזרים",
  "ממציא", "יוצר", "מקים", "מקימים", "עולם",
  "the", "and", "for", "with", "that", "from", "his", "her",
  "israel", "israeli", "israelis",
]);

function normalizeText(s: string): string {
  return (
    s
      .toLowerCase()
      // Remove quote marks WITHOUT splitting the word: זק"א → זקא.
      .replace(/["'“”‘’׳״`]/g, "")
      // Strip niqqud / cantillation.
      .replace(/[֑-ׇ]/g, "")
      // Final letters → base forms.
      .replace(/[ךםןףץ]/g, (c) => FINAL_LETTERS[c] ?? c)
      // Everything that isn't a Hebrew/Latin letter or digit splits words.
      .replace(/[^a-z0-9א-ת]+/g, " ")
      .trim()
  );
}

// A token plus every form of it with leading Hebrew prefixes stripped
// (up to two, e.g. "והחיסון" → החיסון → חיסון). Two tokens "match" when
// their variant sets intersect.
function tokenVariants(token: string): string[] {
  const variants = [token];
  let t = token;
  for (let i = 0; i < 2; i++) {
    if (t.length > 2 && HEBREW_PREFIXES.has(t[0])) {
      t = t.slice(1);
      variants.push(t);
    } else break;
  }
  return variants;
}

function isStopword(token: string): boolean {
  return tokenVariants(token).some((v) => STOPWORDS.has(v));
}

// Content tokens of a title: normalized, ≥2 chars, stopwords dropped.
export function contentTokens(title: string): string[] {
  return normalizeText(title)
    .split(" ")
    .filter((t) => t.length >= 2 && !isStopword(t));
}

function tokensMatch(a: string, b: string): boolean {
  const va = tokenVariants(a);
  const vb = new Set(tokenVariants(b));
  return va.some((v) => vb.has(v));
}

// Returns the overlap ratio: what fraction of the SHORTER title's content
// tokens appear (prefix-aware) in the other title. null when unmeasurable.
export function titleOverlap(titleA: string, titleB: string): number | null {
  const ta = contentTokens(titleA);
  const tb = contentTokens(titleB);
  if (ta.length === 0 || tb.length === 0) return null;
  const [shorter, longer] = ta.length <= tb.length ? [ta, tb] : [tb, ta];
  const matched = shorter.filter((t) => longer.some((o) => tokensMatch(t, o)));
  // Require ≥2 shared tokens unless the shorter title is fully contained,
  // so a single generic word can't flag on its own.
  if (matched.length < 2 && matched.length < shorter.length) return 0;
  return matched.length / shorter.length;
}

const TITLE_THRESHOLD = 0.6;

// ─── dedup jsonb (people / keywords) ────────────────────────────────────────

function normalizedSet(values: unknown): Set<string> {
  if (!Array.isArray(values)) return new Set();
  return new Set(
    values
      .filter((v): v is string => typeof v === "string")
      .map((v) => normalizeText(v))
      .filter(Boolean)
  );
}

function sharedPeople(a: Entry, b: Entry): string[] {
  const pa = normalizedSet(a.dedup?.people);
  const pb = normalizedSet(b.dedup?.people);
  return [...pa].filter((p) => pb.has(p));
}

function sharedKeywords(a: Entry, b: Entry): string[] {
  const ka = [...normalizedSet(a.dedup?.keywords)];
  const kb = [...normalizedSet(b.dedup?.keywords)];
  // Prefix-aware, single-word keywords match through their variants.
  return ka.filter((k) => kb.some((o) => tokensMatch(k, o)));
}

// ─── Missing-media check ────────────────────────────────────────────────────

export function hasNoMedia(entry: Entry): boolean {
  const hasUrl = typeof entry.media_url === "string" && entry.media_url.trim() !== "";
  const hasGallery =
    Array.isArray(entry.media_urls) &&
    entry.media_urls.some((u) => typeof u === "string" && u.trim() !== "");
  return !hasUrl && !hasGallery;
}

// ─── Main entry point ───────────────────────────────────────────────────────

export function findDuplicates(
  submission: Entry,
  published: Entry[]
): DuplicateMatch[] {
  const subVideoId = extractYouTubeId(submission.media_url);
  const matches: DuplicateMatch[] = [];

  for (const entry of published) {
    const reasons: string[] = [];

    if (subVideoId && extractYouTubeId(entry.media_url) === subVideoId) {
      reasons.push("אותו סרטון יוטיוב");
    }

    const overlap = titleOverlap(submission.title, entry.title);
    if (overlap !== null && overlap >= TITLE_THRESHOLD) {
      reasons.push(`כותרת דומה (${Math.round(overlap * 100)}% חפיפה)`);
    }

    const people = sharedPeople(submission, entry);
    if (people.length >= 1) {
      reasons.push(`אותם אנשים: ${people.join(", ")}`);
    }
    const keywords = sharedKeywords(submission, entry);
    if (keywords.length >= 2) {
      reasons.push(`מילות מפתח משותפות: ${keywords.join(", ")}`);
    }

    if (reasons.length > 0) {
      matches.push({ id: entry.id, title: entry.title, reason: reasons.join(" · ") });
    }
  }

  return matches;
}
