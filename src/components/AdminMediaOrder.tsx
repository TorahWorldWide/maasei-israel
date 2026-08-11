"use client";

import { useCallback, useEffect, useState } from "react";
import { useLang } from "@/components/LangProvider";
import { t } from "@/lib/i18n";
import { ytId } from "@/lib/youtube";
import type { MediaEntry } from "@/lib/data";

function move(urls: string[], from: number, to: number): string[] {
  const next = [...urls];
  const [item] = next.splice(from, 1);
  next.splice(to, 0, item);
  return next;
}

function Row({
  url,
  index,
  last,
  onMove,
}: {
  url: string;
  index: number;
  last: boolean;
  onMove: (to: number) => void;
}) {
  const { lang } = useLang();
  const video = ytId(url);
  return (
    <li className="flex items-center gap-3 bg-white border border-slate-200 rounded-xl p-2.5">
      <span className="w-6 shrink-0 text-center text-sm font-bold text-slate-400">
        {index + 1}
      </span>
      <div className="w-24 h-16 shrink-0 rounded-lg overflow-hidden bg-slate-100 flex items-center justify-center">
        {video ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`https://img.youtube.com/vi/${video}/mqdefault.jpg`}
            alt=""
            className="w-full h-full object-cover"
          />
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={url} alt="" className="w-full h-full object-cover" loading="lazy" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        {index === 0 && (
          <span className="inline-block text-[11px] font-bold text-amber-700 bg-amber-100 rounded-full px-2 py-0.5 mb-1">
            {t(lang, "adminImagesLead")}
          </span>
        )}
        {video && (
          <span className="inline-block text-[11px] font-bold text-blue-700 bg-blue-100 rounded-full px-2 py-0.5 mb-1 ms-1">
            {t(lang, "adminImagesVideo")}
          </span>
        )}
        <p dir="ltr" className="text-[11px] text-slate-400 truncate">
          {decodeURIComponent(url.split("/").pop() || url)}
        </p>
      </div>
      <div className="flex items-center gap-1 shrink-0">
        <button
          onClick={() => onMove(0)}
          disabled={index === 0}
          title={t(lang, "adminImagesMoveFirst")}
          className="px-2 py-1 rounded-lg text-xs font-semibold bg-amber-50 text-amber-700 hover:bg-amber-100 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          ★
        </button>
        <button
          onClick={() => onMove(index - 1)}
          disabled={index === 0}
          title={t(lang, "adminImagesEarlier")}
          className="px-2 py-1 rounded-lg text-sm bg-slate-100 hover:bg-slate-200 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          ↑
        </button>
        <button
          onClick={() => onMove(index + 1)}
          disabled={last}
          title={t(lang, "adminImagesLater")}
          className="px-2 py-1 rounded-lg text-sm bg-slate-100 hover:bg-slate-200 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          ↓
        </button>
      </div>
    </li>
  );
}

export default function AdminMediaOrder({ password }: { password: string }) {
  const { lang } = useLang();
  const [entries, setEntries] = useState<MediaEntry[] | null>(null);
  const [error, setError] = useState<"adminLoadError" | "adminNetworkError" | null>(null);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<MediaEntry | null>(null);
  const [urls, setUrls] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState<"ok" | "fail" | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const res = await fetch("/api/admin/media", {
        headers: { "x-admin-password": password },
      });
      if (!res.ok) {
        setError("adminLoadError");
        return;
      }
      const json = await res.json();
      setEntries(json.entries as MediaEntry[]);
    } catch {
      setError("adminNetworkError");
    }
  }, [password]);

  useEffect(() => {
    load();
  }, [load]);

  const pick = (entry: MediaEntry) => {
    setSelected(entry);
    setUrls(entry.media_urls);
    setSaved(null);
  };

  const save = async () => {
    if (!selected) return;
    setSaving(true);
    setSaved(null);
    try {
      const res = await fetch("/api/admin/media", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-password": password,
        },
        body: JSON.stringify({ id: selected.id, media_urls: urls }),
      });
      const json = await res.json();
      if (!res.ok || !json.ok) {
        setSaved("fail");
        return;
      }
      setSaved("ok");
      setSelected({ ...selected, media_urls: json.media_urls, media_url: json.media_urls[0] });
      setEntries(
        (entries ?? []).map((e) =>
          e.id === selected.id ? { ...e, media_urls: json.media_urls } : e
        )
      );
    } catch {
      setSaved("fail");
    } finally {
      setSaving(false);
    }
  };

  const dirty =
    selected !== null && urls.join(" ") !== selected.media_urls.join(" ");
  const visible = (entries ?? []).filter((e) =>
    query.trim() ? e.title.includes(query.trim()) : true
  );

  return (
    <div className="flex flex-col gap-6">
      <p className="text-sm text-slate-500 bg-slate-100 border border-slate-200 rounded-xl px-4 py-3 leading-relaxed">
        {t(lang, "adminImagesHint")}
      </p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-5 py-4 rounded-xl">
          {t(lang, error)}
        </div>
      )}

      {entries === null && !error && (
        <p className="text-center py-10 text-slate-400">{t(lang, "adminLoading")}</p>
      )}

      {entries !== null && entries.length === 0 && (
        <p className="text-center py-10 text-slate-400">{t(lang, "adminImagesEmpty")}</p>
      )}

      {entries !== null && entries.length > 0 && (
        <>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t(lang, "adminImagesSearch")}
            className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
          />

          <div className="flex flex-col gap-1.5 max-h-64 overflow-y-auto">
            {visible.map((e) => (
              <button
                key={e.id}
                onClick={() => pick(e)}
                className={`text-start px-3 py-2 rounded-xl text-sm border transition-colors ${
                  selected?.id === e.id
                    ? "bg-blue-50 border-blue-300 text-blue-900 font-semibold"
                    : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                }`}
              >
                {e.title}
                <span className="text-slate-400 font-normal"> · {e.media_urls.length}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {!selected && entries !== null && entries.length > 0 && (
        <p className="text-center py-6 text-slate-400 text-sm">
          {t(lang, "adminImagesPick")}
        </p>
      )}

      {selected && (
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 flex flex-col gap-4">
          <h3 className="font-bold text-slate-900">{t(lang, "adminImagesTitle")}</h3>
          <ul className="flex flex-col gap-2">
            {urls.map((url, i) => (
              <Row
                key={url}
                url={url}
                index={i}
                last={i === urls.length - 1}
                onMove={(to) => {
                  setUrls(move(urls, i, to));
                  setSaved(null);
                }}
              />
            ))}
          </ul>
          <div className="flex items-center gap-3 flex-wrap">
            <button
              onClick={save}
              disabled={!dirty || saving}
              className="bg-blue-800 text-white font-bold px-5 py-2 rounded-xl text-sm hover:bg-blue-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? t(lang, "adminImagesSaving") : t(lang, "adminImagesSave")}
            </button>
            <button
              onClick={() => {
                setUrls(selected.media_urls);
                setSaved(null);
              }}
              disabled={!dirty || saving}
              className="text-sm text-slate-500 hover:text-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {t(lang, "adminImagesReset")}
            </button>
            {saved === "ok" && (
              <span className="text-sm text-green-700">{t(lang, "adminImagesSaved")}</span>
            )}
            {saved === "fail" && (
              <span className="text-sm text-red-700">{t(lang, "adminImagesSaveError")}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
