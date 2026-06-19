"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import type { Entry } from "@/lib/data";

interface PendingResult {
  entries: Entry[];
  configured: boolean;
}

function AdminLogin({
  onLogin,
}: {
  onLogin: (pw: string) => void;
}) {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/admin/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: input }),
      });
      const data = await res.json();
      if (data.reason === "unconfigured") {
        setError("מנהל אינו מוגדר. יש להגדיר ADMIN_PASSWORD ו-Supabase.");
      } else if (!data.ok) {
        setError("סיסמה שגויה.");
      } else {
        onLogin(input);
      }
    } catch {
      setError("שגיאת תקשורת. נסה שוב.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-blue-900 text-white">
        <div className="max-w-md mx-auto px-4 py-4 flex items-center gap-3">
          <Link href="/" className="text-white/60 hover:text-white/90 text-sm">← חזרה</Link>
          <span className="text-white/30">|</span>
          <h1 className="text-lg font-bold">כניסת מנהל</h1>
        </div>
      </header>
      <main className="flex-1 flex items-center justify-center p-6">
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 w-full max-w-sm flex flex-col gap-5"
        >
          <h2 className="text-xl font-bold text-slate-900">כניסת מנהל</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              סיסמה
            </label>
            <input
              type="password"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="הזן סיסמת מנהל"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 transition-shadow"
              autoFocus
            />
          </div>
          {error && (
            <p className="text-red-600 text-sm bg-red-50 border border-red-200 px-4 py-2.5 rounded-xl">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading || !input}
            className="bg-blue-800 text-white font-bold py-2.5 rounded-xl hover:bg-blue-900 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "מתחבר..." : "כניסה"}
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

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 flex flex-col gap-3">
      <div className="flex items-start gap-3 flex-wrap">
        <span className="text-xs bg-blue-100 text-blue-800 px-2.5 py-0.5 rounded-full font-medium">
          {entry.category}
        </span>
        {entry.year && (
          <span className="text-xs text-slate-400">{entry.year}</span>
        )}
        <span className="text-xs text-slate-400 mr-auto">
          {new Date(entry.created_at).toLocaleDateString("he-IL")}
        </span>
      </div>

      <h3 className="text-lg font-bold text-slate-900">{entry.title}</h3>
      <p className="text-sm text-slate-600 leading-relaxed">{entry.description}</p>

      <a
        href={entry.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm text-blue-700 hover:text-blue-900 underline underline-offset-2 flex items-center gap-1"
      >
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
        מקור: {entry.source_label || entry.source_url}
      </a>

      {entry.submitted_by && (
        <p className="text-xs text-slate-400">הוגש על-ידי: {entry.submitted_by}</p>
      )}

      <div className="flex gap-3 pt-1">
        <button
          onClick={() => act("approve")}
          disabled={busy !== null}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-xl text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {busy === "approve" ? "מאשר..." : "✓ אישור"}
        </button>
        <button
          onClick={() => act("reject")}
          disabled={busy !== null}
          className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 font-semibold py-2 rounded-xl text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {busy === "reject" ? "דוחה..." : "✕ דחייה"}
        </button>
      </div>
    </div>
  );
}

function AdminQueue({ password }: { password: string }) {
  const [data, setData] = useState<PendingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/admin/pending", {
        headers: { "x-admin-password": password },
      });
      if (!res.ok) {
        setError("שגיאה בטעינת ההגשות.");
        return;
      }
      const json: PendingResult = await res.json();
      setData(json);
    } catch {
      setError("שגיאת תקשורת.");
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
            <Link href="/" className="text-white/60 hover:text-white/90 text-sm">← חזרה</Link>
            <span className="text-white/30">|</span>
            <h1 className="text-lg font-bold">ניהול הגשות</h1>
          </div>
          <button
            onClick={load}
            className="text-white/60 hover:text-white/90 text-sm flex items-center gap-1"
            title="רענן"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            רענן
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-10">
        {loading && (
          <div className="text-center py-16 text-slate-400">
            <p>טוען הגשות...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-5 py-4 rounded-xl mb-6">
            {error}
          </div>
        )}

        {data && !data.configured && (
          <div className="bg-amber-50 border border-amber-200 text-amber-800 px-5 py-4 rounded-xl text-sm">
            <p className="font-semibold">Supabase אינו מוגדר.</p>
            <p className="mt-1">יש להגדיר את משתני הסביבה NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY ו-SUPABASE_SERVICE_ROLE_KEY להפעלת תור ההגשות.</p>
          </div>
        )}

        {data && data.configured && data.entries.length === 0 && (
          <div className="text-center py-16 text-slate-400">
            <p className="text-lg">אין הגשות ממתינות לאישור.</p>
          </div>
        )}

        {data && data.configured && data.entries.length > 0 && (
          <div className="flex flex-col gap-6">
            <p className="text-sm text-slate-500">
              {data.entries.length} הגשות ממתינות לאישור
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
