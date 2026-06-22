export type Lang = "he" | "en";

type Strings = {
  // nav
  submit: string;
  admin: string;
  adminLogin: string;
  // catalog
  catalogTitle: string;
  catalogSubtitle: string;
  // footer
  documentedItems: string;
  footerNote: string;
  // deed page
  backToAll: string;
  source: string;
  citationsHeading: string;
  actLabel: string;
  rippleLabel: string;
  // share proof
  shareProof: string;
  copied: string;
  // entry card
  fullPage: string;
};

const dict: Record<Lang, Strings> = {
  he: {
    submit: "שלחו מעשה טוב",
    admin: "ניהול",
    adminLogin: "כניסת מנהל",
    catalogTitle: "כל המעשים הטובים",
    catalogSubtitle:
      "חפשו, סננו לפי קטגוריה ותקופה, וגלו אחד אחד — כל פריט עם מקור מאומת.",
    documentedItems: "פריטים מתועדים",
    footerNote: "כל פריט מלווה במקור מאומת · מוזיקה: Kevin MacLeod (CC-BY)",
    backToAll: "חזרה לכל המעשים",
    source: "מקור",
    citationsHeading: "הוכחות",
    actLabel: "חלק א׳ · הניצוץ",
    rippleLabel: "חלק ב׳ · האור",
    shareProof: "שתף הוכחה",
    copied: "הועתק!",
    fullPage: "לעמוד המלא",
  },
  en: {
    submit: "Submit a Good Deed",
    admin: "Admin",
    adminLogin: "Admin Login",
    catalogTitle: "All Good Deeds",
    catalogSubtitle:
      "Search, filter by category and era, and discover one by one — every item with a verified source.",
    documentedItems: "documented items",
    footerNote:
      "Every item backed by a verified source · Music: Kevin MacLeod (CC-BY)",
    backToAll: "Back to all deeds",
    source: "Source",
    citationsHeading: "Verified Citations",
    actLabel: "Part 1 · The Spark",
    rippleLabel: "Part 2 · The Light",
    shareProof: "Share Proof",
    copied: "Copied!",
    fullPage: "Full page",
  },
};

export function t(lang: Lang, key: keyof Strings): string {
  return dict[lang][key];
}
