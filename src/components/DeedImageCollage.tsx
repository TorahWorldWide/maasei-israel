"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";

const MAX_IMAGES = 10;

// A responsive collage of the still images attached to a deed, shown beneath
// the video. With 3+ pictures the first tile spans 2×2 for a classy varied
// layout. Clicking a tile opens a simple full-size lightbox; tiles whose
// image fails to load are hidden entirely.
export default function DeedImageCollage({
  images,
  title,
}: {
  images: string[];
  title: string;
}) {
  const { lang } = useLang();
  const [hidden, setHidden] = useState<Set<number>>(new Set());
  const [openSrc, setOpenSrc] = useState<string | null>(null);

  // Close the lightbox on Escape.
  useEffect(() => {
    if (!openSrc) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpenSrc(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openSrc]);

  const visible = images
    .slice(0, MAX_IMAGES)
    .map((src, i) => ({ src, i }))
    .filter(({ i }) => !hidden.has(i));

  if (visible.length === 0) return null;

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
            onClick={() => setOpenSrc(src)}
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
              onError={() =>
                setHidden((prev) => {
                  const next = new Set(prev);
                  next.add(i);
                  return next;
                })
              }
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

      {/* Lightbox — click anywhere (or Escape) to close */}
      {openSrc && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label={t(lang, "galleryLabel")}
          onClick={() => setOpenSrc(null)}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8"
          style={{ background: "rgba(5,12,28,0.9)", backdropFilter: "blur(6px)" }}
        >
          <button
            onClick={() => setOpenSrc(null)}
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
            src={openSrc}
            alt={title}
            className="max-w-full max-h-[90vh] object-contain rounded-xl shadow-2xl shadow-black/60"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
