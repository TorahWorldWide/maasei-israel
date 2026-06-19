"use client";

import { useState, useMemo } from "react";
import type { Entry } from "@/lib/data";
import EntryCard from "./EntryCard";
import Slideshow from "./Slideshow";

const CATEGORIES = ["הכל", "חסד", "המצאה מדעית", "תרומה לעולם", "היסטורי"] as const;
const ERAS = ["הכל", "עתיק", "טרום המדינה", "המאה ה-20", "עכשווי"] as const;

function getEra(year: number | null): string {
  if (!year) return "עתיק";
  if (year < 1900) return "עתיק";
  if (year < 1948) return "טרום המדינה";
  if (year < 2000) return "המאה ה-20";
  return "עכשווי";
}

interface FeedProps {
  entries: Entry[];
}

export default function Feed({ entries }: FeedProps) {
  const [category, setCategory] = useState("הכל");
  const [era, setEra] = useState("הכל");
  const [search, setSearch] = useState("");
  const [slideshowIndex, setSlideshowIndex] = useState<number | null>(null);

  const filtered = useMemo(() => {
    return entries.filter((e) => {
      if (category !== "הכל" && e.category !== category) return false;
      if (era !== "הכל" && getEra(e.year) !== era) return false;
      if (search.trim()) {
        const q = search.trim().toLowerCase();
        if (
          !e.title.toLowerCase().includes(q) &&
          !e.description.toLowerCase().includes(q)
        )
          return false;
      }
      return true;
    });
  }, [entries, category, era, search]);

  return (
    <>
      {/* Controls */}
      <div className="flex flex-col gap-4 mb-8">
        {/* Search */}
        <div className="relative max-w-sm">
          <input
            type="search"
            placeholder="חיפוש..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-10 pl-4 py-2.5 rounded-full border border-[rgba(201,168,74,0.25)] bg-[#0f234d]/70 text-sm text-white placeholder:text-blue-200/40 focus:outline-none focus:ring-2 focus:ring-[#c9a84a]/40 focus:border-[#c9a84a]/60 transition-shadow"
            aria-label="חיפוש פריטים"
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
        <div className="flex flex-wrap gap-2" role="group" aria-label="סינון לפי קטגוריה">
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
              {cat}
            </button>
          ))}
        </div>

        {/* Era chips */}
        <div className="flex flex-wrap gap-2" role="group" aria-label="סינון לפי תקופה">
          {ERAS.map((e) => (
            <button
              key={e}
              onClick={() => setEra(e)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-all duration-150 ${
                era === e
                  ? "bg-sky-500/90 text-white border-sky-400"
                  : "bg-[#0f234d]/50 text-blue-200/60 border-[rgba(201,168,74,0.15)] hover:border-sky-400/50 hover:text-sky-200"
              }`}
              aria-pressed={era === e}
            >
              {e}
            </button>
          ))}
        </div>
      </div>

      {/* Results count */}
      {search.trim() && (
        <p className="text-sm text-blue-200/60 mb-5">
          {filtered.length} תוצאות עבור &ldquo;{search}&rdquo;
        </p>
      )}

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20 text-blue-200/40">
          <p className="text-lg">לא נמצאו פריטים.</p>
          <button
            onClick={() => {
              setCategory("הכל");
              setEra("הכל");
              setSearch("");
            }}
            className="mt-3 text-[#e6c66e] hover:text-[#f0d585] text-sm underline"
          >
            נקה סינון
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((entry, i) => (
            <EntryCard
              key={entry.id}
              entry={entry}
              onClick={() => setSlideshowIndex(i)}
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
