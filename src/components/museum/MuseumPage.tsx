"use client";

import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import type {
  MuseumDisagreement,
  MuseumMedia,
  MuseumPageData,
  MuseumParagraph,
  MuseumSource,
  MuseumStation,
} from "@/lib/museum";
import { distinctShots, sized, sourcesOf } from "@/lib/museum";
import { MxStrings, STRINGS, useS, type MxLang } from "./strings";
import { useLang } from "@/components/LangProvider";
import "./museum.css";
import "./museum-looks.css";
import "./museum-looks-a.css";
import "./museum-structure.css";
import "./museum-backdrop.css";

// Trial looks for comparison (?look=a|b|c); undefined = the current navy look.
//   a  catalogue  (open-design "kami": paper, one ink-blue, one serif)
//   b  newspaper  (open-design "wired": white broadsheet, black rules)
//   c  archive    (open-design "ibm" Carbon: grey layers, Plex Sans Hebrew, blue 60)
//   a1–a5  five takes on the catalogue (a): see museum-looks.css
// The page background (data/museum/<slug>.backdrop.json, written by museum_line.py's backdrop stage):
// one of the page's own photos plus the colour set derived from it. Caption and credit come from the
// page's media row, so they follow the page language.
export type MuseumBackdrop = { media: string; img: string; img_small?: string; palette: Record<string, string>; passed?: boolean; [k: string]: unknown };
export type MuseumLook = "a" | "b" | "c" | "a1" | "a2" | "a3" | "a4" | "a5";
const LOOK_NAMES: [MuseumLook | undefined, string][] = [[undefined, "נוכחי"], ["a1", "קטלוג"], ["a2", "לוח"], ["a3", "שער"], ["a4", "אלבום"], ["a5", "מפתח"]];
const STILL: (MuseumLook | undefined)[] = ["b", "c", "a2", "a3", "a4", "a5"];
// station numbers as Hebrew letters (א׳ … כ׳), used by one look
const HEB = ["א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "יא", "יב", "יג", "יד", "טו", "טז", "יז", "יח", "יט", "כ"];
const hebNum = (n: number) => { const h = HEB[n - 1] ?? String(n); return h.length > 1 ? `${h[0]}״${h.slice(1)}` : `${h}׳`; };

// ---------------------------------------------------------------------------
// The deed as an exhibition: an entrance wall (animated collage + the story in
// four sentences), then stations in the order the story happened. Each station
// hangs its own photos and videos beside its text, numbers its sources, and
// shows a disagreement between sources side by side instead of choosing one.
// Motion: one entrance sequence and a slow collage; everything else answers a
// click. prefers-reduced-motion turns all of it off (museum.css).
// ---------------------------------------------------------------------------

type Ctx = {
  page: MuseumPageData;
  showVideo: (id: string) => void;
  media: Map<string, MuseumMedia>;
  openImage: (m: MuseumMedia) => void;
};

function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const q = window.matchMedia("(prefers-reduced-motion: reduce)");
    const on = () => setReduced(q.matches);
    on();
    q.addEventListener("change", on);
    return () => q.removeEventListener("change", on);
  }, []);
  return reduced;
}

// ---------- the entrance collage -------------------------------------------

const TILE_SHAPES = ["mx-t-a", "mx-t-b", "mx-t-c", "mx-t-d", "mx-t-e", "mx-t-f", "mx-t-g"];

