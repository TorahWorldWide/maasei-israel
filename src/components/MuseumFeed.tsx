"use client";

import { useState } from "react";
import { useLang } from "@/components/LangProvider";
import type { ReelCard } from "@/lib/museumReel";
import "./museum-entrance.css";

/** 26.11: the written deeds as a calm scroll feed under the cinema reel. */
const STEP = 18;

export default function MuseumFeed({ cards }: { cards: ReelCard[] }) {
  const { lang } = useLang();
  const en = lang === "en";
  const [n, setN] = useState(STEP);
  if (!cards.length) return null;
  return (
    <section className="mfeed" aria-labelledby="mfeed-h">
      <div className="mfeed-in">
        <h2 id="mfeed-h" className="mfeed-h">{en ? "All the deeds" : "כל המעשים"}</h2>
        <p className="mfeed-sub">{en ? "Scroll at your own pace. Open any deed to read it all." : "גללו בנחת. כל מעשה נפתח לסיפור המלא."}</p>
        <div className="mfeed-grid">
          {cards.slice(0, n).map((c) => (
            <a key={c.slug} href={`/museum/${c.slug}`} className="mcard">
              <span className="mcard-img">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={c.thumb} alt="" loading="lazy" />
                <span className="mcard-play" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                </span>
              </span>
              <span className="mcard-t">
                <b>{en ? c.deedEn || c.deed : c.deed}</b>
                {c.year && <em>{c.year}</em>}
              </span>
              <p className="mcard-l">{en ? c.lineEn || c.line : c.line}</p>
            </a>
          ))}
        </div>
        {n < cards.length && (
          <div className="mfeed-more">
            <button onClick={() => setN((v) => v + STEP)}>
              {en ? `More deeds (${cards.length - n})` : `עוד מעשים (${cards.length - n})`}
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
