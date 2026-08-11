"use client";

import { useEffect, useMemo, useState } from "react";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";
import type { ImageProvenance } from "@/lib/data";

// Rule 8 lets a deed carry up to 20 pictures when all of them are good.
const MAX_IMAGES = 20;

type Item = { src: string; i: number; prov?: ImageProvenance };

const clean = (v?: string | null) => (v && String(v).trim() ? String(v).trim() : undefined);

function captionOf(lang: string, p?: ImageProvenance) {
  if (!p) return undefined;
  return lang === "en"
    ? clean(p.caption_en) ?? clean(p.caption_he)
    : clean(p.caption_he) ?? clean(p.caption_en);
}

function groupOf(lang: string, p?: ImageProvenance) {
  if (!p) return undefined;
  return lang === "en"
    ? clean(p.group_en) ?? clean(p.group)
    : clean(p.group) ?? clean(p.group_en);
}

function creditOf(p?: ImageProvenance) {
  if (!p) return undefined;
  const who = clean(p.credit) ?? clean(p.credit_line) ?? clean(p.photographer);
  const when = clean(p.shot_when) ?? clean(p.date) ?? clean(p.year as string);
  return [when, who].filter(Boolean).join(" · ") || undefined;
}

// A responsive collage of the still images attached to a deed. When the entry
// carries image provenance (rules 44–46) the pictures are laid out by group —
// each group under its own heading, each picture over its caption, on the
// phone exactly as on the desktop. Without provenance the plain grid is kept.
// Clicking a tile opens a lightbox with the full caption; tiles whose image
// fails to load are hidden entirely.
export default function DeedImageCollage({
  images,
  title,
  provenance,
}: {
  images: string[];
  title: string;
  provenance?: ImageProvenance[];
}) {
  const { lang } = useLang();
  const [hidden, setHidden] = useState<Set<number>>(new Set());
  const [openIdx, setOpenIdx] = useState<number | null>(null);

  // Close the lightbox on Escape.
  useEffect(() => {
    if (openIdx === null) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpenIdx(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openIdx]);

  const byUrl = useMemo(() => {
    const m = new Map<string, ImageProvenance>();
    for (const p of provenance ?? []) {
      if (!p?.url) continue;
      m.set(p.url, p);
      try {
        m.set(decodeURI(p.url), p);
      } catch {
        // Malformed escape sequence — the raw key above still matches.
      }
    }
    return m;
  }, [provenance]);

  const visible: Item[] = images
    .slice(0, MAX_IMAGES)
    .map((src, i) => ({ src, i, prov: byUrl.get(src) }))
    .filter(({ i }) => !hidden.has(i));

  const hide = (i: number) => setHidden((prev) => new Set(prev).add(i));

  const open = visible.find((it) => it.i === openIdx);
  const openCaption = captionOf(lang, open?.prov);
  const openCredit = creditOf(open?.prov);

  const lightbox =
    openIdx === null || !open ? null : (
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t(lang, "galleryLabel")}
        onClick={() => setOpenIdx(null)}
        className="fixed inset-0 z-50 flex flex-col items-center justify-center p-4 sm:p-8"
        style={{ background: "rgba(5,12,28,0.9)", backdropFilter: "blur(6px)" }}
      >
        <button
          onClick={() => setOpenIdx(null)}
          aria-label={t(lang, "ariaClose")}
          className="absolute top-4 left-4 rounded-full p-2.5 transition-all hover:scale-110"
          style={{
            background: "rgba(201,168,74,0.16)",
            color: "#e6c66e",
            border: "1px solid rgba(201,168,74,0.4)",
          }}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={open.src}
          alt={openCaption ?? title}
          className="max-w-full max-h-[76vh] object-contain rounded-xl shadow-2xl shadow-black/60"
          onClick={(e) => e.stopPropagation()}
        />
        {(openCaption || openCredit) && (
          <div onClick={(e) => e.stopPropagation()} className="mt-4 max-w-2xl text-center">
            {openCaption && (
              <p className="text-sm text-blue-50/90 leading-relaxed">{openCaption}</p>
            )}
            {openCredit && (
              <p className="mt-1.5 text-[11px] text-blue-200/50">{openCredit}</p>
            )}
          </div>
        )}
      </div>
    );

  if (visible.length === 0) return null;

  const captioned = visible.some(
    (it) => captionOf(lang, it.prov) || groupOf(lang, it.prov)
  );

  // ── Plain collage — entries that carry no provenance yet ──────────────────
  if (!captioned) {
    const many = visible.length >= 3;
    return (
      <>
        <div
          role="group"
          aria-label={t(lang, "galleryLabel")}
          data-testid="image-collage"
          className={
            visible.length === 1
              ? "mb-8"
              : many
                ? "grid grid-cols-2 sm:grid-cols-3 auto-rows-[9rem] sm:auto-rows-[12rem] lg:auto-rows-[14rem] gap-3 sm:gap-4 mb-8"
                : "grid grid-cols-2 gap-3 sm:gap-4 mb-8"
          }
        >
          {visible.map(({ src, i }, pos) => (
            <button
              key={i}
              type="button"
              onClick={() => setOpenIdx(i)}
              aria-label={t(lang, "ariaOpenImage")}
              className={`group relative block w-full overflow-hidden rounded-xl shadow-lg shadow-black/40 border border-[rgba(201,168,74,0.15)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#c9a84a] ${
                many && pos === 0 ? "col-span-2 row-span-2" : ""
              }`}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={src}
                alt={`${title}${images.length > 1 ? ` (${i + 1})` : ""}`}
                loading="lazy"
                onError={() => hide(i)}
                className={
                  visible.length === 1
                    ? "w-full max-h-[55vh] object-cover transition-transform duration-300 group-hover:scale-[1.02]"
                    : many
                      ? "absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
                      : "w-full h-64 sm:h-80 object-cover transition-transform duration-300 group-hover:scale-[1.03]"
                }
              />
            </button>
          ))}
        </div>
        {lightbox}
      </>
    );
  }

  // ── Captioned collage — consecutive pictures that share a group travel
  //    together under one heading (rule 45); a picture standing on its own
  //    gets the full width and its own line of explanation (rules 44, 46).
  const runs: { group?: string; items: Item[] }[] = [];
  for (const it of visible) {
    const g = groupOf(lang, it.prov);
    const last = runs[runs.length - 1];
    if (g && last && last.group === g) last.items.push(it);
    else runs.push({ group: g, items: [it] });
  }

  const Tile = ({ item, wide }: { item: Item; wide?: boolean }) => {
    const caption = captionOf(lang, item.prov);
    const credit = creditOf(item.prov);
    return (
      <figure className="flex flex-col">
        <button
          type="button"
          onClick={() => setOpenIdx(item.i)}
          aria-label={t(lang, "ariaOpenImage")}
          className="group relative block w-full overflow-hidden rounded-xl shadow-lg shadow-black/40 border border-[rgba(201,168,74,0.15)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#c9a84a]"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={item.src}
            alt={caption ?? title}
            loading="lazy"
            onError={() => hide(item.i)}
            className={
              // A picture standing on its own is shown whole: cropping a wide
              // frame to a fixed height cuts the head off a portrait.
              wide
                ? "mx-auto w-auto max-w-full max-h-[65vh] object-contain transition-transform duration-300 group-hover:scale-[1.02]"
                : "w-full h-36 sm:h-52 lg:h-60 object-cover transition-transform duration-300 group-hover:scale-[1.03]"
            }
          />
        </button>
        {(caption || credit) && (
          <figcaption className="mt-2 px-0.5">
            {caption && (
              <p className="text-[11px] sm:text-xs text-blue-100/70 leading-snug line-clamp-3">
                {caption}
              </p>
            )}
            {credit && (
              <p className="mt-1 text-[10px] sm:text-[11px] text-blue-200/40 line-clamp-1">
                {credit}
              </p>
            )}
          </figcaption>
        )}
      </figure>
    );
  };

  return (
    <>
      <div
        role="group"
        aria-label={t(lang, "galleryLabel")}
        data-testid="image-collage"
        className="mb-8 flex flex-col gap-7 sm:gap-9"
      >
        {runs.map((run, ri) => (
          <section key={ri}>
            {run.group && (
              <h3 className="flex items-center gap-3 mb-3 text-xs sm:text-sm font-medium text-[#c9a84a]">
                <span>{run.group}</span>
                <span aria-hidden="true" className="flex-1 h-px bg-[rgba(201,168,74,0.22)]" />
              </h3>
            )}
            {run.items.length === 1 ? (
              <Tile item={run.items[0]} wide={!run.group} />
            ) : (
              <div
                className={`grid grid-cols-2 gap-3 sm:gap-4 ${
                  run.items.length > 2 ? "lg:grid-cols-3" : ""
                }`}
              >
                {run.items.map((item) => (
                  <Tile key={item.i} item={item} />
                ))}
              </div>
            )}
          </section>
        ))}
      </div>
      {lightbox}
    </>
  );
}
