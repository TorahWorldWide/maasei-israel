"use client";

import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import type { CSSProperties } from "react";
import type { Entry } from "@/lib/data";
import { entryCategories } from "@/lib/data";
import { useLang } from "@/components/LangProvider";
import { t, pick, categoryLabel } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { ytId, loadYouTubeApi, YT_UNPLAYABLE_ERRORS } from "@/lib/youtube";
import Slideshow from "./Slideshow";

interface TheaterProps {
  entries: Entry[];
}

// Four moods — totally different feels. Mood 1 is the default (the one Tomer liked).
const MOODS = [
  { num: 1, key: "mood1" as const, file: "/audio/inspire.mp3" },
  { num: 2, key: "mood2" as const, file: "/audio/uplift.mp3" },
  { num: 3, key: "mood3" as const, file: "/audio/calm.mp3" },
  { num: 4, key: "mood4" as const, file: "/audio/epic.mp3" },
];

function moodLabel(lang: Lang, i: number): string {
  return t(lang, MOODS[i].key);
}

const GOLD = "#c9a84a";
const GOLD_BRIGHT = "#e6c66e";
const CLAMP: CSSProperties = {
  display: "-webkit-box",
  WebkitBoxOrient: "vertical",
  WebkitLineClamp: 9,
  overflow: "hidden",
};

