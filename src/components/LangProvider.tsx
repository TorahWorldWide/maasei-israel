"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { LANG_COOKIE, type Lang } from "@/lib/i18n";

interface LangCtx {
  lang: Lang;
  setLang: (l: Lang) => void;
}

const LangContext = createContext<LangCtx>({ lang: "he", setLang: () => {} });

const LEGACY_KEY = "maasei.lang";

function writeCookie(l: Lang) {
  document.cookie = `${LANG_COOKIE}=${l}; path=/; max-age=31536000; samesite=lax`;
}

export function LangProvider({
  children,
  initialLang = "he",
}: {
  children: React.ReactNode;
  initialLang?: Lang;
}) {
  const [lang, setLangState] = useState<Lang>(initialLang);

  // Visitors who picked a language before the cookie existed keep their choice.
  useEffect(() => {
    if (document.cookie.includes(`${LANG_COOKIE}=`)) return;
    const legacy = localStorage.getItem(LEGACY_KEY) as Lang | null;
    if (legacy !== "he" && legacy !== "en") return;
    writeCookie(legacy);
    if (legacy !== initialLang) {
      applyLang(legacy);
      setLangState(legacy);
    }
  }, [initialLang]);

  function applyLang(l: Lang) {
    document.documentElement.lang = l;
    document.documentElement.dir = l === "he" ? "rtl" : "ltr";
  }

  // 27.11: the page flips right/left when the language changes, so it fades out
  // quickly, flips while hidden, and fades back in (no fade for reduced motion).
  function setLang(l: Lang) {
    writeCookie(l);
    localStorage.setItem(LEGACY_KEY, l);
    const root = document.documentElement;
    const swap = () => {
      setLangState(l);
      applyLang(l);
    };
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return swap();
    root.classList.add("lang-fade");
    window.setTimeout(() => {
      swap();
      requestAnimationFrame(() => requestAnimationFrame(() => root.classList.remove("lang-fade")));
    }, 180);
  }

  return (
    <LangContext.Provider value={{ lang, setLang }}>
      {children}
    </LangContext.Provider>
  );
}

export function useLang(): LangCtx {
  return useContext(LangContext);
}
