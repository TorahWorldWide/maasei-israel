"use client";

import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import type { Entry } from "@/lib/data";

function ytId(url: string): string | null {
  const m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/);
  return m ? m[1] : null;
}

interface TheaterProps {
  entries: Entry[];
}

const ROTATE_MS = 22000; // auto-advance every 22s for embeds

export default function Theater({ entries }: TheaterProps) {
  // Featured = anything with playable video; fall back to any media; then all.
  const featured = useMemo(() => {
    const vids = entries.filter(
      (e) =>
        (e.media_type === "video_embed" && ytId(e.media_url || "")) ||
        (e.media_type === "video_upload" && e.media_url)
    );
    if (vids.length) return vids;
    const media = entries.filter((e) => e.media_url);
    return media.length ? media : entries;
  }, [entries]);

  const [idx, setIdx] = useState(0);
  const [musicOn, setMusicOn] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const current = featured[idx];

  const go = useCallback(
    (dir: number) => {
      setIdx((i) => {
        const n = featured.length;
        if (!n) return 0;
        return (i + dir + n) % n;
      });
    },
    [featured.length]
  );

  const jump = useCallback((i: number) => setIdx(i), []);

  // auto-advance for embeds (uploads advance on ended)
  useEffect(() => {
    if (!current) return;
    if (current.media_type === "video_upload") return; // handled by onEnded
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => go(1), ROTATE_MS);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [current, idx, go]);

  // keyboard arrows (RTL: ArrowRight = previous, ArrowLeft = next)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") go(1);
      else if (e.key === "ArrowLeft") go(-1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [go]);

  // music control with gentle fade
  const toggleMusic = useCallback(() => {
    const a = audioRef.current;
    if (!a) return;
    if (musicOn) {
      a.pause();
      setMusicOn(false);
    } else {
      a.volume = 0;
      a.play()
        .then(() => {
          setMusicOn(true);
          // fade in
          let v = 0;
          const id = setInterval(() => {
            v += 0.05;
            if (v >= 0.6) {
              v = 0.6;
              clearInterval(id);
            }
            a.volume = v;
          }, 120);
        })
        .catch(() => setMusicOn(false));
    }
  }, [musicOn]);

  useEffect(() => {
    return () => {
      if (audioRef.current) audioRef.current.pause();
    };
  }, []);

  if (!current) return null;

  const id = current.media_type === "video_embed" ? ytId(current.media_url || "") : null;
  const embedSrc = id
    ? `https://www.youtube.com/embed/${id}?autoplay=1&mute=1&controls=1&rel=0&modestbranding=1&playsinline=1&loop=1&playlist=${id}`
    : null;

  // The poetic two-part split that flanks the screen.
  // חלק א׳ · הניצוץ = the deed itself (the human spark).
  // חלק ב׳ · האור = the light it cast on the world.
  const spark = (current.act && current.act.trim()) || current.title;
  const light = (current.ripple && current.ripple.trim()) || current.description;

  return (
    <section className="relative bg-gradient-to-b from-blue-950 via-blue-900 to-blue-800 overflow-hidden">
      {/* faint star watermark */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none" aria-hidden="true">
        <svg viewBox="0 0 200 200" className="w-[700px] h-[700px] opacity-[0.04]">
          <polygon points="100,10 10,170 190,170" fill="none" stroke="white" strokeWidth="3" />
          <polygon points="100,190 190,30 10,30" fill="none" stroke="white" strokeWidth="3" />
        </svg>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 pt-8 pb-10">
        {/* Title row */}
        <div className="text-center mb-6">
          <p className="text-blue-300/80 text-xs font-medium uppercase tracking-[0.25em] mb-2">
            — מעשי ישראל —
          </p>
          <h1 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight">
            מעשים טובים של עם ישראל
          </h1>
        </div>

        {/* THREE-PANEL STAGE: right = חלק א׳ · הניצוץ · center = screen · left = חלק ב׳ · האור */}
        <div className="grid grid-cols-1 md:grid-cols-[1fr_minmax(0,2.3fr)_1fr] gap-4 md:gap-5 items-center">
          {/* RIGHT PANEL — חלק א׳ · הניצוץ (the deed) */}
          <aside
            key={`spark-${current.id}`}
            className="panel-rise order-2 md:order-1 text-center md:text-right"
          >
            <div className="inline-flex items-center gap-2 mb-2 text-sky-300/90">
              <span className="text-2xl leading-none" aria-hidden="true">✦</span>
              <span className="text-xs font-semibold tracking-wide">חלק א׳ · הניצוץ</span>
            </div>
            <p className="text-white text-base md:text-lg font-bold leading-relaxed">
              {spark}
            </p>
            <div className="mt-3 flex items-center gap-2 justify-center md:justify-start">
              <span className="text-[11px] bg-white/10 text-white/85 px-2.5 py-0.5 rounded-full">
                {current.category}
              </span>
              {current.year && <span className="text-blue-300/60 text-xs">{current.year}</span>}
            </div>
          </aside>

          {/* CENTER — THE THEATER SCREEN */}
          <div className="relative order-1 md:order-2">
            <div className="relative rounded-2xl overflow-hidden bg-black shadow-2xl shadow-blue-950/60 ring-1 ring-white/10 aspect-video">
              {embedSrc ? (
                <iframe
                  key={current.id}
                  src={embedSrc}
                  title={current.title}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="absolute inset-0 w-full h-full border-0"
                />
              ) : current.media_type === "video_upload" && current.media_url ? (
                <video
                  key={current.id}
                  src={current.media_url}
                  autoPlay
                  muted
                  playsInline
                  controls
                  onEnded={() => go(1)}
                  className="absolute inset-0 w-full h-full object-contain bg-black"
                />
              ) : current.media_url && current.media_type === "image" ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={current.media_url} alt={current.title} className="absolute inset-0 w-full h-full object-cover" />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center bg-blue-900/60">
                  <svg viewBox="0 0 100 100" className="w-32 h-32 opacity-20" aria-hidden="true">
                    <polygon points="50,5 5,85 95,85" fill="none" stroke="white" strokeWidth="2" />
                    <polygon points="50,95 95,15 5,15" fill="none" stroke="white" strokeWidth="2" />
                  </svg>
                </div>
              )}
            </div>

            {/* Prev / Next (RTL: right = previous) */}
            {featured.length > 1 && (
              <>
                <button
                  onClick={() => go(1)}
                  aria-label="הקודם"
                  className="absolute right-2 md:-right-4 top-1/2 -translate-y-1/2 bg-white/15 hover:bg-white/30 text-white rounded-full p-2.5 md:p-3 backdrop-blur-sm transition-colors"
                >
                  <svg className="w-5 h-5 md:w-6 md:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
                <button
                  onClick={() => go(-1)}
                  aria-label="הבא"
                  className="absolute left-2 md:-left-4 top-1/2 -translate-y-1/2 bg-white/15 hover:bg-white/30 text-white rounded-full p-2.5 md:p-3 backdrop-blur-sm transition-colors"
                >
                  <svg className="w-5 h-5 md:w-6 md:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              </>
            )}
          </div>

          {/* LEFT PANEL — חלק ב׳ · האור (its light in the world) */}
          <aside
            key={`light-${current.id}`}
            className="panel-rise-delay order-3 text-center md:text-left"
          >
            <div className="inline-flex items-center gap-2 mb-2 text-amber-200/90">
              <span className="text-2xl leading-none" aria-hidden="true">☀</span>
              <span className="text-xs font-semibold tracking-wide">חלק ב׳ · האור</span>
            </div>
            <p className="text-blue-50/90 text-sm md:text-base leading-relaxed line-clamp-6 md:line-clamp-none">
              {light}
            </p>
            <a
              href={current.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-block text-sky-300 hover:text-sky-100 text-sm underline underline-offset-2 transition-colors"
            >
              מקור: {current.source_label || "צפה בהוכחה"}
            </a>
          </aside>
        </div>

        {/* Dots + music */}
        <div className="mt-7 flex flex-col items-center gap-4">
          {/* dots */}
          {featured.length > 1 && (
            <div className="flex flex-wrap justify-center gap-2 max-w-md">
              {featured.map((e, i) => (
                <button
                  key={e.id}
                  onClick={() => jump(i)}
                  aria-label={`עבור לסרטון ${i + 1}`}
                  className={`h-2 rounded-full transition-all duration-200 ${
                    i === idx ? "w-7 bg-white" : "w-2 bg-white/30 hover:bg-white/60"
                  }`}
                />
              ))}
            </div>
          )}

          {/* Music button — prominent */}
          <button
            onClick={toggleMusic}
            className={`group flex items-center gap-2.5 px-6 py-3 rounded-full font-semibold text-sm transition-all shadow-lg ${
              musicOn
                ? "bg-white text-blue-900 shadow-white/20"
                : "bg-blue-600 text-white hover:bg-blue-500 shadow-blue-900/40"
            }`}
          >
            {musicOn ? (
              <>
                <span className="flex items-end gap-0.5 h-4" aria-hidden="true">
                  <span className="w-1 bg-blue-900 rounded-full animate-pulse" style={{ height: "60%" }} />
                  <span className="w-1 bg-blue-900 rounded-full animate-pulse" style={{ height: "100%", animationDelay: "0.15s" }} />
                  <span className="w-1 bg-blue-900 rounded-full animate-pulse" style={{ height: "40%", animationDelay: "0.3s" }} />
                </span>
                השתקת מוזיקה
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8 5v14l11-7z" />
                </svg>
                נגן מוזיקה מרגשת
              </>
            )}
          </button>
          <p className="text-blue-300/50 text-[11px]">הסרטונים מתנגנים ללא קול — הפעל מוזיקה לחוויה מלאה</p>
        </div>

        {/* scroll hint */}
        <div className="mt-8 text-center">
          <a href="#catalog" className="inline-flex flex-col items-center text-blue-200/70 hover:text-white transition-colors">
            <span className="text-sm mb-1">כל המעשים — חפש, סנן, גלה</span>
            <svg className="w-6 h-6 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </a>
        </div>
      </div>

      {/* hidden audio element */}
      <audio ref={audioRef} src="/audio/inspire.mp3" loop preload="none" />
    </section>
  );
}
