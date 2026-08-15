# ביקורת אדוורסרית — turkey-hospital

**מזהה המעש:** `f0ca86ec-0a88-4963-b340-ad2e4f790c2b`
**נבדק:** `canonical.json` כפי שהוא ב-15.8.2026, אחרי בדיקת המנוע
**הבודק:** קורא עוין, כלל 140. לא כתבתי דבר בדף ולא נגעתי בשדותיו.
**היקף:** 14 פעולות רשת מתוך 25. שלושה־עשר מקורות נמשכו כ-HTML גולמי ונבדקו מול הטקסט
החי, לא מול היומן. `WebFetch` לא הופעל על אף מקור — הכלי הזה כבר שיבש ציטוט אחד בתיק
הזה, וכל ציטוט כאן נבדק מילה-במילה בטקסט המקורי.

**התוצאה: 2 critical · 8 major · 6 minor.**

**הממצא החמור ביותר:** הציטוט שעליו עומדת המחלוקת המרכזית של הדף — "נכנסנו לבית
החולים והוא היה נטוש" — מיוחס בדף לרופא הלא נכון.

**שער 176 עומד, אבל רק על רגל אחת.** הרגל הקונקרטית מוכחת; הרגל הדוקטרינרית קורסת
בבדיקה (ממצא M8).

---

## מה בדקתי מול המקור החי

