"use client";

import Link from "next/link";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";
import LangToggle from "@/components/LangToggle";

export default function SiteHeader() {
  const { lang } = useLang();

  return (
    <header className="bg-[#081026]/85 backdrop-blur-md text-white sticky top-0 z-40 border-b border-[rgba(201,168,74,0.25)]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <svg viewBox="0 0 100 100" className="w-7 h-7" aria-hidden="true">
            <polygon
              points="50,8 12,80 88,80"
              fill="none"
              stroke="#c9a84a"
              strokeWidth="5"
            />
            <polygon
              points="50,92 88,20 12,20"
              fill="none"
              stroke="#c9a84a"
              strokeWidth="5"
            />
          </svg>
          <span
            className="text-xl font-bold tracking-tight"
            style={{ fontFamily: "var(--font-frank-ruhl), serif" }}
          >
            מעשי ישראל
          </span>
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <LangToggle />
          <Link
            href="/submit"
            className="bg-gradient-to-b from-[#e6c66e] to-[#c9a84a] text-[#0a1834] font-semibold px-4 py-2 rounded-full hover:from-[#f0d585] hover:to-[#d4b35a] transition-colors shadow-sm"
          >
            {t(lang, "submit")}
          </Link>
          <Link
            href="/admin"
            className="text-white/45 hover:text-white/85 transition-colors text-xs"
          >
            {t(lang, "admin")}
          </Link>
        </nav>
      </div>
    </header>
  );
}
