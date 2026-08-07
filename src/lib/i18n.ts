export type Lang = "he" | "en";

type Strings = {
  // nav / brand
  siteTitle: string;
  submit: string;
  admin: string;
  adminLogin: string;
  // catalog
  catalogTitle: string;
  catalogSubtitle: string;
  searchPlaceholder: string;
  searchAria: string;
  filterByCategory: string;
  filterByEra: string;
  resultsWord: string; // "<n> results for"
  noItems: string;
  clearFilter: string;
  // footer
  documentedItems: string;
  footerNote: string;
  // deed page / cards
  backToAll: string;
  source: string;
  citationsHeading: string;
  actLabel: string;
  rippleLabel: string;
  backedBySingle: string;
  sourcesVerified: string; // "<n> verified sources"
  pageAbbr: string;
  // theater
  proofAndSources: string;
  allDeeds: string;
  playMusic: string;
  nowPlaying: string;
  mood1: string;
  mood2: string;
  mood3: string;
  mood4: string;
  ariaPrev: string;
  ariaNext: string;
  ariaClose: string;
  ariaExpand: string;
  slideshowLabel: string;
  // citations
  proofHeading: string;
  jumpToSource: string;
  jumpTitle: string;
  // share proof
  shareProof: string;
  copied: string;
  shareMore: string;
  // entry card
  fullPage: string;
  // overview
  overviewKicker: string;
  // video fallback (embedding disabled by the owner)
  videoUnavailable: string;
  watchOnYoutube: string;
  // deed media gallery (video carousel + image collage)
  galleryLabel: string;
  ariaOpenImage: string;
};

const dict: Record<Lang, Strings> = {
  he: {
    siteTitle: "מעשי ישראל",
    submit: "שלחו מעשה טוב",
    admin: "ניהול",
    adminLogin: "כניסת מנהל",
    catalogTitle: "כל המעשים הטובים",
    catalogSubtitle:
      "חפשו, סננו לפי קטגוריה ותקופה, וגלו אחד אחד — כל פריט עם מקור מאומת.",
    searchPlaceholder: "חיפוש...",
    searchAria: "חיפוש פריטים",
    filterByCategory: "סינון לפי קטגוריה",
    filterByEra: "סינון לפי תקופה",
    resultsWord: "תוצאות עבור",
    noItems: "לא נמצאו פריטים.",
    clearFilter: "נקה סינון",
    documentedItems: "פריטים מתועדים",
    footerNote: "כל פריט מלווה במקור מאומת · מוזיקה: Kevin MacLeod (CC-BY)",
    backToAll: "חזרה לכל המעשים",
    source: "מקור",
    citationsHeading: "הוכחות",
    actLabel: "חלק א׳ · הניצוץ",
    rippleLabel: "חלק ב׳ · האור",
    backedBySingle: "מגובה במקור מאומת",
    sourcesVerified: "מקורות מאומתים",
    pageAbbr: "עמ׳",
    proofAndSources: "מקורות והוכחות",
    allDeeds: "כל המעשים",
    playMusic: "נגן מוזיקה מרגשת",
    nowPlaying: "מתנגן",
    mood1: "מרגש",
    mood2: "השראה",
    mood3: "רוגע",
    mood4: "עוצמתי",
    ariaPrev: "הקודם",
    ariaNext: "הבא",
    ariaClose: "סגור",
    ariaExpand: "הרחבה — קרא עוד",
    slideshowLabel: "מצגת מעשים טובים",
    proofHeading: "ההוכחה — מקורות מאומתים",
    jumpToSource: "קפוץ למקור",
    jumpTitle: "לחצו כדי לקפוץ למקום המדויק במקור",
    shareProof: "שתף הוכחה",
    copied: "הועתק!",
    shareMore: "עוד מעשים",
    fullPage: "לעמוד המלא",
    overviewKicker: "התמונה הגדולה",
    videoUnavailable: "הסרטון הזה מוגבל לצפייה ביוטיוב בלבד",
    watchOnYoutube: "צפייה ביוטיוב",
    galleryLabel: "גלריית תמונות",
    ariaOpenImage: "פתיחת תמונה בגודל מלא",
  },
  en: {
    siteTitle: "Maasei Israel",
    submit: "Submit a Good Deed",
    admin: "Admin",
    adminLogin: "Admin Login",
    catalogTitle: "All the Good Deeds",
    catalogSubtitle:
      "Search, filter by category and era, and discover them one by one — every item with a verified source.",
    searchPlaceholder: "Search...",
    searchAria: "Search items",
    filterByCategory: "Filter by category",
    filterByEra: "Filter by era",
    resultsWord: "results for",
    noItems: "No items found.",
    clearFilter: "Clear filters",
    documentedItems: "documented items",
    footerNote:
      "Every item backed by a verified source · Music: Kevin MacLeod (CC-BY)",
    backToAll: "Back to all deeds",
    source: "Source",
    citationsHeading: "Verified Citations",
    actLabel: "Part 1 · The Spark",
    rippleLabel: "Part 2 · The Light",
    backedBySingle: "Backed by a verified source",
    sourcesVerified: "verified sources",
    pageAbbr: "p.",
    proofAndSources: "Sources & Proof",
    allDeeds: "All deeds",
    playMusic: "Play inspiring music",
    nowPlaying: "Now playing",
    mood1: "Moving",
    mood2: "Inspiring",
    mood3: "Calm",
    mood4: "Epic",
    ariaPrev: "Previous",
    ariaNext: "Next",
    ariaClose: "Close",
    ariaExpand: "Expand — read more",
    slideshowLabel: "Good deeds slideshow",
    proofHeading: "The Proof — Verified Sources",
    jumpToSource: "Jump to source",
    jumpTitle: "Click to jump to the exact spot in the source",
    shareProof: "Share Proof",
    copied: "Copied!",
    shareMore: "More deeds",
    fullPage: "Full page",
    overviewKicker: "The Big Picture",
    videoUnavailable: "This video can only be watched on YouTube",
    watchOnYoutube: "Watch on YouTube",
    galleryLabel: "Image gallery",
    ariaOpenImage: "Open image full size",
  },
};

