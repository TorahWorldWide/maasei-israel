"use client";

import Link from "next/link";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";

export default function SiteFooter({ entryCount }: { entryCount?: number }) {
  const { lang } = useLang();

  return (
    <footer className="border-t border-[#cbbfa8] bg-[#e0d7c4] py-8 text-center text-sm text-[#63554a]">
      <div className="max-w-6xl mx-auto px-4 flex flex-col gap-2">
        {/* the mark between two short fading hairlines: the same motif that opens the pages */}
        <div aria-hidden="true" className="relative mx-auto w-fit before:absolute before:top-1/2 before:right-full before:mr-3 before:h-px before:w-14 before:bg-linear-to-l before:from-[#6b4426]/45 before:to-transparent after:absolute after:top-1/2 after:left-full after:ml-3 after:h-px after:w-14 after:bg-linear-to-r after:from-[#6b4426]/45 after:to-transparent">
        <svg
          viewBox="0 0 100 100"
          className="w-6 h-6 mx-auto opacity-60"
          aria-hidden="true"
        >
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
        </div>
        {entryCount !== undefined && (
          <p>
            {t(lang, "siteTitle")} &mdash;{" "}
            <span className="font-medium text-[#6b4426]">{entryCount}</span>{" "}
            {t(lang, "documentedItems")}
          </p>
        )}
        <p className="text-xs text-[#63554a]/80">{t(lang, "footerNote")}</p>
        <p className="text-xs">
          <Link
            href="/admin"
            className="hover:text-[#221b14] transition-colors"
          >
            {t(lang, "adminLogin")}
          </Link>
        </p>
      </div>
    </footer>
  );
}
