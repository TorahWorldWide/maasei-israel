"use client";

import { useState, useRef } from "react";
import Link from "next/link";

const CATEGORIES = ["חסד", "המצאה מדעית", "תרומה לעולם", "היסטורי"] as const;
const MEDIA_TYPES = [
  { value: "image", label: "ללא מדיה / תמונה בקישור" },
  { value: "video_embed", label: "סרטון YouTube (קישור)" },
  { value: "video_upload", label: "העלאת וידאו/תמונה מהמחשב" },
] as const;

const ALLOWED_MIME = [
  "video/mp4",
  "video/quicktime",
  "video/webm",
  "video/x-matroska",
  "video/3gpp",
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
];
const MAX_BYTES = 52428800; // 50 MB

interface FormState {
  title: string;
  description: string;
  category: string;
  year: string;
  media_type: string;
  media_url: string;
  source_url: string;
  source_label: string;
  submitted_by: string;
}

const EMPTY_FORM: FormState = {
  title: "",
  description: "",
  category: "חסד",
  year: "",
  media_type: "image",
  media_url: "",
  source_url: "",
  source_label: "",
  submitted_by: "",
};

function validate(form: FormState, uploading: boolean): Record<string, string> {
  const errs: Record<string, string> = {};
  if (!form.title.trim()) errs.title = "שם הפריט נדרש";
  if (!form.description.trim()) errs.description = "תיאור נדרש";
  if (!form.source_url.trim()) {
    errs.source_url = "קישור מקור הוא שדה חובה — כל פריט חייב הוכחה";
  } else if (!/^https?:\/\/.+/.test(form.source_url.trim())) {
    errs.source_url = "יש להזין קישור תקין (מתחיל ב-http:// או https://)";
  }
  if (!form.source_label.trim()) errs.source_label = "שם המקור נדרש";
  if (uploading) errs.media_url = "המתינו לסיום העלאת הקובץ";
  return errs;
}

const inputCls = (err?: string) =>
  `w-full px-4 py-2.5 rounded-xl border text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 transition-shadow ${
    err
      ? "border-red-400 focus:ring-red-200"
      : "border-slate-200 focus:ring-blue-200 focus:border-blue-400"
  }`;

// Upload a file straight to Supabase Storage via a one-time signed URL.
async function uploadToSupabase(
  file: File,
  onProgress: (pct: number) => void
): Promise<string> {
  // 1) ask our server for a signed upload URL
  const res = await fetch("/api/upload-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contentType: file.type, size: file.size }),
  });
  const data = await res.json();
  if (!res.ok || !data.ok) throw new Error(data.error ?? "נכשלה יצירת קישור העלאה");

  // 2) PUT the file directly to Supabase Storage with progress
  const uploadEndpoint: string = data.uploadUrl;

  await new Promise<void>((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", uploadEndpoint, true);
    xhr.setRequestHeader("Content-Type", file.type);
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
    };
    xhr.onload = () =>
      xhr.status >= 200 && xhr.status < 300
        ? resolve()
        : reject(new Error("ההעלאה נכשלה (" + xhr.status + ")"));
    xhr.onerror = () => reject(new Error("שגיאת רשת בהעלאה"));
    xhr.send(file);
  });

  // 3) the public URL is where the file now lives
  return data.publicUrl;
}

