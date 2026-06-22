"use client";

import { useLang } from "@/components/LangProvider";

export default function LangToggle() {
  const { lang, setLang } = useLang();

  return (
    <button
      onClick={() => setLang(lang === "he" ? "en" : "he")}
      className="text-xs font-medium text-blue-200/60 hover:text-[#c9a84a] transition-colors border border-[rgba(201,168,74,0.3)] hover:border-[rgba(201,168,74,0.6)] rounded-full px-2.5 py-1"
      aria-label={lang === "he" ? "Switch to English" : "החלף לעברית"}
    >
      {lang === "he" ? "EN" : "עב"}
    </button>
  );
}
