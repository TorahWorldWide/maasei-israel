import "./museum-entrance.css";

/**
 * 26.11: the entrance band of the whole site, right above the cinema reel.
 * Tomer: the very top must be videos playing like a cinema, so this stays a
 * short crown (kicker, flag stripes, title, one line), and the reel follows.
 */
const fmt = (n: number) => n.toLocaleString("he-IL");

export default function MuseumEntrance({ deeds, sources }: { deeds: number; sources: number }) {
  return (
    <section className="ent" aria-labelledby="ent-title">
      <div className="ent-head">
        <div className="ent-flag" aria-hidden="true">
          <span />
          <svg viewBox="0 0 100 100">
            <polygon points="50,8 12,80 88,80" fill="none" stroke="currentColor" strokeWidth="5" />
            <polygon points="50,92 88,20 12,20" fill="none" stroke="currentColor" strokeWidth="5" />
          </svg>
          <span />
        </div>
        <h1 id="ent-title" className="ent-title">מעשי ישראל</h1>
        <p className="ent-sub">מה עם ישראל נתן לעולם: ריפוי, מדע, חסד והצלה.</p>
        {deeds > 0 && (
          <p className="ent-stats">
            <span><b>{fmt(deeds)}</b> מעשים</span>
            <span className="ent-dot" aria-hidden="true">·</span>
            <span><b>{fmt(sources)}</b> מקורות</span>
          </p>
        )}
      </div>
    </section>
  );
}
