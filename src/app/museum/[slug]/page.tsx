import fs from "node:fs/promises";
import path from "node:path";
import { notFound } from "next/navigation";
import { cookies } from "next/headers";
import { LANG_COOKIE } from "@/lib/i18n";
import type { Metadata } from "next";
import type { CSSProperties } from "react";
import { SITE_TITLE_BILINGUAL } from "@/lib/i18n";
import type { MuseumPageData } from "@/lib/museum";
import { isReadyMuseum } from "@/lib/ready";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import MuseumPage, { type MuseumLook, type MuseumBackdrop } from "@/components/museum/MuseumPage";
import { Bellefair, Bona_Nova, David_Libre, IBM_Plex_Mono, IBM_Plex_Sans_Hebrew, Noto_Serif_Hebrew } from "next/font/google";

// Faces for the three trial looks (?look=a|b|c). Not preloaded: only the look
// in use downloads its files.
const notoSerif = Noto_Serif_Hebrew({ variable: "--font-noto-serif-he", subsets: ["hebrew", "latin"], weight: ["400", "500"], display: "swap", preload: false });
const davidLibre = David_Libre({ variable: "--font-david", subsets: ["hebrew", "latin"], weight: ["400", "500", "700"], display: "swap", preload: false });
const plexHe = IBM_Plex_Sans_Hebrew({ variable: "--font-plex-he", subsets: ["hebrew", "latin"], weight: ["300", "400", "600"], display: "swap", preload: false });
const plexMono = IBM_Plex_Mono({ variable: "--font-plex-mono", subsets: ["latin"], weight: ["400"], display: "swap", preload: false });
const bellefair = Bellefair({ variable: "--font-bellefair", subsets: ["hebrew", "latin"], weight: "400", display: "swap", preload: false });
const bonaNova = Bona_Nova({ variable: "--font-bona", subsets: ["hebrew", "latin"], weight: ["400", "700"], display: "swap", preload: false });
const LOOK_FONTS = [notoSerif.variable, davidLibre.variable, plexHe.variable, plexMono.variable, bellefair.variable, bonaNova.variable].join(" ");
const LOOKS: MuseumLook[] = ["a", "b", "c", "a1", "a2", "a3", "a4", "a5"];

// The museum version of a deed page, read from data/museum/<slug>.json (format:
// data/museum/schema/museum-page.schema.json). No database, no writes, never
// indexed: a preview surface until a page is approved and published.
export const dynamic = "force-dynamic";

// The page background chosen by museum_line.py's backdrop stage, with its derived colour set.
async function readBackdrop(slug: string): Promise<MuseumBackdrop | undefined> {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(slug)) return undefined;
  try {
    const d = JSON.parse(await fs.readFile(path.join(process.cwd(), "data", "museum", `${slug}.backdrop.json`), "utf8"));
    // a colour set that failed its contrast check is never shown
    return d.schema === "maasei-backdrop/1" && d.media && d.passed ? (d as MuseumBackdrop) : undefined;
  } catch {
    return undefined;
  }
}

async function readMuseum(slug: string, lang: "he" | "en" = "he"): Promise<MuseumPageData | null> {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(slug)) return null;
  // the English page is a checked translation, written by museum_line.py's english stage
  const file = path.join(process.cwd(), "data", "museum", lang === "en" ? `${slug}.en.json` : `${slug}.json`);
  try {
    const doc = JSON.parse(await fs.readFile(file, "utf8")) as MuseumPageData;
    return doc.schema === "maasei-museum/1" ? doc : null;
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const page = await readMuseum(slug);
  if (!page) return { title: SITE_TITLE_BILINGUAL, robots: { index: false, follow: false } };
  const description = page.trailer.map((s) => s.text).join(" ").slice(0, 160);
  return {
    title: `${page.title} | ${SITE_TITLE_BILINGUAL}`,
    description,
    robots: { index: false, follow: false },
  };
}

export default async function MuseumRoute({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ look?: string | string[]; lang?: string | string[]; draft?: string }>;
}) {
  const { slug } = await params;
  const sp = await searchParams;
  const raw = sp.look;
  // language: ?lang=en|he in the address (a direct link), else the site's saved choice
  const rawLang = Array.isArray(sp.lang) ? sp.lang[0] : sp.lang;
  const saved = (await cookies()).get(LANG_COOKIE)?.value;
  const lang: "he" | "en" = rawLang === "en" || rawLang === "he" ? rawLang : saved === "en" ? "en" : "he";
  const asked = Array.isArray(raw) ? raw[0] : raw;
  // a4 (אלבום) is the chosen look, and since 13.11 it hangs over the deed's own background photo with
  // the colours derived from it (data/museum/<slug>.backdrop.json; a deed without one keeps the sand
  // paper). ?look=a4cream shows the album without the background, ?look=0 the old navy page, the other
  // trial looks stay reachable with ?look=…; the switcher at the bottom appears only when ?look= is present.
  const plain = asked === "a4cream";
  const look = asked === "0" ? undefined : asked === "a4bg" || plain ? "a4" : LOOKS.find((l) => l === asked) ?? "a4";
  const preview = asked !== undefined;
  const bd = look === "a4" && !plain ? await readBackdrop(slug) : undefined;
  const P = bd?.palette ?? {};
  const bdStyle = bd
    ? ({
        "--bd-img": `url("${bd.img}")`,
        "--bd-img-s": `url("${bd.img_small ?? bd.img}")`,
        "--bd-tone": P.tone,
        "--bd-paper": P.paper,
        "--bd-surface": P.surface,
        "--bd-band": P.band,
        "--bd-tint": P.tint,
        "--bd-rule": P.rule,
        "--bd-header": P.header,
        "--bd-text": P.text,
        "--bd-text2": P.text2,
        "--bd-accent": P.accent,
        "--bd-meta": P.meta,
        "--bd-shadow": P.shadow,
      } as CSSProperties)
    : undefined;
  const page = await readMuseum(slug);
  if (!page) notFound();
  const pageEn = await readMuseum(slug, "en");
  // 27.11: an unfinished page is not public; ?draft=1 (or a ?look= preview) still opens it
  if (!isReadyMuseum(page as Parameters<typeof isReadyMuseum>[0], !!pageEn) && sp.draft !== "1" && !preview) notFound();
  return (
    <div className={`mx-page min-h-screen flex flex-col ${LOOK_FONTS}`} data-look={look ?? "0"} data-bg={bd ? "" : undefined} style={bdStyle}>
      <SiteHeader />
      <MuseumPage page={page} pageEn={pageEn} initialLang={rawLang === "en" || rawLang === "he" ? rawLang : lang} look={look} preview={preview} backdrop={bd} bgPreview={!!bd} />
      <SiteFooter />
    </div>
  );
}
