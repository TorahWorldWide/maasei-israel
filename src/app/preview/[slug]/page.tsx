import fs from "node:fs/promises";
import path from "node:path";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import type { Entry, ImageProvenance } from "@/lib/data";
import { SITE_TITLE_BILINGUAL } from "@/lib/i18n";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import DeedPageBody from "@/components/DeedPageBody";

// The preview branch only. A deed page rendered from a JSON file in the repo
// (written by ~/company/tools/md2site.py) through the SAME component tree as
// /deed/[id] — so what Tomer sees is the real page, not a mock. No Supabase,
// no write of any kind, and never indexed.
export const dynamic = "force-dynamic";

async function readPreview(slug: string): Promise<Entry | null> {
  // A slug is a file name here, so anything that could climb out of the folder
  // is refused before it reaches the filesystem.
  if (!/^[a-z0-9][a-z0-9-]*$/.test(slug)) return null;
  const file = path.join(process.cwd(), "data", "preview", `${slug}.json`);
  let raw: string;
  try {
    raw = await fs.readFile(file, "utf8");
  } catch {
    return null;
  }
  const doc = JSON.parse(raw) as Partial<Entry> & Record<string, unknown>;

  // The converter also writes a `lab` block (claims, markers, warnings) and a
  // `video_provenance` block that the site has no field for. They stay in the
  // file — nothing is deleted — but they are not handed to the page.
  const {
    lab: _lab,
    video_provenance: _video,
    written_by: _writtenBy,
    deed_id: _deedId,
    ...entryFields
  } = doc;
  void _lab;
  void _video;
  void _writtenBy;
  void _deedId;

  // The ‹מ-XXX› identifiers ride along on each picture. They are the internal
  // layer, not something a reader is shown — and serialized props are page
  // source. They stay in the file; they do not reach the browser.
  const provenance = doc.audit?.image_provenance;
  if (Array.isArray(provenance)) {
    entryFields.audit = {
      image_provenance: provenance.map((p) => {
        const { m_ids: _mIds, ...rest } = p as ImageProvenance & { m_ids?: string[] };
        void _mIds;
        return rest;
      }),
    };
  }

  // Defaults for anything the components assume but the file may not carry.
  // These belong here and not in the converter: the converter must never
  // invent a value that could be mistaken for something a source said.
  return {
    id: slug,
    title: "",
    description: "",
    category: "חסד",
    year: null,
    media_type: "image",
    media_url: "",
    source_url: "",
    source_label: "",
    status: "approved",
    created_at: new Date().toISOString(),
    ...entryFields,
  } as Entry;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const entry = await readPreview(slug);
  if (!entry)
    return {
      title: `תצוגה מקדימה לא נמצאה · Preview Not Found | ${SITE_TITLE_BILINGUAL}`,
      robots: { index: false, follow: false },
    };

  const description = entry.description.slice(0, 160);
  return {
    title: `${entry.title} | ${SITE_TITLE_BILINGUAL}`,
    description,
    robots: { index: false, follow: false },
    openGraph: { title: `${entry.title} | ${SITE_TITLE_BILINGUAL}`, description },
    twitter: {
      card: "summary_large_image",
      title: `${entry.title} | ${SITE_TITLE_BILINGUAL}`,
      description,
    },
  };
}

export default async function PreviewPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const entry = await readPreview(slug);
  if (!entry) notFound();

  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <div className="max-w-3xl mx-auto w-full px-4 sm:px-6 pt-4">
        <p className="text-[11px] text-blue-200/40 border border-[rgba(201,168,74,0.15)] rounded-full px-3 py-1 inline-block">
          תצוגה מקדימה · לא באתר החי · ‎data/preview/{slug}.json
        </p>
      </div>
      <DeedPageBody entry={entry} />
      <SiteFooter />
    </div>
  );
}
