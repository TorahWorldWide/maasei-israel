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


-- ─── Seed: 8 verified starter entries ───────────────────────
insert into entries (title, description, category, year, media_type, media_url, source_url, source_label, submitted_by, status, created_at) values
  ('יונאס סאלק ויתר על הפטנט לחיסון הפוליו', 'ד"ר יונאס סאלק, רופא יהודי-אמריקאי, פיתח ב-1955 את החיסון הראשון נגד שיתוק ילדים (פוליו) ששיתק מאות אלפי ילדים בשנה. כששאלו אותו למי שייך הפטנט, ענה: "לאנשים. אין פטנט. האם היית מפטנט את השמש?". הוויתור הציל מיליונים והנגיש את החיסון לעולם כולו בחינם.', 'חסד', 1955, 'image', NULL, 'https://he.wikipedia.org/wiki/%D7%99%D7%95%D7%A0%D7%90%D7%A1_%D7%A1%D7%90%D7%9C%D7%A7', 'ויקיפדיה — יונאס סאלק', NULL, 'approved', '2026-06-19T00:00:01Z'),
  ('טפטפות — ההמצאה הישראלית שמאכילה את העולם', 'המהנדס שמחה בלאס וקיבוץ חצרים פיתחו בשנות ה-60 את שיטת ההשקיה בטפטפות (חברת נטפים). השיטה חוסכת עד 70% מהמים לעומת השקיה רגילה ומאפשרת לגדל מזון במדבר. כיום היא בשימוש בלמעלה מ-110 מדינות ומסייעת להאכיל אזורים צחיחים ברחבי העולם.', 'תרומה לעולם', 1965, 'image', NULL, 'https://he.wikipedia.org/wiki/%D7%94%D7%A9%D7%A7%D7%99%D7%94_%D7%91%D7%98%D7%A4%D7%98%D7%95%D7%A3', 'ויקיפדיה — השקיה בטפטוף', NULL, 'approved', '2026-06-19T00:00:02Z'),
  ('"להציל לב של ילד" — ניתוחי לב בחינם לילדים מכל העולם', 'הארגון הישראלי Save a Child''s Heart מעניק ניתוחי לב מצילי-חיים בחינם לילדים ממדינות מתפתחות, ללא קשר לדת, גזע או לאום. מאז 1995 טופלו למעלה מ-6,000 ילדים מ-65 מדינות, רבים מהן מדינות ערביות ואפריקאיות ללא יחסים עם ישראל.', 'חסד', 1995, 'image', NULL, 'https://en.wikipedia.org/wiki/Save_a_Child%27s_Heart', 'Wikipedia — Save a Child''s Heart', NULL, 'approved', '2026-06-19T00:00:03Z'),
  ('הדיסק-און-קי (USB) — המצאה של דב מורן', 'היזם הישראלי דב מורן, מייסד חברת M-Systems, המציא בסוף שנות ה-90 את ה-Disk-on-Key — כונן ה-USB הנייד שהפך לסטנדרט עולמי לאחסון נתונים. ההמצאה שינתה את אופן העברת המידע בעולם כולו.', 'המצאה מדעית', 2000, 'image', NULL, 'https://he.wikipedia.org/wiki/%D7%93%D7%91_%D7%9E%D7%95%D7%A8%D7%9F', 'ויקיפדיה — דב מורן', NULL, 'approved', '2026-06-19T00:00:04Z'),
  ('זק"א — מתנדבים שמצילים ומכבדים את המתים', 'ארגון זק"א (זיהוי קורבנות אסון) מורכב מאלפי מתנדבים שמגיעים ראשונים לזירות פיגועים, תאונות ואסונות — מצילים פצועים ומלקטים שרידים כדי להביא את הנפטרים לקבר ישראל בכבוד. הארגון פועל בהתנדבות מלאה ונקרא לסייע גם באסונות בינלאומיים ברחבי העולם.', 'חסד', 1995, 'image', NULL, 'https://he.wikipedia.org/wiki/%D7%96%D7%A7%22%D7%90', 'ויקיפדיה — זק"א', NULL, 'approved', '2026-06-19T00:00:05Z'),
  ('אלברט איינשטיין ותורת היחסות', 'אלברט איינשטיין, פיזיקאי יהודי, ניסח את תורת היחסות הפרטית (1905) והכללית (1915) ששינו מן היסוד את הבנת האדם את הזמן, החלל והכבידה. עבודתו היא יסוד לפיזיקה המודרנית, ל-GPS שאנו משתמשים בו יומיום ולחקר היקום. ב-1921 זכה בפרס נובל לפיזיקה.', 'המצאה מדעית', 1915, 'image', NULL, 'https://he.wikipedia.org/wiki/%D7%90%D7%9C%D7%91%D7%A8%D7%98_%D7%90%D7%99%D7%99%D7%A0%D7%A9%D7%98%D7%99%D7%99%D7%9F', 'ויקיפדיה — אלברט איינשטיין', NULL, 'approved', '2026-06-19T00:00:06Z'),
  ('רות הנדלר והשד התותב לנשים אחרי סרטן', 'רות הנדלר, יזמת יהודייה-אמריקאית שהמציאה את בובת הברבי, חלתה בסרטן השד ועברה כריתה. לאחר שלא מצאה פתרון הולם, פיתחה ב-1975 את "Nearly Me" — שד תותב ריאליסטי שהחזיר ביטחון ותחושת שלמות למיליוני נשים שהחלימו מסרטן השד ברחבי העולם.', 'תרומה לעולם', 1975, 'image', NULL, 'https://en.wikipedia.org/wiki/Ruth_Handler', 'Wikipedia — Ruth Handler', NULL, 'approved', '2026-06-19T00:00:07Z'),
  ('Waze — אפליקציית הניווט הישראלית החינמית', 'Waze פותחה בישראל (2008) ומאפשרת לנהגים ברחבי העולם לנווט בחינם תוך שיתוף מידע על פקקים, תאונות ומכשולים בזמן אמת. האפליקציה, שמשרתת מאות מיליוני משתמשים, חוסכת זמן, דלק ותאונות — דוגמה לחסד טכנולוגי המבוסס על עזרה הדדית בין נהגים.', 'המצאה מדעית', 2008, 'image', NULL, 'https://he.wikipedia.org/wiki/Waze', 'ויקיפדיה — Waze', NULL, 'approved', '2026-06-19T00:00:08Z');
