"use client";

import { useEffect, useRef, useState } from "react";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";
import { loadYouTubeApi, YT_UNPLAYABLE_ERRORS } from "@/lib/youtube";

// A YouTube player for the deed page that detects when the owner has disabled
// embedding (or the video was removed) and shows a "watch on YouTube" fallback
// instead of a dead frame.
export default function DeedVideo({
  videoId,
  watchUrl,
}: {
  videoId: string;
  watchUrl: string;
}) {
  const { lang } = useLang();
  const mountRef = useRef<HTMLDivElement | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const playerRef = useRef<any>(null);
  const [blocked, setBlocked] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setBlocked(false);
    loadYouTubeApi().then(() => {
      if (cancelled || !mountRef.current) return;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const YT = (window as any).YT;
      if (!YT || !YT.Player) return;
      if (playerRef.current) {
        try {
          playerRef.current.destroy();
        } catch {}
        playerRef.current = null;
      }
      playerRef.current = new YT.Player(mountRef.current, {
        videoId,
        width: "100%",
        height: "100%",
        playerVars: { rel: 0, modestbranding: 1, playsinline: 1 },
        events: {
          onError: (e: { data: number }) => {
            if (YT_UNPLAYABLE_ERRORS.has(e.data)) setBlocked(true);
          },
        },
      });
    });
    return () => {
      cancelled = true;
      if (playerRef.current) {
        try {
          playerRef.current.destroy();
        } catch {}
        playerRef.current = null;
      }
    };
  }, [videoId]);

  return (
    <div className="relative w-full aspect-video rounded-xl overflow-hidden mb-8 shadow-xl shadow-black/50 bg-black">
      <div ref={mountRef} className="absolute inset-0 w-full h-full" />
      {blocked && (
        <div
          className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-5 text-center px-6"
          style={{ background: "#0b1e42" }}
        >
          <svg className="w-14 h-14" viewBox="0 0 24 24" fill="none" stroke="#c9a84a" strokeWidth={1.4} aria-hidden="true">
            <rect x="2" y="5" width="20" height="14" rx="3" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 9l5 3-5 3V9z" fill="#c9a84a" />
          </svg>
          <p className="text-sm max-w-xs text-[#e6c66e]">{t(lang, "videoUnavailable")}</p>
          <a
            href={watchUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full font-semibold text-sm text-[#0a1834] transition-all hover:scale-[1.04]"
            style={{ background: "linear-gradient(to bottom, #e6c66e, #c9a84a)" }}
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M8 5v14l11-7z" />
            </svg>
            {t(lang, "watchOnYoutube")}
          </a>
        </div>
      )}
    </div>
  );
}