function Collage({ images, onOpen, still, every = 4200 }: { images: MuseumMedia[]; onOpen: (m: MuseumMedia) => void; still?: boolean; every?: number }) {
  const L = useS();
  const reduced = useReducedMotion() || !!still;
  const tiles = Math.min(TILE_SHAPES.length, images.length);
  // Which image each tile shows. Every few seconds one tile turns over to the
  // next image that is not on the wall, so the whole set passes in review.
  const [slots, setSlots] = useState(() => images.slice(0, tiles).map((_, i) => i));
  const next = useRef(tiles);
  const turn = useRef(0);
  useEffect(() => {
    if (reduced || images.length <= tiles) return;
    const t = setInterval(() => {
      setSlots((s) => {
        const copy = [...s];
        const slot = turn.current % tiles;
        turn.current += 1;
        let n = next.current % images.length;
        while (copy.includes(n)) n = (n + 1) % images.length;
        copy[slot] = n;
        next.current = n + 1;
        return copy;
      });
    }, every);
    return () => clearInterval(t);
  }, [reduced, images.length, tiles, every]);

  if (!tiles) return null;
  return (
    <div className="mx-collage" data-n={tiles} aria-label={L.collage}>
      {slots.map((imgIndex, i) => {
        const m = images[imgIndex];
        return (
          <button
            key={i}
            type="button"
            className={`mx-tile ${TILE_SHAPES[i]}`}
            style={{ animationDelay: `${0.12 * i}s` }}
            onClick={() => onOpen(m)}
            aria-label={L.enlarge(m.caption)}
          >
            {/* keyed on the image so a turn-over cross-fades a new element in */}
            <img key={m.id} src={sized(m.url, 900)} alt={m.caption} loading={i < 3 ? "eager" : "lazy"} className="mx-kb" style={{ animationDelay: `${-3 * i}s` }} />
          </button>
        );
      })}
    </div>
  );
}

// ---------- media on a station wall ----------------------------------------

function Credit({ m }: { m: MuseumMedia }) {
  const L = useS();
  return (
    <span className="mx-credit">
      {m.kind === "video" ? L.channel : L.photo}
      <bdi>{m.credit}</bdi>
      {" · "}
      {m.licence_url ? (
        <a href={m.licence_url} target="_blank" rel="noopener noreferrer">
          <bdi>{m.licence}</bdi>
        </a>
      ) : (
        <bdi>{m.licence}</bdi>
      )}
      {" · "}
      <a href={m.source_page} target="_blank" rel="noopener noreferrer">
        {m.kind === "video" ? L.watchAtSource : <bdi>{m.source_name}</bdi>}
      </a>
    </span>
  );
}

// The embed cannot choose an audio track (the IFrame API has none; tested 13.11 on RTL's French
// report: with hl=en the title turns English but the audio stays "French (FR) original"), so the
// placard says the video's language and where a track in the page's language is.
function wantedTracks(L: ReturnType<typeof useS>) {
  return L.dir === "ltr" ? ["en"] : ["he", "en"];
}
function VideoLang({ m }: { m: MuseumMedia }) {
  const L = useS();
  if (!m.spoken) return null;
  const want = wantedTracks(L);
  const name = (c: string) => L.langNames[c] ?? c;
  const alt = want.find((w) => w !== m.spoken && (m.audio_tracks ?? []).includes(w));
  const pageLang = want[0];
  return (
    <span className="mx-video-lang">
      {L.spokenIn(name(m.spoken))}
      {m.spoken !== pageLang && alt ? L.trackHint(name(alt)) : ""}
    </span>
  );
}

function Video({ m }: { m: MuseumMedia }) {
  const L = useS();
  const [play, setPlay] = useState(false);
  const id = m.youtube_id;
  if (!id) return null;
  return (
    <figure className="mx-figure">
      <div className="mx-video">
        {play ? (
          <iframe
            src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&playsinline=1&hl=${L.dir === "ltr" ? "en" : "he"}&cc_lang_pref=${L.dir === "ltr" ? "en" : "he"}`}
            title={m.caption}
            allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
            allowFullScreen
          />
        ) : (
          <button type="button" className="mx-video-facade" onClick={() => setPlay(true)} aria-label={L.play(m.caption)}>
            <img src={`https://i.ytimg.com/vi/${id}/hqdefault.jpg`} alt="" loading="lazy" />
            <span className="mx-play" aria-hidden="true" />
          </button>
        )}
      </div>
      <figcaption className="mx-placard">
        <span className="mx-placard-text">{m.caption}</span>
        <VideoLang m={m} />
        {m.date && <span className="mx-date">{m.date.split("-").reverse().join(".")}</span>}
        <Credit m={m} />
      </figcaption>
    </figure>
  );
}

