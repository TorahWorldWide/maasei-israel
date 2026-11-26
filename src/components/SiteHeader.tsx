"use client";

import Link from "next/link";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";
import LangToggle from "@/components/LangToggle";

export default function SiteHeader() {
  const { lang } = useLang();

  return (
    <header className="bg-[#e0d7c4]/95 backdrop-blur-md text-[#221b14] sticky top-0 z-40 border-b border-[#cbbfa8]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <svg viewBox="0 0 100 100" className="w-7 h-7" aria-hidden="true">
            <polygon
              points="50,8 12,80 88,80"
              fill="none"
              stroke="#6b4426"
              strokeWidth="5"
            />
            <polygon
              points="50,92 88,20 12,20"
              fill="none"
              stroke="#6b4426"
              strokeWidth="5"
            />
          </svg>
          <span
            className="text-xl font-bold tracking-tight"
            style={{ fontFamily: "var(--font-david), serif" }}
          >
            {t(lang, "siteTitle")}
          </span>
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <LangToggle />
          <Link
            href="/submit"
            className="bg-[#6b4426] text-[#f6f1e6] font-semibold px-4 py-2 rounded-full hover:bg-[#553419] transition-colors shadow-sm"
          >
            {t(lang, "submit")}
          </Link>
          <Link
            href="/admin"
            className="text-[#63554a] hover:text-[#221b14] transition-colors text-xs"
          >
            {t(lang, "admin")}
          </Link>
        </nav>
      </div>
    </header>
  );
}
