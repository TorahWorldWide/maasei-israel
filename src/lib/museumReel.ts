import fs from "node:fs/promises";
import path from "node:path";
import type { Entry } from "@/lib/data";
import { ytId } from "@/lib/youtube";

/**
 * 26.11: the written museum deeds (data/museum/<slug>.json) as the main page's
 * cinema reel and scroll feed. data/museum/reel.json holds one embeddable
 * YouTube video per deed, in the order the reel plays them.
 */
export type ReelCard = {
  slug: string;
  deed: string;
  deedEn?: string;
  year?: string;
  line: string;
  lineEn?: string;
  thumb: string;
};

type MuseumDoc = {
  schema?: string;
  deed?: string;
  year?: string;
  title?: string;
  trailer?: { text: string }[];
};

const DIR = path.join(process.cwd(), "data", "museum");

async function readJson<T>(file: string): Promise<T | undefined> {
  try {
    return JSON.parse(await fs.readFile(path.join(DIR, file), "utf8")) as T;
  } catch {
    return undefined;
  }
}

export async function getMuseumReel(): Promise<{ entries: Entry[]; cards: ReelCard[]; sources: number }> {
  const reel = (await readJson<{ reel: { slug: string; video: string }[] }>("reel.json"))?.reel ?? [];
  const entries: Entry[] = [];
  const cards: ReelCard[] = [];
  let sources = 0;
  for (const { slug, video } of reel) {
    if (!/^[a-z0-9][a-z0-9-]*$/.test(slug)) continue;
    const [he, en] = await Promise.all([readJson<MuseumDoc & { sources?: unknown[] }>(`${slug}.json`), readJson<MuseumDoc>(`${slug}.en.json`)]);
    const id = ytId(video);
    if (!he || he.schema !== "maasei-museum/1" || !id) continue;
    sources += Array.isArray(he.sources) ? he.sources.length : 0;
    const tr = (he.trailer ?? []).map((s) => s.text);
    const trEn = (en?.trailer ?? []).map((s) => s.text);
    const yearNum = parseInt(he.year ?? "", 10);
    // 27.11: the English file keeps the Hebrew name in "deed"; its English name is "title"
    const enName = [en?.title, en?.deed].find((x) => x && !/[֐-׿]/.test(x));
    entries.push({
      id: `museum-${slug}`,
      href: `/museum/${slug}`,
      title: he.deed ?? he.title ?? slug,
      title_en: enName,
      description: tr.slice(0, 2).join(" "),
      description_en: trEn.length ? trEn.slice(0, 2).join(" ") : undefined,
      category: "תרומה לעולם",
      year: Number.isFinite(yearNum) ? yearNum : null,
      media_type: "video_embed",
      media_url: video,
      source_url: "",
      source_label: "",
    } as Entry);
    cards.push({
      slug,
      deed: he.deed ?? slug,
      deedEn: enName,
      year: he.year,
      line: tr[0] ?? "",
      lineEn: trEn[0],
      thumb: `https://i.ytimg.com/vi/${id}/hqdefault.jpg`,
    });
  }
  return { entries, cards, sources };
}
