# ביקורת אדברסרית — הדיסק-און-קי / דב מורן ו-M-Systems

- **at:** 2026-08-14
- **by:** adversarial-140 / opus
- **verdict:** fail-must-fix
- **claims_checked:** 34

## סיכום

הדף כתוב היטב, והשלד שלו עומד: שלושת הממציאים על US6148354, תאריך ההגשה 5.4.1999,
ההשקה ב-15.12.2000, שני הפרסים (שניהם אומתו היום אצל הגוף המעניק עצמו), הקדימות של
עשרה חודשים על הבקשה הסינגפורית, אי-הזהות בין שני מסמכי הפטנט, והסירוב הנכון לכתוב
"הדיסק-און-קי הרג את הדיסקט". שתיים מחמש ההתקפות שמנויות ב-ENGINE.md הותקפו בפועל
מול המסמכים הראשוניים והמשפט שרד אותן.

אבל שישה דברים בדף אינם מחזיקים, וחמישה מהם נוגעים לליבה. **הכבד מכולם: פסק הדין
הסינגפורי קבע שהצד הישראלי הפר את הפטנט וחייב אותו בפיצויים — והדף אינו אומר זאת
באף מקום.** לצידו: מספר בסעיף החותם שגוי פי כ-64; משפט שמייחס לבית המשפט עמדה
שהוא לא נקט בה; שני מספרים שגויים בשורה אחת בסעיף שכולו כרונולוגיה; ופרט פיזי
("על האריזה היה שמה של IBM") שחוזר בארבעה מקומות ושהמקור היחיד אומר משהו אחר.

שני ממצאים חשובים נשענים על מסמכים ראשוניים שהיומן רשם כ**לא ניתנים למשיכה**: שני
פסקי הדין מ-elitigation.sg נמשכו היום במלואם ונקראו מילה במילה. מה שנמצא שם סותר
את הדף בשלוש נקודות ומאשש אותו בשתיים.

## Findings

### 1. must-fix — פסק הדין קבע הפרה וחיוב בפיצויים; הדף לא אומר זאת
- **where:** `sections/09-piska-91.json` body/body_en · `fields.json` summary_short · `fields.json` aftermath
- **claim:** הדף כותב "הוא קיבל את תביעת טרק, דחה את תביעת הנגד, ודחה בהוצאות את התביעה שהגישה M-Systems עצמה. בסינגפור הצד הישראלי הפסיד בשני הכיוונים, גם כנתבע וגם כתובע." ו-`summary_short` מסתפק ב"סינגפור פסקה לטובת טרק בשתי ערכאות". בשום מקום בדף לא נאמר **מה** הפסיד הצד הישראלי כנתבע.
- **evidence:** [2005] SGHC 90, פסקה 131, מילה במילה: `"Given that this court has concluded that the Patent is valid, and that the defendants did commit infringement of the Patent…"` · פסקה 142, מילה במילה: `"Suit 604/2002/N is dismissed with costs. Damages are ordered to be assessed."` · [2005] SGCA 55, פסקה 1, מילה במילה: `"…appealed against Lai Kew Chai J's decision (reported at [2005] 3 SLR 389) that they had infringed Singapore patent No 87504 (WO 01/61692), which was granted to the respondent, Trek Technology (Singapore) Pte Ltd ('Trek'), and were therefore liable in damages for the infringement. We dismissed the appeal."` קורא הדף אינו יכול ללמוד ממנו שהחברה הישראלית נמצאה מפרה ושחויבה בפיצויים. זו ההשמטה הכבדה ביותר בדף, והיא פועלת לטובת הצד הישראלי.
- **תיקון מוצע:** להוסיף בסעיף 09 את שתי הקביעות בלשונן ("the defendants did commit infringement of the Patent" · "Damages are ordered to be assessed"), ולתקן את `summary_short` כך שיאמר שהצד הישראלי נמצא מפר וחויב בפיצויים, ולא רק ש"סינגפור פסקה לטובת טרק".
- **source_url:** https://www.elitigation.sg/gd/s/2005_SGHC_90 · https://www.elitigation.sg/gd/s/2005_SGCA_55

### 2. must-fix — "ובית המשפט לא חלק על כך": ייחוס עמדה לבית משפט שמעולם לא נקט בה
- **where:** `sections/09-piska-91.json` body, פסקה חמישית
- **claim:** "הישראלים הגישו קודם, בעשרה חודשים, **ובית המשפט לא חלק על כך**"
- **evidence:** בטקסט המלא של [2005] SGHC 90 המחרוזת `"1999"` מופיעה **פעם אחת בלבד**, ורק על Netac: `"There was also no evidence that Netac had produced a prototype device in August 1999."` המחרוזות `"April 1999"`, `"6148354"` ו-`"285,706"` מופיעות **אפס פעמים**. בית המשפט לא דן בתאריך ההגשה הישראלי, לא הזכיר אותו ולא קבע לגביו דבר. הצירוף `"and this is not disputed"` בפסקה 91, שהדף עצמו מצטט, נסמך על **תוכן** האזכורים ("do not disclose any device with an integrated plug") ולא על תאריך כלשהו. הדף הופך שתיקה להסכמה שיפוטית.
- **תיקון מוצע:** "בית המשפט לא דן בתאריך ההגשה הישראלי כלל. הוא התייחס למסמך של M-Systems כאל פריור-ארט, וקבע רק מה כתוב בו ומה אינו כתוב בו."
- **source_url:** https://www.elitigation.sg/gd/s/2005_SGHC_90

