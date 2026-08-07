import type { Entry } from "@/lib/data";

// Eras are DERIVED from `year` at runtime, never stored. The year is the single
// source of truth; a stored tag could drift away from it.
export type Era = { key: string; from: number; to: number };

const SPAN = 100;

export function eraOf(year: number | null | undefined): Era | null {
  if (!year || !Number.isFinite(year)) return null;
  const from = Math.floor(year / SPAN) * SPAN;
  return { key: `${from}-${from + SPAN}`, from, to: from + SPAN };
}

export function eraFromKey(key: string): Era | null {
  const m = key.match(/^(-?\d+)-(-?\d+)$/);
  if (!m) return null;
  const from = Number(m[1]);
  const to = Number(m[2]);
  if (to - from !== SPAN) return null;
  return { key, from, to };
}

export function erasPresent(entries: Entry[]): Era[] {
  const byKey = new Map<string, Era>();
  for (const entry of entries) {
    const era = eraOf(entry.year);
    if (era) byKey.set(era.key, era);
  }
  return [...byKey.values()].sort((a, b) => a.from - b.from);
}

export function eraDisplay(era: Era): string {
  return `${era.from}–${era.to}`;
}