// All the deed's videos in one viewer under the collage: one at a time, with arrows, swipe and the
// arrow keys to move between them, and the video's own explanation under it. Stations that a video
// belongs to link to it ("צפייה בסרטון"), which moves the viewer to that video and scrolls up to it.
function VideoViewer({ videos, at, setAt }: { videos: MuseumMedia[]; at: number; setAt: (n: number) => void }) {
  const L = useS();
  const touch = useRef<number | null>(null);
  if (!videos.length) return null;
  const n = videos.length;
  const go = (d: number) => setAt((at + d + n) % n);
  const m = videos[at];
  return (
    <section
      id="mx-videos"
      className="mx-viewer"
      aria-roledescription={L.viewerRole}
      aria-label={L.viewerLabel(n)}
      tabIndex={-1}
      onKeyDown={(e) => {
        // the arrow that points the way the text reads is "next"
        const fwd = L.dir === "rtl" ? "ArrowLeft" : "ArrowRight";
        const back = L.dir === "rtl" ? "ArrowRight" : "ArrowLeft";
        if (e.key === fwd) go(1);
        if (e.key === back) go(-1);
      }}
      onTouchStart={(e) => (touch.current = e.touches[0].clientX)}
      onTouchEnd={(e) => {
        if (touch.current == null) return;
        const dx = e.changedTouches[0].clientX - touch.current;
        touch.current = null;
        // in right-to-left the next video waits on the left, so dragging right brings it
        if (Math.abs(dx) > 48) go((L.dir === "rtl" ? dx > 0 : dx < 0) ? 1 : -1);
      }}
    >
      <div className="mx-viewer-stage">
        {n > 1 && (
          <button type="button" className="mx-viewer-btn mx-viewer-prev" onClick={() => go(-1)} aria-label={L.prevVideo}>
            <span aria-hidden="true">{L.prevGlyph}</span>
          </button>
        )}
        <Video key={m.id} m={m} />
        {n > 1 && (
          <button type="button" className="mx-viewer-btn mx-viewer-next" onClick={() => go(1)} aria-label={L.nextVideo}>
            <span aria-hidden="true">{L.nextGlyph}</span>
          </button>
        )}
      </div>
      {n > 1 && (
        <div className="mx-viewer-dots" role="tablist" aria-label={L.pickVideo}>
          <span className="mx-viewer-count" aria-live="polite">
            {L.videoOf(at + 1, n)}
          </span>
          {videos.map((v, i) => (
            <button key={v.id} type="button" role="tab" aria-selected={i === at} aria-label={L.videoN(i + 1, v.caption)} onClick={() => setAt(i)} />
          ))}
        </div>
      )}
    </section>
  );
}

function Photo({ m, onOpen, lead }: { m: MuseumMedia; onOpen: (m: MuseumMedia) => void; lead?: boolean }) {
  const L = useS();
  return (
    <figure className={`mx-figure ${lead ? "mx-lead" : ""}`}>
      <button type="button" className="mx-photo" onClick={() => onOpen(m)} aria-label={L.enlarge(m.caption)}>
        <img
          src={sized(m.url, lead ? 1100 : 700)}
          alt={m.caption}
          loading="lazy"
          width={m.width}
          height={m.height}
          className={m.width && m.height && m.height > m.width ? "mx-tall" : undefined}
        />
      </button>
      <figcaption className="mx-placard">
        <span className="mx-placard-text">{m.caption}</span>
        <Credit m={m} />
      </figcaption>
    </figure>
  );
}

// Photos beside the centred text: on wide screens they hang in the margins, alternating right and
// left; on narrower screens they sit after the text in a row of two. Videos are in the viewer.
function Margins({ photos, ctx }: { photos: MuseumMedia[]; ctx: Ctx }) {
  if (!photos.length) return null;
  const right = photos.filter((_, i) => i % 2 === 0);
  const left = photos.filter((_, i) => i % 2 === 1);
  return (
    <>
      <div className="mx-margin mx-margin-r">
        {right.map((m) => (
          <Photo key={m.id} m={m} onOpen={ctx.openImage} />
        ))}
      </div>
      <div className="mx-margin mx-margin-l">
        {left.map((m) => (
          <Photo key={m.id} m={m} onOpen={ctx.openImage} />
        ))}
      </div>
    </>
  );
}

function Wall({ ids, ctx }: { ids: string[]; ctx: Ctx }) {
  const items = ids.map((id) => ctx.media.get(id)).filter(Boolean) as MuseumMedia[];
  if (!items.length) return null;
  const [first, ...rest] = items;
  return (
    <div className="mx-wall">
      {first.kind === "video" ? <Video m={first} /> : <Photo m={first} onOpen={ctx.openImage} lead />}
      {rest.length > 0 && (
        <div className="mx-wall-rest">
          {rest.map((m) => (m.kind === "video" ? <Video key={m.id} m={m} /> : <Photo key={m.id} m={m} onOpen={ctx.openImage} />))}
        </div>
      )}
    </div>
  );
}

