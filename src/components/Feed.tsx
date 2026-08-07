"use client";

import { useState, useMemo, useEffect, useRef } from "react";
import type { Entry } from "@/lib/data";
import { entryCategories } from "@/lib/data";
import { useLang } from "@/components/LangProvider";
import { t, categoryLabel } from "@/lib/i18n";
import { eraOf, erasPresent, eraDisplay } from "@/lib/era";
import EntryCard from "./EntryCard";
import Slideshow from "./Slideshow";

const CATEGORIES = ["הכל", "חסד", "המצאה מדעית", "תרומה לעולם", "היסטורי"] as const;

interface FeedProps {
  entries: Entry[];
  // From ?era=1800-1900,2000-2100 — parsed on the server so a shared link renders
  // already filtered instead of flashing the full catalog first.
  initialEras?: string[];
}

export default function Feed({ entries, initialEras = [] }: FeedProps) {
  const { lang } = useLang();
  const allEras = useMemo(() => erasPresent(entries), [entries]);

  const [category, setCategory] = useState("הכל");
  const [eras, setEras] = useState<string[]>(() => {
    const valid = new Set(erasPresent(entries).map((e) => e.key));
    return initialEras.filter((k) => valid.has(k));
  });
  const [search, setSearch] = useState("");
  const [slideshowIndex, setSlideshowIndex] = useState<number | null>(null);

  const skipUrlWrite = useRef(true);

  useEffect(() => {
    if (skipUrlWrite.current) {
      skipUrlWrite.current = false;
      return;
    }
    const params = new URLSearchParams(window.location.search);
    if (eras.length) params.set("era", eras.join(","));
    else params.delete("era");
    const qs = params.toString();
    window.history.replaceState(null, "", qs ? `?${qs}` : window.location.pathname);
  }, [eras]);

  const toggleEra = (key: string) =>
    setEras((prev) => (prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]));

  // Everything except the era filter — the era counters are computed off this so
  // they stay truthful under an active category/search.
  const beforeEra = useMemo(() => {
    return entries.filter((e) => {
      if (category !== "הכל" && !entryCategories(e).includes(category as Entry["category"]))
        return false;
      if (search.trim()) {
        const q = search.trim().toLowerCase();
        const haystack = [e.title, e.description, e.title_en, e.description_en]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [entries, category, search]);

  const eraCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const e of beforeEra) {
      const era = eraOf(e.year);
      if (era) counts.set(era.key, (counts.get(era.key) ?? 0) + 1);
    }
    return counts;
  }, [beforeEra]);

  const filtered = useMemo(() => {
    if (!eras.length) return beforeEra;
    return beforeEra.filter((e) => eras.includes(eraOf(e.year)?.key ?? ""));
  }, [beforeEra, eras]);

  return (
    <>
      {/* Controls */}
      <div className="flex flex-col gap-4 mb-8">
        {/* Search */}
        <div className="relative max-w-sm">
          <input
            type="search"
            placeholder={t(lang, "searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-10 pl-4 py-2.5 rounded-full border border-[rgba(201,168,74,0.25)] bg-[#0f234d]/70 text-sm text-white placeholder:text-blue-200/40 focus:outline-none focus:ring-2 focus:ring-[#c9a84a]/40 focus:border-[#c9a84a]/60 transition-shadow"
            aria-label={t(lang, "searchAria")}
          />
          <svg
            className="absolute right-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-blue-200/40 pointer-events-none"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z"
            />
          </svg>
        </div>

        {/* Category chips */}
        <div className="flex flex-wrap gap-2" role="group" aria-label={t(lang, "filterByCategory")}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all duration-150 ${
                category === cat
                  ? "bg-gradient-to-b from-[#e6c66e] to-[#c9a84a] text-[#0a1834] border-[#c9a84a] shadow-sm"
                  : "bg-[#0f234d]/60 text-blue-100/80 border-[rgba(201,168,74,0.2)] hover:border-[#c9a84a]/50 hover:text-white"
              }`}
              aria-pressed={category === cat}
            >
              {categoryLabel(lang, cat)}
            </button>
          ))}
        </div>

        {/* Era chips — multi-select, union across the chosen centuries */}
        <div className="flex flex-wrap items-center gap-2" role="group" aria-label={t(lang, "filterByEra")}>
          {allEras.map((era) => {
            const on = eras.includes(era.key);
            return (
              <button
                key={era.key}
                onClick={() => toggleEra(era.key)}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition-all duration-150 ${
                  on
                    ? "bg-sky-500/90 text-white border-sky-400"
                    : "bg-[#0f234d]/50 text-blue-200/60 border-[rgba(201,168,74,0.15)] hover:border-sky-400/50 hover:text-sky-200"
                }`}
                aria-pressed={on}
              >
                <span dir="ltr">{eraDisplay(era)}</span>
                <span className={`ms-1.5 ${on ? "text-white/70" : "text-blue-200/40"}`}>
                  · {eraCounts.get(era.key) ?? 0}
                </span>
              </button>
            );
          })}
          {eras.length > 0 && (
            <button
              onClick={() => setEras([])}
              className="text-xs text-[#e6c66e] hover:text-[#f0d585] underline underline-offset-2"
            >
              {t(lang, "clearFilter")}
            </button>
          )}
        </div>
      </div>

      {/* Results count */}
      {search.trim() && (
        <p className="text-sm text-blue-200/60 mb-5">
          {filtered.length} {t(lang, "resultsWord")} &ldquo;{search}&rdquo;
        </p>
      )}

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20 text-blue-200/40">
          <p className="text-lg">{t(lang, "noItems")}</p>
          <button
            onClick={() => {
              setCategory("הכל");
              setEras([]);
              setSearch("");
            }}
            className="mt-3 text-[#e6c66e] hover:text-[#f0d585] text-sm underline"
          >
            {t(lang, "clearFilter")}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((entry, i) => (
            <EntryCard
              key={entry.id}
              entry={entry}
              onClick={() => setSlideshowIndex(i)}
              onEraClick={(key) => setEras([key])}
            />
          ))}
        </div>
      )}

      {/* Slideshow overlay */}
      {slideshowIndex !== null && (
        <Slideshow
          entries={filtered}
          initialIndex={slideshowIndex}
          onClose={() => setSlideshowIndex(null)}
        />
      )}
    </>
  );
}
