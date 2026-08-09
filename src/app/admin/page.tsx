"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import type { Entry } from "@/lib/data";
import { useLang } from "@/components/LangProvider";
import { t, pick, categoryLabel } from "@/lib/i18n";

interface PendingResult {
  entries: Entry[];
  configured: boolean;
}

// Error states are held as dict keys so a language flip re-renders them.
type LoginErrorKey =
  | "adminUnconfigured"
  | "adminWrongPassword"
  | "adminNetworkErrorRetry";

type QueueErrorKey = "adminLoadError" | "adminNetworkError";

function AdminLogin({
  onLogin,
}: {
  onLogin: (pw: string) => void;
}) {
  const { lang } = useLang();
  const [input, setInput] = useState("");
  const [error, setError] = useState<LoginErrorKey | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch("/api/admin/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: input }),
      });
      const data = await res.json();
      if (data.reason === "unconfigured") {
        setError("adminUnconfigured");
      } else if (!data.ok) {
        setError("adminWrongPassword");
      } else {
        onLogin(input);
      }
    } catch {
      setError("adminNetworkErrorRetry");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-blue-900 text-white">
        <div className="max-w-md mx-auto px-4 py-4 flex items-center gap-3">
          <Link href="/" className="text-white/60 hover:text-white/90 text-sm">← {t(lang, "back")}</Link>
          <span className="text-white/30">|</span>
          <h1 className="text-lg font-bold">{t(lang, "adminLogin")}</h1>
        </div>
      </header>
      <main className="flex-1 flex items-center justify-center p-6">
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 w-full max-w-sm flex flex-col gap-5"
        >
          <h2 className="text-xl font-bold text-slate-900">{t(lang, "adminLogin")}</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              {t(lang, "adminPassword")}
            </label>
            <input
              type="password"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t(lang, "adminPasswordPlaceholder")}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 transition-shadow"
              autoFocus
            />
          </div>
          {error && (
            <p className="text-red-600 text-sm bg-red-50 border border-red-200 px-4 py-2.5 rounded-xl">
              {t(lang, error)}
            </p>
          )}
          <button
            type="submit"
            disabled={loading || !input}
            className="bg-blue-800 text-white font-bold py-2.5 rounded-xl hover:bg-blue-900 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? t(lang, "adminLoggingIn") : t(lang, "adminEnter")}
          </button>
        </form>
      </main>
    </div>
  );
}

function SubmissionRow({
  entry,
  password,
  onAction,
}: {
  entry: Entry;
  password: string;
  onAction: () => void;
}) {
  const { lang } = useLang();
  const [busy, setBusy] = useState<"approve" | "reject" | null>(null);

  const act = async (action: "approve" | "reject") => {
    setBusy(action);
    try {
      await fetch(`/api/admin/${action}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-password": password,
        },
        body: JSON.stringify({ id: entry.id }),
      });
      onAction();
    } finally {
      setBusy(null);
    }
  };

  const sourceLabel =
    pick(lang, entry.source_label, entry.source_label_en) || entry.source_url;

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 flex flex-col gap-3">
      <div className="flex items-start gap-3 flex-wrap">
        <span className="text-xs bg-blue-100 text-blue-800 px-2.5 py-0.5 rounded-full font-medium">
          {categoryLabel(lang, entry.category)}
        </span>
        {entry.year && (
          <span className="text-xs text-slate-400">{entry.year}</span>
        )}
        <span className="text-xs text-slate-400 ms-auto">
          {new Date(entry.created_at).toLocaleDateString(
            lang === "he" ? "he-IL" : "en-GB"
          )}
        </span>
      </div>

      <h3 className="text-lg font-bold text-slate-900">
        {pick(lang, entry.title, entry.title_en)}
      </h3>
      <p className="text-sm text-slate-600 leading-relaxed">
        {pick(lang, entry.description, entry.description_en)}
      </p>

      <a
        href={entry.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm text-blue-700 hover:text-blue-900 underline underline-offset-2 flex items-center gap-1"
      >
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
        {t(lang, "source")}: {sourceLabel}
      </a>

      {entry.submitted_by && (
        <p className="text-xs text-slate-400">
          {t(lang, "adminSubmittedBy")}: {entry.submitted_by}
        </p>
      )}

      <div className="flex gap-3 pt-1">
        <button
          onClick={() => act("approve")}
          disabled={busy !== null}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-xl text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {busy === "approve" ? t(lang, "adminApproving") : t(lang, "adminApprove")}
        </button>
        <button
          onClick={() => act("reject")}
          disabled={busy !== null}
          className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 font-semibold py-2 rounded-xl text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {busy === "reject" ? t(lang, "adminRejecting") : t(lang, "adminReject")}
        </button>
      </div>
    </div>
  );
}

function AdminQueue({ password }: { password: string }) {
  const { lang } = useLang();
  const [data, setData] = useState<PendingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<QueueErrorKey | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/admin/pending", {
        headers: { "x-admin-password": password },
      });
      if (!res.ok) {
        setError("adminLoadError");
        return;
      }
      const json: PendingResult = await res.json();
      setData(json);
    } catch {
      setError("adminNetworkError");
    } finally {
      setLoading(false);
    }
  }, [password]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-blue-900 text-white sticky top-0 z-40 shadow-md">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-white/60 hover:text-white/90 text-sm">← {t(lang, "back")}</Link>
            <span className="text-white/30">|</span>
            <h1 className="text-lg font-bold">{t(lang, "adminQueueTitle")}</h1>
          </div>
          <button
            onClick={load}
            className="text-white/60 hover:text-white/90 text-sm flex items-center gap-1"
            title={t(lang, "adminRefresh")}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {t(lang, "adminRefresh")}
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-10">
        {loading && (
          <div className="text-center py-16 text-slate-400">
            <p>{t(lang, "adminLoading")}</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-5 py-4 rounded-xl mb-6">
            {t(lang, error)}
          </div>
        )}

        {data && !data.configured && (
          <div className="bg-amber-50 border border-amber-200 text-amber-800 px-5 py-4 rounded-xl text-sm">
            <p className="font-semibold">{t(lang, "adminSupabaseUnconfiguredTitle")}</p>
            <p className="mt-1">{t(lang, "adminSupabaseUnconfiguredBody")}</p>
          </div>
        )}

        {data && data.configured && data.entries.length === 0 && (
          <div className="text-center py-16 text-slate-400">
            <p className="text-lg">{t(lang, "adminNoPending")}</p>
          </div>
        )}

        {data && data.configured && data.entries.length > 0 && (
          <div className="flex flex-col gap-6">
            <p className="text-sm text-slate-500">
              {data.entries.length} {t(lang, "adminPendingCount")}
            </p>
            {data.entries.map((entry) => (
              <SubmissionRow
                key={entry.id}
                entry={entry}
                password={password}
                onAction={load}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default function AdminPage() {
  const [password, setPassword] = useState<string | null>(null);

  if (!password) {
    return <AdminLogin onLogin={setPassword} />;
  }

  return <AdminQueue password={password} />;
}
