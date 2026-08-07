# Tagging audit — current state (2026-08-07)

Read-only audit of the `entries` table (Supabase project `gpgqjuthztuhtdqlkixo`) and of how the
site consumes tags. **207 approved entries** were fetched via REST (`status=eq.approved`).
Companion file: [`proposed-tags.json`](./proposed-tags.json) — proposed `century` / `countries` /
`has_video` values for every published entry.

## 1. Tag-like fields that exist today

| Field | Where | Values | Notes |
|---|---|---|---|
| `category` (text, NOT NULL) | DB + UI chips | `חסד` 60 · `המצאה מדעית` 86 · `תרומה לעולם` 45 · `היסטורי` 16 | The only real tag. CHECK constraint allows exactly these 4. |
| `categories` (array) | DB + `entryCategories()` in `src/lib/data.ts` | **NULL for all 207 rows** | Multi-tag support is built in code (UI filters/badges by it when present) but has never been populated. |
| `year` (integer) | DB → derived "era" chips | 1180–2025, **0 rows missing** | Not stored as a tag; `Feed.tsx` derives an era at render time. |
| `media_type` | DB | `image` 131 · `video_embed` 76 · `video_upload` 0 | Effectively a has-video flag already (`video_embed` ⇔ has video), but the UI never filters by it. |
| `status` | DB | all `approved` | Not a visitor-facing tag. |
| — country | — | **does not exist anywhere** | Location is only implicit in free text. |
| — keywords | — | does not exist as a column | "Dedup keywords" live only in `company-scripts/maasei_ledger.py` / `maasei_leads.py` (title word-overlap test at insert time), nothing is stored per entry. |

## 2. How the filter UI consumes them (`src/components/Feed.tsx`)

* **Category chips** — `CATEGORIES = ["הכל","חסד","המצאה מדעית","תרומה לעולם","היסטורי"]`, matched
  against `entryCategories(e)` (falls back to the single `category` since `categories` is always null).
* **Era chips** — `ERAS = ["הכל","עתיק","טרום המדינה","המאה ה-20","עכשווי"]` computed by `getEra(year)`:
  `<1900 → עתיק`, `<1948 → טרום המדינה`, `<2000 → המאה ה-20`, else `עכשווי`.
  * `year === null` is bucketed as `עתיק` — currently latent (no null years), but a modern entry
    saved without a year would silently appear under "ancient".
  * "עתיק" lumps the Rambam (1180) together with 1848/1892 — a 700-year bucket.
* **Free-text search** over `title`/`description` (+ English fields). No location or video filter exists.
* `OverviewPanel.tsx` shows historian stats only; it does not consume tags.

## 3. Current-state problems found in the data

### 3.1 Near-duplicate entries (the biggest issue)
The script-side dedup compares title words only, so re-phrased resubmissions slipped through.
Same deed published more than once (index = position in `created_at desc` order, as in the dump):

* **זק"א ×3** — `dc4981dc` (1995), `94c70fad` (1989), `be2c23a1` (1995)
* **יד שרה ×2** — `74f8c8ac`, `9cdfb538` (both 1976)
* **עזר מציון ×2** — `db664bcd`, `41f71ed3` (both 1979)
* **איחוד הצלה ×2** — `242965d3`, `82e7d021` (both 2006)
* **זכרון מנחם ×2** — `3345051f`, `378c6e2a` (both 1990)
* **ICQ/מירביליס ×2** — `767f5172`, `8a38381b` (both 1996)
* **PillCam ×2** — `9c2cdce3` (Given Imaging, 2001), `c1bab11d` (גבריאל אידן, 2001)
* **טבל (Tevel) ×2** — `991fe9d2` (2017), `3426ff78` (2021)
* **IsraAID אפגניסטן ×2** — `65705b8c`, `e6b2739c` (both 2021)
* **IsraAID איטליה ×2** — `5aab0fea`, `310fc0e4` (both 2016)
* Related-but-arguably-distinct clusters worth an editorial decision: Watergen (`013c0d90` Gaza /
  `11d9733b` global), Turkey 2023 (`63d62fcb` rescue / `676c6376` ZAKA convoy / `f0ca86ec` field
  hospital), Haiti (`9bd005b9` IDF 2010 / `cddbf703` IsraAID 2010 / `cd441e22` IsraAID 2021).