export default function SubmitPage() {
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [persisted, setPersisted] = useState(true);

  // upload state
  const [fileName, setFileName] = useState("");
  const [uploadPct, setUploadPct] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploadDone, setUploadDone] = useState(false);
  const [uploadErr, setUploadErr] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const set = (key: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value }));

  const onMediaTypeChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const v = e.target.value;
    // reset upload/url state when switching media mode
    setForm((f) => ({ ...f, media_type: v, media_url: "" }));
    setFileName("");
    setUploadPct(0);
    setUploadDone(false);
    setUploadErr("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadErr("");
    setUploadDone(false);
    setUploadPct(0);

    if (!ALLOWED_MIME.includes(file.type)) {
      setUploadErr("סוג קובץ לא נתמך. מותר וידאו (mp4/mov/webm) או תמונה.");
      return;
    }
    if (file.size > MAX_BYTES) {
      setUploadErr("הקובץ גדול מדי. מקסימום 50MB.");
      return;
    }

    setFileName(file.name);
    setUploading(true);
    try {
      const url = await uploadToSupabase(file, setUploadPct);
      setForm((f) => ({ ...f, media_url: url }));
      setUploadDone(true);
    } catch (err) {
      setUploadErr(err instanceof Error ? err.message : "ההעלאה נכשלה");
      setFileName("");
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate(form, uploading);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setStatus("loading");
    try {
      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          year: form.year ? parseInt(form.year, 10) : null,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "שגיאה");
      setPersisted(data.persisted ?? true);
      setStatus("success");
      setForm(EMPTY_FORM);
      setFileName("");
      setUploadPct(0);
      setUploadDone(false);
    } catch {
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <header className="bg-blue-900 text-white">
          <div className="max-w-2xl mx-auto px-4 sm:px-6 py-4">
            <Link href="/" className="text-xl font-bold">מעשי ישראל</Link>
          </div>
        </header>
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-green-100 text-center max-w-md w-full">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-slate-900 mb-2">תודה!</h2>
            <p className="text-slate-600">
              ההגשה נשלחה ותיבדק לפני פרסום.
            </p>
            {!persisted && (
              <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 px-4 py-2.5 rounded-xl mt-4">
                שימו לב: מסד הנתונים אינו מחובר עדיין. ההגשה תישמר לאחר חיבור Supabase.
              </p>
            )}
            <div className="flex gap-3 justify-center mt-6">
              <button
                onClick={() => setStatus("idle")}
                className="text-sm text-blue-700 hover:text-blue-900 underline"
              >
                שלחו פריט נוסף
              </button>
              <Link href="/" className="text-sm text-slate-500 hover:text-slate-700 underline">
                חזרה לדף הבית
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const isUpload = form.media_type === "video_upload";
  const isYouTube = form.media_type === "video_embed";

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-blue-900 text-white">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-3">
          <Link href="/" className="text-white/60 hover:text-white/90 transition-colors text-sm">
            ← חזרה
          </Link>
          <span className="text-white/30">|</span>
          <h1 className="text-lg font-bold">שלחו מעשה טוב</h1>
        </div>
      </header>

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 sm:px-6 py-10">
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl p-6 md:p-8 shadow-sm border border-slate-100 flex flex-col gap-5"
          noValidate
        >
          <div>
            <h2 className="text-2xl font-bold text-slate-900">הגשת מעשה טוב</h2>
            <p className="text-sm text-slate-500 mt-1">
              כל פריט חייב לכלול קישור מקור מאומת. ללא מקור — ההגשה לא תתקבל.
            </p>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              שם הפריט <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.title}
              onChange={set("title")}
              placeholder='לדוגמה: "חיסון נגד פוליו"'
              className={inputCls(errors.title)}
            />
            {errors.title && (
              <p className="text-red-500 text-xs mt-1">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              תיאור <span className="text-red-500">*</span>
            </label>
            <textarea
              value={form.description}
              onChange={set("description")}
              rows={4}
              placeholder="תארו את המעשה הטוב, ההמצאה או התרומה..."
              className={inputCls(errors.description)}
            />
            {errors.description && (
              <p className="text-red-500 text-xs mt-1">{errors.description}</p>
            )}
          </div>

          {/* Category + Year */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                קטגוריה <span className="text-red-500">*</span>
              </label>
              <select value={form.category} onChange={set("category")} className={inputCls()}>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                שנה (אופציונלי)
              </label>
              <input
                type="number"
                value={form.year}
                onChange={set("year")}
                placeholder="2024"
                min={1}
                max={new Date().getFullYear()}
                className={inputCls()}
              />
            </div>
          </div>

          {/* Source — highlighted as required */}
          <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-4 flex flex-col gap-3">
            <p className="text-sm font-semibold text-blue-800 flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              מקור מאומת — חובה
            </p>
            <div>
              <label className="block text-xs font-medium text-blue-700 mb-1">
                קישור למקור <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                value={form.source_url}
                onChange={set("source_url")}
                placeholder="https://..."
                className={inputCls(errors.source_url)}
              />
              {errors.source_url && (
                <p className="text-red-500 text-xs mt-1">{errors.source_url}</p>
              )}
            </div>
            <div>
              <label className="block text-xs font-medium text-blue-700 mb-1">
                שם המקור <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.source_label}
                onChange={set("source_label")}
                placeholder='לדוגמה: "ויקיפדיה" או "הניו יורק טיימס"'
                className={inputCls(errors.source_label)}
              />
              {errors.source_label && (
                <p className="text-red-500 text-xs mt-1">{errors.source_label}</p>
              )}
            </div>
          </div>

          {/* Media */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              מדיה (אופציונלי)
            </label>
            <select value={form.media_type} onChange={onMediaTypeChange} className={inputCls()}>
              {MEDIA_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* YouTube link mode */}
          {isYouTube && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                קישור לסרטון YouTube
              </label>
              <input
                type="url"
                value={form.media_url}
                onChange={set("media_url")}
                placeholder="https://youtube.com/watch?v=..."
                className={inputCls()}
              />
            </div>
          )}

          {/* Direct upload mode */}
          {isUpload && (
            <div className="rounded-xl border-2 border-dashed border-blue-200 bg-blue-50/40 p-5 flex flex-col gap-3">
              <p className="text-sm font-semibold text-blue-800 flex items-center gap-1.5">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.9A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                העלאת וידאו או תמונה מהמחשב
              </p>
              <p className="text-xs text-blue-600/80">
                וידאו (MP4 / MOV / WEBM) או תמונה, עד 50MB. הקובץ נשמר בצורה מאובטחת.
              </p>

              <input
                ref={fileInputRef}
                type="file"
                accept="video/*,image/*"
                onChange={handleFile}
                disabled={uploading}
                className="block w-full text-sm text-slate-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-800 file:text-white file:text-sm file:font-medium file:cursor-pointer hover:file:bg-blue-900 disabled:opacity-60"
              />

              {fileName && (
                <p className="text-xs text-slate-600 truncate">📎 {fileName}</p>
              )}

              {uploading && (
                <div className="flex flex-col gap-1">
                  <div className="h-2 w-full bg-blue-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 transition-all duration-150"
                      style={{ width: `${uploadPct}%` }}
                    />
                  </div>
                  <p className="text-xs text-blue-700">מעלה... {uploadPct}%</p>
                </div>
              )}

              {uploadDone && !uploading && (
                <p className="text-xs text-green-700 bg-green-50 border border-green-200 px-3 py-2 rounded-lg flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  הקובץ הועלה בהצלחה
                </p>
              )}

              {uploadErr && (
                <p className="text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
                  {uploadErr}
                </p>
              )}
              {errors.media_url && (
                <p className="text-red-500 text-xs">{errors.media_url}</p>
              )}
            </div>
          )}

          {/* Submitted by */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              שם לקרדיט (אופציונלי)
            </label>
            <input
              type="text"
              value={form.submitted_by}
              onChange={set("submitted_by")}
              placeholder="השם שלכם"
              className={inputCls()}
            />
          </div>

          {status === "error" && (
            <p className="text-red-600 text-sm bg-red-50 border border-red-200 px-4 py-2.5 rounded-xl">
              אירעה שגיאה. אנא נסו שוב.
            </p>
          )}

          <button
            type="submit"
            disabled={status === "loading" || uploading}
            className="bg-blue-800 text-white font-bold px-6 py-3 rounded-xl hover:bg-blue-900 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {status === "loading" ? "שולח..." : uploading ? "ממתין לסיום העלאה..." : "שלח הגשה"}
          </button>
        </form>
      </main>
    </div>
  );
}
