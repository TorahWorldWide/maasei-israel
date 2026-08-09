import type { Metadata } from "next";
import { cookies, headers } from "next/headers";
import { Rubik, Heebo, Frank_Ruhl_Libre } from "next/font/google";
import { LangProvider } from "@/components/LangProvider";
import { SITE_TITLE_BILINGUAL, LANG_COOKIE, type Lang } from "@/lib/i18n";
import "./globals.css";

const rubik = Rubik({
  variable: "--font-rubik",
  subsets: ["latin", "hebrew"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

const heebo = Heebo({
  variable: "--font-heebo",
  subsets: ["latin", "hebrew"],
  weight: ["300", "400", "500", "600"],
  display: "swap",
});

const frankRuhl = Frank_Ruhl_Libre({
  variable: "--font-frank-ruhl",
  subsets: ["latin", "hebrew"],
  weight: ["400", "500", "700", "900"],
  display: "swap",
});

export const metadata: Metadata = {
  title: SITE_TITLE_BILINGUAL,
  description:
    "אוסף מתועד של מעשים טובים, המצאות ותרומות של עם ישראל לעולם — כל פריט עם הוכחה. · A documented collection of the good deeds, inventions and contributions of the Jewish people to the world — every entry with proof.",
};

/**
 * A saved choice always wins. Otherwise Israeli visitors land in Hebrew and the
 * rest of the world lands in English. Deciding this on the server keeps the
 * first paint in the right language instead of flashing Hebrew and swapping.
 */
async function resolveLang(): Promise<Lang> {
  const saved = (await cookies()).get(LANG_COOKIE)?.value;
  if (saved === "he" || saved === "en") return saved;

  const country = (await headers()).get("x-vercel-ip-country");
  if (!country) return "he";
  return country === "IL" ? "he" : "en";
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const lang = await resolveLang();

  return (
    <html
      lang={lang}
      dir={lang === "he" ? "rtl" : "ltr"}
      className={`${rubik.variable} ${heebo.variable} ${frankRuhl.variable}`}
    >
      <body className="min-h-screen flex flex-col">
        <LangProvider initialLang={lang}>{children}</LangProvider>
      </body>
    </html>
  );
}
