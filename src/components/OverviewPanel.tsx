import type { Overview } from "@/lib/data";

/**
 * The historian's "state of the nation" panel. Shows the big-picture headline,
 * key stats, and the narrative — the running total of what these deeds add up to.
 * Renders nothing until the historian has written a revision.
 */
export default function OverviewPanel({ overview }: { overview: Overview }) {
  const stats = overview.stats || {};
  const statEntries = Object.entries(stats).filter(
    ([, v]) => v !== null && v !== undefined && String(v).length > 0
  );

  // Friendly Hebrew labels for known stat keys.
  const LABELS: Record<string, string> = {
    entries: "מעשים מתועדים",
    documented_lives_helped: "נפשות שנעזרו (מתועד)",
    countries_reached: "מדינות",
    year_min: "מהשנה",
    year_max: "עד השנה",
  };

  return (
    <section className="relative w-full" style={{ background: "linear-gradient(to bottom, #0a1834, #081026)" }}>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-14 text-center">
        <div className="gold-rule max-w-[140px] mx-auto mb-5" />
        <p className="text-[11px] font-medium uppercase tracking-[0.3em] mb-3" style={{ color: "rgba(201,168,74,0.8)" }}>
          התמונה הגדולה{overview.date_range ? ` · ${overview.date_range}` : ""}
        </p>

        {/* Headline */}
        <h2
          className="text-2xl md:text-4xl font-extrabold leading-tight text-white max-w-3xl mx-auto"
          style={{ fontFamily: "var(--font-frank-ruhl), serif" }}
        >
          {overview.headline}
        </h2>

        {/* Stats row */}
        {statEntries.length > 0 && (
          <div className="mt-8 flex flex-wrap justify-center gap-4 md:gap-8">
            {statEntries.map(([k, v]) => (
              <div key={k} className="flex flex-col items-center min-w-[5.5rem]">
                <span className="text-2xl md:text-3xl font-extrabold" style={{ color: "#e6c66e" }}>
                  {String(v)}
                </span>
                <span className="text-[11px] md:text-xs text-blue-200/60 mt-1">
                  {LABELS[k] || k}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Narrative */}
        {overview.narrative && (
          <div className="mt-8 text-blue-100/75 text-sm md:text-base leading-relaxed max-w-2xl mx-auto whitespace-pre-line text-right">
            {overview.narrative}
          </div>
        )}

        <div className="gold-rule max-w-[140px] mx-auto mt-8" />
      </div>
    </section>
  );
}
