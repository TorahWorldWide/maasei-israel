import Link from "next/link";
import { getApprovedEntries } from "@/lib/data";
import Feed from "@/components/Feed";

export const dynamic = "force-dynamic";

export default async function Home() {
  const entries = await getApprovedEntries();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-blue-900 text-white sticky top-0 z-40 shadow-md">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold tracking-tight">
            מעשי ישראל
          </Link>
          <nav className="flex items-center gap-3 text-sm">
            <Link
              href="/submit"
              className="bg-white text-blue-900 font-semibold px-4 py-2 rounded-full hover:bg-blue-50 transition-colors"
            >
              שלחו מעשה טוב
            </Link>
            <Link
              href="/admin"
              className="text-white/55 hover:text-white/90 transition-colors text-xs"
            >
              ניהול
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="relative bg-gradient-to-b from-blue-900 via-blue-800 to-blue-700 text-white overflow-hidden">
        {/* Faint Star of David watermark */}
        <div
          className="absolute inset-0 flex items-center justify-center pointer-events-none"
          aria-hidden="true"
        >
          <svg
            viewBox="0 0 200 200"
            className="w-[600px] h-[600px] opacity-[0.035]"
          >
            <polygon
              points="100,10 10,170 190,170"
              fill="none"
              stroke="white"
              strokeWidth="3"
            />
            <polygon
              points="100,190 190,30 10,30"
              fill="none"
              stroke="white"
              strokeWidth="3"
            />
          </svg>
        </div>

        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-24 text-center">
          <p className="text-blue-300/80 text-sm font-medium uppercase tracking-widest mb-4">
            — תיעוד של מעשים טובים —
          </p>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight">
            מעשי ישראל
          </h1>
          <p className="text-lg md:text-xl text-blue-100 max-w-2xl mx-auto leading-relaxed mb-3">
            אוסף מתועד של מעשים טובים, המצאות ותרומות של עם ישראל לעולם —
            כל פריט עם הוכחה.
          </p>
          <p className="text-sm text-blue-300/70 flex items-center justify-center gap-1.5 mb-8">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            כל פריט כולל קישור מקור מאומת
          </p>
          <Link
            href="/submit"
            className="inline-block bg-white text-blue-900 font-bold px-8 py-3 rounded-full hover:bg-blue-50 transition-colors text-lg shadow-xl shadow-blue-950/40"
          >
            שלחו מעשה טוב ←
          </Link>
        </div>
      </section>

      {/* Feed */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-12">
        <Feed entries={entries} />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-100 bg-white py-6 text-center text-sm text-slate-400">
        <div className="max-w-6xl mx-auto px-4 flex flex-col gap-1">
          <p>
            מעשי ישראל &mdash;{" "}
            <span className="font-medium text-slate-500">{entries.length}</span>{" "}
            פריטים מתועדים
          </p>
          <p className="text-xs">
            <Link
              href="/admin"
              className="hover:text-slate-600 transition-colors"
            >
              כניסת מנהל
            </Link>
          </p>
        </div>
      </footer>
    </div>
  );
}
