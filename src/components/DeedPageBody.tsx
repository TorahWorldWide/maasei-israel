"use client";

import Link from "next/link";
import { useLang } from "@/components/LangProvider";
import { t, pick, categoryLabel, locatorLabel } from "@/lib/i18n";
import ShareProof from "@/components/ShareProof";
import DeedVideoCarousel, { type CarouselVideo } from "@/components/DeedVideoCarousel";
import DeedImageCollage from "@/components/DeedImageCollage";
import type { Entry } from "@/lib/data";
import { entryCategories } from "@/lib/data";
import { ytId as extractYouTubeId } from "@/lib/youtube";
import { eraOf, eraDisplay } from "@/lib/era";

// A labelled block of prose. Blank lines in the text are real paragraph breaks.
function Section({ label, text, inGrid }: { label: string; text?: string; inGrid?: boolean }) {
  if (!text) return null;
  const paragraphs = text.split(/\n\s*\n/).filter((p) => p.trim());
  return (
    <div
      className={`bg-[#0f234d]/60 rounded-xl p-4 border border-[rgba(201,168,74,0.15)]${inGrid ? "" : " mb-8"}`}
    >
      <p className="text-xs text-[#c9a84a] font-medium mb-1">{label}</p>
      <div className="flex flex-col gap-3">
        {paragraphs.map((p, i) => (
          <p key={i} className="text-sm text-blue-100/80 leading-relaxed">
            {p}
          </p>
        ))}
      </div>
    </div>
  );
}

// Two short blocks read well side by side; two essays do not.
function sideBySide(act?: string, ripple?: string): boolean {
  return (act?.length ?? 0) <= 400 && (ripple?.length ?? 0) <= 400;
}

