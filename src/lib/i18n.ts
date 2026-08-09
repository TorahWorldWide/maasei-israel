export type Lang = "he" | "en";

// Page <title>s are rendered before the reader's language is known — so the
// brand is written bilingually.
export const SITE_TITLE_BILINGUAL = "מעשי ישראל · Maasei Israel";

// Read by the server (root layout), written by the client. Must live outside a
// "use client" module, or the server only sees a client reference. No dot in
// the name — Next's cookie store can't get() a dotted key.
export const LANG_COOKIE = "maasei_lang";

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
  // shared
  back: string;
  backHome: string;
  // submit form — headings & fields
  submitFormTitle: string;
  submitFormIntro: string;
  submitFieldTitle: string;
  submitTitlePlaceholder: string;
  submitFieldDescription: string;
  submitDescriptionPlaceholder: string;
  submitFieldCategory: string;
  submitFieldYear: string;
  submitSourceBoxTitle: string;
  submitFieldSourceUrl: string;
  submitFieldSourceLabel: string;
  submitSourceLabelPlaceholder: string;
  submitFieldMedia: string;
  mediaNone: string;
  mediaYoutube: string;
  mediaUpload: string;
  submitFieldYoutubeUrl: string;
  submitUploadBoxTitle: string;
  submitUploadHint: string;
  submitUploading: string;
  submitUploadDone: string;
  submitFieldCredit: string;
  submitCreditPlaceholder: string;
  submitGenericError: string;
  submitSending: string;
  submitWaitingUpload: string;
  submitButton: string;
  // submit form — success screen
  submitThanks: string;
  submitSuccessBody: string;
  submitNotPersisted: string;
  submitAnother: string;
  // submit form — validation
  errTitleRequired: string;
  errDescriptionRequired: string;
  errSourceUrlRequired: string;
  errSourceUrlInvalid: string;
  errSourceLabelRequired: string;
  errWaitForUpload: string;
  // submit form — upload failures raised in the browser
  errFileType: string;
  errFileTooLarge: string;
  errUploadFailed: string;
  errUploadNetwork: string;
  // admin — login
  adminPassword: string;
  adminPasswordPlaceholder: string;
  adminLoggingIn: string;
  adminEnter: string;
  adminUnconfigured: string;
  adminWrongPassword: string;
  adminNetworkErrorRetry: string;
  // admin — queue
  adminQueueTitle: string;
  adminRefresh: string;
  adminLoading: string;
  adminLoadError: string;
  adminNetworkError: string;
  adminSupabaseUnconfiguredTitle: string;
  adminSupabaseUnconfiguredBody: string;
  adminNoPending: string;
  adminPendingCount: string; // "<n> submissions awaiting review"
  adminSubmittedBy: string;
  adminApprove: string;
  adminApproving: string;
  adminReject: string;
  adminRejecting: string;
  // API error codes (server routes send a `code`; the client renders these)
  apiSourceRequired: string;
  apiSourceInvalid: string;
  apiInternal: string;
  apiStorageUnconfigured: string;
  apiFileType: string;
  apiFileTooLarge: string;
  apiSignedUrlFailed: string;
  apiUnauthorized: string;
  apiMissingId: string;
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
    back: "חזרה",
    backHome: "חזרה לדף הבית",
    submitFormTitle: "הגשת מעשה טוב",
    submitFormIntro:
      "כל פריט חייב לכלול קישור מקור מאומת. ללא מקור — ההגשה לא תתקבל.",
    submitFieldTitle: "שם הפריט",
    submitTitlePlaceholder: 'לדוגמה: "חיסון נגד פוליו"',
    submitFieldDescription: "תיאור",
    submitDescriptionPlaceholder: "תארו את המעשה הטוב, ההמצאה או התרומה...",
    submitFieldCategory: "קטגוריה",
    submitFieldYear: "שנה (אופציונלי)",
    submitSourceBoxTitle: "מקור מאומת — חובה",
    submitFieldSourceUrl: "קישור למקור",
    submitFieldSourceLabel: "שם המקור",
    submitSourceLabelPlaceholder: 'לדוגמה: "ויקיפדיה" או "הניו יורק טיימס"',
    submitFieldMedia: "מדיה (אופציונלי)",
    mediaNone: "ללא מדיה / תמונה בקישור",
    mediaYoutube: "סרטון YouTube (קישור)",
    mediaUpload: "העלאת וידאו/תמונה מהמחשב",
    submitFieldYoutubeUrl: "קישור לסרטון YouTube",
    submitUploadBoxTitle: "העלאת וידאו או תמונה מהמחשב",
    submitUploadHint:
      "וידאו (MP4 / MOV / WEBM) או תמונה, עד 50MB. הקובץ נשמר בצורה מאובטחת.",
    submitUploading: "מעלה...",
    submitUploadDone: "הקובץ הועלה בהצלחה",
    submitFieldCredit: "שם לקרדיט (אופציונלי)",
    submitCreditPlaceholder: "השם שלכם",
    submitGenericError: "אירעה שגיאה. אנא נסו שוב.",
    submitSending: "שולח...",
    submitWaitingUpload: "ממתין לסיום העלאה...",
    submitButton: "שלח הגשה",
    submitThanks: "תודה!",
    submitSuccessBody: "ההגשה נשלחה ותיבדק לפני פרסום.",
    submitNotPersisted:
      "שימו לב: מסד הנתונים אינו מחובר עדיין. ההגשה תישמר לאחר חיבור Supabase.",
    submitAnother: "שלחו פריט נוסף",
    errTitleRequired: "שם הפריט נדרש",
    errDescriptionRequired: "תיאור נדרש",
    errSourceUrlRequired: "קישור מקור הוא שדה חובה — כל פריט חייב הוכחה",
    errSourceUrlInvalid: "יש להזין קישור תקין (מתחיל ב-http:// או https://)",
    errSourceLabelRequired: "שם המקור נדרש",
    errWaitForUpload: "המתינו לסיום העלאת הקובץ",
    errFileType: "סוג קובץ לא נתמך. מותר וידאו (mp4/mov/webm) או תמונה.",
    errFileTooLarge: "הקובץ גדול מדי. מקסימום 50MB.",
    errUploadFailed: "ההעלאה נכשלה",
    errUploadNetwork: "שגיאת רשת בהעלאה",
    adminPassword: "סיסמה",
    adminPasswordPlaceholder: "הזן סיסמת מנהל",
    adminLoggingIn: "מתחבר...",
    adminEnter: "כניסה",
    adminUnconfigured: "מנהל אינו מוגדר. יש להגדיר ADMIN_PASSWORD ו-Supabase.",
    adminWrongPassword: "סיסמה שגויה.",
    adminNetworkErrorRetry: "שגיאת תקשורת. נסה שוב.",
    adminQueueTitle: "ניהול הגשות",
    adminRefresh: "רענן",
    adminLoading: "טוען הגשות...",
    adminLoadError: "שגיאה בטעינת ההגשות.",
    adminNetworkError: "שגיאת תקשורת.",
    adminSupabaseUnconfiguredTitle: "Supabase אינו מוגדר.",
    adminSupabaseUnconfiguredBody:
      "יש להגדיר את משתני הסביבה NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY ו-SUPABASE_SERVICE_ROLE_KEY להפעלת תור ההגשות.",
    adminNoPending: "אין הגשות ממתינות לאישור.",
    adminPendingCount: "הגשות ממתינות לאישור",
    adminSubmittedBy: "הוגש על-ידי",
    adminApprove: "✓ אישור",
    adminApproving: "מאשר...",
    adminReject: "✕ דחייה",
    adminRejecting: "דוחה...",
    apiSourceRequired: "מקור (source_url) הוא שדה חובה",
    apiSourceInvalid: "קישור מקור אינו תקין",
    apiInternal: "שגיאה פנימית",
    apiStorageUnconfigured: "אחסון אינו מוגדר",
    apiFileType: "סוג קובץ לא נתמך. מותר וידאו או תמונה בלבד.",
    apiFileTooLarge: "הקובץ גדול מדי. מקסימום 50MB.",
    apiSignedUrlFailed: "נכשלה יצירת קישור העלאה",
    apiUnauthorized: "אין הרשאה",
    apiMissingId: "מזהה חסר",
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
    back: "Back",
    backHome: "Back to home",
    submitFormTitle: "Submit a Good Deed",
    submitFormIntro:
      "Every entry must include a link to a verified source. Without a source, the submission will not be accepted.",
    submitFieldTitle: "Entry name",
    submitTitlePlaceholder: 'For example: "The polio vaccine"',
    submitFieldDescription: "Description",
    submitDescriptionPlaceholder:
      "Describe the good deed, the invention or the contribution...",
    submitFieldCategory: "Category",
    submitFieldYear: "Year (optional)",
    submitSourceBoxTitle: "Verified source — required",
    submitFieldSourceUrl: "Link to the source",
    submitFieldSourceLabel: "Source name",
    submitSourceLabelPlaceholder:
      'For example: "Encyclopaedia Britannica" or "The New York Times"',
    submitFieldMedia: "Media (optional)",
    mediaNone: "No media / image by link",
    mediaYoutube: "YouTube video (link)",
    mediaUpload: "Upload a video/image from your computer",
    submitFieldYoutubeUrl: "YouTube video link",
    submitUploadBoxTitle: "Upload a video or image from your computer",
    submitUploadHint:
      "Video (MP4 / MOV / WEBM) or an image, up to 50MB. Your file is stored securely.",
    submitUploading: "Uploading...",
    submitUploadDone: "File uploaded successfully",
    submitFieldCredit: "Name for credit (optional)",
    submitCreditPlaceholder: "Your name",
    submitGenericError: "Something went wrong. Please try again.",
    submitSending: "Sending...",
    submitWaitingUpload: "Waiting for the upload to finish...",
    submitButton: "Send submission",
    submitThanks: "Thank you!",
    submitSuccessBody:
      "Your submission was sent and will be reviewed before publication.",
    submitNotPersisted:
      "Please note: the database is not connected yet. Your submission will be saved once Supabase is connected.",
    submitAnother: "Submit another entry",
    errTitleRequired: "An entry name is required",
    errDescriptionRequired: "A description is required",
    errSourceUrlRequired:
      "A source link is required — every entry needs proof",
    errSourceUrlInvalid:
      "Please enter a valid link (starting with http:// or https://)",
    errSourceLabelRequired: "A source name is required",
    errWaitForUpload: "Please wait for the file upload to finish",
    errFileType:
      "Unsupported file type. Video (mp4/mov/webm) or an image only.",
    errFileTooLarge: "That file is too large. 50MB maximum.",
    errUploadFailed: "The upload failed",
    errUploadNetwork: "Network error during upload",
    adminPassword: "Password",
    adminPasswordPlaceholder: "Enter the admin password",
    adminLoggingIn: "Signing in...",
    adminEnter: "Sign in",
    adminUnconfigured:
      "Admin is not configured. ADMIN_PASSWORD and Supabase must be set.",
    adminWrongPassword: "Wrong password.",
    adminNetworkErrorRetry: "Connection error. Please try again.",
    adminQueueTitle: "Submission Queue",
    adminRefresh: "Refresh",
    adminLoading: "Loading submissions...",
    adminLoadError: "Failed to load the submissions.",
    adminNetworkError: "Connection error.",
    adminSupabaseUnconfiguredTitle: "Supabase is not configured.",
    adminSupabaseUnconfiguredBody:
      "Set the environment variables NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY to enable the submission queue.",
    adminNoPending: "No submissions are awaiting review.",
    adminPendingCount: "submissions awaiting review",
    adminSubmittedBy: "Submitted by",
    adminApprove: "✓ Approve",
    adminApproving: "Approving...",
    adminReject: "✕ Reject",
    adminRejecting: "Rejecting...",
    apiSourceRequired: "A source (source_url) is required",
    apiSourceInvalid: "The source link is not valid",
    apiInternal: "Internal error",
    apiStorageUnconfigured: "Storage is not configured",
    apiFileType: "Unsupported file type. Video or images only.",
    apiFileTooLarge: "That file is too large. 50MB maximum.",
    apiSignedUrlFailed: "Could not create an upload link",
    apiUnauthorized: "Unauthorized",
    apiMissingId: "Missing id",
  },
};