// ---------- text with its source numbers -----------------------------------

// A Hebrew prefix written with a hyphen (ב-1994, ל-CBS, לא-ניתוחיות) must not end a line: in centred
// text a line ending in "לא-" looks like an accident. A word joiner after the hyphen removes the break.
const WJ = String.fromCharCode(0x2060);
const HEB_PREFIX = new RegExp("(^|[\\s(\"'])([" + String.fromCharCode(0x5d0) + "-" + String.fromCharCode(0x5ea) + "]{1,3})-(?=\\S)", "g");
const glue = (t: string) => t.replace(HEB_PREFIX, `$1$2-${WJ}`);

function Prose({ paragraphs, numberOf, anchor }: { paragraphs: MuseumParagraph[]; numberOf: (claims: string[]) => number[]; anchor: string }) {
  const L = useS();
  return (
    <div className="mx-prose">
      {paragraphs.map((p, i) => (
        <p key={i}>
          {p.map((s, j) => (
            <Fragment key={j}>
              {glue(s.text)}
              {/* word joiner: the source number stays on the line of the sentence it belongs to */}
              {numberOf(s.claims).length > 0 && "⁠"}
              {numberOf(s.claims).length > 0 && (
                // the numbers of one sentence stay together and never start a line alone
                <span className="mx-refs">
                  {numberOf(s.claims).map((n) => (
                    <a key={n} href={`#${anchor}-src-${n}`} className="mx-ref" aria-label={L.sourceN(n)}>
                      {n}
                    </a>
                  ))}
                </span>
              )}{" "}
            </Fragment>
          ))}
        </p>
      ))}
    </div>
  );
}

