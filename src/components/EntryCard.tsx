"use client";

import type { Entry } from "@/lib/data";

function normalizeVideoUrl(url: string): string {
  const ytMatch = url.match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/
  );
  if (ytMatch) return `https://www.youtube.com/embed/${ytMatch[1]}`;
  return url;
}

const CATEGORY_COLORS: Record<string, string> = {
  חסד: "bg-sky-100 text-sky-800",
  "המצאה מדעית": "bg-blue-100 text-blue-800",
  "תרומה לעולם": "bg-indigo-100 text-indigo-800",
  היסטורי: "bg-slate-100 text-slate-700",
};

function StarPlaceholder({ category }: { category: string }) {
  return (
    <div className="relative flex items-center justify-center w-full h-full bg-gradient-to-br from-blue-900 to-blue-700 overflow-hidden">
      <svg
        viewBox="0 0 100 100"
        className="absolute inset-0 w-full h-full opacity-10"
        aria-hidden="true"
      >
        <polygon
          points="50,5 5,85 95,85"
          fill="none"
          stroke="white"
          strokeWidth="2"
        />
        <polygon
          points="50,95 95,15 5,15"
          fill="none"
          stroke="white"
          strokeWidth="2"
        />
      </svg>
      <span className="relative z-10 text-white text-sm font-medium px-3 py-1 rounded-full bg-white/10">
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
      className="group bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 flex flex-col cursor-pointer"
      onClick={onClick}
      role="article"
    >
      {/* Media */}
      <div className="relative w-full aspect-video bg-slate-100 flex-shrink-0">
        {embedUrl ? (
          <iframe
            src={embedUrl}
            title={entry.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="absolute inset-0 w-full h-full border-0"
            loading="lazy"
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
      <div className="flex flex-col flex-1 p-4 gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
              CATEGORY_COLORS[entry.category] ?? "bg-slate-100 text-slate-600"
            }`}
          >
            {entry.category}
          </span>
          {entry.year && (
            <span className="text-xs text-slate-400">{entry.year}</span>
          )}
        </div>

        <h3 className="text-lg font-bold text-slate-900 leading-snug line-clamp-2">
          {entry.title}
        </h3>

        <p className="text-sm text-slate-600 leading-relaxed line-clamp-3 flex-1">
          {entry.description}
        </p>

        <a
          href={entry.source_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="text-xs text-blue-700 hover:text-blue-900 font-medium flex items-center gap-1 underline underline-offset-2 decoration-blue-300 hover:decoration-blue-600 transition-colors mt-auto pt-1"
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
