"use client";

import Link from "next/link";
import type { Entry } from "@/lib/data";
import ShareProof from "@/components/ShareProof";

function normalizeVideoUrl(url: string): string {
  const ytMatch = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/
  );
  if (ytMatch) return `https://www.youtube.com/embed/${ytMatch[1]}`;
  return url;
}

const CATEGORY_COLORS: Record<string, string> = {
  חסד: "bg-sky-400/15 text-sky-200 border border-sky-400/25",
  "המצאה מדעית": "bg-blue-400/15 text-blue-200 border border-blue-400/25",
  "תרומה לעולם": "bg-indigo-400/15 text-indigo-200 border border-indigo-400/25",
  היסטורי: "bg-amber-400/15 text-amber-200 border border-amber-400/25",
};

function StarPlaceholder({ category }: { category: string }) {
  return (
    <div className="relative flex items-center justify-center w-full h-full bg-gradient-to-br from-[#0f234d] to-[#0a1834] overflow-hidden">
      <svg
        viewBox="0 0 100 100"
        className="absolute inset-0 w-full h-full opacity-[0.12]"
        aria-hidden="true"
      >
        <polygon points="50,5 5,85 95,85" fill="none" stroke="#c9a84a" strokeWidth="2" />
        <polygon points="50,95 95,15 5,15" fill="none" stroke="#c9a84a" strokeWidth="2" />
      </svg>
      <span className="relative z-10 text-[#e6c66e] text-sm font-medium px-3 py-1 rounded-full bg-[#c9a84a]/10 border border-[#c9a84a]/20">
        {category}
      </span>
    </div>
  );
}

interface EntryCardProps {
  entry: Entry;
  onClick?: () => void;
}

export default function EntryCard({ entry, onClick }: EntryCardProps) {
  const embedUrl =
    entry.media_type === "video_embed" && entry.media_url
      ? normalizeVideoUrl(entry.media_url)
      : null;

  return (
    <div
      className="group bg-[#0f234d]/80 backdrop-blur-sm rounded-2xl border border-[rgba(201,168,74,0.18)] overflow-hidden hover:border-[rgba(201,168,74,0.5)] hover:-translate-y-1 hover:shadow-xl hover:shadow-black/40 transition-all duration-200 flex flex-col cursor-pointer"
      onClick={onClick}
      role="article"
    >
      {/* Media */}
      <div className="relative w-full aspect-video bg-[#0a1834] flex-shrink-0">
        {embedUrl ? (
          <iframe
            src={embedUrl}
            title={entry.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="absolute inset-0 w-full h-full border-0"
            loading="lazy"
          />
        ) : entry.media_url && entry.media_type === "video_upload" ? (
          <video
            src={entry.media_url}
            controls
            preload="metadata"
            className="absolute inset-0 w-full h-full object-cover bg-black"
            onClick={(e) => e.stopPropagation()}
          />
        ) : entry.media_url && entry.media_type === "image" ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={entry.media_url}
            alt={entry.title}
            className="absolute inset-0 w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <StarPlaceholder category={entry.category} />
        )}
      </div>

      {/* Content */}
      <div className="flex flex-col flex-1 p-5 gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
              CATEGORY_COLORS[entry.category] ?? "bg-white/10 text-blue-100 border border-white/15"
            }`}
          >
            {entry.category}
          </span>
          {entry.year && (
            <span className="text-xs text-blue-200/45">{entry.year}</span>
          )}
        </div>

        <Link
          href={`/deed/${entry.id}`}
          onClick={(e) => e.stopPropagation()}
          className="hover:text-[#e6c66e] transition-colors"
        >
          <h3 className="text-lg font-bold text-white leading-snug line-clamp-2" style={{ fontFamily: "var(--font-frank-ruhl), serif" }}>
            {entry.title}
          </h3>
        </Link>

        <p className="text-sm text-blue-100/70 leading-relaxed line-clamp-3 flex-1">
          {entry.description}
        </p>

        {entry.citations && entry.citations.length > 0 && (
          <div className="flex items-center gap-1.5 text-[11px] font-medium" style={{ color: "#e6c66e" }}>
            <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {entry.citations.length === 1 ? "מגובה במקור מאומת" : `${entry.citations.length} מקורות מאומתים`}
          </div>
        )}

        <div
          onClick={(e) => e.stopPropagation()}
          className="mt-auto pt-1"
        >
          <ShareProof entry={entry} size="sm" />
        </div>

        <a
          href={entry.source_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="text-xs text-[#e6c66e] hover:text-[#f0d585] font-medium flex items-center gap-1 underline underline-offset-2 decoration-[#c9a84a]/40 hover:decoration-[#c9a84a] transition-colors"
        >
          <svg
            className="w-3 h-3 flex-shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
            />
          </svg>
          מקור: {entry.source_label || entry.source_url}
        </a>
      </div>
    </div>
  );
}
