"use client";

import Link from "next/link";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";

export default function SiteFooter({ entryCount }: { entryCount?: number }) {
  const { lang } = useLang();

  return (
    <footer className="border-t border-[rgba(201,168,74,0.2)] bg-[#081026] py-8 text-center text-sm text-blue-200/50">
      <div className="max-w-6xl mx-auto px-4 flex flex-col gap-2">
        <svg
          viewBox="0 0 100 100"
          className="w-6 h-6 mx-auto opacity-60"
          aria-hidden="true"
        >
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
        {entryCount !== undefined && (
          <p>
            מעשי ישראל &mdash;{" "}
            <span className="font-medium text-[#c9a84a]">{entryCount}</span>{" "}
            {t(lang, "documentedItems")}
          </p>
        )}
        <p className="text-xs text-blue-200/35">{t(lang, "footerNote")}</p>
        <p className="text-xs">
          <Link
            href="/admin"
            className="hover:text-blue-200/70 transition-colors"
          >
            {t(lang, "adminLogin")}
          </Link>
        </p>
      </div>
    </footer>
  );
}
