import "./museum-entrance.css";

/**
 * 26.11: the entrance band of the whole site, right above the cinema reel.
 * Tomer: the very top must be videos playing like a cinema, so this stays a
 * short crown (kicker, flag stripes, title, one line), and the reel follows.
 */
const fmt = (n: number) => n.toLocaleString("he-IL");

export default function MuseumEntrance({ deeds, sources }: { deeds: number; sources: number }) {
  return (
    <section className="ent ent-slim" aria-labelledby="ent-title">
      {/* 27.11: one quiet line, so the cinema is seen right away */}
      <h1 id="ent-title" className="sr-only">מעשי ישראל</h1>
      <p className="ent-line">
        <span>מה עם ישראל נתן לעולם</span>
        {deeds > 0 && (
          <>
            <span className="ent-dot" aria-hidden="true">·</span>
            <span><b>{fmt(deeds)}</b> מעשים</span>
            <span className="ent-dot" aria-hidden="true">·</span>
            <span><b>{fmt(sources)}</b> מקורות</span>
          </>
        )}
      </p>
    </section>
  );
}
