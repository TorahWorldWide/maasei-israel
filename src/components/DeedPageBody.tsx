"use client";

import Link from "next/link";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";
import ShareProof from "@/components/ShareProof";
import type { Entry } from "@/lib/data";

function extractYouTubeId(url: string): string | null {
  const m = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/
  );
  return m?.[1] ?? null;
}

export default function DeedPageBody({ entry }: { entry: Entry }) {
  const { lang } = useLang();

  const ytId =
    entry.media_type === "video_embed" && entry.media_url
      ? extractYouTubeId(entry.media_url)
      : null;

  return (
    <main className="flex-1 w-full">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
        {/* Back link */}
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-[#c9a84a] hover:text-[#e6c66e] text-sm mb-8 transition-colors"
        >
          <span aria-hidden="true">{lang === "he" ? "→" : "←"}</span>
          {t(lang, "backToAll")}
        </Link>

        {/* Category + Year */}
        <div className="flex items-center gap-2 flex-wrap mb-4">
          <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-[#c9a84a]/15 text-[#e6c66e] border border-[#c9a84a]/25">
            {entry.category}
          </span>
          {entry.year && (
            <span className="text-xs text-blue-200/45">{entry.year}</span>
          )}
        </div>

        {/* Title */}
        <h1
          className="text-3xl md:text-4xl font-extrabold text-[#e6c66e] leading-tight mb-6"
          style={{ fontFamily: "var(--font-frank-ruhl), serif" }}
        >
          {entry.title}
        </h1>

        {/* Video */}
        {ytId && (
          <div className="relative w-full aspect-video rounded-xl overflow-hidden mb-8 shadow-xl shadow-black/50">
            <iframe
              src={`https://www.youtube-nocookie.com/embed/${ytId}`}
              title={entry.title}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="absolute inset-0 w-full h-full border-0"
            />
          </div>
        )}

        {/* Description */}
        <p className="text-base text-blue-100/80 leading-relaxed mb-8">
          {entry.description}
        </p>

        {/* Act / Ripple */}
        {(entry.act || entry.ripple) && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
            {entry.act && (
              <div className="bg-[#0f234d]/60 rounded-xl p-4 border border-[rgba(201,168,74,0.15)]">
                <p className="text-xs text-[#c9a84a] font-medium mb-1">
                  {t(lang, "actLabel")}
                </p>
                <p className="text-sm text-blue-100/80">{entry.act}</p>
              </div>
            )}
            {entry.ripple && (
              <div className="bg-[#0f234d]/60 rounded-xl p-4 border border-[rgba(201,168,74,0.15)]">
                <p className="text-xs text-[#c9a84a] font-medium mb-1">
                  {t(lang, "rippleLabel")}
                </p>
                <p className="text-sm text-blue-100/80">{entry.ripple}</p>
              </div>
            )}
          </div>
        )}

        {/* Citations */}
        {entry.citations && entry.citations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-sm font-semibold text-[#c9a84a] mb-3 uppercase tracking-wider">
              {t(lang, "citationsHeading")}
            </h2>
            <ul className="flex flex-col gap-3">
              {entry.citations.map((c, i) => (
                <li
                  key={i}
                  className="bg-[#0f234d]/60 rounded-xl p-4 border border-[rgba(201,168,74,0.15)]"
                >
                  <blockquote className="text-sm text-blue-100/80 italic mb-2">
                    &ldquo;{c.quote}&rdquo;
                  </blockquote>
                  <a
                    href={c.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-[#c9a84a] hover:text-[#e6c66e] underline underline-offset-2 decoration-[#c9a84a]/40 hover:decoration-[#c9a84a] transition-colors"
                  >
                    — {c.source_label}
                    {c.locator && `, עמ׳ ${c.locator}`}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Source + Share */}
        <div className="flex items-center justify-between gap-4 flex-wrap border-t border-[rgba(201,168,74,0.15)] pt-6">
          <a
            href={entry.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-[#c9a84a] hover:text-[#e6c66e] underline underline-offset-2 decoration-[#c9a84a]/40 hover:decoration-[#c9a84a] transition-colors"
          >
            {t(lang, "source")}: {entry.source_label || entry.source_url}
          </a>
          <ShareProof entry={entry} />
        </div>
      </div>
    </main>
  );
}
