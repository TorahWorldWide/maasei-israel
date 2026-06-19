# מעשי ישראל — Maasei Israel

> אוסף מתועד של מעשים טובים, המצאות ותרומות של עם ישראל לעולם — כל פריט עם הוכחה.  
> A documented collection of good deeds, inventions, and contributions of the Jewish people — every item with a verifiable source.

## Running locally / הרצה מקומית

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The site runs in **read-only seed mode** without env vars — 8 pre-loaded verified entries are displayed immediately.

## Supabase setup / הקמת מסד נתונים

1. Create a new project at [supabase.com](https://supabase.com)
2. In your project → **SQL Editor**, paste and run the full contents of `supabase/schema.sql`
3. Go to **Project Settings → API** and copy your keys

## Environment variables / משתני סביבה

Set these in Vercel (Project Settings → Environment Variables):

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL (e.g. `https://xxx.supabase.co`) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous (public) key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key — **server-only, never exposed to client** |
| `ADMIN_PASSWORD` | Password for the `/admin` panel |

Copy `.env.example` to `.env.local` for local development.

## How it works / איך זה עובד

- **Without env vars** — the site deploys instantly in read-only mode, showing 8 seed entries from `src/data/entries.json`. Submission form returns success but data is not persisted.
- **With Supabase env vars** — `getApprovedEntries()` queries the live `entries` table; submissions land in the `submissions` table pending admin review.
- **Admin panel** (`/admin`) — password-protected queue to approve or reject pending submissions. Requires both `ADMIN_PASSWORD` and Supabase configured.

## Tech stack

- Next.js 16 (App Router) + React 19 + TypeScript
- Tailwind CSS v4
- Supabase (PostgreSQL + RLS) — optional, graceful fallback to seed data
- Rubik + Heebo Hebrew fonts via next/font/google