### 3. must-fix — "חודש לפני היריד" וגם "הגיש את בקשת הפטנט שלו": שני מספרים שגויים בשורה אחת, בסעיף שכולו כרונולוגיה
- **where:** `sections/08-arbaa-toanim-labechora.json` body/body_en, פסקה שנייה
- **claim:** "הן טאן, האיש שמאחורי טרק, הגיש את בקשת הפטנט שלו ב-2000, חודש לפני היריד"
- **evidence (א — המרווח):** [2005] SGCA 55 פסקה 2, מילה במילה: `"On 21 February 2000, Trek filed an application for a Singapore patent (the 'patent') with respect to a portable data storage device. Trek claimed that the patent protected its product, 'ThumbDrive', which was unveiled at an international exhibition in Germany **a week after** the application for the patent was submitted in Singapore."` בית המשפט לערעורים אומר במפורש "שבוע", לא "חודש". אימות עצמאי בן-הזמן: ZDNet, "CeBIT 2000: A summary", מתוארך 28 בפברואר 2000, פותח ב-`"Now that our time in Hannover is nearing to a close…"` — כלומר היריד כבר הסתיים או עמד להסתיים ב-28.2.2000, ולא נערך במרץ. (היומן, שורה 649, רשם "CeBIT, מרץ 2000" — וזה מקור השגיאה.)
- **evidence (ב — מי הגיש):** [2005] SGHC 90 פסקה 108, מילה במילה: `"The inventive concept underlying the ThumbDrive was developed by one Poo Teng Pin ('Poo') and one Marcus Cheng ('Marcus')… Marcus, who was Head of the Engineering Department and tasked to liase with patent agents and prepare the patent application, named himself as the sole inventor. Trek subsequently came to realise that Poo had been omitted from the patent application."` המבקשת הייתה **Trek**, והממציאים הרשומים הם מרקוס צ'נג ופו טנג פין. הן טאן אינו ממציא רשום. שתי השגיאות מגיעות מ-IEEE Spectrum (`"Tan had filed a patent application for his invention in 2000, a month before the German tech fair"`) — מקור משני שהמקור הראשוני של הדף עצמו סותר.
- **הערה על הסימטריה (בדיקה ב'):** זו בדיוק אי-האיזון שביקשת לחפש, והיא פועלת לרעת הצד הסינגפורי. סעיף 04 נותן לצד הישראלי רשימת ממציאים מדויקת בת שלושה שמות מן המסמך הרשמי; סעיף 08 מכווץ את הצד הסינגפורי לאיש אחד ש"הגיש את בקשת הפטנט **שלו**" — כשהמסמך הראשוני שהדף מצטט בסעיף הבא נוקב בשני שמות אחרים.
- **תיקון מוצע:** "טרק הגישה את בקשת הפטנט ב-21 בפברואר 2000, שבוע לפני שההתקן הוצג ביריד; הממציאים הרשומים בה הם מרקוס צ'נג ופו טנג פין. הישראלים הגישו באפריל 1999, כעשרה חודשים קודם לכן."
- **source_url:** https://www.elitigation.sg/gd/s/2005_SGCA_55 · https://www.elitigation.sg/gd/s/2005_SGHC_90 · https://www.zdnet.com/article/cebit-2000-a-summary

### 4. must-fix — "כונן שלם הוא שתי דקות של סרטון": שגוי פי כ-64
- **where:** `sections/13-bachazara-lamegera.json` body (`"כונן שלם הוא שתי דקות של סרטון."`) ו-body_en (`"An entire drive is two minutes of video."`)
- **claim:** כונן של 128 ג'יגה-בייט מכיל שתי דקות של וידאו 4K.
- **evidence:** Engadget, מילה במילה: `"Their relatively small capacities — most brands top out at 128GB — make them useless when dealing with large files. Many people now deal with larger files than ever. New smartphones can produce libraries of 4K video which take up roughly 1GB for every minute of footage at high frame rates."` 128 ג'יגה-בייט חלקי ג'יגה-בייט לדקה = **128 דקות**, כלומר קצת יותר משעתיים. הדף עצמו נוקב בשני המספרים בשתי השורות שלפני, ואז מחשב אותם לא נכון. זה המשפט האחרון של הפסקה הראשונה בסעיף החותם, והוא הנקודה שהקורא לוקח איתו.
- **תיקון מוצע:** "כונן שלם הוא כשעתיים של צילום." (הטיעון עצמו — שהתקרה היא שדחקה את החפץ — נשאר תקף, ואף חזק יותר כשהמספר נכון.)
- **source_url:** https://www.engadget.com/2229010/usb-flash-drives-becoming-obsolete

### 5. must-fix — "על האריזה היה שמה של IBM": פרט פיזי בלי מקור, והמקור היחיד אומר משהו אחר
- **where:** `sections/01-hamegera.json` (`"בארצות הברית הוא נמכר תחת שמה של IBM"`) · `sections/07-15-bedetsember-2000.json` (`"ועל האריזה היה שמה של IBM"`) · `fields.json` description · `fields.json` summary_short · `ENGINE.md` ("ההשקה ב-15.12.2000 תחת שמה של IBM")
- **claim:** המוצר נמכר בארה"ב תחת שמה של IBM, ושמה של IBM הופיע על האריזה.
- **evidence:** המקור היחיד לכך בכל היומן הוא IEEE Spectrum, מילה במילה: `"In 2000, IBM began selling M-Systems' 8-MB storage devices in the United States under the less-than-memorable name DiskOnKey."` המקור אומר ש-IBM **מכרה** את המוצר, ושהשם שתחתיו נמכר הוא **DiskOnKey** — כלומר כמעט ההפך מ"תחת שמה של IBM". המילה "אריזה" (packaging) אינה מופיעה באף מקור ביומן; זהו פרט פיזי מומצא. היומן עצמו (שורה 262) כותב את ההיקש — "המותג היה של IBM, המוצר של M-Systems" — כמסקנה, והדף הפך אותה לתיאור חושי.
- **תיקון מוצע:** "בארצות הברית מכרה אותו IBM, בשם DiskOnKey" — זה בדיוק מה שהמקור אומר. אם רוצים את האריזה, צריך מקור לאריזה.
- **source_url:** https://spectrum.ieee.org/thumb-drive

### 6. must-fix — "הצד הישראלי הוא שפתח את ההליך המשפטי, ולא להפך" נאמר כעובדה, ושני מקורות סותרים אותו
- **where:** `sections/09-piska-91.json` body, סוף הפסקה הראשונה
- **claim:** משפט חתוך, בקול הדף עצמו, אחרי פסקה שכולה מיוחסת ל-M-Systems ("בגרסת M-Systems עצמה, בדוח החתום שהגישה…"). המשפט יוצא מן הייחוס אל קול הדף ומכריע שאלה שנויה במחלוקת.
- **evidence (א):** IEEE Spectrum, המקור המשני המרכזי של הדף, אומר את ההפך: `"Beginning in 2002, Tan brought suit in Singapore against a handful of companies (including Electec, FE Global Electronics, M-Systems, and Ritronics Components) for patent infringement."` **evidence (ב):** בית המשפט דחה את ההנחה שעליה בנוי כל המשפט — שהמכתבים היו "מכתבי איום". [2005] SGHC 90 פסקה 131, מילה במילה: `"I am of the view that the two letters, which were at the centre of this part of the dispute, were nothing more than letters exploring the possibility of a business collaboration, and any allegation that groundless threats were made is misconceived."` בפסקי הדין עצמם אין תאריכי הגשה לתביעות, ולכן שאלת "מי פתח" **לא ניתנת להכרעה מן המסמכים הראשוניים** — מה שהופך את המשפט הנחרץ "ולא להפך" לבלתי-נסבל תחת כלל 30.
- **תיקון מוצע:** להשאיר את הסיפור בקול המיוחס, ולהוסיף את שני הצדדים: "לפי הדוח של החברה עצמה, היא שפתחה; IEEE Spectrum מתאר את טרק כמי שפתחה ב-2002 בסדרת תביעות. בית המשפט לא נדרש לשאלה מי הקדים, וקבע לגבי המכתבים ש'were nothing more than letters exploring the possibility of a business collaboration'."
- **source_url:** https://spectrum.ieee.org/thumb-drive · https://www.elitigation.sg/gd/s/2005_SGHC_90

### 7. moderate — פסקת Netac: תרגום כמעט-מילולי מ-IEEE, בלי ייחוס, על שני אנשים חיים ומזוהים בשמם
- **where:** `sections/08-arbaa-toanim-labechora.json` body, פסקה רביעית
- **claim:** "שני מהנדסים, צ'נג שיאוהואה ודנג גואושון, ראו בטרק לוחות פיתוח של זיכרון פלאש, ואז עזבו… **חרף ההסכם הזה** ביקשה Netac פטנט משלה על ההתקן בתוך סין, וקיבלה אותו."
- **evidence:** זהו תרגום צמוד של IEEE Spectrum: `"Cheng Xiaohua and Deng Guoshun had previously worked for Trek and had seen some development boards related to flash memory. They returned to Shenzhen, China, and founded Netac in 1999… Netac and Trek subsequently even entered into an agreement under which Trek would fund some of Netac's research and development… Despite this collaboration, Netac sought and was granted a patent on the thumb drive within China."` הפסקה הקודמת באותו סעיף פותחת ב"**לפי אותה כתבה**"; הפסקה הזאת אינה נושאת שום ייחוס, והיא זו שנושאת רמיזה שלילית (נטילת ידע, הפרת הסכם) על שני אנשים חיים הנקובים בשמם המלא. זה בדיוק הרף הכפול של כלל 139. בנוסף הדף משמיט את המשפט של IEEE שמסביר למה הכתבה ממסגרת זאת כך (`"Netac's claim to (and production of) its thumb drive fit this pattern of appropriation"`) — כלומר הקורא מקבל את הרמיזה בלי המקור ובלי הסייג.
- **תיקון מוצע:** לפתוח גם את הפסקה הזאת ב"לפי אותה כתבה", ולתאר את הטענה במקום את הרמיזה.
- **source_url:** https://spectrum.ieee.org/thumb-drive

### 8. moderate — הדף לא אומר מה הייתה טענת Netac, ולא מוסר את הפורום היחיד שדן בה ודחה אותה
- **where:** `sections/08` פסקה רביעית · `sections/10-ota-sheela-arba-tshuvot.json` ("בסין נותרה Netac עם פטנט משלה על ההתקן")
- **claim:** Netac מוצגת כטוענת בכורה רביעית חיה, על בסיס פטנט סיני, בלי שנאמר מה בדיוק היא טענה ובלי שנאמר שערכאה בדקה את הטענה ודחתה אותה.
- **evidence:** הטענה עצמה מנוסחת ב-[2005] SGHC 90 פסקה 105(c): `"Ritronics alleges that 2 former Trek employees had developed the ThumbDrive invention and that the rightful owner of the ThumbDrive invention is a Chinese company called Netac Technology Ltd."` וההכרעה — פסקה 120: `"the Chinese Patent and corresponding applications to the European Patent Office ('EPO') were filed by Netac after the Patent's priority date. It does not constitute prior art in the present proceedings."` פסקה 121: `"The Chinese Patent teaches and explicitly requires the use of one of three different cables… The integrated plug element is also missing."` פסקה 122: `"The chronology does not support Ritronics' theory that Trek stole the invention."` פסקה 123: `"There is no evidence to show that they can lay claim to the ownership of the patent."` זו הבדיקה של סעיף ב' מוחלת באופן סימטרי: טענה שנויה במחלוקת מוצגת בלי מי פסק בה, מתי, ומה.
- **תיקון מוצע:** להוסיף בסעיף 10 שורה אחת: בית המשפט העליון בסינגפור (Lai Kew Chai J, 12.5.2005) בחן את טענת Netac וקבע שהפטנט הסיני הוגש אחרי תאריך הקדימות של טרק, שאין בו תקע משולב, ושאין ראיה לגניבה.
- **source_url:** https://www.elitigation.sg/gd/s/2005_SGHC_90

### 9. moderate — "7 מיליארד דולר" נמסר כעובדה; במקור זה נתון של חברת מחקר-שוק
- **where:** `sections/01-hamegera.json` body (`"ב-2021 עברו מכירות כונני ההבזק בעולם, אצל כל היצרנים יחד, 7 מיליארד דולר בשנה."`) · `fields.json` numbers[3]
- **claim:** המספר מופיע בלי ייחוס, כעובדה על העולם.
- **evidence:** IEEE Spectrum, מילה במילה: `"In 2021, global sales of the devices from all manufacturers surpassed $7 billion, a number that is expected to rise to more than $10 billion by 2028, **according to Vantage Market Research**."` היומן עצמו מתעד שהחוקר בדק כעשרה אתרי מחקר-שוק, מצא שהם סותרים זה את זה בסדרי גודל (מ-6.1 מיליארד ועד 1,561 מיליארד דולר), ופסל את כולם — ואז המספר האחד ששרד נכנס לדף בלי הייחוס שהיה כל ההצדקה שלו. עוגן השנה (2021) קיים ותקין לפי כלל 138; מה שחסר הוא מי מדד.
- **תיקון מוצע:** "לפי חברת המחקר Vantage Market Research, שמצוטטת ב-IEEE Spectrum, עברו ב-2021 מכירות כונני ההבזק בעולם 7 מיליארד דולר בשנה."
- **source_url:** https://spectrum.ieee.org/thumb-drive

### 10. moderate — "מה שקבוע בכל הגרסאות הוא נסיעת העבודה לארצות הברית ב-1998" — לא נכון לפי ציטוטי היומן עצמם
- **where:** `sections/03-new-york-1998.json` body, פסקה שנייה · `fields.json` the_moment · כותרת הסעיף ("ניו יורק, 1998")
- **claim:** השנה 1998 והנסיעה לארה"ב מוצגות כמכנה המשותף של כל הגרסאות — כלומר כגרעין המאומת של הרגע.
- **evidence:** משלוש הגרסאות הכשרות (הרביעית סומנה ביומן "לכותב: אל תשתמש בזה"): גרסת הטכניון אומרת רק `"something that happened to me in the U.S."` — בלי שנה. שורת הפרס של קרן אדוארד ריין (`"How a Flat Computer Battery Led to Millions of Bytes on a Key Chain"`) אינה מזכירה לא ארה"ב ולא שנה. רק Humans of Tel Aviv נוקב: `"During an important business trip to New York in 1998, my computer crashed and I found myself without a presentation and with 200 people staring at me."` כלומר השנה, העיר ומספר האנשים נשענים על **מקור אחד**, שהוא גם היחיד שאין לו תאריך פרסום. השגיאה מקורה ביומן (שורה 562) והדף ירש אותה.
- **תיקון מוצע:** "מה שחוזר בכל הגרסאות הוא ההרצאה שהיה אמור לתת והמחשב שבגד בו. המקום, השנה ומספר האנשים מגיעים ממקור אחד בלבד."
- **source_url:** https://www.humansoftelaviv.co.il/dov-moran-the-inventor-of-the-usb-flash-drive · https://www.technion.ac.il/en/blog/article/25-years-since-the-invention-that-changed-the-world-of-data-storage

### 11. moderate — "הגרסה המוקדמת מכולן" ו"כותרת ההרצאה… בטקס הפרס": שני אפיונים שאין להם בסיס במקור
- **where:** `sections/03-new-york-1998.json` body · `fields.json` the_moment
- **claim:** "הגרסה המוקדמת מכולן היא **כותרת ההרצאה** שקרן אדוארד ריין רשמה לצד שמו **בטקס הפרס** ב-2012"
- **evidence:** המחרוזת עצמה אומתה היום מילה במילה בכרונולוגיה הרשמית של הקרן. אבל: (א) באותה כרונולוגיה השדה הזה מחזיק אצל זוכים אחרים את **נושא הפרס** ולא כותרת הרצאה — 2011, Wolfgang Hilberg: `"Invention of the radio clock"`; Raymond S. Tomlinson: `"Invention of the today so-called e-mail"`; 2012 פרס הטכנולוגיה, Bradford Parkinson: `"The Development of the Global Positioning System (GPS)"`. שום דבר בעמוד אינו אומר "הרצאה" ואינו אומר "טקס". (ב) "המוקדמת מכולן" הוא דירוג כרונולוגי שאי אפשר לבסס: ליומן אין תאריך פרסום ל-Humans of Tel Aviv (רשום רק "נמשך: 2026-08-14"), ולכן אי אפשר לדעת שהיא מאוחרת מ-2012. הערך הראייתי של הפריט תלוי בדיוק בשני האפיונים האלה.
- **תיקון מוצע:** "השורה שרשמה קרן אדוארד ריין לצד שמו ב-2012 מדברת גם היא על סוללה ריקה" — בלי "הרצאה", בלי "טקס", ובלי "המוקדמת מכולן".
- **source_url:** https://www.eduard-rhein-stiftung.de/en/chronology

### 12. moderate — הזהות בין "the Ban patent" ל-US6148354 נטענת בלי החוליה המגשרת
- **where:** `sections/09-piska-91.json` body, פסקה רביעית
- **claim:** "'the Ban reference' הוא מסמך הפטנט של M-Systems: פסק הדין מזהה אותו כבקשת הפטנט הסינגפורית של החברה"
- **evidence:** פסק הדין מגדיר אותו כך, פסקה 49(d), מילה במילה: `"Singapore Patent Application No 200203303-3 (derived from PCT application PCT/US00/07087) ('Ban patent'), which discloses a method of building a cable-connected desktop storage device that enables flash modules to be attached via USB and operate as a file storage device."` הקורא שיבדוק ימצא **מספר מסמך אחר לגמרי** מזה שהדף נוקב בו בסעיף 06 (US6148354), והדף אינו נותן לו את הגשר. הגשר קיים ואומת בבדיקה הזאת: WO2000060476A1 הוא בקשת PCT/US2000/007087, ממציאים Ban / Moran / Ogdan, נמחית מקורית M Systems Flash Disk Pionners Ltd, תאריך קדימות 1999-04-05 — כלומר אותה משפחת פטנטים בדיוק. הטענה **נכונה**; מה שחסר הוא שתי המילים שמאפשרות לקורא לאמת אותה.
- **תיקון מוצע:** להוסיף את הסוגריים מפסקה 49(d) ("derived from PCT application PCT/US00/07087"), ומשפט אחד: זו הבקשה הסינגפורית מאותה משפחה של US6148354, אותם שלושה ממציאים ואותו תאריך קדימות.
- **source_url:** https://www.elitigation.sg/gd/s/2005_SGHC_90 · https://patents.google.com/patent/WO2000060476A1/en

### 13. moderate — ציטוט השופט Kitchin מובא כאילו נקרא מפסק הדין; הוא מובא דרך IPKat, והמקור הראשוני לא ניתן לאמת
- **where:** `sections/10-ota-sheela-arba-tshuvot.json` body, פסקה ראשונה
- **claim:** "בינואר 2008 בחן השופט Kitchin את הסוגיות מחדש ומצא שהגורם ששמע את התיק צדק בכל נקודה ונקודה. את התיקונים פסל: `'I have found the proposed amendment is not allowable because it would result in the specification disclosing additional matter'`"
- **evidence:** היומן (שורות 198–215) רושם במפורש שהציטוט מגיע מ-The IPKat, ושהמקור הראשוני לא נמשך: BAILII "נחסם על ידי מערכת Anubis anti-bot", CaseMine `__FETCH_FAILED__ every route blocked`. ניסיתי שוב היום את שני המסלולים: BAILII מחזיר אתגר proof-of-work של Anubis, ו-Wayback החזיר 429/503. **לא ניתן לאמת** את הציטוט מול פסק הדין עצמו. גם מספר הפטנט הבריטי GB 2371653 ותאריך ההחלטה 8.11.2006 נשארים לא מאומתים לפי היומן — והדף בחוכמה אינו נוקב בהם. בכל שאר הדף, כשהדף מצטט מסמך משפטי, הוא נותן את המקור בגוף הטקסט; כאן הוא לא.
- **תיקון מוצע:** "בלשון פסק הדין, כפי שהוא מובא ב-IPKat".
- **source_url:** https://ipkitten.blogspot.com/2008/01/m-systems-v-trek-2000-usb-sticks-get.html · https://www.bailii.org/ew/cases/EWHC/Patents/2008/102.html (חסום)

### 14. moderate — הציטוט על פרס IEEE נלקח מוויקי, לא מן הגוף המעניק
- **where:** `sections/12-ma-kiblu-hashlosha.json` body, פסקה שנייה
- **claim:** "**בלשון ויקי ההיסטוריה של הארגון**, החידושים של השלושה בעת עבודתם ב-M-Systems הם שהניעו את יצירת כונן ה-USB. מדיניות הפרס, כפי שהיא רשומה שם, מאפשרת הענקה ליחיד, לכמה זוכים או לצוות של שלושה לכל היותר."
- **evidence:** בדיקה היום בעמוד הגוף המעניק (IEEE Magnetics Society) מאשרת את **עצם הפרס והזוכים** מילה במילה: `"IEEE Reynold B. Johnson Information Storage Systems Award 2015 Dov Moran, Amir Ban, and Simon Litsyn"` — כלל 151 מתקיים לגבי העובדה. אבל **נוסח ההנמקה** ו**מדיניות הפרס** אינם מופיעים בעמוד הזה כלל (חיפוש אחר `"not more than three"` בעמוד המעניק מחזיר אפס תוצאות); שניהם מגיעים מ-ETHW, שהוא ויקי. הדף עצמו מודה בכך ("בלשון ויקי ההיסטוריה"), וזה לזכותו — אבל שתי הטענות המהותיות בפסקה, ובכללן ההנמקה שמייחסת לשלושה את יצירת כונן ה-USB, נשענות על ויקי בלבד.
- **תיקון מוצע:** או למצוא את נוסח ההנמקה באתר הפרס עצמו, או להוריד את ההנמקה ולהשאיר את מה שאומת: השם, השנה, שלושת הזוכים.
- **source_url:** https://ieeemagnetics.org/ieee-technical-field-award/ieee-reynold-b-johnson-information-storage-systems-award

### 15. moderate — השוואת המחירים מערבבת שני מטבעות ומשמיטה את מי שמדד
- **where:** `sections/11-ma-kara-ladisket.json` body, פסקה רביעית
- **claim:** "חבילה של עשרה דיסקטים במרכז טוקיו — פחות מ-15 מגה-בייט יחד — עלתה כשישה דולר, וכונן USB של 4 ג'יגה-בייט נמכר בקנדה בפחות מעשרים. פי כמאתיים ושבעים נפח, **בפחות מפי ארבעה מחיר**."
- **evidence:** CBC, מילה במילה: `"A four-gigabyte USB key generally retails for less than $20 in Canada. A 10-pack of Sony 3.5-inch floppy disks, which altogether total less than 15 megabytes of memory, sells in central Tokyo for about $6 US, **according to PC Magazine**."` המקור מסמן במפורש שאחד המחירים הוא **דולר אמריקאי** והשני **בקנדה** (כלומר דולר קנדי) — יחס ההמרה ב-2010 היה כ-1:1.03 אבל אלה עדיין שני מטבעות, והדף מוחק את ההבחנה ומחשב עליה יחס. בנוסף, הייחוס "according to PC Magazine" נשמט, כך שהמחיר בטוקיו מופיע כאילו CBC מדדה אותו. גם "פי כמאתיים ושבעים" נגזר מ"פחות מ-15 מגה-בייט" — חסם עליון — ולכן היחס האמיתי הוא **לפחות** 270, לא "כ-270".
- **תיקון מוצע:** לשמור על סימון המטבעות כבמקור, להוסיף "לפי PC Magazine, בציטוט CBC", ולכתוב "יותר מפי מאתיים ושבעים".
- **source_url:** https://www.cbc.ca/news/science/sony-to-pull-plug-on-floppy-disks-1.941854

### 16. moderate — "ביפן נמכרו 47 מיליון דיסקטים ב-2002": המקור אינו אומר "ביפן" במשפט הזה
- **where:** `sections/11-ma-kara-ladisket.json` body, פסקה שלישית · `fields.json` numbers[4] ו-numbers[5] (התוויות: "מכירות דיסקטים **ביפן**")
- **claim:** שני המספרים מיוחסים במפורש ליפן, גם בגוף הדף וגם בתוויות המספרים.
- **evidence:** CBC, מילה במילה: `"Floppy disks are still commonly used in Japan, where Sony has 70 per cent of the market share. Companies sold about 12 million floppy disks in 2009, although that's a steep decline from 2002, when 47 million disks were purchased."` המשפט שנושא את שני המספרים אינו מגביל אותם ליפן; ההגבלה מוסקת מן המשפט הקודם. ההיקש סביר, אבל ההבדל בין 47 מיליון ביפן ל-47 מיליון בעולם הוא סדר גודל, והתווית ב-`fields.json` מציגה אותו כאילו הוא מצוטט.
- **תיקון מוצע:** "לפי CBC, בהקשר של שוק הדיסקטים היפני, נמכרו 47 מיליון דיסקטים ב-2002 וכ-12 מיליון ב-2009" — או, אם רוצים לנקוב ביפן חד-משמעית, למצוא מקור שאומר זאת במשפט אחד.
- **source_url:** https://www.cbc.ca/news/science/sony-to-pull-plug-on-floppy-disks-1.941854

### 17. moderate — "לא נמדד מעולם": שלילה גורפת על מצב הידע בעולם, שנשענת על חיפוש שלנו
- **where:** `sections/13-bachazara-lamegera.json` body, פסקה שנייה
- **claim:** "ההסבר שחוזר ברשת — שהענן והטלפונים החליפו אותו — **לא נמדד מעולם**. חיפוש אחריו מעלה פורומים ופוסטים, ולא סקר, דוח או נתון שמראים תחלופה כזאת."
- **evidence:** המשפט השני הוא דיווח ישר על מה שהחיפוש העלה, והוא בסדר גמור. המשפט הראשון הוא טענה על העולם — שאיש מעולם לא מדד — ואין לה שום מקור. זו בדיוק ההמרה של "לא מצאנו" ל"אין", שכלל 161 נועד למנוע. הדף עושה את זה נכון במקום אחר ("לאירוע אין עד חיצוני… לא מצאתי אימות עצמאי"), ולכן חוסר העקביות בולט.
- **תיקון מוצע:** "לא מצאנו שנמדד" / "אין לנו מדידה שלו".
- **source_url:** — (אין; זו הנקודה)

### 18. minor — "ה-Zip Drive… שהוצג ב-1994… החזיק עד 750 מגה-בייט" מוצג בקול הדף
- **where:** `sections/02-ma-haya-bimkomo.json` body
- **claim:** הצירוף שנה+קיבולת נמסר כעובדה; רק **ההסבר לכישלון** מיוחס ל-IEEE ("IEEE Spectrum תולה זאת בין השאר בתחרות של דיסקים קשיחים…").
- **evidence:** IEEE Spectrum, מילה במילה: `"The Iomega Zip Drive, called a 'superfloppy' drive and introduced in 1994, could store up to 750 MB of data and was writable, but it never gained widespread popularity, partly due to competition from cheaper and higher-capacity hard drives."` כלומר הצירוף כולו הוא של IEEE. הצמדת "1994" ל-"750 מגה-בייט" חשודה בעיניי — לא סביר שדגם ההשקה החזיק 750 מגה-בייט — אבל **לא ניתן לאמת**: לא מצאתי בסבב הזה מקור ראשוני של Iomega לכרונולוגיית הדגמים, ואיני מנחש. מה שכן ניתן לומר: אם הצירוף שגוי, השגיאה היא של IEEE, והדף אימץ אותה לקולו שלו במקום לייחס אותה.
- **תיקון מוצע:** לייחס את כל המשפט ל-IEEE ("לפי IEEE Spectrum, ה-Zip Drive… הוצג ב-1994 והחזיק עד 750 מגה-בייט"), או לאמת את הצירוף במקור נפרד.
- **source_url:** https://spectrum.ieee.org/thumb-drive

### 19. minor — "בנובמבר 2000 הכריזה M-Systems על המוצר": המקור אומר "זמן קצר אחר כך"
- **where:** `sections/07-15-bedetsember-2000.json` body, פתיחה
- **claim:** תאריך חודש להכרזה.
- **evidence:** הטכניון, מילה במילה: `"The patent for the Disk On Key was approved on November 14, 2000, and shortly afterward, it was revealed to the public."` "shortly afterward" יכול להיות נובמבר ויכול להיות דצמבר; הדף בוחר. היקש סביר, אבל הוא נכתב כאילו המקור אמר אותו.
- **תיקון מוצע:** "זמן קצר אחרי אישור הפטנט ב-14 בנובמבר 2000 נחשף המוצר לציבור."
- **source_url:** https://www.technion.ac.il/en/blog/article/25-years-since-the-invention-that-changed-the-world-of-data-storage

### 20. minor — "תוקפו פג ב-5 באפריל 2019" נמסר כעובדה, והוא הנחה של Google Patents; ושני ה-reissue אינם מוזכרים
- **where:** `sections/06-ma-hapatent-amar.json` body
- **claim:** "הפטנט הוענק ב-14 בנובמבר 2000 ומספרו US6148354; תוקפו פג ב-5 באפריל 2019, עשרים שנה מיום ההגשה."
- **evidence:** בעמוד Google Patents התאריך הזה יושב בשורה שכותרתה `"Anticipated expiration"`, ובאותו עמוד עצמו רשום: `"The legal status is an assumption and is not a legal conclusion. Google has not performed a legal analysis and makes no representation as to the accuracy of the status listed."` בנוסף, אותו עמוד מראה שהפטנט **הונפק מחדש פעמיים** ב-12.1.2011: `USRE44641E1` ("USB flash memory device with integrated USB controller") ו-`USRE44653E1` ("USB flash memory device with integral memory technology driver"), שניהם עם אותו תאריך קדימות 1999-04-05. עובדה לא-טריוויאלית על מסמך שהדף מקדיש לו סעיף שלם.
- **תיקון מוצע:** "לפי Google Patents, תאריך הפקיעה הצפוי הוא 5.4.2019" — ולשקול שורה על שני ה-reissue מ-2011.
- **source_url:** https://patents.google.com/patent/US6148354A/en

### 21. minor — "ארבעה טוענים": המקור המרכזי של הדף מונה גם חמישי
- **where:** `sections/08` heading ("ארבעה טוענים לבכורה") · `sections/10` heading ("אותה שאלה, ארבע תשובות") · `sections/13` סיום · `fields.json` summary_short
- **claim:** מסגרת המספר ארבע היא השלד המבני של חצי מן הדף ושל שורת הסיום שלו.
- **evidence:** IEEE Spectrum, מילה במילה: `"Somewhat less credibly, inventors in Malaysia and China have also claimed to be the first to come up with the thumb drive."` כלומר אותו מקור שממנו הדף לוקח את ארבעת הטוענים מונה גם טוען מלזי. אפשר להצדיק את הסינון (המקור עצמו אומר "less credibly"), אבל הדף לא אומר שסינן.
- **תיקון מוצע:** שורה אחת: "IEEE מזכירה גם טוענים ממלזיה, ומסייגת אותם כפחות אמינים."
- **source_url:** https://spectrum.ieee.org/thumb-drive

### 22. minor — "בתי משפט בשלוש יבשות" סופר ערכאה שאינה בית משפט
- **where:** `sections/01-hamegera.json` body ("היא הגיעה לבתי משפט בשלוש יבשות, ולא הוכרעה עד היום")
- **claim:** שלוש יבשות של בתי משפט.
- **evidence:** ארבעת הפורומים בדף הם: בית המשפט העליון ובית המשפט לערעורים בסינגפור (אסיה), בית משפט בבריטניה (אירופה), ועדת הסחר הבין-לאומית האמריקאית (צפון אמריקה) והליך פטנטים בסין (אסיה). ה-ITC היא **ועדה מנהלית**, לא בית משפט, ומתן פטנט בסין אינו הליך שיפוטי. בתי משפט ממש היו בשתי יבשות.
- **תיקון מוצע:** "היא הגיעה לערכאות בשלוש יבשות" — מילה אחת פותרת.
- **source_url:** https://spectrum.ieee.org/thumb-drive

### 23. minor — `infobox.json` ריק, והדף מלא בעובדות בפורמט אינפובוקס
- **where:** `infobox.json` (`{"rows": []}`) · `canonical.json` infobox.rows
- **claim:** —
- **evidence:** לדף יש מספר פטנט, תאריך הגשה, תאריך הענקה, תאריך השקה, קיבולת השקה, מקום התכנון, מקום הייצור ושני פרסים — כולם מאומתים, כולם בעלי `source_url`, וכולם בדיוק החומר שהאינפובוקס נועד לו. אין ממצא עובדתי כאן, זו הערת שלמות.
- **source_url:** —

## Held (טענות שנבדקו והחזיקו)

- **שלושת הממציאים על הפטנט, בסדר הזה** — Google Patents, `"Inventor Amir Ban Dov Moran Oron Ogdan"`; אימות שני: IEEE Spectrum, `"This was granted to Amir Ban, Dov Moran, and Oron Ogdan in November 2000."`
- **בקשה 5.4.1999 · מספר בקשה 09/285,706 · הענקה 14.11.2000 · שם הפטנט** — Google Patents, `"Application number US09/285,706"`, `"Priority date … 1999-04-05"`, וכותרת `"Architecture for a universal serial bus-based PC flash disk"`.
- **הסבה לחברה באותו יום** — Google Patents legal events: `"1999-04-05 Assigned to M-SYSTEMS FLASH DISK PIONEERS LTD. … ASSIGNMENT OF ASSIGNORS INTEREST"`.
- **"לא כתוב בו גוף עם תקע משולב, ואין בו צורת מוצר" — החזיק בבדיקה עצמאית של המסמך עצמו.** תקפתי את זה ישירות: בטקסט התיאור המלא של US6148354 המילה `"plug"` מופיעה **אפס פעמים**, המילה `"housing"` אפס פעמים, והמסמך מתאר במפורש חיבור בכבל: `"Host platform 44 is connected to USB flash device 46 according to the present invention through a USB cable 48."` כלומר הקביעה של הדף נכונה **בלי להסתמך על בית המשפט כלל** — וזו גם הסיבה שאפיון בית המשפט (`"a method of building a cable-connected desktop storage device"`) מדויק.
- **פסקה 91 מילה במילה** — [2005] SGHC 90: `"The Lexar, Ban and TDK references do not disclose any device with an integrated plug, and this is not disputed"`. אומת בטקסט המלא.
- **"this court has concluded that the Patent is valid"** — [2005] SGHC 90 פסקה 131, מילה במילה. אומת.
- **דחיית הערעור ב-30.12.2005 בהוצאות** — [2005] SGCA 55, פסקה 1: `"We dismissed the appeal and now give the reasons for our decision."`
- **פסקה 29 — הדיסק-און-קי הושק אחרי ה-ThumbDrive, ואיש לא חלק על כך** — [2005] SGHC 90 מילה במילה: `"there did not appear to be any dispute that DOK and Diskey … were made, launched or sold after the launch of the ThumbDrive at the CeBIT 2000 exhibition in 2000."` הדף מביא זאת נאמנה, וזו נקודה שפועלת נגד הצד הישראלי — לזכות הדף שהיא בפנים.
- **הפער של עשרה חודשים** — אומת סופית היום מול המקור הראשוני, ופותר פריט שהיומן השאיר פתוח: [2005] SGCA 55 פסקה 2, `"On 21 February 2000, Trek filed an application for a Singapore patent"`. מול 5.4.1999 — עשרה חודשים וחצי. **התקפה 2 ב-ENGINE.md נכשלה; D1 עומד.**
- **אי-הזהות בין שני מסמכי הפטנט (D2)** — **התקפה 3, החזקה מכולן, נכשלה.** "the Ban patent" בפסק הדין הוא Singapore Patent Application No 200203303-3, `"derived from PCT application PCT/US00/07087"` — מספר אחר מזה שבדף. בדקתי את החוליה: WO2000060476A1 = PCT/US2000/007087, ממציאים Ban / Moran / Ogdan, נמחית מקורית M Systems Flash Disk Pionners Ltd, קדימות 1999-04-05. אותה משפחת פטנטים. הזיהוי של הדף **נכון** (ראה ממצא 12 על החוליה החסרה בטקסט).
- **פרס התרבות של קרן אדוארד ריין, 2012, לדב מורן, והנימוק** — אומת היום בכרונולוגיה הרשמית של הקרן, מילה במילה: `"Cultural Award Dov Moran How a Flat Computer Battery Led to Millions of Bytes on a Key Chain In recognition of the idea and invention of a small standardized and portable data memory stick, today known as USB-Stick or USB Flash Drive."` גם התיקון שהדף עושה — שזה **פרס התרבות** ולא פרס הטכנולוגיה — מאושש: פרס הטכנולוגיה של 2012 מופיע באותו עמוד על שם Bradford Parkinson על ה-GPS. כלל 151 מתקיים.
- **פרס ריינולד ב' ג'ונסון של IEEE, 2015, לשלושה** — אומת היום אצל הגוף המעניק, מילה במילה: `"IEEE Reynold B. Johnson Information Storage Systems Award 2015 Dov Moran, Amir Ban, and Simon Litsyn"`. גם התיקון של שם הפרס מול דף הטכניון מאושש. כלל 151 מתקיים.
- **"אין ראיה ישירה לירידה במכירות" + דירוג רמה 1 של מוזיאון המדיה המיושנת** — Engadget מילה במילה: `"The Museum of Obsolete Media still rates USB flash drives at a 1, indicating a low risk of obsolescence… But while there's no direct evidence of declining flash drive sales, they've fallen out of favor…"` **התקפה 4 ב-ENGINE.md נכשלה; A עומד.**
- **הדיסק-און-קי לא פתח את מות הדיסקט** — CBC מילה במילה: `"Apple stopped designing computers with standard floppy disk drives in 1998, and Dell followed suit in 2003."` והדף אומר זאת מפורשות: "הדיסק-און-קי הצטרף לכוחות שכבר פעלו, ולא פתח את המהלך." זו בדיוק ההימנעות מ"סלל את הדרך" שכלל 176 דורש, והיא נעשית ביוזמת הדף.
- **הודעת סוני, אפריל 2010, הפסקה במרץ 2011** — CBC מילה במילה: `"Sony has announced it will stop selling the 30-year-old storage format in Japan in March 2011 because of dwindling sales."` (הכתבה מתוארכת Apr 26, 2010.)
- **1.44 מגה-בייט לדיסקט** — IEEE מילה במילה: `"even double-sided, double-density disks could store only 1.44 MB of data."`
- **8 מגה-בייט בהשקה, 32 בפרימיום, 4 טרה-בייט היום** — הטכניון מילה במילה: `"The original storage capacity was 8MB for the basic model and up to 32MB for the premium version. Today, the maximum capacity for a USB drive of the same size is 4 terabytes."` עוגני שנה קיימים (כלל 138).
- **"פי 128" בתוך פחות משלוש שנים (8 מגה-בייט → ג'יגה-בייט אחד, נכון ל-2002)** — החישוב נכון, ועוגן השנה במקום.
- **הייצור בסין ובטאיוואן, וההפרדה מן המפעל בכפר סבא** — דוח ה-20-F של החברה עצמה, כמתועד ביומן. **התקפה 5 ב-ENGINE.md: לא נמצא שום מסמך שמראה ייצור דיסק-און-קי בכפר סבא. הסייג עומד.** (לא ניתן לאמת מעבר ליומן בסבב הזה — לא משכתי מחדש את ה-20-F.)
- **הציטוט של שמעון שמואלי מדצמבר 2022** — אומת בגוף התגובות תחת כתבת IEEE, מילה במילה: `"Too bad the author did not contact me (and I assume others) as the story of the invention/innovation could be even more interesting."` גם התאריך (16 Dec, 2022) תואם.
- **טענת IBM היא על "היבט" של המכשיר, ומבוססת על דוח פנימי חסוי** — IEEE מילה במילה: `"IBM has its own claim to the invention of an aspect of the device, based on a year-2000 confidential internal report written by one of its employees, Shimon Shmueli."` הדף מוסר את הסייג במדויק ואומר שאי אפשר לבדוק את הטענה לגופה.
- **כותרת המשנה של כתבת IEEE** — מילה במילה: `"Thumb drive, USB drive, memory stick: Whatever you call it, it's the brainchild of an unsung Singapore inventor"`. הדף מביא אותה במלואה ואומר במפורש שהיא מייחסת את ההמצאה לצד הסינגפורי. זו בחירה הגונה: הדף מציג את המקור העוין לצד הישראלי בלשונו החדה ביותר.
- **הסייג של הכתב על המצאות דיגיטליות** — הדף מסיים את סעיף 08 בו, וזה מדויק למקור: `"Seldom can inventions in digital technology be attributed to a single person or company…"`
- **"ניצחון מוסרי" ומיליוני התקנים בלי רישיון** — IEEE מילה במילה: `"But even the decision in Singapore was little more than a moral victory. By the late 2000s, millions of thumb drives had already been produced, by countless companies, without Trek's license."`
- **ה-ITC לא העניק לטרק הרבה** — IEEE מילה במילה: `"Tan also pursued, with little success, claims at the United States International Trade Commission against other companies, including Imation, IronKey, Patriot, and Verbatim."` הדף מייחס במפורש ("כך IEEE Spectrum").
- **תוצאת בריטניה** — שני דומיינים עצמאיים: IPKat, ו-IEEE (`"An appeals court in the United Kingdom, however, was not persuaded, and Trek lost its patent there in 2008."`). **התוצאה** עומדת; הציטוט השיפוטי הוא ממצא 13.
- **הסייג "כל ארבע הגרסאות הן מורן מספר על מורן"** — הדף כותב זאת במפורש: "לאירוע אין עד חיצוני. אין תיעוד בן-הזמן משנת 1998, אין רישום של הכנס, וכל ארבע הגרסאות הן מורן מספר על מורן." זה בדיוק מה שכלל 157 דורש מרגע שנשען על עדות עצמית מאוחרת, והדף עושה זאת בלי שביקשו ממנו.
- **גרסה ד' (וידאו הטכניון 2017) אינה בדף** — היומן סימן "לכותב: אל תשתמש בזה", והדף אכן אינו משתמש בה. ציות מלא.
- **גבול הגזרה של המעש** — סרקתי את כל שלושה-עשר הסקשנים, את `fields.json` ואת `canonical.json`: אין בשום מקום ערבוב בין הדיסק-און-קי כמוצר לבין תקן מחבר ה-USB של Intel. תקן ה-USB מוזכר רק כמפרט שהמוצר תואם לו, וזה נכון ונכון להיאמר.

## כלל 178 — מקורות בזהירות

`grep -Ei "haaretz|themarker|הארץ|דה.?מרקר"` על כל תיקיית `canonical/disk-on-key/` (כולל `canonical.json`, `fields.json`, כל הסקשנים ו-`ENGINE.md`) — **אפס תוצאות**. אף טענה בדף אינה נשענת על מקור מן הרשימה, לא לבדו ולא בכלל. היומן כן משתמש ב-TheMarker בנקודה אחת (סכום פרס אדוארד ריין), מסמן זאת מפורשות ככפוף לכלל 178, ומציין שדף הטכניון הוא המקור השני — והדף בסופו של דבר **לא כתב את הסכום בכלל**. זה יישום נקי של הכלל.

## חמש ההתקפות על משפט המנוע (ENGINE.md)

הופעלו בפועל, לא נסקרו.

1. **מסמך שיראה הכרעה גלובלית אחת** — לא נמצא. ההפך: סינגפור פסקה לטובת טרק בשתי ערכאות, בריטניה ביטלה את הפטנט של טרק, ה-ITC נתן לטרק מעט, וסין נתנה ל-Netac פטנט. **F עומד.**
2. **תאריך הגשה סינגפורי מוקדם מ-5.4.1999** — הותקף מול המקור הראשוני ונכשל: [2005] SGCA 55 §2 קובע 21.2.2000. **D1 עומד**, ובזכות ההתקפה הזאת נסגר פריט שהיומן השאיר פתוח.
3. **זהות מושא שני הפטנטים** — ההתקפה הכי מבטיחה, כי פסק הדין נוקב במספר מסמך אחר לגמרי. נכשלה: WO2000060476A1 קושר את PCT/US00/07087 לאותם שלושה ממציאים ולאותו תאריך קדימות, וקריאה עצמאית בטקסט של US6148354 מאשרת אפס אזכורי "plug" וחיבור מפורש "through a USB cable 48". **D2 עומד, ועומד חזק יותר משעמד לפני הבדיקה.**
4. **ראיה למכירות יורדות** — לא נמצאה, והמקור שהדף מצטט אומר במפורש שאין. **A עומד.**
5. **מסמך שיראה ייצור בכפר סבא** — לא נמצא. **הסייג בסעיף 07 עומד.**

**המסקנה על משפט המנוע:** חמשת רכיביו לא הופלו. הבעיות בדף אינן במשפט — הן בגוף.

## מה קרה בעולם בפועל (כלל 176)

**הדף עומד בכלל, אבל עם פער אחד שצריך להיאמר בקול.**

מה שהוכח בפועל: מסמך פטנט חי עם שלושה שמות ותאריכים מדויקים; מוצר פיזי שיוצר אצל
קבלני משנה בסין ובטאיוואן ונמכר לקהל הרחב בתאריך ידוע; קפיצת קיבולת מ-8 מגה-בייט
ל-4 טרה-בייט באותה צורת גוף; דיסקט שיצא משימוש בתאריכים מתועדים (אפל 1998, דל 2003,
סוני 2010/2011, 47→12 מיליון); שוק בהיקף 7 מיליארד דולר ב-2021; והתדיינות אמיתית
בערכאות של שלוש יבשות עם פסקי דין שאפשר לפתוח ולקרוא. **אין כאן שום "פתח פתח"
ושום "סלל את הדרך"** — ולזכות הדף ייאמר שהוא **מסרב** לטענה הזאת מפורשות: "הדיסק-און-קי
הצטרף לכוחות שכבר פעלו, ולא פתח את המהלך." זו שורה שרוב הדפים לא היו כותבים על עצמם.

**הפער:** כל מספרי ההשפעה בדף הם ברמת **הקטגוריה** — כונני הבזק בעולם, כל היצרנים יחד —
ולא ברמת **המוצר הישראלי**. אין בדף ולו מספר אחד על הדיסק-און-קי עצמו: כמה יחידות
נמכרו, איזו הכנסה, איזה נתח שוק. והמקור המרכזי של הדף אומר במפורש שהקטגוריה נשלטה
בידי אחרים: `"millions of thumb drives had already been produced, by countless companies, without Trek's license"`.
כלומר השרשרת רצה: פטנט ישראלי → קטגוריית מוצר → שינוי בעולם, כשהחוליה האמצעית —
מה שהמוצר **הזה** עשה בפועל — אינה נמדדת. ליומן יש הסבר טוב לכך: החוקר בדק כעשרה
אתרי מחקר-שוק ופסל את כולם כסותרים זה את זה בסדרי גודל. **התיקון אינו למצוא מספר,
אלא לומר את הפער.** משפט אחד בדף — "מספרי המכירות של הדיסק-און-קי עצמו לא נמצאו
במקור אמין; המספרים כאן הם של הקטגוריה כולה" — הופך חולשה ראייתית ליושרה, וזה
בדיוק מה שהדף כבר עושה יפה במקומות אחרים (הרגע, הדעיכה, הייצור).

## תקציב

23 ממצאים (6 must-fix · 11 moderate · 6 minor) · 34 טענות נבדקו · ~25 משיכות רשת.
**המסמכים הראשוניים ש"לא ניתן היה למשוך" — נמשכו:** שני פסקי הדין מ-elitigation.sg,
שהיומן רשם כ-`archive_failed` בלי שום snapshot ב-Wayback, נמשכו במלואם ב-curl עם
User-Agent של דפדפן ונקראו מילה במילה. משם באו חמישה ממצאים ושבעה פריטי Held.
**מה שלא ניתן לאמת ונרשם ככזה:** הטקסט הראשוני של פסק הדין הבריטי (BAILII חסום
ב-Anubis proof-of-work, CaseMine חסום, Wayback החזיר 429/503); כרונולוגיית דגמי
ה-Zip Drive של Iomega; דוח ה-20-F של M-Systems (לא נמשך מחדש בסבב הזה).
