-- ============================================================
-- Maasei Israel — Supabase Schema
-- ============================================================
-- How to use:
--   1. Create a new Supabase project at https://supabase.com
--   2. Open the SQL Editor in your project dashboard
--   3. Paste this entire file and click "Run"
--   4. Copy your project URL, anon key, and service role key
--      into Vercel environment variables (see README.md)
-- ============================================================

-- Enable UUID generation
create extension if not exists "uuid-ossp";

-- ─── entries ────────────────────────────────────────────────
-- Approved entries shown publicly on the site.
create table if not exists entries (
  id           uuid        primary key default uuid_generate_v4(),
  title        text        not null,
  description  text        not null,
  category     text        not null check (category in ('חסד', 'המצאה מדעית', 'תרומה לעולם', 'היסטורי')),
  year         integer,
  media_type   text        not null default 'image' check (media_type in ('video_embed', 'video_upload', 'image')),
  media_url    text        not null default '',
  source_url   text        not null,
  source_label text        not null default '',
  submitted_by text,
  status       text        not null default 'approved' check (status in ('pending', 'approved')),
  created_at   timestamptz not null default now()
);

-- ─── submissions ────────────────────────────────────────────
-- Pending submissions awaiting admin review.
create table if not exists submissions (
  id           uuid        primary key default uuid_generate_v4(),
  title        text        not null,
  description  text        not null,
  category     text        not null check (category in ('חסד', 'המצאה מדעית', 'תרומה לעולם', 'היסטורי')),
  year         integer,
  media_type   text        not null default 'image' check (media_type in ('video_embed', 'video_upload', 'image')),
  media_url    text        not null default '',
  source_url   text        not null,
  source_label text        not null default '',
  submitted_by text,
  status       text        not null default 'pending',
  created_at   timestamptz not null default now()
);

-- ─── Row Level Security ──────────────────────────────────────
alter table entries    enable row level security;
alter table submissions enable row level security;

-- Public (anon key) can SELECT approved entries only
create policy "public_read_approved_entries"
  on entries
  for select
  using (status = 'approved');

-- Public (anon key) can INSERT new submissions
create policy "public_insert_submissions"
  on submissions
  for insert
  with check (true);

-- All other operations (entries insert/update, submissions read/update/delete)
-- require the service role key, which bypasses RLS automatically.
-- No additional policies are needed for service-role operations.