function SourceList({ sources, anchor, page, claimIds }: { sources: MuseumSource[]; anchor: string; page: MuseumPageData; claimIds: string[] }) {
  const L = useS();
  if (!sources.length) return null;
  return (
    <div className="mx-sources">
      <h3 className="mx-sources-h">{L.stationSources}</h3>
      <ol>
        {sources.map((s, i) => {
          const quotes = page.claims.filter((c) => c.source === s.id && claimIds.includes(c.id));
          return (
            <li key={s.id} id={`${anchor}-src-${i + 1}`}>
              <span className="mx-src-n">{i + 1}</span>
              <div>
                <a href={s.url} target="_blank" rel="noopener noreferrer" className="mx-src-label">
                  <bdi>{s.label}</bdi>
                </a>
                {s.archive_url && (
                  <a href={s.archive_url} target="_blank" rel="noopener noreferrer" className="mx-src-arch">
                    {L.archived}
                  </a>
                )}
                {quotes.length > 0 && (
                  <details className="mx-quotes">
                    <summary>{L.whatSourceSays(quotes.length)}</summary>
                    <ul>
                      {quotes.map((q) => (
                        <li key={q.id} dir="auto">
                          {/[\u0590-\u05ff]/.test(q.quote) ? `„${q.quote}“` : `“${q.quote}”`}
                          {page.translation?.quote_translations?.[q.id] && (
                            <span className="mx-quote-tr" dir="ltr">
                              {L.translation}
                              {page.translation.quote_translations[q.id]}
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

// ---------- where the sources disagree -------------------------------------

// "Who: what they say" -> the speaker and the claim, so the speaker (often a
// Latin name such as JNS) can be isolated and set apart from the Hebrew text.
function splitSays(says: string): [string | null, string] {
  const m = says.match(/^([^:]{1,70}?):\s+([\s\S]+)$/);
  return m ? [m[1], m[2]] : [null, says];
}

function Disagreement({ d, page }: { d: MuseumDisagreement; page: MuseumPageData }) {
  const L = useS();
  return (
    <section className="mx-dis" aria-label={L.disagreeLabel(d.question)}>
      <h3 className="mx-dis-q">
        <span className="mx-dis-tag">{L.disagree}</span>
        {d.question}
      </h3>
      {/* one row per version: who said it, what they said, the source */}
      <ol className="mx-dis-cols">
        {d.versions.map((v, i) => {
          const src = sourcesOf(page, v.claims);
          const [who, what] = splitSays(v.says);
          return (
            <li key={i} className="mx-dis-card">
              {who && (
                <p className="mx-dis-who">
                  <bdi>{who}</bdi>
                </p>
              )}
              <p className="mx-dis-says">{what}</p>
              {src.length > 0 && (
                <p className="mx-dis-src">
                  <span className="mx-dis-src-k">{L.sourceK(src.length)}</span>
                  {src.map((s, k) => (
                    <Fragment key={s.id}>
                      {k > 0 ? "; " : ""}
                      <a href={s.url} target="_blank" rel="noopener noreferrer">
                        <bdi>{s.label}</bdi>
                      </a>
                    </Fragment>
                  ))}
                </p>
              )}
            </li>
          );
        })}
      </ol>
      <p className="mx-dis-note">{L.disNote}</p>
    </section>
  );
}

// ---------- a station ------------------------------------------------------

function Station({ st, index, ctx }: { st: MuseumStation; index: number; ctx: Ctx }) {
  const L = useS();
  const anchor = st.id;
  const claimIds = useMemo(() => {
    const ids: string[] = [];
    for (const p of st.paragraphs) for (const s of p) for (const c of s.claims) if (!ids.includes(c)) ids.push(c);
    return ids;
  }, [st]);
  const sources = useMemo(() => sourcesOf(ctx.page, claimIds), [ctx.page, claimIds]);
  const claimSource = useMemo(() => new Map(ctx.page.claims.map((c) => [c.id, c.source])), [ctx.page]);
  const numberOf = (claims: string[]) => {
    const ns: number[] = [];
    for (const c of claims) {
      const n = sources.findIndex((s) => s.id === claimSource.get(c)) + 1;
      if (n && !ns.includes(n)) ns.push(n);
    }
    return ns;
  };
  const dis = (st.disagreements ?? []).map((id) => ctx.page.disagreements?.find((d) => d.id === id)).filter(Boolean) as MuseumDisagreement[];
  const hard = st.kind === "hard";
  const own = (st.media ?? []).map((id) => ctx.media.get(id)).filter(Boolean) as MuseumMedia[];
  const photos = distinctShots(own.filter((m) => m.kind === "image"));
  const vids = own.filter((m) => m.kind === "video");
  return (
    <section id={anchor} className={`mx-station ${hard ? "mx-hard" : ""}`} aria-labelledby={`${anchor}-h`}>
      <header className="mx-st-head">
        <span className="mx-st-num" aria-hidden="true" data-heb={hebNum(index + 1)}>
          {index + 1}
        </span>
        <div>
          <p className="mx-st-kicker">{hard ? L.hardKicker : L.stationK(index + 1)}</p>
          <h2 id={`${anchor}-h`} className="mx-st-title">
            {st.title}
          </h2>
        </div>
      </header>
      <div className={`mx-st-body ${photos.length ? "mx-st-has-margins" : ""}`} data-n={photos.length}>
        <div className="mx-st-text">
          <Prose paragraphs={st.paragraphs} numberOf={numberOf} anchor={anchor} />
          {vids.length > 0 && (
            <p className="mx-st-videos">
              {vids.map((v) => (
                <button key={v.id} type="button" className="mx-st-video-link" onClick={() => ctx.showVideo(v.id)}>
                  <span aria-hidden="true">▶</span> {L.watchVideo}
                  {v.caption}
                </button>
              ))}
            </p>
          )}
          {dis.map((d) => (
            <Disagreement key={d.id} d={d} page={ctx.page} />
          ))}
          <SourceList sources={sources} anchor={anchor} page={ctx.page} claimIds={claimIds} />
        </div>
        <Margins photos={photos} ctx={ctx} />
      </div>
    </section>
  );
}

// ---------- the station map (sticky) ---------------------------------------

function StationMap({ stations }: { stations: MuseumStation[] }) {
  const L = useS();
  const [active, setActive] = useState(stations[0]?.id);
  const bar = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const els = stations.map((s) => document.getElementById(s.id)).filter(Boolean) as HTMLElement[];
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) setActive(e.target.id);
      },
      { rootMargin: "-40% 0px -55% 0px" },
    );
    els.forEach((el) => io.observe(el));
    let raf = 0;
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        if (!els.length || !bar.current) return;
        const top = els[0].getBoundingClientRect().top + window.scrollY;
        const last = els[els.length - 1];
        const end = last.getBoundingClientRect().bottom + window.scrollY - window.innerHeight;
        const p = Math.min(1, Math.max(0, (window.scrollY - top) / Math.max(1, end - top)));
        bar.current.style.transform = `scaleX(${p})`;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      io.disconnect();
      window.removeEventListener("scroll", onScroll);
    };
  }, [stations]);
  useEffect(() => {
    // scroll ONLY the tab strip sideways; scrollIntoView also scrolled the whole page and made it jump (23.11)
    const a = document.querySelector<HTMLElement>(`.mx-map a[data-id="${active}"]`);
    const strip = a?.closest("ol");
    if (!a || !strip) return;
    const ar = a.getBoundingClientRect();
    const sr = strip.getBoundingClientRect();
    strip.scrollBy({ left: ar.left + ar.width / 2 - (sr.left + sr.width / 2), behavior: "smooth" });
  }, [active]);
  return (
    <nav className="mx-map" aria-label={L.map}>
      <ol>
        {stations.map((s, i) => (
          <li key={s.id}>
            <a href={`#${s.id}`} data-id={s.id} aria-current={active === s.id ? "true" : undefined}>
              <span className="mx-map-n">{i + 1}</span>
              {s.title}
            </a>
          </li>
        ))}
      </ol>
      <div className="mx-map-progress" ref={bar} aria-hidden="true" />
    </nav>
  );
}

// ---------- lightbox -------------------------------------------------------

function Lightbox({ m, onClose }: { m: MuseumMedia | null; onClose: () => void }) {
  const L = useS();
  const ref = useRef<HTMLDialogElement | null>(null);
  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (m && !d.open) d.showModal();
    if (!m && d.open) d.close();
  }, [m]);
  return (
    <dialog ref={ref} className="mx-lightbox" onClose={onClose} onClick={(e) => e.target === ref.current && onClose()}>
      {m && (
        <figure>
          <img src={sized(m.url, 1600)} alt={m.caption} />
          <figcaption className="mx-placard">
            <span className="mx-placard-text">{m.caption}</span>
            <Credit m={m} />
          </figcaption>
          <button type="button" className="mx-close" onClick={onClose} aria-label={L.close}>
            ×
          </button>
        </figure>
      )}
    </dialog>
  );
}

// 27.11: the site's marked note ("asterisk") at the end of a page — facts with their sources,
// then the site's own short view, plainly labelled as such.
function EditorNote({ note, en }: { note: NonNullable<MuseumPageData["editor_note"]>; en: boolean }) {
  const t = en ? note.en : note.he;
  return (
    <aside className="mx-note" aria-labelledby="note-h" dir={en ? "ltr" : "rtl"} lang={en ? "en" : "he"}>
      <h2 id="note-h">
        <span aria-hidden="true">*</span> {en ? "A note from the site" : "הערת האתר"}
      </h2>
      {t.text.map((p, i) => (
        <p key={i}>{p}</p>
      ))}
      {t.opinion && (
        <p className="mx-note-view">
          <b>{en ? "Our view: " : "דעת האתר: "}</b>
          {t.opinion}
        </p>
      )}
      <p className="mx-note-src">{en ? "Sources:" : "מקורות:"}</p>
      <ul className="mx-note-src">
        {note.sources.map((s) => (
          <li key={s.url} dir="auto">
            <a href={s.url} target="_blank" rel="noopener noreferrer">
              {s.label}
            </a>
          </li>
        ))}
      </ul>
    </aside>
  );
}

// ---------- the page --------------------------------------------------------

export default function MuseumPage(props: {
  page: MuseumPageData;
  pageEn?: MuseumPageData | null;
  initialLang?: MxLang;
  look?: MuseumLook;
  preview?: boolean;
  backdrop?: MuseumBackdrop;
  bgPreview?: boolean;
}) {
  // The language starts as the server chose it (?lang=, else the site's cookie) and then follows
  // the header's EN / עב button. A ?lang= in the address is saved like the button's choice.
  const site = useLang();
  const [lang, setLangHere] = useState<MxLang>(props.initialLang ?? "he");
  const mounted = useRef(false);
  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;
      if (props.initialLang && props.initialLang !== site.lang) site.setLang(props.initialLang);
      return;
    }
    setLangHere(site.lang);
  }, [site.lang]); // eslint-disable-line react-hooks/exhaustive-deps
  const en = lang === "en" && !!props.pageEn;
  return (
    <MxStrings.Provider value={STRINGS[en ? "en" : "he"]}>
      <MuseumBody {...props} page={en ? props.pageEn! : props.page} wantedEn={lang === "en"} note={props.page.editor_note} />
    </MxStrings.Provider>
  );
}

function MuseumBody({ page, look, preview, backdrop, bgPreview, wantedEn, note }: { page: MuseumPageData; look?: MuseumLook; preview?: boolean; backdrop?: MuseumBackdrop; bgPreview?: boolean; wantedEn?: boolean; note?: MuseumPageData["editor_note"] }) {
  const L = useS();
  const media = useMemo(() => new Map(page.media.map((m) => [m.id, m])), [page]);
  const [lightbox, setLightbox] = useState<MuseumMedia | null>(null);
  // videos in story order: the stations' own videos first, then the rest
  const allVideos = useMemo(() => {
    const order: string[] = [];
    for (const st of page.stations) for (const id of st.media ?? []) if (media.get(id)?.kind === "video" && !order.includes(id)) order.push(id);
    for (const m of page.media) if (m.kind === "video" && !order.includes(m.id)) order.push(m.id);
    const want = wantedTracks(L);
    const rank = (m: MuseumMedia) => {
      const i = want.indexOf(m.spoken ?? "");
      if (i >= 0) return i;
      const j = want.findIndex((w) => (m.audio_tracks ?? []).includes(w));
      return j >= 0 ? want.length + j : 2 * want.length;
    };
    return (order.map((id) => media.get(id)!) as MuseumMedia[])
      .map((m, k) => [m, k] as const)
      .sort((a, b) => rank(a[0]) - rank(b[0]) || a[1] - b[1])
      .map(([m]) => m);
  }, [page, media, L]);
  const [vidAt, setVidAt] = useState(0);
  const showVideo = (id: string) => {
    const i = allVideos.findIndex((v) => v.id === id);
    if (i >= 0) setVidAt(i);
    document.getElementById("mx-videos")?.scrollIntoView({ behavior: "smooth", block: "center" });
    (document.getElementById("mx-videos") as HTMLElement | null)?.focus({ preventScroll: true });
  };
  const ctx: Ctx = { page, media, openImage: setLightbox, showVideo };
  const images = page.media.filter((m) => m.kind === "image");
  // the entrance never hangs two crops of one photograph side by side
  // the photo that is the page background is not hung again on the entrance wall
  const heroImages = distinctShots([
    ...(page.hero_media ?? []).map((id) => media.get(id)).filter((m): m is MuseumMedia => !!m && m.kind === "image"),
    ...images.filter((m) => !(page.hero_media ?? []).includes(m.id)),
  ].filter((m) => m.id !== backdrop?.media));
  const trailerClaims = page.trailer.flatMap((s) => s.claims);
  const trailerSources = sourcesOf(page, trailerClaims);
  const counts = page.check.counts ?? {};
  const unknownSources = sourcesOf(page, (page.unknowns ?? []).flatMap((s) => s.claims));
  const videos = page.media.filter((m) => m.kind === "video").length;

  return (
    <main className="mx-root flex-1 w-full" dir={L.dir} lang={L.dir === "ltr" ? "en" : "he"} data-look={look ?? "0"} data-cat={look?.startsWith("a") ? "" : undefined}>
      {/* The entrance wall */}
      <section className="mx-entrance">
        {/* the title comes first, above the photos (Tomer, 23.11) */}
        <div className="mx-entrance-text">
          <Link href="/" className="mx-back">
            {L.back}
          </Link>
          {wantedEn && L.dir === "rtl" && (
            <p className="mx-only-he" dir="ltr" lang="en">
              {STRINGS.en.onlyHebrew}
            </p>
          )}
          <p className="mx-entrance-meta">{L.exhibitionOf(page.stations.length)}</p>
          <h1 className="mx-title">{page.title}</h1>
        </div>
        <Collage images={heroImages} onOpen={setLightbox} still={STILL.includes(look)} every={look === "a" || look === "a1" ? 7000 : 4200} />
        {heroImages[0] && (
          <p className="mx-plate-cap">
            <span>{heroImages[0].caption}</span> <Credit m={heroImages[0]} />
          </p>
        )}
        <div className="mx-entrance-shade" aria-hidden="true" />
        <VideoViewer videos={allVideos} at={vidAt} setAt={setVidAt} />
      </section>

      <div className="mx-intro">
        <div className="mx-trailer">
          {page.trailer.map((s, i) => (
            <span key={i}>{s.text} </span>
          ))}
          <p className="mx-trailer-src">
            {L.trailerSources}
            {trailerSources.map((s, i) => (
              <a key={s.id} href={s.url} target="_blank" rel="noopener noreferrer">
                {i > 0 ? " · " : ""}
                <bdi>{s.label}</bdi>
              </a>
            ))}
          </p>
        </div>
        {page.glance && page.glance.length > 0 && (
          <dl className="mx-glance">
            {page.glance.map((g) => (
              <div key={g.label}>
                <dt>{g.label}</dt>
                <dd>{g.value}</dd>
              </div>
            ))}
          </dl>
        )}
        <p className={`mx-check ${page.check.passed ? "mx-check-ok" : ""}`}>
          {page.check.passed
            ? L.checkedOk(counts.confirmed ?? 0)
            : L.notChecked}{" "}
          {L.counts(page.stations.length, page.sources.length, images.length, videos)}
        </p>
      </div>

      <StationMap stations={page.stations} />

      <div className="mx-stations">
        {page.stations.map((st, i) => (
          <Station key={st.id} st={st} index={i} ctx={ctx} />
        ))}
      </div>

      {page.unknowns && page.unknowns.length > 0 && (
        <section className="mx-unknowns" aria-labelledby="unknowns-h">
          <h2 id="unknowns-h">{L.unknowns}</h2>
          <ul>
            {page.unknowns.map((u, i) => (
              <li key={i}>{u.text}</li>
            ))}
          </ul>
          {unknownSources.length > 0 && (
            <p className="mx-trailer-src">
              {L.by}
              {unknownSources.map((s, i) => (
                <a key={s.id} href={s.url} target="_blank" rel="noopener noreferrer">
                  {i > 0 ? " · " : ""}
                  <bdi>{s.label}</bdi>
                </a>
              ))}
            </p>
          )}
        </section>
      )}

      {note && <EditorNote note={note} en={L.dir === "ltr"} />}

      <section className="mx-credits" aria-labelledby="credits-h">
        <h2 id="credits-h">{L.credits}</h2>
        <p>{L.creditsNote}</p>
        {backdrop && media.get(backdrop.media) && (
          <p className="mx-bd-credit">
            {L.backdrop}
            {media.get(backdrop.media)!.caption} (<bdi>{media.get(backdrop.media)!.credit}</bdi> · <bdi>{media.get(backdrop.media)!.licence}</bdi>)
          </p>
        )}
        <ol>
          {page.media.map((m) => (
            <li key={m.id} dir={L.dir}>
              <a href={m.source_page} target="_blank" rel="noopener noreferrer" className="mx-cr-cap">
                {m.caption}
              </a>
              <span className="mx-cr-meta">
                {m.kind === "video" ? L.channel : L.photo}
                <bdi>{m.credit}</bdi>
                {L.licence}
                {m.licence_url ? (
                  <a href={m.licence_url} target="_blank" rel="noopener noreferrer">
                    <bdi>{m.licence}</bdi>
                  </a>
                ) : (
                  <bdi>{m.licence}</bdi>
                )}
                {L.source}
                <bdi>{m.source_name}</bdi>
                {m.role === "related" && L.related}
              </span>
            </li>
          ))}
        </ol>
      </section>

      <Lightbox m={lightbox} onClose={() => setLightbox(null)} />

      {/* preview only (?look= present): switch between the trial looks */}
      {preview && <nav className="mx-looks" aria-label={L.looks}>
        <span>{L.looksK}</span>
        {LOOK_NAMES.map(([l, name]) => (
          <a key={name} href={`?look=${l ?? "0"}`} aria-current={l === look && (l !== "a4" || !!bgPreview) ? "true" : undefined}>
            {l === "a4" ? "אלבום ורקע" : name}
          </a>
        ))}
        <a href="?look=a4cream" aria-current={look === "a4" && !bgPreview ? "true" : undefined}>
          אלבום בלי רקע
        </a>
      </nav>}
    </main>
  );
}
