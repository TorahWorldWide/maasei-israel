"use client";

import { useState } from "react";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";
import DeedVideo from "@/components/DeedVideo";

// One playable video: the 11-char YouTube id plus the original url
// (used for the "watch on YouTube" fallback when embedding is disabled).
export interface CarouselVideo {
  id: string;
  watchUrl: string;
}

// A minimal carousel for deed pages that have several videos: the embedded
// player plus slim prev/next arrows and a small counter. With a single video
// it renders the plain player — identical to the pre-carousel behavior.
// RTL convention (matching Theater/Slideshow): prev sits on the right with a
// right-pointing chevron, next on the left with a left-pointing chevron.
export default function DeedVideoCarousel({
  videos,
}: {
  videos: CarouselVideo[];
}) {
  const { lang } = useLang();
  const [index, setIndex] = useState(0);

  if (videos.length === 0) return null;
  const current = videos[Math.min(index, videos.length - 1)];

  const go = (delta: number) =>
    setIndex((i) => (i + delta + videos.length) % videos.length);

  if (videos.length === 1) {
    return <DeedVideo videoId={current.id} watchUrl={current.watchUrl} />;
  }

  return (
    <div>
      {/* key forces a clean player remount when the video swaps */}
      <DeedVideo key={current.id} videoId={current.id} watchUrl={current.watchUrl} />

      {/* Slim control row: prev (right) · counter · next (left) */}
      <div className="flex items-center justify-center gap-5 -mt-4 mb-8">
        <button
          onClick={() => go(-1)}
          aria-label={t(lang, "ariaPrev")}
          className="rounded-full p-2 transition-all hover:scale-110"
          style={{
            background: "rgba(201,168,74,0.12)",
            color: "#e6c66e",
            border: "1px solid rgba(201,168,74,0.35)",
          }}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
        <span
          dir="ltr"
          className="text-xs text-blue-200/60 tabular-nums select-none"
          data-testid="video-counter"
        >
          {index + 1}/{videos.length}
        </span>
        <button
          onClick={() => go(1)}
          aria-label={t(lang, "ariaNext")}
          className="rounded-full p-2 transition-all hover:scale-110"
          style={{
            background: "rgba(201,168,74,0.12)",
            color: "#e6c66e",
            border: "1px solid rgba(201,168,74,0.35)",
          }}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
