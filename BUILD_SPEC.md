# Build spec — Maasei Israel frontend growth features

You are working in the Next.js 16 (App Router) repo at /home/ubuntu/maasei-israel.
This is Tomer's LIVE site (maasei-israel.vercel.app). Be surgical and safe.

## HARD CONSTRAINTS (read first, do not violate)
- DO NOT touch anything in `company-scripts/`, `docs/`, `supabase/`, or any
  Python file. Backend is done and frozen.
- DO NOT change the existing data-fetch behavior: `src/lib/data.ts` falls back to
  `src/data/entries.json` seed when Supabase env vars are absent. Preserve that
  fallback in every new function you add (try Supabase, catch -> seed).
- DO NOT remove or restructure existing components (Theater, Feed, EntryCard,
  Slideshow, OverviewPanel, CitationList). You may ADD to them minimally.
- Keep the existing visual language: navy background (#081026 / #0a1834), gold
  accent (#c9a84a), Hebrew RTL, fonts already wired in layout.tsx.
- Every page must keep `export const dynamic = "force-dynamic";` where the
  existing pages use it.
- The build MUST pass: `npm run build` with zero errors. TypeScript strict.
- DO NOT run any git command. DO NOT deploy. Just write code. I will review,
  build, and deploy.

## Entry shape (from src/lib/data.ts — already defined, import it)
Entry { id, title, description, category, year, media_type, media_url,
        source_url, source_label, act?, ripple?, citations?: Citation[],
        status, created_at }
Citation { quote, source_label, source_url, locator? }
media_url for video_embed is a YouTube watch/share URL.

## FEATURE 1 — Per-entry pages (SEO + shareable deep links)
Goal: every deed has its own URL so Google indexes it and Tomer can link one
specific proof in a debate.
1. In src/lib/data.ts add `getEntryById(id: string): Promise<Entry | null>` —
   query Supabase entries by id (status approved), fall back to finding it in the
   seed JSON; return null if not found. Keep the same try/catch->seed pattern.
2. Create route `src/app/deed/[id]/page.tsx`:
   - Server component, `force-dynamic`.
   - Loads the entry; if null -> `notFound()`.
   - Renders: the title (large, gold-accent serif), year + category badge, the
     YouTube video embedded (reuse the same embed approach the Theater/EntryCard
     uses — extract the YouTube id from media_url and use an <iframe> to
     youtube-nocookie.com/embed/<id>), the description, act/ripple if present,
     and the citations each as a clickable link to its source_url with the quote
     shown. Include a "חזרה לכל המעשים" link back to "/".
   - Match the site's navy/gold RTL styling.
   - Add `export async function generateMetadata({ params })`: title = entry
     title + " | מעשי ישראל", description = entry.description (trimmed ~160
     chars), openGraph + twitter card with title/description and an OG image URL
     pointing to `/deed/[id]/opengraph-image` (see step 3), and
     `alternates.canonical` = `/deed/<id>`.
   - Add JSON-LD via a <script type="application/ld+json">: schema.org Article
     (headline=title, datePublished=created_at, articleBody=description,
     about=category) AND include the source as `citation`/`isBasedOn` =
     entry.source_url. Make it valid JSON-LD.
3. Create `src/app/deed/[id]/opengraph-image.tsx` using next/og ImageResponse
   (1200x630): navy background, gold Star-of-David mark, the entry title in
   large Hebrew text (RTL), and "מעשי ישראל" wordmark. Keep it dependency-light
   (ImageResponse is built into next). Handle missing entry gracefully (generic
   card).
4. Make existing EntryCard titles link to `/deed/<id>` (wrap the title or add a
   "לעמוד המלא" link) WITHOUT breaking the existing card layout or the slideshow.

## FEATURE 2 — Share-the-proof button
Goal: one tap copies a debate-ready proof (claim + source + page link).
1. Create `src/components/ShareProof.tsx` (client component):
   - Props: entry (or the fields title, source_url, source_label, id, and the
     first citation quote if any).
   - A gold button labeled "שתף הוכחה". On click:
     - Build text: `"<title>\n<first citation quote, if any>\nמקור: <source_label> <source_url>\nעוד מעשים: https://maasei-israel.vercel.app/deed/<id>"`.
     - Use `navigator.share({text})` if available (mobile), else
       `navigator.clipboard.writeText(text)` and show a tiny "הועתק!" confirmation
       for ~2s.
   - Accessible, RTL, matches gold styling.
2. Place ShareProof on the per-entry page (Feature 1) and inside EntryCard
   (small, unobtrusive). Don't disrupt existing layout.

## FEATURE 3 — Bilingual UI (Hebrew default, English toggle)
Goal: Tomer debates in English; the site chrome should be readable in English.
Entry CONTENT stays Hebrew (the deeds are Hebrew-sourced) — only translate the
UI/chrome strings and switch document direction.
1. Create `src/lib/i18n.ts`: a dictionary of all UI strings in he + en
   (header nav, buttons, catalog heading + subtitle, footer text, per-entry page
   labels like "Back to all deeds", "Source", "Share proof", category names
   optionally with English glosses). Export `type Lang = "he" | "en"` and a
   `t(lang, key)` helper.
2. Create `src/components/LangProvider.tsx` (client context) that holds the
   current lang, persists it to localStorage ("maasei.lang"), and sets
   document.documentElement.lang + dir ("rtl" for he, "ltr" for en) on change.
   Default "he".
3. Add a small language toggle (he / EN) in the header nav (page.tsx and the
   per-entry page header). Wrap the app so client components can read the lang.
4. Apply translations to the static UI strings in: header, catalog headings,
   footer, the per-entry page labels, ShareProof button, and the submit page
   header if trivial. DO NOT attempt to translate entry titles/descriptions.
   When lang=en, keep Hebrew entry content but show English chrome around it.
   Keep it simple — a partial-but-correct English chrome is the goal, not a
   full content translation.

## Definition of done
- `npm run build` passes clean.
- Visiting `/deed/<some-seed-id>` renders a full styled page with video,
  citations, JSON-LD in the HTML, and working OG image at
  `/deed/<id>/opengraph-image`.
- Home page still works exactly as before, plus card titles link to deed pages
  and show a share button.
- A header toggle switches UI chrome he<->en and flips dir.
- No backend/python/docs files changed. No git/deploy run.

Seed entry ids to test with (from src/data/entries.json): use
`seed-salk-polio`, `seed-drip-irrigation`, `seed-usb-flash-drive`.
