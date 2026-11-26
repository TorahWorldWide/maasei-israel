import { getApprovedEntries, getOverview } from "@/lib/data";
import Feed from "@/components/Feed";
import Theater from "@/components/Theater";
import OverviewPanel from "@/components/OverviewPanel";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import CatalogHeading from "@/components/CatalogHeading";
import MuseumEntrance from "@/components/MuseumEntrance";
import MuseumFeed from "@/components/MuseumFeed";
import { getMuseumReel } from "@/lib/museumReel";

export const dynamic = "force-dynamic";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ era?: string }>;
}) {
  const [entries, overview, params, reel] = await Promise.all([
    getApprovedEntries(),
    getOverview(),
    searchParams,
    getMuseumReel(),
  ]);
  const initialEras = params.era?.split(",").filter(Boolean) ?? [];

  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />

      {/* 26.11: a short crown, then the cinema reel of the written museum deeds
          (videos play one after another), then the deeds as a scroll feed */}
      <MuseumEntrance deeds={reel.cards.length} sources={reel.sources} />

      <div id="theater" className="scroll-mt-16">
        <Theater entries={reel.entries.length ? reel.entries : entries} />
      </div>

      <MuseumFeed cards={reel.cards} />

      {/* The historian's big-picture overview (renders once written) */}
      {overview && <OverviewPanel overview={overview} />}

      {/* Catalog — stays navy, no white break */}
      <main id="catalog" className="flex-1 w-full scroll-mt-20 relative">
        <div className="max-w-6xl mx-auto w-full px-4 sm:px-6 py-14">
          <CatalogHeading />
          <Feed entries={entries} initialEras={initialEras} />
        </div>
      </main>

      <SiteFooter entryCount={entries.length} />
    </div>
  );
}
