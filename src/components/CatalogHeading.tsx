"use client";

import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";

export default function CatalogHeading() {
  const { lang } = useLang();
  return (
    <div className="mb-10 text-center">
      <div className="gold-rule max-w-xs mx-auto mb-6" />
      <h2 className="text-3xl md:text-4xl font-extrabold text-white">
        {t(lang, "catalogTitle")}
      </h2>
      <p className="text-blue-200/70 text-sm mt-3 max-w-lg mx-auto leading-relaxed">
        {t(lang, "catalogSubtitle")}
      </p>
      <div className="gold-rule max-w-xs mx-auto mt-6" />
    </div>
  );
}