export function t(lang: Lang, key: keyof Strings): string {
  return dict[lang][key];
}

// ---------------------------------------------------------------------------
// API error codes.
//
// Server routes cannot read the user's language (it lives in localStorage), so
// they answer with a stable machine-readable `code` alongside a Hebrew `error`
// fallback. The browser maps the code to a translated message here.
// ---------------------------------------------------------------------------
export type ApiErrorCode =
  | "source_required"
  | "source_invalid"
  | "internal"
  | "storage_unconfigured"
  | "file_type"
  | "file_too_large"
  | "signed_url_failed"
  | "unauthorized"
  | "missing_id";

const API_ERROR_KEYS: Record<ApiErrorCode, keyof Strings> = {
  source_required: "apiSourceRequired",
  source_invalid: "apiSourceInvalid",
  internal: "apiInternal",
  storage_unconfigured: "apiStorageUnconfigured",
  file_type: "apiFileType",
  file_too_large: "apiFileTooLarge",
  signed_url_failed: "apiSignedUrlFailed",
  unauthorized: "apiUnauthorized",
  missing_id: "apiMissingId",
};

// Translate an API error. Falls back to the server's own message (and finally
// to a generic internal error) when the code is unknown — e.g. a raw Supabase
// message bubbling up.
export function apiError(
  lang: Lang,
  code: unknown,
  fallback?: unknown
): string {
  if (typeof code === "string" && code in API_ERROR_KEYS) {
    return t(lang, API_ERROR_KEYS[code as ApiErrorCode]);
  }
  if (typeof fallback === "string" && fallback.trim()) return fallback;
  return t(lang, "apiInternal");
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

// A locator is either a bare PDF page number ("12") or a prose hint
// ("opening paragraph, 8 June 2023"). Only the former gets a "p." prefix.
export function locatorLabel(
  lang: Lang,
  locator: string | null | undefined,
  locatorEn: string | null | undefined
): string {
  const text = pick(lang, locator, locatorEn).trim();
  if (!text) return "";
  return /^\d+$/.test(text) ? `${t(lang, "pageAbbr")} ${text}` : text;
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

// Eras are numeric century ranges (see @/lib/era) — identical in he/en, so they
// need no label table.

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