export default function Theater({ entries }: TheaterProps) {
  const { lang } = useLang();
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
  // Video ids that failed to embed (owner-disabled / removed) — we swap in a
  // "watch on YouTube" fallback and skip past them so the stage keeps flowing.
  const [blocked, setBlocked] = useState<Record<string, true>>({});
  const [musicOn, setMusicOn] = useState(false);
  const [trackIdx, setTrackIdx] = useState(0);
  const [pickerHover, setPickerHover] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fadeRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // YouTube player: mount target div + the player instance + a stable ref to `go`.
  const ytMountRef = useRef<HTMLDivElement | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ytPlayerRef = useRef<any>(null);
  const goRef = useRef<(dir: number) => void>(() => {});

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

  // keep a stable ref so the YT event callback always calls the latest `go`
  useEffect(() => {
    goRef.current = go;
  }, [go]);

  const currentYtId =
    current && current.media_type === "video_embed" ? ytId(current.media_url || "") : null;
  const isBlocked = !!(currentYtId && blocked[currentYtId]);

  // YouTube embeds: build a real Player so we know when the video ENDS, and only
  // then advance. No timer — videos play to their natural end. Manual arrows/dots
  // still work anytime. (Uploaded videos advance via the <video> onEnded handler.)
  useEffect(() => {
    if (!currentYtId) {
      // tearing down (non-YT slide) — destroy any existing player
      if (ytPlayerRef.current) {
        try {
          ytPlayerRef.current.destroy();
        } catch {}
        ytPlayerRef.current = null;
      }
      return;
    }
    let cancelled = false;
    loadYouTubeApi().then(() => {
      if (cancelled || !ytMountRef.current) return;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const YT = (window as any).YT;
      if (!YT || !YT.Player) return;
      // Destroy previous player before building a new one.
      if (ytPlayerRef.current) {
        try {
          ytPlayerRef.current.destroy();
        } catch {}
        ytPlayerRef.current = null;
      }
      ytPlayerRef.current = new YT.Player(ytMountRef.current, {
        videoId: currentYtId,
        width: "100%",
        height: "100%",
        playerVars: {
          autoplay: 1,
          mute: 1,
          controls: 1,
          rel: 0,
          modestbranding: 1,
          playsinline: 1,
        },
        events: {
          onStateChange: (e: { data: number }) => {
            // 0 === YT.PlayerState.ENDED → advance to the next video
            if (e.data === 0) goRef.current(1);
          },
          onError: (e: { data: number }) => {
            // Owner disabled embedding / video removed → show fallback + skip.
            if (YT_UNPLAYABLE_ERRORS.has(e.data) && currentYtId) {
              setBlocked((prev) => (prev[currentYtId] ? prev : { ...prev, [currentYtId]: true }));
            }
          },
        },
      });
    });
    return () => {
      cancelled = true;
      if (ytPlayerRef.current) {
        try {
          ytPlayerRef.current.destroy();
        } catch {}
        ytPlayerRef.current = null;
      }
    };
  }, [currentYtId]);

  // keyboard arrows (RTL: ArrowRight = previous, ArrowLeft = next).
  // Disabled while the depth modal is open — it owns the keyboard then.
  useEffect(() => {
    if (modalOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") go(1);
      else if (e.key === "ArrowLeft") go(-1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [go, modalOpen]);

  // A blocked (un-embeddable) video can't play — after a short beat, move on so
  // the stage never gets stuck. Only when there's somewhere else to go.
  useEffect(() => {
    if (!isBlocked || featured.length <= 1 || modalOpen) return;
    const tid = setTimeout(() => goRef.current(1), 6500);
    return () => clearTimeout(tid);
  }, [isBlocked, featured.length, modalOpen, current?.id]);

  const fadeTo = useCallback((target: number) => {
    const a = audioRef.current;
    if (!a) return;
    if (fadeRef.current) clearInterval(fadeRef.current);
    fadeRef.current = setInterval(() => {
      const diff = target - a.volume;
      if (Math.abs(diff) < 0.06) {
        a.volume = target;
        if (fadeRef.current) clearInterval(fadeRef.current);
        return;
      }
      a.volume = Math.min(1, Math.max(0, a.volume + (diff > 0 ? 0.05 : -0.07)));
    }, 110);
  }, []);

  // Play a specific mood (switch track + play with fade).
  const playMood = useCallback(
    (i: number) => {
      const a = audioRef.current;
      if (!a) return;
      const changing = i !== trackIdx;
      setTrackIdx(i);
      if (changing) {
        a.src = MOODS[i].file;
      }
      a.volume = 0;
      a.play()
        .then(() => {
          setMusicOn(true);
          fadeTo(0.6);
        })
        .catch(() => setMusicOn(false));
    },
    [trackIdx, fadeTo]
  );

  // Main button: toggle play/pause. Turning ON plays the current mood AND
  // (because musicOn becomes true) reveals the 4 mood buttons.
  const toggleMusic = useCallback(() => {
    const a = audioRef.current;
    if (!a) return;
    if (musicOn) {
      a.pause();
      setMusicOn(false);
    } else {
      playMood(trackIdx);
    }
  }, [musicOn, trackIdx, playMood]);

  // Open the depth modal on the current deed; pause the ambient music so the
  // deed's own video/audio isn't fighting it.
  const openModal = useCallback(() => {
    const a = audioRef.current;
    if (a && musicOn) {
      a.pause();
      setMusicOn(false);
    }
    setModalOpen(true);
  }, [musicOn]);

  useEffect(() => {
    return () => {
      if (fadeRef.current) clearInterval(fadeRef.current);
      if (audioRef.current) audioRef.current.pause();
    };
  }, []);

  if (!current) return null;

  // Show the 4 mood buttons whenever playing, or while hovering the control (desktop).
  const showPicker = musicOn || pickerHover;

  // Poetic two-part split shown in the rails flanking the screen (desktop only).
  // The side panels are a teaser; the deed page carries the full text, which
  // since the standard pass can run to several paragraphs.
  const spark = pick(lang, current.act, current.act_en);
  const light = pick(lang, current.ripple, current.ripple_en);

  return (
    <section className="stage relative overflow-hidden">
      {/* stage lighting — dimmed house */}
      <div className="stage-beam stage-beam-r" aria-hidden="true" />
      <div className="stage-beam stage-beam-l" aria-hidden="true" />
      <div className="stage-haze" aria-hidden="true" />
      <div className="stage-vignette" aria-hidden="true" />

      <div className="relative z-10 mx-auto px-0 sm:px-6 pt-6 sm:pt-8 md:pt-9 pb-10">
        {/* THE STAGE — title crowns it, the screen is the show, story sits below.
            On wide desktops the poetic spark/light flank the screen in the margins. */}
        <div className="mx-auto xl:grid xl:items-center xl:gap-8 xl:max-w-[1640px] xl:[grid-template-columns:minmax(0,1fr)_auto_minmax(0,1fr)]">
          {/* SPARK — reading-start side; flips automatically with dir (rtl/ltr) */}
          <aside key={`spark-${current.id}`} className="hidden xl:block justify-self-end max-w-[17rem] panel-rise" style={{ textAlign: "end" }}>
            {spark && (
              <div className="pe-6" style={{ borderInlineEnd: "1px solid rgba(201,168,74,0.22)" }}>
                <p className="text-[11px] tracking-[0.14em] uppercase mb-2.5" style={{ color: GOLD }}>
                  {t(lang, "actLabel")}
                </p>
                <p className="text-[13.5px] leading-relaxed text-blue-100/70" style={CLAMP}>{spark}</p>
              </div>
            )}
          </aside>

        <div className="relative mx-auto" style={{ maxWidth: "min(100vw, 1240px, calc((100vh - 20rem) * 16 / 9))" }}>
          {/* TITLE — crowning the screen */}
          <div key={`ttl-${current.id}`} className="panel-rise mb-4 sm:mb-5 px-4 text-center">
            <div className="flex items-center justify-center gap-x-2.5 gap-y-1 flex-wrap">
              {entryCategories(current).map((cat) => (
                <span
                  key={cat}
                  className="text-[11px] px-2.5 py-0.5 rounded-full flex-shrink-0"
                  style={{ color: GOLD_BRIGHT, background: "rgba(201,168,74,0.12)", border: "1px solid rgba(201,168,74,0.3)" }}
                >
                  {categoryLabel(lang, cat)}
                </span>
              ))}
              <h2
                className="text-lg md:text-3xl font-bold leading-tight"
                style={{ fontFamily: "var(--font-frank-ruhl), serif", color: GOLD_BRIGHT }}
                title={pick(lang, current.title, current.title_en)}
              >
                {pick(lang, current.title, current.title_en)}
              </h2>
              {current.year && <span className="text-blue-300/55 text-xs flex-shrink-0">{current.year}</span>}
            </div>
          </div>

          {/* the screen + arrows (arrows centered on the screen itself) */}
          <div className="relative">
            {featured.length > 1 && (
              <>
                <button
                  onClick={() => go(1)}
                  aria-label={t(lang, "ariaPrev")}
                  className="absolute z-30 right-1 sm:right-2 md:-right-6 top-1/2 -translate-y-1/2 rounded-full p-3 md:p-4 backdrop-blur-sm transition-all hover:scale-110"
                  style={{ background: "rgba(201,168,74,0.16)", color: GOLD_BRIGHT, border: "1px solid rgba(201,168,74,0.4)" }}
                >
                  <svg className="w-7 h-7 md:w-9 md:h-9" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
                <button
                  onClick={() => go(-1)}
                  aria-label={t(lang, "ariaNext")}
                  className="absolute z-30 left-1 sm:left-2 md:-left-6 top-1/2 -translate-y-1/2 rounded-full p-3 md:p-4 backdrop-blur-sm transition-all hover:scale-110"
                  style={{ background: "rgba(201,168,74,0.16)", color: GOLD_BRIGHT, border: "1px solid rgba(201,168,74,0.4)" }}
                >
                  <svg className="w-7 h-7 md:w-9 md:h-9" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              </>
            )}

            <div className="screen-glow relative rounded-none sm:rounded-2xl overflow-hidden bg-black aspect-video">
              {currentYtId ? (
                <div key={current.id} className="absolute inset-0 w-full h-full">
                  <div ref={ytMountRef} className="w-full h-full" />
                </div>
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
                <img src={current.media_url} alt={pick(lang, current.title, current.title_en)} className="absolute inset-0 w-full h-full object-cover" />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center" style={{ background: "#0f234d" }}>
                  <svg viewBox="0 0 100 100" className="w-32 h-32" style={{ opacity: 0.25 }} aria-hidden="true">
                    <polygon points="50,5 5,85 95,85" fill="none" stroke={GOLD} strokeWidth="2" />
                    <polygon points="50,95 95,15 5,15" fill="none" stroke={GOLD} strokeWidth="2" />
                  </svg>
                </div>
              )}

              {/* video can't be embedded (owner-disabled / removed) → graceful fallback */}
              {isBlocked && (
                <div className="absolute inset-0 z-[15] flex flex-col items-center justify-center gap-5 text-center px-6" style={{ background: "#0b1e42" }}>
                  <svg className="w-14 h-14" viewBox="0 0 24 24" fill="none" stroke={GOLD} strokeWidth={1.4} aria-hidden="true">
                    <rect x="2" y="5" width="20" height="14" rx="3" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M10 9l5 3-5 3V9z" fill={GOLD} />
                  </svg>
                  <p className="text-sm max-w-xs" style={{ color: GOLD_BRIGHT }}>{t(lang, "videoUnavailable")}</p>
                  <a
                    href={current.media_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full font-semibold text-sm transition-all hover:scale-[1.04]"
                    style={{ background: `linear-gradient(to bottom, ${GOLD_BRIGHT}, ${GOLD})`, color: "#0a1834" }}
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" /></svg>
                    {t(lang, "watchOnYoutube")}
                  </a>
                </div>
              )}

              {/* expand → depth modal (sits above the iframe so the corner stays clickable) */}
              <button
                onClick={openModal}
                aria-label={t(lang, "ariaExpand")}
                className="absolute z-20 top-3 left-3 rounded-full p-2 backdrop-blur-md transition-all hover:scale-110"
                style={{ background: "rgba(10,24,52,0.7)", color: GOLD_BRIGHT, border: "1px solid rgba(201,168,74,0.4)" }}
              >
                <svg className="w-4 h-4 md:w-5 md:h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              </button>

              {/* position counter — scales to any number of deeds (replaces the dots) */}
              <div
                className="absolute z-20 top-3 right-3 text-[11px] tabular-nums px-2.5 py-1 rounded-full backdrop-blur-md"
                style={{ background: "rgba(10,24,52,0.7)", color: GOLD_BRIGHT, border: "1px solid rgba(201,168,74,0.3)" }}
              >
                {idx + 1} / {featured.length}
              </div>
            </div>
            {/* footlight glow spilling up from the floor */}
            <div className="footlight" aria-hidden="true" />
          </div>
        </div>

          {/* LIGHT — reading-end side */}
          <aside key={`light-${current.id}`} className="hidden xl:block justify-self-start max-w-[17rem] panel-rise" style={{ textAlign: "start" }}>
            {light && (
              <div className="ps-6" style={{ borderInlineStart: "1px solid rgba(201,168,74,0.22)" }}>
                <p className="text-[11px] tracking-[0.14em] uppercase mb-2.5" style={{ color: GOLD }}>
                  {t(lang, "rippleLabel")}
                </p>
                <p className="text-[13.5px] leading-relaxed text-blue-100/70" style={CLAMP}>{light}</p>
              </div>
            )}
          </aside>
        </div>

        {/* STORY — the full explanation, right under the screen */}
        <div
          key={`desc-${current.id}`}
          className="panel-rise mt-5 sm:mt-6 mx-auto max-w-2xl px-5 text-center"
        >
          {current.description && (
            <p className="text-[15px] sm:text-base leading-relaxed text-blue-100/80">
              {pick(lang, current.description, current.description_en)}
            </p>
          )}

          <button
            onClick={openModal}
            className="mt-4 inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full font-semibold text-sm transition-all hover:scale-[1.04]"
            style={{ background: `linear-gradient(to bottom, ${GOLD_BRIGHT}, ${GOLD})`, color: "#0a1834", boxShadow: "0 8px 22px -10px rgba(201,168,74,0.5)" }}
          >
            {t(lang, "proofAndSources")}
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        {/* music */}
        <div className="mt-7 flex flex-col items-center gap-4">
          {/* Music control — main button + 4-mood picker */}
          <div
            className="relative flex flex-col items-center"
            onMouseEnter={() => setPickerHover(true)}
            onMouseLeave={() => setPickerHover(false)}
          >
            <div
              className={`flex items-center gap-2 mb-3 transition-all duration-200 ${
                showPicker ? "opacity-100 translate-y-0 pointer-events-auto" : "opacity-0 translate-y-2 pointer-events-none"
              }`}
              aria-hidden={!showPicker}
            >
              {MOODS.map((m, i) => {
                const active = musicOn && i === trackIdx;
                return (
                  <button
                    key={m.num}
                    onClick={() => playMood(i)}
                    className={`flex flex-col items-center justify-center rounded-xl px-3 py-2 min-w-[3.4rem] transition-all ${showPicker ? "pop-in" : ""}`}
                    style={{
                      animationDelay: `${i * 0.05}s`,
                      background: active
                        ? `linear-gradient(to bottom, ${GOLD_BRIGHT}, ${GOLD})`
                        : "rgba(15,35,77,0.85)",
                      color: active ? "#0a1834" : GOLD_BRIGHT,
                      border: `1px solid ${active ? GOLD : "rgba(201,168,74,0.3)"}`,
                    }}
                    aria-label={`${t(lang, "playMusic")} ${m.num} — ${moodLabel(lang, i)}`}
                  >
                    <span className="text-base font-bold leading-none">{m.num}</span>
                    <span className="text-[10px] mt-0.5 leading-none">{moodLabel(lang, i)}</span>
                  </button>
                );
              })}
            </div>

            <button
              onClick={toggleMusic}
              className="group flex items-center gap-2.5 px-6 py-3 rounded-full font-semibold text-sm transition-all shadow-lg"
              style={
                musicOn
                  ? { background: `linear-gradient(to bottom, ${GOLD_BRIGHT}, ${GOLD})`, color: "#0a1834", boxShadow: "0 10px 30px -8px rgba(201,168,74,0.5)" }
                  : { background: "rgba(201,168,74,0.14)", color: GOLD_BRIGHT, border: `1px solid ${GOLD}` }
              }
            >
              {musicOn ? (
                <>
                  <span className="flex items-end gap-0.5 h-4" aria-hidden="true">
                    <span className="w-1 rounded-full animate-pulse" style={{ height: "60%", background: "#0a1834" }} />
                    <span className="w-1 rounded-full animate-pulse" style={{ height: "100%", background: "#0a1834", animationDelay: "0.15s" }} />
                    <span className="w-1 rounded-full animate-pulse" style={{ height: "40%", background: "#0a1834", animationDelay: "0.3s" }} />
                  </span>
                  {t(lang, "nowPlaying")} · {moodLabel(lang, trackIdx)}
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                  {t(lang, "playMusic")}
                </>
              )}
            </button>
          </div>
        </div>

        {/* scroll hint — minimal */}
        <div className="mt-6 text-center">
          <a href="#catalog" className="inline-flex flex-col items-center transition-colors" style={{ color: "rgba(201,168,74,0.6)" }}>
            <span className="text-xs mb-0.5">{t(lang, "allDeeds")}</span>
            <svg className="w-5 h-5 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </a>
        </div>
      </div>

      {/* depth modal — the "separate window" for going deep (media + description + citations) */}
      {modalOpen && (
        <Slideshow entries={featured} initialIndex={idx} onClose={() => setModalOpen(false)} />
      )}

      {/* hidden audio element — src starts on mood 1, swapped when switching */}
      <audio ref={audioRef} src={MOODS[0].file} loop preload="none" />
    </section>
  );
}
