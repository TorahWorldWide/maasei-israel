import { getApprovedEntries, getOverview } from "@/lib/data";
import Feed from "@/components/Feed";
import Theater from "@/components/Theater";
import OverviewPanel from "@/components/OverviewPanel";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import CatalogHeading from "@/components/CatalogHeading";

export const dynamic = "force-dynamic";

export default async function Home() {
  const [entries, overview] = await Promise.all([
    getApprovedEntries(),
    getOverview(),
  ]);

  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />

      {/* Theater (auto-playing video reel + music) */}
      <Theater entries={entries} />

      {/* The historian's big-picture overview (renders once written) */}
      {overview && <OverviewPanel overview={overview} />}

      {/* Catalog — stays navy, no white break */}
      <main id="catalog" className="flex-1 w-full scroll-mt-20 relative">
        <div className="max-w-6xl mx-auto w-full px-4 sm:px-6 py-14">
          <CatalogHeading />
          <Feed entries={entries} />
        </div>
      </main>

      <SiteFooter entryCount={entries.length} />
    </div>
  );
}
