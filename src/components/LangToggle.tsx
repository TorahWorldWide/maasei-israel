"use client";

import { useLang } from "@/components/LangProvider";

export default function LangToggle() {
  const { lang, setLang } = useLang();

  return (
    <button
      onClick={() => setLang(lang === "he" ? "en" : "he")}
      className="text-xs font-medium text-[#63554a] hover:text-[#6b4426] transition-colors border border-[#cbbfa8] hover:border-[#6b4426] rounded-full px-2.5 py-1"
      aria-label={lang === "he" ? "החלף לאנגלית" : "Switch to Hebrew"}
    >
      {lang === "he" ? "EN" : "עב"}
    </button>
  );
}
