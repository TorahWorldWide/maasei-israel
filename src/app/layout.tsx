import type { Metadata } from "next";
import { Rubik, Heebo, Frank_Ruhl_Libre } from "next/font/google";
import { LangProvider } from "@/components/LangProvider";
import { SITE_TITLE_BILINGUAL } from "@/lib/i18n";
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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="he"
      dir="rtl"
      className={`${rubik.variable} ${heebo.variable} ${frankRuhl.variable}`}
    >
      <body className="min-h-screen flex flex-col">
        <LangProvider>{children}</LangProvider>
      </body>
    </html>
  );
}
