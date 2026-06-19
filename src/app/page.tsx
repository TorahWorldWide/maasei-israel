import Link from "next/link";
import { getApprovedEntries, getOverview } from "@/lib/data";
import Feed from "@/components/Feed";
import Theater from "@/components/Theater";
import OverviewPanel from "@/components/OverviewPanel";

export const dynamic = "force-dynamic";

export default async function Home() {
  const [entries, overview] = await Promise.all([
    getApprovedEntries(),
    getOverview(),
  ]);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-[#081026]/85 backdrop-blur-md text-white sticky top-0 z-40 border-b border-[rgba(201,168,74,0.25)]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            {/* small gold star-of-david mark */}
            <svg viewBox="0 0 100 100" className="w-7 h-7" aria-hidden="true">
              <polygon points="50,8 12,80 88,80" fill="none" stroke="#c9a84a" strokeWidth="5" />
              <polygon points="50,92 88,20 12,20" fill="none" stroke="#c9a84a" strokeWidth="5" />
            </svg>
            <span className="text-xl font-bold tracking-tight" style={{ fontFamily: "var(--font-frank-ruhl), serif" }}>
              מעשי ישראל
            </span>
          </Link>
          <nav className="flex items-center gap-3 text-sm">
            <Link
              href="/submit"
              className="bg-gradient-to-b from-[#e6c66e] to-[#c9a84a] text-[#0a1834] font-semibold px-4 py-2 rounded-full hover:from-[#f0d585] hover:to-[#d4b35a] transition-colors shadow-sm"
            >
              שלחו מעשה טוב
            </Link>
            <Link
              href="/admin"
              className="text-white/45 hover:text-white/85 transition-colors text-xs"
            >
              ניהול
            </Link>
          </nav>
        </div>
      </header>

      {/* Theater (auto-playing video reel + music) */}
      <Theater entries={entries} />

      {/* The historian's big-picture overview (renders once written) */}
      {overview && <OverviewPanel overview={overview} />}

      {/* Catalog — stays navy, no white break */}
      <main id="catalog" className="flex-1 w-full scroll-mt-20 relative">
        <div className="max-w-6xl mx-auto w-full px-4 sm:px-6 py-14">
          <div className="mb-10 text-center">
            <div className="gold-rule max-w-xs mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-extrabold text-white">
              כל המעשים הטובים
            </h2>
            <p className="text-blue-200/70 text-sm mt-3 max-w-lg mx-auto leading-relaxed">
              חפשו, סננו לפי קטגוריה ותקופה, וגלו אחד אחד — כל פריט עם מקור מאומת.
            </p>
            <div className="gold-rule max-w-xs mx-auto mt-6" />
          </div>
          <Feed entries={entries} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[rgba(201,168,74,0.2)] bg-[#081026] py-8 text-center text-sm text-blue-200/50">
        <div className="max-w-6xl mx-auto px-4 flex flex-col gap-2">
          <svg viewBox="0 0 100 100" className="w-6 h-6 mx-auto opacity-60" aria-hidden="true">
            <polygon points="50,8 12,80 88,80" fill="none" stroke="#c9a84a" strokeWidth="5" />
            <polygon points="50,92 88,20 12,20" fill="none" stroke="#c9a84a" strokeWidth="5" />
          </svg>
          <p>
            מעשי ישראל &mdash;{" "}
            <span className="font-medium text-[#c9a84a]">{entries.length}</span>{" "}
            פריטים מתועדים
          </p>
          <p className="text-xs text-blue-200/35">
            כל פריט מלווה במקור מאומת · מוזיקה: Kevin MacLeod (CC-BY)
          </p>
          <p className="text-xs">
            <Link href="/admin" className="hover:text-blue-200/70 transition-colors">
              כניסת מנהל
            </Link>
          </p>
        </div>
      </footer>
    </div>
  );
}
