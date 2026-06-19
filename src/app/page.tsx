import Link from "next/link";
import { getApprovedEntries } from "@/lib/data";
import Feed from "@/components/Feed";
import Theater from "@/components/Theater";

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

      {/* Theater (auto-playing video reel + music) */}
      <Theater entries={entries} />

      {/* Catalog */}
      <main id="catalog" className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-12 scroll-mt-20">
        <div className="mb-8 text-center">
          <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900">
            כל המעשים הטובים
          </h2>
          <p className="text-slate-500 text-sm mt-2">
            חפשו, סננו לפי קטגוריה ותקופה, וגלו אחד אחד — כל פריט עם מקור מאומת.
          </p>
        </div>
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
            <Link href="/admin" className="hover:text-slate-600 transition-colors">
              כניסת מנהל
            </Link>
          </p>
        </div>
      </footer>
    </div>
  );
}