export function t(lang: Lang, key: keyof Strings): string {
  return dict[lang][key];
}

// Pick a translated value: use the English field when in English and it exists,
// otherwise fall back to the Hebrew original (so the UI is never blank).
export function pick(
  lang: Lang,
  he: string | null | undefined,
  en: string | null | undefined
): string {
  if (lang === "en" && en != null && en !== "") return en;
  return he ?? "";
}

// Category labels. Keys are the canonical Hebrew category values stored in the DB
// (plus "הכל" = the "All" filter chip).
export const CATEGORY_LABELS: Record<Lang, Record<string, string>> = {
  he: {
    הכל: "הכל",
    חסד: "חסד",
    "המצאה מדעית": "המצאה מדעית",
    "תרומה לעולם": "תרומה לעולם",
    היסטורי: "היסטורי",
  },
  en: {
    הכל: "All",
    חסד: "Kindness",
    "המצאה מדעית": "Scientific Invention",
    "תרומה לעולם": "Contribution to the World",
    היסטורי: "Historical",
  },
};

export function categoryLabel(lang: Lang, cat: string): string {
  return CATEGORY_LABELS[lang][cat] ?? cat;
}

// Era labels (the canonical Hebrew era buckets computed from `year`).
export const ERA_LABELS: Record<Lang, Record<string, string>> = {
  he: {
    הכל: "הכל",
    עתיק: "עתיק",
    "טרום המדינה": "טרום המדינה",
    "המאה ה-20": "המאה ה-20",
    עכשווי: "עכשווי",
  },
  en: {
    הכל: "All",
    עתיק: "Ancient",
    "טרום המדינה": "Pre-State",
    "המאה ה-20": "20th Century",
    עכשווי: "Contemporary",
  },
};

export function eraLabel(lang: Lang, era: string): string {
  return ERA_LABELS[lang][era] ?? era;
}

// Overview panel stat labels.
export const OVERVIEW_STAT_LABELS: Record<Lang, Record<string, string>> = {
  he: {
    entries: "מעשים מתועדים",
    documented_lives_helped: "נפשות שנעזרו (מתועד)",
    countries_reached: "מדינות",
    year_min: "מהשנה",
    year_max: "עד השנה",
  },
  en: {
    entries: "documented deeds",
    documented_lives_helped: "lives helped (documented)",
    countries_reached: "countries",
    year_min: "from year",
    year_max: "to year",
  },
};