export default function DeedPageBody({ entry }: { entry: Entry }) {
  const { lang } = useLang();
  const era = eraOf(entry.year);

  // Video entries: media_urls may hold a MIX of extra YouTube videos and still
  // images. Split by whether a YouTube id can be extracted — anything that is
  // not a YouTube url is treated as an image for the collage.
  // The video list is the master media_url (always first) plus every YouTube
  // url from media_urls, deduplicated by video id.
  const videos: CarouselVideo[] = [];
  const extraImages: string[] = [];
  if (entry.media_type === "video_embed") {
    const seen = new Set<string>();
    const masterId = entry.media_url ? extractYouTubeId(entry.media_url) : null;
    if (masterId) {
      seen.add(masterId);
      videos.push({ id: masterId, watchUrl: entry.media_url });
    }
    for (const url of entry.media_urls ?? []) {
      if (!url) continue;
      const id = extractYouTubeId(url);
      if (id) {
        if (!seen.has(id)) {
          seen.add(id);
          videos.push({ id, watchUrl: url });
        }
      } else {
        extraImages.push(url);
      }
    }
  }

  // Image entries: prefer the multi-image gallery, fall back to the single url.
  const images =
    entry.media_type === "image"
      ? (entry.media_urls && entry.media_urls.length > 0
          ? entry.media_urls
          : entry.media_url
            ? [entry.media_url]
            : [])
      : [];

  return (
    <main className="flex-1 w-full">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-12">
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
          {entryCategories(entry).map((cat) => (
            <span key={cat} className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-[#c9a84a]/15 text-[#e6c66e] border border-[#c9a84a]/25">
              {categoryLabel(lang, cat)}
            </span>
          ))}
          {entry.year && (
            <span className="text-xs text-blue-200/45">{entry.year}</span>
          )}
          {era && (
            <Link
              href={`/?era=${era.key}`}
              dir="ltr"
              className="text-[11px] text-blue-200/30 hover:text-sky-200 transition-colors"
            >
              {eraDisplay(era)}
            </Link>
          )}
        </div>

        {/* Title */}
        <h1
          className="text-3xl md:text-4xl font-extrabold text-[#e6c66e] leading-tight mb-6"
          style={{ fontFamily: "var(--font-frank-ruhl), serif" }}
        >
          {pick(lang, entry.title, entry.title_en)}
        </h1>

      </div>

      {/* All media — video player, collage, image gallery — lives in a wider
          container than the text column so it can spread toward the sides. */}
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6">
        {/* Video(s) — single player, or a carousel with arrows + counter when
            media_urls holds more videos. Graceful fallback when embedding is
            disabled is handled inside DeedVideo. */}
        {videos.length > 0 && <DeedVideoCarousel videos={videos} />}

        {/* Still images attached to a video entry — collage under the player. */}
        {extraImages.length > 0 && (
          <DeedImageCollage images={extraImages} title={pick(lang, entry.title, entry.title_en)} />
        )}

        {/* Image(s) — shown when there is no video. One image fills the frame;
            several render as a responsive gallery. */}
        {images.length > 0 && (
          <div
            className={
              images.length === 1
                ? "w-full rounded-xl overflow-hidden mb-8 shadow-xl shadow-black/50"
                : "grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8"
            }
          >
            {images.map((src, i) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                key={i}
                src={src}
                alt={`${pick(lang, entry.title, entry.title_en)}${images.length > 1 ? ` (${i + 1})` : ""}`}
                className={
                  images.length === 1
                    ? "w-full max-h-[70vh] object-cover rounded-xl"
                    : "w-full h-72 object-cover rounded-xl shadow-lg shadow-black/40"
                }
                loading="lazy"
              />
            ))}
          </div>
        )}
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 pb-12">
        {/* Description */}
        <p className="text-base text-blue-100/80 leading-relaxed mb-8">
          {pick(lang, entry.description, entry.description_en)}
        </p>

        {/* How it began */}
        <Section label={t(lang, "originLabel")} text={pick(lang, entry.origin_story, entry.origin_story_en)} />

        {/* Act / Ripple — side by side while both are short, stacked once they are prose */}
        {(entry.act || entry.ripple) && (
          <div
            className={
              sideBySide(pick(lang, entry.act, entry.act_en), pick(lang, entry.ripple, entry.ripple_en))
                ? "grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8"
                : "flex flex-col gap-4 mb-8"
            }
          >
            <Section inGrid label={t(lang, "actLabel")} text={pick(lang, entry.act, entry.act_en)} />
            <Section inGrid label={t(lang, "rippleLabel")} text={pick(lang, entry.ripple, entry.ripple_en)} />
          </div>
        )}

        {/* What happened next · what they got for it */}
        <Section label={t(lang, "aftermathLabel")} text={pick(lang, entry.aftermath, entry.aftermath_en)} />
        <Section label={t(lang, "recognitionLabel")} text={pick(lang, entry.recognition, entry.recognition_en)} />

        {/* Honors in their name */}
        {entry.honors && entry.honors.length > 0 && (
          <div className="bg-[#0f234d]/60 rounded-xl p-4 border border-[rgba(201,168,74,0.15)] mb-8">
            <p className="text-xs text-[#c9a84a] font-medium mb-2">{t(lang, "honorsLabel")}</p>
            <ul className="flex flex-col gap-1.5">
              {entry.honors.map((h, i) => (
                <li key={i} className="text-sm text-blue-100/80">
                  {h.source ? (
                    <a
                      href={h.source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-[#e6c66e] transition-colors"
                    >
                      {h.what}
                    </a>
                  ) : (
                    h.what
                  )}
                  {h.year ? <span className="text-blue-200/50"> · {h.year}</span> : null}
                </li>
              ))}
            </ul>
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
                  {lang === "en" && c.quote_en ? (
                    <blockquote className="text-xs text-blue-200/65 italic mb-2">
                      &ldquo;{c.quote_en}&rdquo;
                    </blockquote>
                  ) : null}
                  <a
                    href={c.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-[#c9a84a] hover:text-[#e6c66e] underline underline-offset-2 decoration-[#c9a84a]/40 hover:decoration-[#c9a84a] transition-colors"
                  >
                    — {pick(lang, c.source_label, c.source_label_en)}
                    {locatorLabel(lang, c.locator, c.locator_en) &&
                      `, ${locatorLabel(lang, c.locator, c.locator_en)}`}
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
            {t(lang, "source")}: {pick(lang, entry.source_label, entry.source_label_en) || entry.source_url}
          </a>
          <ShareProof entry={entry} />
        </div>
      </div>
    </main>
  );
}
