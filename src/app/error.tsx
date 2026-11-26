"use client";

// Shown when a page cannot read the database (DataUnavailableError in
// src/lib/data.ts) or anything else throws. It says plainly that the deeds
// could not be loaded, instead of quietly showing the 8 seed deeds.
export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="min-h-screen flex items-center justify-center px-4" dir="rtl">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-bold text-[#e6c66e] mb-3" style={{ fontFamily: "var(--font-frank-ruhl), serif" }}>
          לא הצלחנו לטעון את המעשים
        </h1>
        <p className="text-blue-100/80 leading-relaxed mb-6">
          מסד הנתונים לא ענה. נסו שוב בעוד כמה דקות.
          <br />
          <span dir="ltr">The deeds could not be loaded. Please try again in a few minutes.</span>
        </p>
        <button
          type="button"
          onClick={reset}
          className="px-6 py-2.5 rounded-full bg-gradient-to-b from-[#e6c66e] to-[#c9a84a] text-[#0a1834] font-semibold"
        >
          לנסות שוב
        </button>
      </div>
    </main>
  );
}
