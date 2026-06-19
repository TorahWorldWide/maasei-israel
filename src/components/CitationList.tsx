"use client";

import type { Citation } from "@/lib/data";

/**
 * Build a URL that jumps to the EXACT spot in the source.
 *  - PDFs: append #page=N (and a text fragment too — Chrome honors both).
 *  - Web pages: use a Text Fragment (#:~:text=...) so the browser scrolls to
 *    and highlights the exact quoted words. We take a short head/tail slice of
 *    the quote to keep the URL robust (very long exact strings can fail to match).
 */
function deepLink(c: Citation): string {
  const base = c.source_url;
  const isPdf = /\.pdf($|\?|#)/i.test(base) || /\/pdf\//i.test(base);

  // Pick a concise, matchable fragment from the quote.
  const clean = c.quote.replace(/\s+/g, " ").trim();
  const words = clean.split(" ");
  let fragment = "";
  if (words.length <= 9) {
    fragment = encodeURIComponent(clean);
  } else {
    // textStart,textEnd — first 5 words … last 4 words (browser matches the span)
    const start = encodeURIComponent(words.slice(0, 5).join(" "));
    const end = encodeURIComponent(words.slice(-4).join(" "));
    fragment = `${start},${end}`;
  }

  if (isPdf) {
    const page = c.locator && /^\d+$/.test(c.locator) ? `#page=${c.locator}` : "#";
    // Chrome supports page + text fragment together via :~:
    return `${base}${page}${page.includes("#") ? "" : "#"}:~:text=${fragment}`;
  }

  const sep = base.includes("#") ? "" : "#";
  return `${base}${sep}:~:text=${fragment}`;
}

interface CitationListProps {
  citations: Citation[];
  /** "light" = on dark navy (default). */
  variant?: "light";
}

export default function CitationList({ citations }: CitationListProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="#c9a84a" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h4 className="text-sm font-bold" style={{ color: "#e6c66e" }}>
          ההוכחה — מקורות מאומתים
        </h4>
      </div>

      <ul className="flex flex-col gap-3">
        {citations.map((c, i) => (
          <li key={i}>
            <a
              href={deepLink(c)}
              target="_blank"
              rel="noopener noreferrer"
              className="group block rounded-xl border p-3.5 transition-colors hover:border-[rgba(201,168,74,0.6)]"
              style={{
                background: "rgba(10,24,52,0.6)",
                borderColor: "rgba(201,168,74,0.25)",
              }}
              title="לחצו כדי לקפוץ למקום המדויק במקור"
            >
              {/* the verbatim quote */}
              <blockquote
                className="text-sm leading-relaxed border-r-2 pr-3"
                style={{ color: "#eaf1ff", borderColor: "#c9a84a" }}
              >
                &ldquo;{c.quote}&rdquo;
              </blockquote>

              {/* attribution + jump hint */}
              <div className="mt-2.5 flex items-center justify-between gap-2 flex-wrap">
                <span className="text-xs font-medium" style={{ color: "#e6c66e" }}>
                  — {c.source_label}
                  {c.locator ? ` · עמ׳ ${c.locator}` : ""}
                </span>
                <span className="inline-flex items-center gap-1 text-[11px] text-blue-200/60 group-hover:text-blue-100 transition-colors">
                  קפוץ למקור
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </span>
              </div>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
