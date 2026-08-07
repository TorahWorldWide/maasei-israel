"use client";

import { useState } from "react";
import { useLang } from "@/components/LangProvider";
import { t, pick } from "@/lib/i18n";
import type { Entry } from "@/lib/data";

interface Props {
  entry: Pick<
    Entry,
    | "id"
    | "title"
    | "title_en"
    | "source_url"
    | "source_label"
    | "source_label_en"
    | "citations"
  >;
  size?: "sm" | "md";
}

export default function ShareProof({ entry, size = "md" }: Props) {
  const { lang } = useLang();
  const [copied, setCopied] = useState(false);

  const firstCitation = entry.citations?.[0];
  const firstQuote = firstCitation
    ? pick(lang, firstCitation.quote, firstCitation.quote_en)
    : "";
  const text = [
    pick(lang, entry.title, entry.title_en),
    firstQuote ? `"${firstQuote}"` : "",
    `${t(lang, "source")}: ${pick(lang, entry.source_label, entry.source_label_en)} ${entry.source_url}`,
    `${t(lang, "shareMore")}: https://maasei-israel.vercel.app/deed/${entry.id}`,
  ]
    .filter(Boolean)
    .join("\n");

  async function handleShare() {
    try {
      if (navigator.share) {
        await navigator.share({ text });
      } else {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // user cancelled share or clipboard unavailable
    }
  }

  const label = copied ? t(lang, "copied") : t(lang, "shareProof");
  const isSmall = size === "sm";

  return (
    <button
      onClick={handleShare}
      className={`flex items-center gap-1.5 font-semibold rounded-full border transition-colors ${
        isSmall
          ? "text-[11px] px-2.5 py-0.5 border-[#c9a84a]/30 text-[#c9a84a] hover:border-[#c9a84a]/70 hover:bg-[#c9a84a]/10"
          : "text-sm px-4 py-2 bg-gradient-to-b from-[#e6c66e] to-[#c9a84a] text-[#0a1834] border-transparent hover:from-[#f0d585] hover:to-[#d4b35a] shadow-sm"
      }`}
      aria-label={t(lang, "shareProof")}
    >
      {!isSmall && (
        <svg
          className="w-4 h-4 flex-shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
          />
        </svg>
      )}
      {label}
    </button>
  );
}