### 3.2 Category misuse / inconsistency
* **המצאה מדעית vs תרומה לעולם is arbitrary** for the ~60 scientist/Nobel entries. Near-identical
  entries sit in different categories: Lederberg, Gerty Cori, Bloch, Sabin, Yalow, Blumberg,
  Waksman, Elion, Milstein, Levi-Montalcini, Kandel (all `תרומה לעולם`) vs Luria, Nirenberg,
  Axelrod, Chain, Landsteiner, Prusiner, Arthur Kornberg… (all `המצאה מדעית`). Rosalind Franklin is
  `תרומה לעולם` while the same genre of discovery entries is `המצאה מדעית`.
* **היסטורי is a grab-bag**: pre-state history (רוטשילד 1882, דונה גרסיה 1537) sits with modern
  operations (אנטבה 1976, מבצע שלמה 1991) and with a Nobel-chemistry biography (רואלד הופמן) —
  "historic" behaves like an era, which the era chips already cover.
* `ש"י עגנון` (Nobel in **literature**) is filed under `תרומה לעולם` — there is no culture category.
* `categories[]` multi-tagging (e.g., Entebbe = חסד + היסטורי) exists in code but no row uses it.

### 3.3 Year-field semantics drift
All rows have a year, but it means different things: event year (rescues), founding year (orgs),
publication year, or **Nobel-award year** decades after the work (e.g., Lefkowitz `2012` for 1968
work, Alter `2020` for 1970s work, Kohn `1964` work / prize 1998). Two mismatches with the text:
`55c7771e` (בגין) year=1978 vs signing 1979 in the description; `21e70076` (על כנפי נשרים)
year=1949 vs "דצמבר 1948" in the text. The ZAKA triplet carries two different years (1989/1995).
Century tags inherit this drift — fine for filtering, but worth knowing.

### 3.4 Media gaps
* 5 entries (the oldest seed batch) have **no media at all** (`media_url` empty, `media_urls` empty):
  Waze `3186a5e8`, רות הנדלר `eef315da`, איינשטיין `8fcfea36`, זק"א `be2c23a1`, סאלק `a8f55761`.
* `video_upload` is unused; `has_video` is exactly `media_type === "video_embed"` (76 entries).

### 3.5 Content accuracy flag
* `b134e17d` (יואל מוקיר) describes him only as a Tel Aviv University professor; he is primarily at
  Northwestern (TAU is a secondary affiliation) — worth a wording fix.
* 136 of 207 entries have no English translation (`title_en`/`description_en` null) — the English
  site falls back to Hebrew for two-thirds of the catalog.

## 4. Proposed new tags (see `proposed-tags.json` for every entry)

1. **`century`** — computed from `year`, named exactly `"<base>–<base+100>"` (en dash), e.g. 1948 →
   `1900–2000`. Distribution: 1100–1200 ×1, 1500–1600 ×1, 1700–1800 ×1, 1800–1900 ×13,
   1900–2000 ×102, 2000–2100 ×89. `null` if year is ever missing.
2. **`countries`** — Hebrew names of the country/countries where the deed took place, inferred by
   reading each title+description (and well-documented workplaces for scientists). 50 distinct
   values; top: ישראל 98, ארה"ב 58, טורקיה 5, בריטניה 5, פולין 4, איטליה 4, אוסטריה 4.
   Conventions used (owner should confirm):
   * Pre-state Eretz-Israel deeds (רוטשילד, מונטיפיורי, הדסה…) are tagged `ישראל`.
   * Two region-level values where no country applies: `אפריקה` (`70436895` — "10 מדינות אפריקה";
     also on `11d9733b`) and `עזה` (`013c0d90`). Historic name `זאיר` kept as written (`be392166`).
   * Exactly 1 entry left with an empty list: הג'וינט (`9219266d`, "פועל ביותר מ-70 מדינות") —
     a genuinely global organization with no single country of action.
3. **`has_video`** — boolean, today derivable from `media_type === "video_embed"`; storing/filtering
   it gives the requested "עם וידאו / בלי וידאו" chip for free.

### Suggested implementation route (no schema break)
Populate the existing `categories`-style pattern: either new columns (`century text`,
`countries text[]`, `has_video boolean`) or a single `tags text[]`; add three chip rows in
`Feed.tsx` mirroring the era chips. The era chips can then be retired or kept alongside centuries.
Fixing the near-duplicates (merge/delete) should happen **before** tags go live so counts are honest.