| מקור | כתובת | נבדק |
|---|---|---|
| Journal of Emergency Management (Alpert, Malkin, Kobliner-Friedman) | `wmpllc.org/ojs/index.php/jem/article/view/3855`, DOI 10.5055/jem.0870 | 470 · 152 · 17 · 6 ימים · 10/48/27 · 142 · "skeleton staff" · "biggest accomplishment" · רשימת המחברים |
| Disaster Medicine and Public Health Preparedness (קיימברידג', 12.12.2024) | cambridge.org/…/7531CFEA680AA0F5EF37C309FF034AF7 | הגדרות standalone/hybrid · פיליפינים · "1-month leave" · "joined with Turkish volunteers" · 29 צוותים מ-22 מדינות · Level 4 · תרשים 1 |
| Journal of Global Health (PMC10450639) | pmc.ncbi.nlm.nih.gov/articles/PMC10450639/ | 140 · 17 טונות · 60 מיטות · שש מיטות טיפול נמרץ · 470 בשבוע · 150 ילדים · 100 שעות · "never practised before" · תודות (קולר/מרין) · משמרות מעורבות |
| Anadolu, אנגלית, 13.2.2023 | aa.com.tr/en/environment/…/2818017 | מי אמר "deserted" · ציטוט 250 · "Turkish medical teams came… in the past two days" |
| Anadolu Teyit Hattı, טורקית, 17.2.2023 | aa.com.tr/tr/teyithatti/aktuel/…/1815444 | "çadır hastane kurulmadığını" · "10 gün" · "belirlediği hastanelerde" · הודעת השגרירות בטורקית · שורת הפסיקה |
| לשכת הבריאות המחוזית אפיונקרהיסאר, 20.2.2023 | afyonism.saglik.gov.tr/TR-272740/… | "ilk günü" · "ameliyathane ve yoğun bakım" · "ekibimize … dâhil oldu" · "ekiplerimizin sorumluluğunda" |
| WHO/Europe, 17.6.2026 | who.int/europe/news-room/feature-stories/item/leading-through-crisis… | 39 צוותים מ-22 מדינות · UMKE Type 2 מ-2020 · UK-Med · פיימונטה · תרומת המבנה · אי-הזכרת ישראל |
| JNS 25.4.2023 ו-6.2.2023 | jns.org | תעודת ההוקרה לגולן ואך · 230+150 · ציטוט הכט |
| NWS, בחדרי חרדים, NewsBlaze | — | נוסח הודעת דובר צה"ל מ-8.2 |
| רשימת ה-EMT של WHO | who.int | השורה "5 · 2016 · EURO · Israel · GOV · IDF · Type 3" |

---

## critical

### C1 — הציטוט המרכזי מיוחס לאדם הלא נכון

**איפה:** סעיף "באיזה מצב היה בית החולים", עברית ואנגלית; ובעקיפין "הערות מקורות".

**מה הדף אומר:**
> ד"ר ריימון מוקלד מן המשלחת אמר לסוכנות אנדולו ב-13 בפברואר: נכנסנו לבית החולים והוא
> היה נטוש.

ובאנגלית: `Dr. Raymond Mokled of the delegation told the Anadolu Agency on 13 February:
"We entered the hospital and it was deserted."`

**מה המקור אומר** (aa.com.tr, 13.2.2023, מילה-במילה):
> Dr. Wafi Hamed, **a dentist**, said that he came to Türkiye with the Israeli mission and
> started his work in the Kahramanmaras Sahra hospital on Thursday. "We entered the hospital
> and it was deserted … We brought with us medical staff and equipment, including emergency
> rooms, recovery rooms, operations, a dental clinic, and a radiology department…"
>
> **For his part**, Dr. Raymon Mokalled from the Israeli mission said: "Since we arrived here,
> we have provided treatment to more than 250 patients…"

**למה זה critical:** אלה שני דוברים שונים בכתבה אחת. הדף מייחס למוקלד משפט שלא אמר,
ומייחס לרופא משפט שאמר רופא שיניים. זה לא פרט: המילה "נטוש" היא צלע אחת של המחלוקת
שהדף בונה סביבה סעיף שלם, והדף מעמיד אותה כעדות של "רופא מן המשלחת" מול לשכת בריאות
מחוזית. כשמתברר שהדובר הוא רופא השיניים של המשלחת — שהגיע לעבוד במרפאת השיניים ולא
בחדר המיון — משקל העדות משתנה, וההצגה שלה בדף היא ייחוס שגוי. הציטוט השני, זה של
מוקלד על 250 המטופלים, מיוחס בסעיף "9–14 בפברואר: שישה ימים" נכון.

**המקור:** https://www.aa.com.tr/en/environment/doctors-from-israel-continue-treating-earthquake-victims-in-turkiye/2818017

---

### C2 — הדף מוסר לקורא שהטורקים הגיעו רק ביומיים האחרונים; שלושת המאמרים אומרים שעבדו יחד מן היום הראשון

**איפה:** סוף סעיף "באיזה מצב היה בית החולים", תחילת סעיף "15 בפברואר: המסירה", ושדה
`aftermath`.

**מה הדף אומר:**
> מה שאינו ניתן ליישוב הוא המילים "נטוש" ו"ריק" מול צוות מומחים טורקי שפעל שם מן היום
> הראשון. אחד משני התיאורים אינו מדויק, ומן המקורות שקיימים אי אפשר לדעת איזה.

ובסעיף המסירה:
> ב-13 בפברואר, יומיים לפני הסוף, מסרו אנשי המשלחת לסוכנות אנדולו שצוותים רפואיים
> טורקיים הגיעו לבית החולים בימיים האחרונים והחלו לעבוד יחד אתם בטיפול בפצועים.

וב-`aftermath`: "צוותים רפואיים טורקיים כבר עבדו שם לצד הישראלים יומיים קודם לכן."

**מה המקורות אומרים** — שלושתם, ואלה בדיוק המקורות שהדף נשען עליהם:

*Disaster Medicine and Public Health Preparedness:*
> **From February 9, 2023, through February 14, 2023, the Israeli medical staff joined with
> Turkish volunteers** to rehabilitate the existing structure and treat patients in the ED as
> well as the inpatient wards and intensive care unit of the hospital.

*Journal of Emergency Management:*
> **Working alongside volunteer Turkish medical professionals**, they treated patients in the
> emergency department (ED) as well as the inpatient wards and intensive care unit.

*Journal of Global Health:*
> the Turkish government also mobilised medical staff from across Türkiye to support the area,
> creating multi-cultural, multi-linguistic, and multi-disciplinary **Turkish-Israeli teams**…
> **Each working shift consisted of Israeli and Turkish personnel** and one or two translators.

**למה זה critical:** הקורא מקבל שתי עובדות שגויות. האחת — שהעבודה המשותפת עם הטורקים
התחילה ב-13 בפברואר; היא התחילה ב-9 בפברואר, יום הפעילות הראשון, לפי כל שלושת המאמרים.
השנייה — שגרסת לשכת אפיונקרהיסאר עומדת לבדה מול הישראלים ואי אפשר להכריע. אבל הפועל
הטורקי בהודעת הלשכה, `ekibimize … dâhil oldu` ("הצטרף לצוות שלנו"), הוא בדיוק הפועל
האנגלי במאמר של קיימברידג', `joined with Turkish volunteers`. שני הצדדים מתארים את אותו
דבר. הדף לוקח מן המשפט של קיימברידג' את חציו הראשון בלבד — "צוות הליבה קיבל חופשה של
חודש" — ומשמיט את חציו השני, שהוא בדיוק העדות הישראלית התומכת בגרסה הטורקית. משפט
JOGH על משמרות מעורבות אינו מופיע בדף אף לא פעם אחת.

זה מה שהתדריך קורא לו "השמטה שמנקה את הדף מראיה מטרידה", אלא שכאן ההשמטה עובדת לכיוון
ההפוך מן הצפוי: היא מנקה את הדף מראיה שהייתה **מיישבת** את המחלוקת, כדי לשמור על
דרמת "אי אפשר לדעת".

**המקורות:**
https://www.cambridge.org/core/journals/disaster-medicine-and-public-health-preparedness/article/models-of-field-hospital-emergency-departments-the-israeli-experience/7531CFEA680AA0F5EF37C309FF034AF7 ·
https://wmpllc.org/ojs/index.php/jem/article/view/3855 ·
https://pmc.ncbi.nlm.nih.gov/articles/PMC10450639/ ·
https://afyonism.saglik.gov.tr/TR-272740/depremin-ilk-gununde-bolgeye-giden-ekip-kahramanmaras-necip-fazil-sehir-hastanesini-faaliyete-gecirerek-hizmet-verdi.html

---

## major

### M1 — כתובת המקור של המספר המרכזי בדף מחזירה 404

**איפה:** `numbers[0]` (470) ו-`numbers[1]` (152).

הדף מפנה בשניהם ל-`https://wmpllc.org/ojs/index.php/jem/article/view/4160`. הכתובת
מחזירה דף שגיאה של 1,276 בתים:

> 404 Not Found Stack Trace: File: /home/radjr1/domains/wmpllc.org/public_html/ojs/pages/article/ArticleHandler.inc.php line 107…

המאמר האמיתי הוא `view/3855` — "If you rebuild it, they will come—The contribution of the
Israel Defense Forces Field Hospital Team to the treatment of the 2023 earthquake victims in
Turkey", DOI 10.5055/jem.0870. הקורא שילחץ על המקור של 470 — המספר שהדף כולו נשען עליו —
יקבל stack trace של PHP. זה הממצא הפשוט ביותר לתיקון והמזיק ביותר לשרשרת הראיות.

### M2 — סתירה לא רשומה על מי פיקד על מה, ומפקד בית החולים לפי JOGH אינו בדף כלל

**מה הדף אומר** (סעיף "8 בפברואר, לפנות בוקר", כעובדה, בלי סייג):
> את המשלחת הוביל מפקד חטיבת החילוץ וההדרכה של פיקוד העורף, אל"ם אלעד אדרי; את ההיערכות
> המקדימה הוביל סגן קצין הרפואה הראשי אל"ם ד"ר תומר קולר, שנקבע כמפקד בית החולים.

**מה המקור אומר** (JOGH, תודות):
> We would like to acknowledge **Colonel Tomer Koler, MD, head of the delegation** and
> **Colonel (reserve) Prof. Ofer Merin, MD, head of the field hospital**…

שני התפקידים סותרים. עופר מרין — שלפי המאמר השפיט היה מפקד בית החולים — אינו מוזכר
בדף אף פעם, אף שאותו מאמר מפנה גם למאמר שלו על המודל השיתופי (Merin et al., NEJM 2014).
הסתירה אינה מופיעה ב"הערות מקורות" ואינה ברשימת "מה שלא נמצא", וכלל 30 מחייב שתופיע.
היא גם נושאת משקל: סעיף "מה קיבלה המשלחת הרפואית" קובע ש"אף דיווח על הטקס אינו מזכיר
הוקרה **למפקד בית החולים, אל"ם ד"ר תומר קולר**" — טענה שנשענת על תפקיד שנוי במחלוקת.

### M3 — "מודל היברידי" אינו ראיה ל"לא הוקמו אוהלים", והמאמר עצמו מוכיח זאת

**מה הדף אומר** (סעיף "השם שנשאר"):
> העובדה: בית חולים באוהלים לא הוקם. כך מסר משרד הבריאות הטורקי… **וכך מתארים גם שלושת
> המאמרים השפיטים: מודל היברידי, כוח אדם וציוד בתוך מבנה קיים.**

**מה המקור אומר** — אותו מאמר של קיימברידג', על הדוגמה ההיברידית שלו עצמו, הפיליפינים 2013:
> The team integrated with the Severo Verallo Memorial District Hospital… **Several tents were
> set up on the grounds of the hospital to serve as the ED** which was staffed solely by the
> Israeli team…

ובכיתוב תרשים 1:
> (a) **The hybrid model used in the Philippines depicting the emergency department in tents
> outside the existing hospital.**

התווית "היברידי" אינה שוללת אוהלים; במקרה שקיימברידג' עצמו מביא כדוגמה למודל ההיברידי,
חדר המיון עמד באוהלים בחצר בית החולים. שלושת המאמרים תומכים בכך שהטיפול ניתן בתוך
המבנה — לא בכך שלא הוקמו אוהלים. הדף מגייס אותם לטענה שהם אינם אומרים, ובאותו סעיף
עצמו הוא מודה שהשאלה על המאהל פתוחה. הראיה היחידה ל"לא הוקמו אוהלים" נשארת משרד
הבריאות הטורקי, לבדו.

### M4 — "את שלושתם כתבו אנשי המשלחת עצמם" נאמר כעובדה ואינו במקור

**מה הדף אומר** (סעיף "9 בפברואר" וסעיף "המודל שנכנס לספרות", וכן ב"הערות מקורות"):
> כך נכתב במאמר ב-Journal of Emergency Management, **שמחבריו הם אנשי המשלחת**. …
> את שלושתם כתבו אנשי המשלחת עצמם, ולכן הם ספרות שפיטה ודיווח עצמי בעת ובעונה אחת.

**מה המקורות אומרים:** אף אחד משלושת המאמרים אינו קובע שמחבריו היו חברי המשלחת.
שיוכי המחברים ב-JEM: Evan Avraham Alpert — הדסה עין כרם והאוניברסיטה העברית;
Michael Malkin — חיל הרפואה, צה"ל; Deganit Kobliner-Friedman — שערי צדק. ב-DMPHP:
Alpert, Giora Weiser, Shai Schul, Eran Mashiach, Amit Shaham, Kobliner-Friedman, כשהמחבר
המכותב הוא Alpert מהדסה. שני המאמרים כתובים בגוף שלישי על "the Israeli team"; רק
JOGH כותב בגוף ראשון ("our personnel", "we re-opened"). הדף הופך הסקה סבירה לעובדה,
ומעמיס עליה מבנה שלם: הקביעה שמשרד הבריאות הטורקי הוא "המקור הבלתי-תלוי היחיד בעניין
— כל השאר הם אנשי המשלחת עצמה או דוברות ישראלית" נשענת על ייחוס שאינו מאומת.

### M5 — הכשל שהביקורת הפנימית הסירה מן המנוע עדיין חי ב-ripple ובגוף

`audit.rule_173` מצהיר שרכיב D של משפט המנוע נוסח מחדש "בלי 'רוב' ובלי אחוז, מפני ש-17
שחולצו מן ההריסות אינם כל פצועי הרעידה". אותה הסקה עצמה שרדה בשני מקומות:

`ripple`:
> פחות מארבעה אחוזים מן המטופלים הגיעו מן ההריסות — שבעה־עשר מתוך 470 — … **ההשפעה,
> אם כן, אינה רק טיפול בפצועים** אלא גם החזרת רפואת שגרה לאוכלוסייה שנשארה בלעדיה.

סעיף "9–14 בפברואר":
> שבעה־עשר מתוך 470 הם פחות מארבעה אחוזים. **את השאר** תיאר רופא מן המשלחת…

**מה המקור אומר:** "The ED staff treated **17 patients removed from the rubble** of the
earthquake" (JEM). זהו מספר החולצים מן ההריסות, לא מספר פצועי הרעידה. פצוע רעידה שהגיע
ברגליו אינו בתוך ה-17 ואינו "השאר" שאינו מרעידת האדמה. שום מקור אינו נוקב בחלוקה בין
נפגעי רעידה לחולים כרוניים מתוך ה-470; הציטוט שהדף מביא כ"שאר" אומר במפורש
"**not only** from the earthquake, **but also** from chronic diseases" — כלומר גם וגם, בלי
פרופורציה. המסקנה "ההשפעה אינה רק טיפול בפצועים" נבנית על מספר שאינו אומר את מה שהדף
אומר. זו בדיוק מחלקת הכשל של כלל 148, בדף שנבנה כדי להימנע ממנה.

### M6 — כחמישים מטופלי השיניים נשתלו במסגרת ששת הימים, והם מספר של שבעה ימים

`summary_short`:
> **בשישה ימים** נבדקו שם **470** מטופלים, בשיא של 152 ביום אחד. שבעה־עשר מהם נשלו
> מהריסות הרעידה… **וכחמישים מהם באו לרופא שיניים.**

`the_moment`: "…ילדים, חולים כרוניים, **וכחמישים בני אדם** שבאו לטפל בשיניים" — בתוך
מסגרת "11 בפברואר… באותם ימים".

הדף עצמו, בסעיף "9–14 בפברואר" וב"הערות מקורות", מפריד נכון: 470 של שישה ימי מיון הוא
המספר של JEM; "כ-50 מטופלי שיניים" מגיע מ**סיכום דובר צה"ל**, שהוא ספירה של שבעה ימים
מסוג "למעלה מ-470 פצועים ונפגעים" — הגדרה אחרת, מכנה אחר. המילה "מהם" בתקציר מחברת
מספר משבעה ימים למכנה של שישה ימים. אותו דבר לגבי "כ-150 ילדים", שאותו הדף כן ממקם
נכון בגוף ("בספירות שמודדות שבוע שלם") אך לא בתקציר. התקציר ו-`the_moment` הם השדות
שהקורא רואה ראשונים, והם היחידים שבהם ההפרדה נשברה.

### M7 — כלל 30: JOGH אומר שהמודל לא תורגל מעולם; הדף אומר את ההפך ואינו מזכיר את המשפט

**מה הדף אומר** (סוף סעיף "9 בפברואר"):
> מה שנזנח ב-9 בפברואר לא היה התוכנית היחידה שהמשלחת ידעה לבצע. **הוא היה הראשונה מבין
> שתיים.**

**מה המקור אומר** (JOGH, אוגוסט 2023, בגוף ראשון, בן-הזמן הקרוב ביותר לאירוע):
> The plan was to operate a field hospital without support or utilities from the affected
> community, yet **we soon realised that aid was required in a model we have never practised
> before.**

זו סתירה חזיתית בין שני מקורות שהדף נשען על שניהם: JOGH (2023) אומר "מודל שמעולם לא
תרגלנו", DMPHP (דצמבר 2024) אומר "שני מודלים שהצוות הישראלי משתמש בהם". הדף אימץ את
המאוחר, בנה עליו את משפט הסיום של הסעיף, ומחק את המוקדם לגמרי — לא בגוף, לא ב"הערות
מקורות", לא ב"מה שלא נמצא". כלל 30 מחייב שמחלוקת תישאר גלויה.

### M8 — "המודל שנכנס לספרות" — המודל היה בספרות עשור לפני קהרמאנמרש

**מה הדף אומר** (כותרת סעיף וגוף):
> **המודל שנכנס לספרות** … מה ששרד את השבוע הוא טיעון מקצועי… המאמר של קיימברידג' הוא
> זה שהופך את המקרה לטיעון.

**מה המקור אומר:** אותו מאמר קובע שהמודל ההיברידי הופעל בפיליפינים אחרי טייפון היאן
ב-2013 ומפנה למקור שלו — `Merin O, Kreiss Y, Lin G, Pras E, Dagan D. Collaboration in
Response to Disaster – Typhoon Yolanda and an Integrative Model. N Engl J Med.
2014;370:1183-4`. גם JOGH מפנה לאותו מאמר: "This collaborative and integrative model,
**previously described by Merin et al.**". כלומר המודל תואר ופורסם ב-New England Journal
of Medicine תשע שנים לפני הרעידה בטורקיה. קהרמאנמרש היא מופע נוסף, לא כניסה לספרות.
הכותרת והטענה מנפחות את מה שהמקרה תרם, וזה הכשל K2 שהתדריך מזהיר מפניו — "המציא את",
במסווה של "נכנס לספרות".

---

## minor

**m1 — שם הדובר.** הדף כותב "ד"ר ריימון מוקלד" / "Dr. Raymond Mokled"; המקור כותב
`Dr. Raymon Mokalled` (ובהמשך הכתבה `Mokallad`). גם אחרי תיקון C1, האיות בדף אינו האיות
של המקור.

**m2 — "המקור הבלתי-תלוי היחיד" נאמר על מקור שקורא לזה בעצמו בית חולים שדה.** אותה
בדיקת עובדות של אנדולו, בשורת הפסיקה שלה, כותבת:
`İsrail sağlık personellerinin güvenlik gerekçesiyle Kahramanmaraş'ta **kurdukları sahra
hastanesinden** çekildiği iddiası gerçeği yansıtmıyor` — "בית החולים השדה **שהקימו**". גם
כתובת המאמר עצמה נושאת את המילים `kurdugu-sahra-hastanesinden`, וגם אנדולו באנגלית קוראת
למקום `the Kahramanmaras Sahra hospital`. הדף מייחס את הישרדות השם ל"אנשי המשלחת עצמה או
דוברות ישראלית" בלבד; סוכנות הידיעות הממלכתית הטורקית השתמשה בו בקולה שלה. העובדה עצמה
(`çadır hastane kurulmadığını`, "בית חולים באוהלים לא הוקם") עומדת — הצגת המקור היא
שחסרה.

**m3 — "כל הטיפול" מול "בבתי החולים" ברבים.** משפט המנוע קובע "כל הטיפול ניתן בתוך המבנה
שלו". משרד הבריאות הטורקי, המקור שהדף מציג כבלתי-תלוי היחיד, אומר:
`sağlık personelinin, bakanlığın belirlediği **hastanelerde** diğer doktorlar ile birlikte
görev yaptığını` — "בבתי החולים שקבע המשרד", ברבים, "יחד עם רופאים אחרים". הדף מתרגם את
זה נכון בסעיף 02, אך משפט המנוע נוקב בכמת מוחלט ("כל") שאף מקור אינו אומר.

**m4 — "כ-150 ילדים".** JOGH נוקב במספר מדויק: `470 patients received treatment, **150** of
whom were children`. הדף מוסיף "כ-" שאינו במקור.

**m5 — היעדר מכתבת תדמית אינו ראיה לאי-הוקרה.** סעיף "מה קיבלה המשלחת הרפואית" ושדה
`recognition` מציגים את היעדר ישראל מסקירת WHO/Europe מול UMKE, UK-Med ופיימונטה. הסקירה
מזכירה 39 צוותים ומביאה שלושה כדוגמאות; היא feature story ולא רשימת מוקרים. הגוף מסייג
נכון ("אינה בין הדוגמאות שנבחרו"), אבל שדה `recognition` אינו מסייג.

**m6 — "על ששת הימים נכתבו שלושה מאמרים".** רק JEM הוא מאמר על המשימה בטורקיה. DMPHP הוא
"Concepts in Disaster Medicine" על מודלים של חדרי מיון בבתי חולים שדה ישראליים, שטורקיה
היא בו אחת מכמה דוגמאות לצד נפאל והפיליפינים; JOGH הוא viewpoint. "נכתבו שלושה מאמרים
על ששת הימים" מגדיל את נפח הספרות.

---

## מה החזיק

כל אלה נבדקו מול המקור החי ועמדו, מילה-במילה:

1. **470 · 152 · 17 · 6 ימים · 10 ניתוחים · 48 מאושפזים · 27 טיפול נמרץ** — כולם ב-JEM,
   בהגדרה שהדף נוקב בה: `A total of 470 patients were examined by the Israeli team in the ED
   during the 6 days of clinical operation. There was a peak of 152 patients on February 11,
   2023. The ED staff treated 17 patients removed from the rubble.` הדף לא רק שאינו כותב
   "470 פצועי רעידת אדמה" — הוא נושא את ההגדרה המלאה בתווית של `numbers[0]`. זהו המקום
   שבו הדף הקודם נכשל, וכאן הוא עומד.
2. **60 מיטות · שש מיטות טיפול נמרץ · חמישה חדרי ניתוח · ארבע מחלקות · 140 איש · 17 טונות**
   — כולם ב-JOGH, מילה-במילה, כולל ההסתמכות על מהנדסי צוות החילוץ.
3. **142 איש** — JEM, `a medical delegation of 142 personnel`.
4. **29 צוותים מ-22 מדינות · התרעה ברמה 4 · 11 מחוזות** — DMPHP.
5. **39 צוותים מ-22 מדינות · UMKE Type 2 מ-2020 · תרומת בית החולים האיטלקי** — WHO/Europe,
   17.6.2026, כולל התאריך שהדף נוקב בו.
6. **ישראל אינה מוזכרת בסקירת WHO/Europe** — נבדק בגוף הכתבה כולה. המופעים היחידים של
   המילה Israel הם בתפריט המדינות של האתר.
7. **הסיווג Type 3 מ-2016** — נבדק ברשימה הרשמית של ארגון הבריאות העולמי ולא רק במאמר.
8. **"çadır hastane kurulmadığını"** — הודעת משרד הבריאות הטורקי, בטורקית, בהקשרה:
   `İsrail ekibinin Türkiye'ye gelirken, yanlarında sahra hastanesi de getirdiğini fakat
   şehirlerdeki hastanelerin kullanıma elverişli olması sebebiyle çadır hastane kurulmadığını
   ifade etti`. התרגום בדף מדויק.
9. **"10 gün"** — משרד הבריאות הטורקי אכן אומר עשרה ימים באזור האסון.
10. **הודעת השגרירות** — `ortak kararıyla` ו-`kademeli olarak` נמצאות בטקסט הטורקי כפי
    שהדף אומר, ובהקשר שהדף מתאר.
11. **בדיקת העובדות** — אנדולו אכן פנתה גם למשרד הבריאות וגם לצד הישראלי, וקבעה
    `gerçeği yansıtmıyor`; הצד הישראלי אכן מסר `planlanan görev süresinin sona ermesi`.
12. **הודעת לשכת אפיונקרהיסאר** — הכותרת, "היום הראשון", חדרי הניתוח והטיפול הנמרץ,
    `ekiplerimizin sorumluluğunda` ומסירת האחריות "היום" — כולם בטקסט הטורקי. הדף מביא
    את הגרסה המתחרה במלואה ובלשונה, ולא ניטרל אותה. **בזה הדף עומד במבחן הקשה של קו
    ההתקפה השלישי** — הכשל שלו הוא במסקנה שהוא מסיק ממנה (C2), לא בהצגתה.
13. **ההוקרה של ארדואן ניתנה לזרוע האחרת** — JNS, 26.4.2023: `A certificate of appreciation
    from Turkish President Recep Tayyip Erdogan was presented on Tuesday to the commander of
    the Israel Defense Forces' National Rescue Unit, Col. (Ret.) Golan Vach`. הדף לא ייחס
    אותה למשלחת הרפואית — וזה הפח שהתדריך רומז אליו במפורש. הדף לא נפל בו.
14. **ציטוט הכט** — JNS, 6.2.2023, מילה-במילה כולל "Right now, the Turkish government only
    asked for search and rescue [assistance]".
15. **ציטוט 250 המטופלים, ציטוט "skeleton staff", ציטוט "biggest accomplishment", ציטוט
    "pre-disaster capacity", ציטוט "1-month leave", ציטוט המודלים standalone/hybrid** —
    כולם מילה-במילה.
16. **הודעת דובר צה"ל מ-8.2** — הנוסח הישראלי משוחזר זהה בשלושה כלים.

---

## שער 176 — מה קרה בעולם בפועל

**עומד, על רגל אחת מתוך שתיים.**

**הרגל שעומדת:** עיר של יותר ממיליון תושבים שמערכת הבריאות שלה קרסה קיבלה בית חולים
מתפקד למשך שבוע. זה אינו "סלל את הדרך ל-": זה 470 מטופלים בחדר מיון, 10 ניתוחים,
48 אשפוזים ו-27 מונשמים, שני מאמרים שפיטים נפרדים מדווחים את אותם מספרים באותה הגדרה,
והמוסד נמסר בחזרה **פועל** — `groups of volunteer Turkish physicians could continue their
operation` (JEM). שרשרת סיבתית מלאה: מי לקח את זה (רופאים טורקים מתנדבים), מתי (15.2.2023),
ומה נבנה ממנו (בית חולים שהמשיך לפעול בלי הפסקת שירות). הכתבה המקומית מיוני 2024 מוסיפה
את הצד השני של אותו מטבע ומחזקת את האמינות: השיקום המלא לא קרה, והמחלקות נשארו סגורות
שישה-עשר חודשים. הדף אומר את שניהם.

**הרגל שאינה עומדת:** "מה ששרד את השבוע הוא טיעון מקצועי". הטיעון המקצועי — המודל
ההיברידי — פורסם ב-New England Journal of Medicine ב-2014 בידי מרין ואחרים, על סמך
הפיליפינים 2013. אין בשום מקור בתיק ראיה שגוף כלשהו שינה דוקטרינה בגלל קהרמאנמרש: אין
ציטוט של צוות זר, אין הנחיה של ארגון הבריאות העולמי, ואין הפניה למקרה מחוץ למעגל
המחברים עצמם. סקירת WHO/Europe, שהיא הגוף המתאם, אינה מזכירה את ישראל כלל. שלושת
המאמרים הם ראיה לכך שהמעש **תועד**, לא לכך שהוא **הופנם**.

**המסקנה לשער:** הדף עובר, אבל דרך ההשפעה הקונקרטית בלבד. סעיף "המודל שנכנס לספרות"
צריך לרדת מטענת תרומה לטענת תיעוד — אחרת הדף נשען בדיוק על סוג ההשפעה שכלל 176 בא
לפסול.

---

## מה לא נבדק, ונשאר פתוח לבודק הבא

- **jpost, article-731197** (מקור הציטוט "abandoned" בסעיף 05 ו"כ-140 רופאים") — האתר
  מחזיר 404 לבוטים. הציטוט של "ג'רוזלם פוסט" בדף לא אומת מול המקור החי.
- **ynet, hkyeguwai** (15 מטוסים, מאות טונות, כ-230 אנשי צוות) — לא נמשך.
- **marassonhaber, יוני 2024** (המחלקות סגורות, נפתח ב-2011, בלי התמוטטות) — לא נמשך;
  זהו המקור היחיד לסעיף "מה נשאר בקהרמאנמרש" כולו.
- **Algemeiner, 12.2.2023** ("יותר מ-300… בית חולים שדה שהקימה ישראל") — לא נמשך.
- **סיכום דובר צה"ל** (המקור ל"למעלה מ-470 פצועים ונפגעים", "כ-150 ילדים", "כ-50 מטופלי
  שיניים", "מאהל בית חולים שדה") — לא נמשך במסגרת הביקורת הזאת, והוא המקור שממנו נובעים
  M6 והשאלה הפתוחה על המאהל.

ארבעת אלה נושאים ביחד שבע טענות בדף. מי שיסגור אותם יסגור את מה שנשאר.

---

**אני לא תיקנתי דבר.** `canonical.json` לא נגעתי בו; `audit.adversarial_review` נשאר
`null`, והכותב הוא שממלא אותו. כלל 150.
