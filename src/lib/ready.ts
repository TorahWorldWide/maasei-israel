import bar from "@/data/ready-bar.json";
import type { Entry } from "@/lib/data";

/**
 * 27.11: "only finished, full pages on the public site" (Tomer). One measurable
 * bar, in src/data/ready-bar.json, shared with scripts/not_ready_report.py:
 *  - an old-catalog deed needs at least `catalog_min_sentences` sentences of text
 *    on its page (Entebbe had 6: mostly photos);
 *  - a museum page needs a passed check with at least `museum_min_confirmed`
 *    confirmed sentences, and its English translation.
 * A deed below the bar is not deleted: it is left out of the catalog and the reel,
 * and its page answers 404 unless opened with ?draft=1.
 */
export const READY_BAR = bar;

// A sentence ends in . ! or ? and has at least 15 characters (so "ד"ר." or a lone number is not one).
export function countSentences(text?: string | null): number {
  if (!text) return 0;
  return text.split(/(?<=[.!?])\s+/).filter((s) => s.trim().length >= 15).length;
}

export function entrySentences(e: Entry): number {
  const parts = [e.description, e.origin_story, e.act, e.ripple, e.aftermath, e.recognition, ...(e.sections ?? []).map((s) => s.body)];
  return parts.reduce((n, p) => n + countSentences(p), 0);
}

export function isReadyEntry(e: Entry): boolean {
  return entrySentences(e) >= bar.catalog_min_sentences;
}

type MuseumCheck = { check?: { passed?: unknown; counts?: { confirmed?: unknown } } };

export function isReadyMuseum(he: MuseumCheck, hasEnglish: boolean): boolean {
  const confirmed = Number(he.check?.counts?.confirmed ?? 0);
  return String(he.check?.passed) === "true" || he.check?.passed === true
    ? confirmed >= bar.museum_min_confirmed && (hasEnglish || !bar.museum_needs_english)
    : false;
}
