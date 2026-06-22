import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getEntryById } from "@/lib/data";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import DeedPageBody from "@/components/DeedPageBody";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const entry = await getEntryById(id);
  if (!entry) return { title: "מעשה לא נמצא | מעשי ישראל" };

  const description = entry.description.slice(0, 160);
  return {
    title: `${entry.title} | מעשי ישראל`,
    description,
    openGraph: {
      title: `${entry.title} | מעשי ישראל`,
      description,
      images: [{ url: `/deed/${id}/opengraph-image` }],
    },
    twitter: {
      card: "summary_large_image",
      title: `${entry.title} | מעשי ישראל`,
      description,
    },
    alternates: {
      canonical: `/deed/${id}`,
    },
  };
}

export default async function DeedPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const entry = await getEntryById(id);
  if (!entry) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: entry.title,
    datePublished: entry.created_at,
    articleBody: entry.description,
    about: entry.category,
    citation: entry.source_url,
    isBasedOn: entry.source_url,
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="min-h-screen flex flex-col">
        <SiteHeader />
        <DeedPageBody entry={entry} />
        <SiteFooter />
      </div>
    </>
  );
}
