"use client";

import { useLang } from "@/components/LangProvider";
import { t, pick } from "@/lib/i18n";
import { visibleInfoboxRows, type Infobox } from "@/lib/data";

// Rule 169 — the fact table at the top of a person page. It is the easiest
// block on the site to read and therefore the easiest to believe, so a row
// without a source is dropped rather than shown unattributed.
export default function DeedInfobox({ infobox }: { infobox?: Infobox }) {
  const { lang } = useLang();
  const rows = visibleInfoboxRows(infobox, lang);
  if (rows.length === 0) return null;

  return (
    <aside className="bg-[#0f234d]/60 rounded-xl border border-[rgba(201,168,74,0.15)] p-4 mb-8 xl:mb-0">
      <p className="text-xs text-[#c9a84a] font-medium mb-3">{t(lang, "infoboxHeading")}</p>
      <dl className="flex flex-col gap-2.5">
        {rows.map((row, i) => {
          const value = pick(lang, row.value, row.value_en);
          return (
            <div key={row.key ?? i} className="flex flex-col gap-0.5">
              <dt className="text-[11px] text-blue-200/50">
                {pick(lang, row.label, row.label_en)}
              </dt>
              <dd className="text-sm text-blue-100/85 leading-snug">
                <a
                  href={row.source}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={t(lang, "infoboxSourceTitle")}
                  className="hover:text-[#e6c66e] transition-colors"
                >
                  {value}
                </a>
              </dd>
            </div>
          );
        })}
      </dl>
    </aside>
  );
}
