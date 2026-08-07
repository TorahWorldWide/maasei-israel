# ביקורת מקורות — Maasei Israel

**תאריך הביקורת:** 2026-08-07 · **מקור הנתונים:** Supabase REST (`entries`, `status=approved`) · read-only, לא שונתה אף שורה.

---

## 1. סך הערכים המפורסמים

**207 ערכים** בסטטוס `approved` בטבלת `entries`.

## 2. הסכימה הנוכחית של המקורות

שני מנגנונים מקבילים, שניהם בטבלת `entries` (וזהה ב-`submissions`):

| שדה | טיפוס | תיאור |
|---|---|---|
| `source_url` | `text not null` | המקור הראשי — URL יחיד ברמת הערך |
| `source_label` | `text not null default ''` | תווית המקור הראשי |
| `source_label_en` | `text` | תרגום התווית |
| `citations` | `jsonb` (מערך) | מערך **סדור** של ציטוטים-הוכחה; נוסף אחרי ה-schema.sql המקורי |

צורת אובייקט Citation בתוך המערך (מוגדר ב-`src/lib/data.ts`):

```ts
interface Citation {
  quote: string;          // ציטוט מילולי מהמקור
  source_label: string;   // ייחוס
  source_url: string;     // ה-URL של המקור
  locator?: string;       // עמוד ב-PDF וכו'
  quote_en?: string;
  source_label_en?: string;
}
```

**מסקנה סכימתית: ריבוי מקורות סדורים לערך כבר נתמך** דרך `citations` (jsonb array; ה-UI ב-`CitationList.tsx` מרנדר את כולם לפי הסדר). **אין צורך במיגרציה.** 
הערות:
- בפועל כמעט תמיד `citations[i].source_url` משכפל את `source_url` הראשי — כלומר היכולת קיימת אך לא מנוצלת.
- 5 ערכים בכלל בלי מערך `citations` (רק `source_url` עליון): `3186a5e8`, `eef315da`, `8fcfea36`, `be2c23a1`, `a8f55761`.
- התפלגות מספר הציטוטים לערך: 0 ציטוטים × 5 ערכים, 1 ציטוטים × 106 ערכים, 2 ציטוטים × 78 ערכים, 3 ציטוטים × 16 ערכים, 4 ציטוטים × 2 ערכים.
- שדה `source_url` העליון הוא יחיד — כדאי שהצנרת תתייחס ל-`citations` כמקור האמת ול-`source_url` כ"מקור מוביל" בלבד.

## 3. ערכים שכל מקורותיהם ויקיפדיה (Wikipedia-only)

**131 מתוך 207 (63.3%)** — כל ה-URLים שלהם (source_url + citations) הם `*.wikipedia.org`.
מתוכם 3 עם שני ערכי ויקיפדיה שונים (עדיין Wikipedia-only).
בסך הכול 136 ערכים מזכירים ויקיפדיה איפשהו; רק 5 מהם משלבים אותה עם מקור לא-ויקיפדי.

## 4. ערכים עם מקור יחיד

**195 מתוך 207 (94.2%)** עם URL ייחודי אחד בלבד (אחרי איחוד source_url עם citations). רק 12 ערכים (5.8%) עם 2 מקורות; אף ערך עם 3+.

## 5. ערכים בלי מקור שמיש / נתוני מקור מתים

**0 ערכים** בלי URL שמיש (לכל הערכים יש לפחות URL http(s) תקין אחד; אין שדות ריקים או ג'אנק).
בדיקת חיוּת (curl, כל 79 ה-URLים הלא-ויקיפדיים): 74 החזירו 200/202; **5 החזירו 403** — ככל הנראה חסימת בוטים ולא דף מת (timesofisrael ×2, fiercebiotech, mobihealthnews, innovationisrael.org.il). כדאי אימות ידני/דפדפן:

- 403: https://innovationisrael.org.il/en/importWinner/515256162
- 403: https://www.fiercebiotech.com/medtech/zebra-medical-partners-to-bring-ai-based-image-analysis-to-google-cloud
- 403: https://www.mobihealthnews.com/news/new-app-called-voiceitt-helps-folks-non-standard-speech-communicate
- 403: https://www.timesofisrael.com/haifa-resident-regains-vision-after-getting-artificial-cornea-implant
- 403: https://www.timesofisrael.com/bodies-of-leader-of-tiny-turkish-jewish-community-and-wife-found-in-quake-ruins

אין אף ערך שמקורו היחיד הוא YouTube — קישורי YouTube מופיעים רק ב-`media_url` (מדיה, לא הוכחה).

## 6. טבלת הערכים הבעייתיים (הגרועים קודם)

### 6א. Wikipedia-only — 131 ערכים (הבעיה החמורה)

| # | id | כותרת | מקור(ות) נוכחיים |
|---|---|---|---|
| 1 | `55b97c24-b71b-4b5c-8aa4-70abb3f5258f` | ישראל הקימה ביפן את בית-החולים השדה הראשון של מדינה זרה אחרי הצונאמי | https://en.wikipedia.org/wiki/Minamisanriku |
| 2 | `2478ebc2-0b40-4fbe-b84b-d82fb16924da` | הברון רוטשילד תמך בהתיישבות היהודית בארץ והיה מרכזי בהקמת תעשיית היין | https://en.wikipedia.org/wiki/Edmond_James_de_Rothschild |
| 3 | `56652d75-b44c-4dbf-903a-57613ecb2280` | דורון אלמוג הקים כפר שיקומי בנגב על שם בנו ערן — 170 דיירים | https://he.wikipedia.org/wiki/%D7%A2%D7%93%D7%99_%D7%A0%D7%92%D7%91 |
| 4 | `3345051f-86fb-46b6-afdd-a1418535dbb9` | זכרון מנחם תומכת בילדים חולי סרטן — הוקמה על שם בנם של המייסדים | https://he.wikipedia.org/wiki/%D7%96%D7%9B%D7%A8%D7%95%D7%9F_%D7%9E%D7%A0%D7%97%D7%9D |
| 5 | `7a7b29cf-bbac-4282-9804-b9639960237d` | ידידים מפעילה כ-65 אלף מתנדבים לסיוע דחוף בדרכים 24 שעות ביממה | https://he.wikipedia.org/wiki/%D7%99%D7%93%D7%99%D7%93%D7%99%D7%9D_-_%D7%A1%D7%99%D7%95%D7%A2_%D7%91%D7%93%D7%A8%D7%9B%D7%99%D7%9D |
| 6 | `daf6f72c-809b-4255-a70a-fd405c252bd2` | בית איזי שפירא ברעננה מסייע לאנשים עם מוגבלות — כ-30 אלף איש בשנה | https://he.wikipedia.org/wiki/%D7%91%D7%99%D7%AA_%D7%90%D7%99%D7%96%D7%99_%D7%A9%D7%A4%D7%99%D7%A8%D7%90 |
| 7 | `75076aa3-5011-4f0c-9601-35038b85d238` | הרב ישראל סלנטר הורה ליהודים לאכול ביום כיפור במגפת הכולרה של 1848 | https://en.wikipedia.org/wiki/Israel_Salanter |
| 8 | `b4a5042d-635a-4704-adcf-0ea35193db13` | כנפיים של קרמבו מונתה יועצת מיוחדת לאו"ם — כמאה סניפים בהובלת בני נוער | https://en.wikipedia.org/wiki/Krembo_Wings |
| 9 | `c73a0339-e4f8-4872-99bd-f133e542ee70` | שלושה ישראלים פיתחו שיטה להוכיח זהות בלי לחשוף את הסוד עצמו | https://en.wikipedia.org/wiki/Feige%E2%80%93Fiat%E2%80%93Shamir_identification_scheme |
| 10 | `dc4981dc-e20c-4143-b4cf-ba7ad20c1b78` | מתנדבי זק"א נחלצים לזירות פיגוע ואסון ומאתרים את שרידי הנספים | https://en.wikipedia.org/wiki/ZAKA |
| 11 | `db664bcd-61f7-491c-bb18-e8d90f97c0a2` | עזר מציון מנהל את מאגר מח העצם היהודי הגדול בעולם ללא תשלום | https://en.wikipedia.org/wiki/Ezer_Mizion |
| 12 | `242965d3-518d-4df1-af36-81747020cbd2` | איחוד הצלה מגיע לנפגעים בתוך 90 שניות ומטפל בכל אדם בחינם | https://en.wikipedia.org/wiki/United_Hatzalah |
| 13 | `74f8c8ac-9530-47be-8ec7-5cb09cf7f01e` | יד שרה משאילה בחינם 244 אלף פריטי ציוד רפואי בשנה לחולים בבית | https://en.wikipedia.org/wiki/Yad_Sarah |
| 14 | `54218e51-c24c-4f1a-b5e3-5345619a6f2a` | אהוד שפירא בנה ממולקולות DNA את המחשב הקטן בעולם שמאבחן סרטן | https://en.wikipedia.org/wiki/Ehud_Shapiro |
| 15 | `1f8554c6-fb15-47cb-b355-36537deb3b74` | רוזלינד פרנקלין: תצלומי הרנטגן שלה הובילו לגילוי מבנה הדנ"א | https://en.wikipedia.org/wiki/Rosalind_Franklin |
| 16 | `94bc92de-0a39-4634-b815-3ba53fe0c873` | הרמב״ם מגדיר שמונה דרגות צדקה שבראשן הפיכת העני לעצמאי | https://en.wikipedia.org/wiki/Maimonides |
| 17 | `474e37c2-7779-4287-b986-33eced4592e4` | אמה לזרוס מסייעת לפליטים יהודים וכותבת את השיר החקוק בפסל החירות | https://en.wikipedia.org/wiki/Emma_Lazarus |
| 18 | `e29af2be-5294-4770-b7ac-226fb5abd5c9` | ליזה מייטנר מסרבת להצטרף לפרויקט מנהטן ולפתח את הפצצה | https://en.wikipedia.org/wiki/Lise_Meitner |
| 19 | `7e63386a-c08a-481e-a89f-d3edfbe436f2` | נתן שטראוס מממן חלב מפוסטר לילדים ומוריד את תמותת התינוקות באמריקה | https://en.wikipedia.org/wiki/Nathan_Straus |
| 20 | `81bfe740-07d5-4bea-860d-03cb8f27dc68` | דונה גרסיה מנדס נסי מקימה רשת מילוט שהצילה מאות אנוסים מהאינקוויזיציה | https://en.wikipedia.org/wiki/Do%C3%B1a_Gracia_Mendes_Nasi |
| 21 | `1f0d0dc0-8beb-4ae8-b21c-031792a4877f` | קומנדו ישראלי מחלץ מאה ושניים בני ערובה משדה התעופה באנטבה | https://en.wikipedia.org/wiki/Operation_Entebbe |
| 22 | `16526318-863d-4cc3-bf83-042d47399ecc` | חיים סלומון ממן את הקונגרס הקונטיננטלי במלחמת העצמאות האמריקנית | https://en.wikipedia.org/wiki/Haym_Salomon |
| 23 | `6dac60dc-f8a7-47ba-bd01-a57195283537` | חנה סנש צונחת לאירופה הכבושה כדי לסייע בהצלת יהודים מהשמדה | https://en.wikipedia.org/wiki/Hannah_Szenes |
| 24 | `6eb585f4-6e3a-4c15-b0de-ae1fa34e6899` | רות גרובר מלווה אלף פליטים מאיטליה לארצות הברית בשם ממשל רוזוולט | https://en.wikipedia.org/wiki/Ruth_Gruber |
| 25 | `f39625f1-c623-4f69-996d-a2984f5f7340` | הברון מוריס דה הירש מקים את חברת ההתיישבות היהודית ליהודי אירופה הנרדפים | https://en.wikipedia.org/wiki/Maurice_de_Hirsch |
| 26 | `8593bc30-c4fa-4e5a-9c67-3b0ca23ec0a4` | יהודה טורו בונה בניו אורלינס בית מחסה לעניים ומרפאה לחולי קדחת צהובה | https://en.wikipedia.org/wiki/Judah_Touro |
| 27 | `860f576d-01d3-4b2e-9885-4d9fb70c3a8e` | הרב אברהם יהושע השל צועד בסלמה לצד מרטין לותר קינג | https://en.wikipedia.org/wiki/Abraham_Joshua_Heschel |
| 28 | `3fe9d9f6-6f2c-4db2-87f6-cdb22092b9aa` | הרב אריה לוין מבקר את אסירי המחתרת בכלא שבמגרש הרוסים | https://en.wikipedia.org/wiki/Aryeh_Levin |
| 29 | `697d6579-e886-4c41-b640-4ac75ad28632` | HIAS, שהוקם למען פליטים יהודים, מסייע היום לפליטים מכל דת ולאום | https://en.wikipedia.org/wiki/HIAS |
| 30 | `9baef596-2c81-4e55-b3e4-fa3f6e896390` | האחות ליליאן וולד מייסדת את הסיעוד הקהילתי באמריקה ואת מרכז הנרי סטריט | https://en.wikipedia.org/wiki/Lillian_Wald |
| 31 | `9219266d-ea61-4772-814f-b76448f18fff` | הג'וינט פועל ביותר מ-70 מדינות ומסייע גם לקהילות לא-יהודיות באסונות | https://en.wikipedia.org/wiki/American_Jewish_Joint_Distribution_Committee |
| 32 | `f15631dd-5d8a-46be-8564-284a6b0b2419` | פול ברן, אחד משני ממציאי מיתוג המנות שבבסיס תקשורת המחשבים בעולם | https://en.wikipedia.org/wiki/Paul_Baran |
| 33 | `74cce16f-dfa0-4d4f-99e8-fcf8b0a83b45` | רשת אורט מכשירה צעירים למקצוע מאז 1880 ביותר ממאה מדינות | https://en.wikipedia.org/wiki/World_ORT |
| 34 | `b7ec9be8-b160-4736-bb9f-8360cf21dc88` | סידני פרבר מפתח את הכימותרפיה נגד לוקמיה בילדים ומקים את קרן ג'ימי | https://en.wikipedia.org/wiki/Sidney_Farber |
| 35 | `c068ebb0-aece-4eaf-97d8-5ca60421f835` | המתמטיקאי אברהם וולד מצמצם את הנזק למפציצי בעלות הברית בעזרת הטיית השורדים | https://en.wikipedia.org/wiki/Abraham_Wald |
| 36 | `8cef8fdf-85b3-4bd3-bd3a-f93914187cdd` | ג'וליוס רוזנוולד ובוקר ט' וושינגטון בונים כ-5,000 בתי ספר לילדים שחורים | https://en.wikipedia.org/wiki/Julius_Rosenwald |
| 37 | `d2254b50-8a53-4788-b40c-d91c6208fe29` | ברנרד לאון ממציא את הדפיברילטור בזרם ישר שמחזיר לב שנעצר לפעום | https://en.wikipedia.org/wiki/Bernard_Lown |
| 38 | `0ff2798c-9471-4568-a351-57f29b70137a` | אברהם יעקבי פותח את מרפאת הילדים הראשונה בארה"ב ומייסד את רפואת הילדים | https://en.wikipedia.org/wiki/Abraham_Jacobi |
| 39 | `020df887-c2f0-4210-8bd9-4239476bb7a5` | מיכאל היידלברגר מפתח חיסון לדלקת ריאות שנוסה בהצלחה על מתגייסי חיל-האוויר | https://en.wikipedia.org/wiki/Michael_Heidelberger |
| 40 | `203a9610-7ea1-4a0f-a5d0-f5f2b0755f98` | הפיזיקאי הישראלי משה פלדנקרייז מייסד שיטת תנועה המבוססת על קשר גוף-נפש | https://en.wikipedia.org/wiki/Moshe_Feldenkrais |
| 41 | `2036f527-7767-428d-80b3-8c018e3ba6e8` | גולדה מאיר מקימה את מש"ב, סוכנות ישראלית שמכשירה מדינות מתפתחות | https://en.wikipedia.org/wiki/MASHAV |
| 42 | `6728ce32-f168-4c99-940c-828b820dbb82` | יהודה פולקמן מגלה שגידולים סרטניים מגייסים כלי-דם ופותח דרך לתרופות חדשות | https://en.wikipedia.org/wiki/Judah_Folkman |
| 43 | `94ad6b8a-03ef-4f23-9e42-2d8ba012a5a4` | אהרן בק מייסד את הטיפול הקוגניטיבי-התנהגותי לדיכאון ולהפרעות חרדה | https://en.wikipedia.org/wiki/Aaron_Beck |
| 44 | `347192a7-eafd-402f-9216-fb7d27795bd2` | שחקנית הוליווד הדי לאמאר שותפה בהמצאת קפיצת-התדרים שבבסיס ה-Wi-Fi | https://en.wikipedia.org/wiki/Hedy_Lamarr |
| 45 | `01ee1f4f-946c-4017-8604-57cd31a326d9` | הנרייטה סאלד ייסדה את הדסה שהביאה רפואה ליהודים ולערבים בארץ | https://en.wikipedia.org/wiki/Henrietta_Szold |
| 46 | `b06d3492-f0a3-4a7c-9e34-ffe5697ba484` | אמיל ברלינר המציא את המיקרופון ואת תקליט הדיסק ששמרו את קול האדם | https://en.wikipedia.org/wiki/Emile_Berliner |
| 47 | `8d1899e7-5a98-48e4-ae1d-564a275fc5cc` | שמעון ויזנטל, ניצול שואה, הקדיש את חייו להביא פושעים נאצים למשפט | https://en.wikipedia.org/wiki/Simon_Wiesenthal |
| 48 | `2ce0b47f-7510-42ef-9022-0569ea8da348` | בלה שיק פיתח בדיקה שחשפה מי עלול לחלות בדיפתריה והצילה ילדים | https://en.wikipedia.org/wiki/B%C3%A9la_Schick<br>https://en.wikipedia.org/wiki/Schick_test |
| 49 | `ff387711-2fcc-48f0-a543-23b0d46c7a07` | אליעזר זמנהוף יצר את אספרנטו כדי שעמים שונים יבינו זה את זה | https://en.wikipedia.org/wiki/L._L._Zamenhof |
| 50 | `ca90fdb4-6025-4890-98aa-911713c5f0a3` | קזימיר פונק טבע את המושג ויטמין וזיהה שמחלות נגרמות ממחסור | https://en.wikipedia.org/wiki/Casimir_Funk |
| 51 | `fe3708df-0a6b-4ff4-9a93-5861da4f2926` | ולדמר האפקין היה הראשון שפיתח חיסונים נגד כולרה ודבר והציל חיים בהודו | https://en.wikipedia.org/wiki/Waldemar_Haffkine |
| 52 | `2fec3788-c71b-4605-99e2-63e7d3799785` | פול זול פיתח החייאה חשמלית ללב ונקרא אבי הטיפול הקרדיולוגי המודרני | https://en.wikipedia.org/wiki/Paul_Zoll |
| 53 | `0707cd3e-586c-4fe8-83d8-6706bebf4530` | חוקרי הטכניון פיתחו את אזילקט שמקל על חולי פרקינסון בעולם | https://en.wikipedia.org/wiki/Rasagiline |
| 54 | `7b8d69d9-cad6-4f0a-ba2f-ebd143133633` | פרוטליקס מגדלת בתאי גזר תרופה לחולי גושה — הראשונה מהצומח שאושרה ב-FDA | https://en.wikipedia.org/wiki/Protalix<br>https://en.wikipedia.org/wiki/Taliglucerase_alfa |
| 55 | `69b9d26c-e02c-4207-a5d5-12a61542154a` | יואב בנימיני ויוסף הוכברג פיתחו שיטה שמסננת תגליות שווא במדע | https://en.wikipedia.org/wiki/Yoav_Benjamini |
| 56 | `378c6e2a-26ff-42b3-bf15-626aaaeb150f` | זכרון מנחם מלווה ילדים חולי סרטן — פאות מתרומות שיער, הכול בחינם | https://en.wikipedia.org/wiki/Zichron_Menachem |
| 57 | `9838c3e9-9d08-4258-80b1-e28a17a1c707` | להקת שלווה של מוזיקאים עם מוגבלות עלתה על במת האירוויזיון בתל אביב | https://en.wikipedia.org/wiki/Shalva_Band |
| 58 | `10794a5a-9a6c-4d60-b5bb-a54f765729d4` | זליג אשחר פיתח תאי CAR-T שמלמדים את מערכת החיסון להשמיד סרטן | https://en.wikipedia.org/wiki/Zelig_Eshhar |
| 59 | `467cf9b1-25ee-4c9b-bb79-27a764830cf0` | מגן דוד אדום מפעיל את שירות הדם הלאומי ואת מוקד החירום 101 | https://en.wikipedia.org/wiki/Magen_David_Adom |
| 60 | `41f71ed3-5aae-4f2f-a35a-3cb64a9a1283` | עזר מציון מפעילה את מאגר מח העצם היהודי הגדול בעולם | https://en.wikipedia.org/wiki/Ezer_Mizion |
| 61 | `9cdfb538-73a8-4c98-b0f3-9c28ce1a5679` | יד שרה משאילה בחינם 244 אלף פריטי ציוד רפואי מדי שנה | https://en.wikipedia.org/wiki/Yad_Sarah |
| 62 | `9e97e78f-a6b4-41ed-82a2-c3ea776ed8b8` | משה מונטיפיורי יזם את משכנות שאננים, השכונה היהודית הראשונה מחוץ לחומות | https://en.wikipedia.org/wiki/Moses_Montefiore<br>https://he.wikipedia.org/wiki/%D7%9E%D7%A9%D7%9B%D7%A0%D7%95%D7%AA_%D7%A9%D7%90%D7%A0%D7%A0%D7%99%D7%9D |
| 63 | `b2dd29f1-f66a-4722-8007-b8019cd4c1e0` | פרופ' חוסאם חאיק, ערבי-ישראלי, המציא 'אף מלאכותי' שמאבחן מחלות מנשיפת האוויר | https://en.wikipedia.org/wiki/Hossam_Haick |
| 64 | `37961ec9-9ed1-43a0-bd51-8a447afaa3d6` | חברת אינסייטק הישראלית פיתחה טיפול באולטרסאונד ממוקד שהורס רקמה בלי חתך | https://en.wikipedia.org/wiki/Insightec |
| 65 | `3b162858-c1d5-4ab1-9953-0ad643089752` | גיל שוד ייסד את צ'ק פוינט — חברת אבטחת הסייבר הטהורה הגדולה בעולם | https://en.wikipedia.org/wiki/Gil_Shwed |
| 66 | `767f5172-cd50-43a6-8de8-a8eeb9444d60` | ארבעה ישראלים צעירים פיתחו את ICQ — תוכנת המסרים המיידיים הראשונה שחיברה מיליונים | https://en.wikipedia.org/wiki/ICQ |
| 67 | `013c0d90-ff65-4962-a25b-c40178778330` | חברת Watergen הישראלית התקינה מתקן להפקת מים מהאוויר בבית חולים לילדים בעזה | https://en.wikipedia.org/wiki/Watergen |
| 68 | `9c2cdce3-4b37-46ce-affc-89c7eb6501c8` | חברת Given Imaging הישראלית פיתחה גלולת מצלמה נבלעת לאבחון מערכת העיכול | https://en.wikipedia.org/wiki/Given_Imaging |
| 69 | `94c70fad-f0ec-43a2-91ce-3cc7a034a520` | מתנדבי זק״א מישראל יוצאים למשימות חילוץ והצלה באסונות ברחבי העולם | https://en.wikipedia.org/wiki/ZAKA |
| 70 | `21e70076-fe0a-4fba-98d3-0ad241ab03cb` | במבצע 'על כנפי נשרים' העלתה ישראל כ-49,000 מיהודי תימן אל הארץ | https://en.wikipedia.org/wiki/Operation_Magic_Carpet_(Yemen) |
| 71 | `77b0cf66-ea10-4c9f-a1b3-5ff1c995ccae` | מבצע שלמה העלה 14,325 יהודים אתיופים לישראל תוך 36 שעות | https://en.wikipedia.org/wiki/Operation_Solomon |
| 72 | `4c8b3ec1-2d85-4c52-9194-7491a81357b0` | יאנוש קורצ'אק סירב לנטוש את יתומיו וליווה אותם עד מחנה ההשמדה טרבלינקה | https://en.wikipedia.org/wiki/Janusz_Korczak |
| 73 | `72aceb04-28e5-4d9c-a891-9093b31fb488` | רחה פרייר הקימה את עליית הנוער והצילה 7,000 ילדים יהודים מגרמניה הנאצית | https://en.wikipedia.org/wiki/Recha_Freier |
| 74 | `82e7d021-9865-4b04-9c19-3db0c240dc3e` | איחוד הצלה מעניק סיוע רפואי מיידי בחינם לכל אדם בישראל | https://en.wikipedia.org/wiki/United_Hatzalah |
| 75 | `290291d4-16a4-4aeb-a8d6-6e3ad8d73d1f` | אבי נתן הישראלי סייע בהקלה על אסונות בחמש מדינות ברחבי העולם | https://en.wikipedia.org/wiki/Abie_Nathan |
| 76 | `14f7a83f-f48a-4947-9631-cf91e7a15088` | שישה רופאים ואחים ישראלים סייעו לנפגעי רעידת אדמה בפרו | https://en.wikipedia.org/wiki/IsraAID |
| 77 | `c0162231-8456-44b0-872a-2df5d7dee718` | ארגון ישראלי חילק אלפי ארוחות ל-35 אלף פליטי מלחמה בגאורגיה | https://en.wikipedia.org/wiki/IsraAID |
| 78 | `65705b8c-4137-4625-a687-f38b206d807a` | IsraAID סייע לפנות יותר מ-160 אזרחים אפגנים פגיעים מקאבול | https://en.wikipedia.org/wiki/IsraAID |
| 79 | `5aab0fea-7de9-453a-ab14-32366e7746ef` | IsraAID שלח 20 מומחי חילוץ וטראומה לרעידת האדמה במרכז איטליה | https://en.wikipedia.org/wiki/IsraAID |
| 80 | `d638148f-9bbd-492c-95ee-8d8038ce83de` | צוותי סיוע ישראליים סייעו בשיקום מיאנמר לאחר ציקלון קטלני | https://en.wikipedia.org/wiki/IsraAID |
| 81 | `57089af8-e03f-419f-b50f-0d90b013abb8` | שישה רופאים ומתנדבים ישראלים סייעו לנפגעי שני טייפונים בפיליפינים | https://en.wikipedia.org/wiki/IsraAID |
| 82 | `7413a27e-5c15-47b4-b816-41ef0453a5f2` | צוות IsraAID הישראלי סייע לשיקום מוזמביק לאחר ציקלון איידאי | https://en.wikipedia.org/wiki/IsraAID |
| 83 | `310fc0e4-0ff1-47b9-8af8-5a0aa6f43437` | ארגון איסראייד היה ארגון הסיוע הזר היחיד בזירת רעידת האדמה במרכז איטליה | https://en.wikipedia.org/wiki/IsraAID |
| 84 | `0f46ffe2-af84-461d-8ba4-b0fc6575261a` | ארגון הסיוע הישראלי איסראייד מספק תמיכה נפשית ומים נקיים לפליטי אוקראינה | https://en.wikipedia.org/wiki/IsraAID |
| 85 | `e6b2739c-ee38-4b8f-9cfe-5a6fecf129e6` | ארגון איסראייד מסייע לחלץ בבטחה יותר מ-160 אפגנים פגיעים מפני שלטון הטליבאן | https://en.wikipedia.org/wiki/IsraAID |
| 86 | `cddbf703-e9ad-4708-bb6b-db6891357f53` | ארגון איסראייד שולח צוות חילוץ ורפואה לחלץ ולטפל בפצועי רעידת האדמה בהאיטי | https://en.wikipedia.org/wiki/IsraAID |
| 87 | `a2185cf0-e522-449f-b982-ba358b8916b3` | פרנסואה אנגלר, שהסתתר כילד יהודי בשואה, ניבא את מנגנון היגס וזכה בנובל לפיזיקה | https://en.wikipedia.org/wiki/Fran%C3%A7ois_Englert |
| 88 | `72d79320-f74a-4ca4-9e81-a108b6096ebb` | מייקל בראון ויוסף גולדשטיין גילו את קולטן הכולסטרול וסללו את הדרך לתרופות הסטטינים | https://en.wikipedia.org/wiki/Joseph_L._Goldstein |
| 89 | `328c104b-9070-4eec-b65d-332eb9425df1` | ז'ורז' שרפק, ניצול מחנה הריכוז דכאו, המציא את גלאי החלקיקים הרב-חוטי וזכה בפרס נובל | https://en.wikipedia.org/wiki/Georges_Charpak |
| 90 | `72aa4514-eeaa-4c62-9c09-75cbd7af671b` | חברת AIVF הישראלית משפרת בעזרת בינה מלאכותית את סיכויי ההפריה החוץ-גופית | https://en.wikipedia.org/wiki/AIVF |
| 91 | `b67a063d-203a-4bb6-be7d-d84c40c91119` | דיוויד בולטימור גילה את אנזים השעתוק ההפוך שפתח דלת למחקר נגיפים וסרטן | https://en.wikipedia.org/wiki/David_Baltimore |
| 92 | `af0c1eaa-3e27-4d45-bcbb-ed0d6f78ebf1` | רוברט פורצגוט גילה שתחמוצת החנקן היא אות כימי חולף בתאי גוף היונקים | https://en.wikipedia.org/wiki/Robert_F._Furchgott |
| 93 | `c91de487-dcc3-4d8d-b19d-8fafe90311a9` | הרווי אלטר גילה שהצהבת שאחרי עירוי דם נגרמת מנגיף צהבת C | https://en.wikipedia.org/wiki/Harvey_J._Alter |
| 94 | `109ff1d4-81aa-4eb6-9c35-73aadb097b97` | חברת איידוק הישראלית פיתחה בינה מלאכותית שמזהה מצבי חירום בסריקות ומזרזת טיפול | https://en.wikipedia.org/wiki/Aidoc |
| 95 | `030d4af2-edab-4417-ae6b-47e0563e64e1` | ברוך בנאסראף גילה את הגנים המאפשרים למערכת החיסון להבחין בין עצמי לזר | https://en.wikipedia.org/wiki/Baruj_Benacerraf |
| 96 | `4016f69d-360f-42ad-bb6c-7b1adb651270` | סידני ברנר ביסס את תולעת הצ'-אלגנס כאורגניזם מודל וזכה בפרס נובל | https://en.wikipedia.org/wiki/Sydney_Brenner |
| 97 | `cc0852cd-4753-4019-9eb4-6084622d625e` | פול ברג זכה בפרס נובל לכימיה על מחקריו פורצי הדרך בחומצות הגרעין | https://en.wikipedia.org/wiki/Paul_Berg |
| 98 | `d1fcf2db-efd5-4bd6-bee8-fb5f4972f598` | יוליוס אקסלרוד חשף כיצד המוח משחרר וממחזר מוליכים עצביים וזכה בפרס נובל | https://en.wikipedia.org/wiki/Julius_Axelrod |
| 99 | `4b74f9e1-4d2b-470b-8a57-48f3a57f693f` | חברת UBQ הישראלית הופכת פסולת ביתית מעורבת לחומר תרמופלסטי מרוכב | https://en.wikipedia.org/wiki/UBQ_Materials |
| 100 | `ab27ca34-0b51-49a2-9e1c-e9a920bd56bf` | חברת אלף פארמס הישראלית מפתחת בשר מתורבת בתחום טכנולוגיית המזון | https://en.wikipedia.org/wiki/Aleph_Farms |
| 101 | `c1c3c223-5b90-4fab-8aed-9e0bd523973c` | לקט ישראל מציל עודפי מזון חקלאי ומחלק אותם לנזקקים בכל הארץ | https://en.wikipedia.org/wiki/Leket_Israel |
| 102 | `7b3aeee2-6c15-4fe9-bedf-ecbeba118d12` | לוי יששר בנה את אב-הטיפוס הראשון של דוד השמש הישראלי | https://en.wikipedia.org/wiki/Levi_Yissar |
| 103 | `8a38381b-4974-409f-bf9e-e7f8b646da89` | מירביליס הישראלית פיתחה את ICQ אחת מתוכנות המסרים הראשונות בעולם | https://en.wikipedia.org/wiki/ICQ |
| 104 | `559c40a5-efcb-47eb-967d-5812ce0a6c97` | אילון לינדנשטראוס זוכה במדליית פילדס, הישראלי הראשון שמנצח את הפרס | https://en.wikipedia.org/wiki/Elon_Lindenstrauss |
| 105 | `2ee61ed6-768f-4c92-9ef7-34e35bddcd97` | איזידור רבי גילה את תהודת הגרעין המגנטית שבבסיס בדיקת ה-MRI | https://en.wikipedia.org/wiki/Isidor_Isaac_Rabi |
| 106 | `fff8180f-f2d9-4c99-b94c-342e51da9654` | רוג'ר קורנברג פענח כיצד המידע הגנטי מועתק מ-DNA ל-RNA | https://en.wikipedia.org/wiki/Roger_D._Kornberg |
| 107 | `e54c9c3d-54e8-4c89-bb05-0b5ece2b2db1` | יעקב בקנשטיין — הפיזיקאי שגילה ראשון שלחורים שחורים יש אנטרופיה | https://en.wikipedia.org/wiki/Jacob_Bekenstein |
| 108 | `cb6d0545-a519-4ead-a914-11cbd2ff891f` | יובל נאמן מסווג את חלקיקי היסוד בשיטת השמיניות — קצין צה"ל שנעשה פיזיקאי | https://en.wikipedia.org/wiki/Yuval_Ne%27eman |
| 109 | `9aab6afc-94d1-4dc8-b1bc-e7769c645c65` | יקיר אהרונוב מתאר חלקיק טעון המושפע מפוטנציאל חשמלי גם ללא שדה | https://en.wikipedia.org/wiki/Aharonov%E2%80%93Bohm_effect |
| 110 | `49d1c1d3-af26-43af-ad54-551f9f250831` | רפאל משולם מבודד לראשונה את ה-THC ומניח יסוד לקנאביס הרפואי בעולם | https://en.wikipedia.org/wiki/Raphael_Mechoulam |
| 111 | `0acf6f46-d604-419a-8bed-93cf147d81ee` | יהושע אנגריסט מפתח שיטת ניסויים טבעיים לזיהוי קשרים סיבתיים בכלכלה | https://en.wikipedia.org/wiki/Joshua_Angrist |
| 112 | `55c7771e-3d56-4e79-a08b-70f102c2a5fe` | מנחם בגין חותם על הסכם השלום עם מצרים ומחזיר את חצי האי סיני | https://en.wikipedia.org/wiki/Menachem_Begin |
| 113 | `452cd129-6707-4961-8a08-6da81587c96f` | רוזלין ילו פיתחה את שיטת הרדיואימונואסיי וזכתה בנובל לרפואה 1977 | https://en.wikipedia.org/wiki/Rosalyn_Yalow |
| 114 | `93ab808f-80c6-434e-9062-543da00f0ef3` | אלברט סייבין פיתח את חיסון הפוליו הפומי שכמעט מיגר את המחלה | https://en.wikipedia.org/wiki/Albert_Sabin |
| 115 | `6dc855b1-a52d-42e1-a3a1-0da990bd3d12` | ריטה לוי-מונטלצ'יני גילתה את גורם גדילת העצב וזכתה בנובל לרפואה 1986 | https://en.wikipedia.org/wiki/Rita_Levi-Montalcini |
| 116 | `06b9e55e-906e-4af9-94b7-673103a2efcc` | ססר מילשטיין פיתח שיטה לייצור נוגדנים חד-שבטיים וזכה בנובל לרפואה 1984 | https://en.wikipedia.org/wiki/C%C3%A9sar_Milstein |
| 117 | `3bdccfc7-c5be-46b6-92f1-af9283950404` | גרטרוד אליון מפתחת את התרופה הראשונה ללוקמיה ותרופות נגד דחיית שתל | https://en.wikipedia.org/wiki/Gertrude_B._Elion |
| 118 | `6778161c-6262-4870-bdf4-e583645053d2` | ברוך בלומברג מזהה את נגיף צהבת B ומפתח חיסון ובדיקת אבחון | https://en.wikipedia.org/wiki/Baruch_Samuel_Blumberg |
| 119 | `c1848f94-e0cd-4c00-8df7-e5ea1db698ba` | סלמן וקסמן זוכה בנובל על הסטרפטומיצין — האנטיביוטיקה הראשונה שריפאה שחפת | https://en.wikipedia.org/wiki/Selman_Waksman |
| 120 | `1cb5ad54-7087-476b-8cf2-78284ca0dc07` | ש"י עגנון היה הסופר העברי הראשון שזכה בפרס נובל לספרות | https://en.wikipedia.org/wiki/Shmuel_Yosef_Agnon |
| 121 | `02d9750e-0e4a-49c4-a8a7-1b7380b8e600` | אריה ורשל ומייקל לויט זכו בנובל לכימיה על מודלים ממוחשבים למולקולות | https://en.wikipedia.org/wiki/Arieh_Warshel |
| 122 | `73312bf9-f3fc-4686-b704-d42220de7ce1` | פרופ' אמנון שעשוע ייסד את מובילאיי לזיהוי סכנות בכביש במצלמה | https://en.wikipedia.org/wiki/Mobileye |
| 123 | `7bac609a-7e76-46fa-91b5-d0b13004344c` | הפרופסורים קדר ורבינוביץ' מהאוניברסיטה העברית פיתחו את עגבניית השרי המסחרית | https://en.wikipedia.org/wiki/Cherry_tomato |
| 124 | `641a403c-114d-4bda-b447-c16f47af3235` | החובש הישראלי ברנרד בר-נתן המציא תחבושת חירום שעוצרת דימום — בחירת צבא ארה"ב | https://en.wikipedia.org/wiki/Emergency_Bandage |
| 125 | `70436895-6629-4572-99c4-460a944f6b31` | ישראלים מתקינים משאבות מים סולאריות בכפרים באפריקה — חמישה מיליון איש מקבלים מים נקיים | https://en.wikipedia.org/wiki/Innovation:_Africa |
| 126 | `295b3325-2db9-4284-b550-072b7b991d93` | דב מורן ממציא את כונן ה-USB — טכנולוגיה שמיליארד בני אדם משתמשים בה | https://en.wikipedia.org/wiki/Dov_Moran |
| 127 | `3186a5e8-62c1-41dc-b071-49a5a92a959e` | Waze — אפליקציית הניווט הישראלית החינמית | https://he.wikipedia.org/wiki/Waze |
| 128 | `eef315da-4cb0-4417-b8f5-62a09dbf7f4e` | רות הנדלר והשד התותב לנשים אחרי סרטן | https://en.wikipedia.org/wiki/Ruth_Handler |
| 129 | `8fcfea36-f680-4a08-8ff1-7a8005c0f7d8` | אלברט איינשטיין ותורת היחסות | https://he.wikipedia.org/wiki/%D7%90%D7%9C%D7%91%D7%A8%D7%98_%D7%90%D7%99%D7%99%D7%A0%D7%A9%D7%98%D7%99%D7%99%D7%9F |
| 130 | `be2c23a1-f2c4-472f-9201-beb8360cfdf9` | זק"א — מתנדבים שמצילים ומכבדים את המתים | https://he.wikipedia.org/wiki/%D7%96%D7%A7%22%D7%90 |
| 131 | `a8f55761-7678-4400-bf6c-33976755cabc` | יונאס סאלק ויתר על הפטנט לחיסון הפוליו | https://he.wikipedia.org/wiki/%D7%92%27%D7%95%D7%A0%D7%90%D7%A1_%D7%A1%D7%90%D7%9C%D7%A7 |

### 6ב. מקור יחיד שאינו ויקיפדיה — 67 ערכים (חלשים, אך פחות דחופים)

| # | id | כותרת | המקור היחיד |
|---|---|---|---|
| 1 | `928d9d1b-83a7-4704-a5a4-3e210ab61b13` | בית-החולים השדה של צה"ל בפיליפינים יילד תינוק שהוריו קראו לו ישראל | https://www.israelnationalnews.com/news/174053 |
| 2 | `a75f341d-c1e4-4366-a374-54de6121deb6` | צוות ישראלי חילץ ילדה בת 10 מהריסות רעידת האדמה בטורקיה 1999 | https://www.eng.buffalo.edu/mceer-reports/00/00-0001.pdf |
| 3 | `1d3bdd7b-00ea-4e83-9808-eb146fee1c90` | כיפת ברזל של דני גולד יירטה מעל 400 רקטות במבצע עמוד ענן | https://english.tau.ac.il/impact/mr_iron_dome |
| 4 | `c62a9a5d-9ba6-4308-b555-0dea855f8545` | האחים ביילסקי הקימו קהילה ביער והצילו יותר מ-1,200 יהודים | https://encyclopedia.ushmm.org/content/en/article/the-bielski-partisans |
| 5 | `be392166-e5ee-49c5-8745-e482650aae71` | מתנדבי צה"ל טיפלו בעשרות אלפי פליטים חולי כולרה בגבול רואנדה-זאיר | https://www.jta.org/archive/israeli-aid-in-rwanda-closes-but-jdc-still-treats-refugees |
| 6 | `18f951aa-720f-449b-8594-48a30ca60e3c` | צה"ל הקים בית חולים שדה לפליטים אלבנים שנמלטו מקוסובו | https://pubmed.ncbi.nlm.nih.gov/15310041 |
| 7 | `01ec7773-716e-438c-bfb9-34ab824a0146` | ישראל מקימה בית חולים שדה במערב אוקראינה ומטפלת בכ-6,000 חולים | https://www.jns.org/world/israel-packs-up-ukraine-field-hospital |
| 8 | `9933892c-a69a-4bef-b3ee-956046629df9` | אדיטל אלע הקימה חברה ישראלית שמייצרת חומרי בנייה דלי-פחמן ממינרלים ממוחזרים | https://innovationisrael.org.il/en/importWinner/515256162 |
| 9 | `7cd2068c-f103-41e7-9c10-92582902e330` | פרופ' מרסל מכלוף מהטכניון פיתחה ננו-חלקיקים שמכוונים תרופה ישירות לתאי הסרטן | https://ats.org/ats-news/nanoghosts-for-a-targeted-fight-against-cancer |
| 10 | `991fe9d2-2509-4182-bbf5-83496afe6add` | חברת טבל הישראלית פיתחה רובוטים מעופפים שקוטפים פרי ופותרים מחסור בעובדים | https://www.fruitnet.com/eurofruit/tevel-secures-funding-for-flying-robot-harvesters/271009.article |
| 11 | `5d6e1196-1eb2-4759-a8fa-de179b30a332` | רננה קרבס פיתחה בחברת אלגאינג צבעי טקסטיל לא רעילים מאצות | https://www.azom.com/article.aspx?ArticleID=21077 |
| 12 | `07de0588-5501-417a-a1d2-35005654f442` | חברת דיפדאב הישראלית מנגישה סרטים וסדרות בעשרות שפות באמצעות בינה מלאכותית | https://www.egassociation.org/industry-news/deepdub-unveils-first-ever-ai-dubbing-technology-with-precise-control-of-characters-accents |
| 13 | `c8143ea3-4b85-44d3-949e-f4e1e6cf077f` | חברת סוס הישראלית מצילה אפרוחים זכרים מהשמדה בתעשיית הביצים | https://www.grow-ny.com/wp-portfolio/soos-technology |
| 14 | `10dba8c5-fcbd-4a4e-a1ed-7ddd8fd8d65e` | בועז גאון מקים את וויסדו שמחבר אנשים במשבר ומפחית בדידות | https://www.cfhu.org/uncategorized/in-conversation-with-ido-aharoni-boaz-gaon-creator-of-the-social-connectivity-app-wisdo |
| 15 | `85517b53-db5e-49e2-aa67-22336e70c9e4` | אקונקריט הישראלית מפתחת בטון ימי שמשקם שוניות וחיים בים לאורך מבנים חופיים | https://nocamels.com/2021/02/san-diego-marine-system-econcrete |
| 16 | `b18b325d-d27b-45dd-a8cc-4ea413ac0897` | גרינאוניקס מגדלת בישראל צמח-על עתיר רכיבים תזונתיים במים ללא אדמה | https://www.foodnavigator-usa.com/Article/2023/12/20/Video-Green-Onyx-launches-its-vertically-farmed-freshwater-lentils-into-space |
| 17 | `f4f5b8ef-03f9-4822-a4fc-c99423b78b08` | דפנה ניסנבאום מקימה בישראל אריזות מתכלות לחלוטין שמחליפות פלסטיק חד-פעמי | https://collateralgood.eu/green-investments/tipa |
| 18 | `3d823ed5-0065-45ed-8396-12d2bf846ef3` | חברת אטלנטיום מחטאת מים באור על-סגול בלי כימיקלים ברחבי העולם | https://www.insatech.com/media/pchnipvx/atlantium_power___energy_and_heavy_industry_bu_e.pdf |
| 19 | `29b4dbb2-124c-4869-96ee-1d44614a6c31` | חברת אלאוס מפעילה בינה מלאכותית שמפחיתה דיכאון וחרדה בטיפול נפשי | https://www.jmir.org/2023/1/e46781/PDF |
| 20 | `64ae6718-f68e-4052-be29-a6d0a85b6891` | חברת סייקי פיתחה משאף ראשון בעולם למינון מדויק של קנאביס רפואי | https://www.newcannabisventures.com/the-syqe-medical-cannabis-inhaler-cleared-for-launch-by-teva-in-israel |
| 21 | `1fa763ff-53c7-479f-a226-62a00c96b88f` | חברת ארלי-סנס מנטרת חולים בלי מגע ומונעת נפילות בבית החולים | https://www.prnewswire.com/news-releases/earlysense-chair-sensor-receives-fda-clearance-265528791.html |
| 22 | `9643b4ef-0ba0-428d-b97e-537791a3c08f` | חברת זברה הישראלית הציעה ניתוח סריקות רפואיות בבינה מלאכותית בדולר אחד לסריקה | https://www.fiercebiotech.com/medtech/zebra-medical-partners-to-bring-ai-based-image-analysis-to-google-cloud |
| 23 | `2b669aca-e540-4d05-ad95-a7db8af7bfba` | חברת ווייסאיט הישראלית פיתחה אפליקציה שמאפשרת לאנשים עם דיבור לקוי לתקשר בקולם | https://www.mobihealthnews.com/news/new-app-called-voiceitt-helps-folks-non-standard-speech-communicate |
| 24 | `c8510771-7176-448d-94d9-84059eb45cd6` | חברת קורנאט הישראלית השתילה קרנית מלאכותית והחזירה ראייה לגבר עיוור בן 78 | https://www.timesofisrael.com/haifa-resident-regains-vision-after-getting-artificial-cornea-implant |
| 25 | `c8deae5e-dfdf-4779-9be7-439991feff1d` | חברת תרניקה הישראלית פיתחה צמיד שמקל על מיגרנה ללא תרופות לילדים ומבוגרים | https://www.clinicalpainadvisor.com/news/nerivio-device-cleared-for-pediatric-migraine-treatment |
| 26 | `43a5ef8d-3c8f-4ae8-98d3-2bef5266df14` | ביווייז מצילה מושבות דבורים מקריסה בכוורת רובוטית מבוססת בינה | https://www.jpost.com/business-and-innovation/tech-and-start-ups/article-702718 |
| 27 | `c12a78f5-7310-4d2b-b7ba-5ada4aa5c50a` | רדיפיין מיט מדפיסה נתחי בשר מהצומח בתלת-ממד שנחתכים כמו סטייק | https://thespoon.tech/redefine-meat-announces-distribution-of-3d-printed-meat-through-israeli-meat-distributor |
| 28 | `3426ff78-0de0-4bfe-af78-3f3262c2e2d8` | טבל אירובוטיקס קוטפת פרי ברחפנים אוטונומיים ופותרת מחסור בקוטפים | https://www.fruitnet.com/eurofruit/tevel-secures-funding-for-flying-robot-harvesters/271009.article |
| 29 | `b22e4c0d-4eb9-480f-96d4-2cb5b63c7225` | קרופ-אקס חוסכת ארבעים אחוז ממי ההשקיה עם חיישני קרקע חכמים | https://en.globes.co.il/en/article-farmers-blind-to-what-happens-under-the-soil-1001264173 |
| 30 | `328701dd-9f17-44a7-892b-e4ea01c53a30` | רמילק מייצרת חלבון חלב אמיתי בתסיסה בלי אף פרה אחת | https://www.greenqueen.com.hk/remilk-gad-dairies-precision-fermentation-israel-the-new-milk-whey-protein |
| 31 | `e49a5150-12ef-47d1-a52c-8898e9c45783` | רוברט לפקוביץ גילה את משפחת הקולטנים שעליה פועלות מחצית התרופות | https://www.nobelprize.org/prizes/chemistry/2012/lefkowitz/facts/ |
| 32 | `4ac630f1-f090-49cf-afbb-76d33da457e5` | וולטר קון פיתח את תורת פונקציונל הצפיפות המשמשת מדעני חומרים בעולם | https://www.nobelprize.org/prizes/chemistry/1998/kohn/facts/ |
| 33 | `c7275cf7-9fdf-478e-b7b0-39b65ec803c9` | רואלד הופמן ניצל מהנאצים במסתור והפך לזוכה פרס נובל לכימיה | https://www.nobelprize.org/prizes/chemistry/1981/hoffmann/facts/ |
| 34 | `b40d8374-7db9-435f-9c06-59dc72b3573c` | דרו וייסמן גילה כיצד לרכך את ה-mRNA ופתח את הדרך לחיסוני הקורונה | https://www.nobelprize.org/prizes/medicine/2023/weissman/facts/ |
| 35 | `8b4d2e86-7803-4120-844c-facc085223a6` | ג'יימס רותמן פיצח את מערכת ההובלה הזעירה בין תאי הגוף | https://www.nobelprize.org/prizes/medicine/2013/rothman/facts/ |
| 36 | `b134e17d-f39d-4d73-aaca-22120cab5e0a` | יואל מוקיר זכה בנובל לכלכלה על פענוח שורשי הצמיחה הכלכלית המתמשכת | https://www.nobelprize.org/prizes/economic-sciences/2025/press-release |
| 37 | `ff4313ea-e24a-4a94-9d04-679f12b34623` | אלי ויזל נשא עדות לשואה והפך את המאבק באדישות למאבק למען שלום | https://www.nobelprize.org/prizes/peace/1986/wiesel/facts/ |
| 38 | `8034d081-bd98-48d9-bbfd-6c91668915bd` | פאול ארליך פיתח נסיוב דם עם נוגדנים שנטרל את רעלן הדיפתריה | https://www.nobelprize.org/prizes/medicine/1908/ehrlich/facts/ |
| 39 | `b3178bb8-79ef-4f14-a948-f43b86af20c2` | ארתור קורנברג בודד את האנזים שמעתיק את ה-DNA של החיים | https://www.nobelprize.org/prizes/medicine/1959/kornberg/facts/ |
| 40 | `805ae241-ef79-4b51-b77e-f2d71f39bd10` | סלבדור לוריה הוכיח שחיידקים מתפתחים במוטציות — כמו כל יצור חי | https://www.nobelprize.org/prizes/medicine/1969/luria/facts/ |
| 41 | `de43ae51-d432-42b2-b414-329c010922e8` | פרנסואה זאקוב חשף כיצד גנים נדלקים ונכבים בתוך התא | https://www.nobelprize.org/prizes/medicine/1965/jacob/facts/ |
| 42 | `9846799f-9821-438b-8d56-321a98e49475` | מרשל נירנברג פיענח את הקוד הגנטי — השפה שבה DNA בונה כל חלבון | https://www.nobelprize.org/prizes/medicine/1968/nirenberg/facts/ |
| 43 | `7f2e9aab-1d66-4a36-9d05-78724250c730` | אוטו לוי הוכיח בניסוי לב-צפרדע שעצבים מדברים בשפה כימית | https://www.nobelprize.org/prizes/medicine/1936/loewi/facts/ |
| 44 | `7d16eeb5-7a61-4189-b9e0-acbb45d02020` | קונרד בלוך מפענח את מנגנון חילוף הכולסטרול וזוכה בפרס נובל לרפואה | https://www.nobelprize.org/prizes/medicine/1964/summary/ |
| 45 | `1261b8a1-55e1-4793-8167-8efd6bed3792` | ארנסט בוריס צ׳יין פיתח את הפניצילין לתרופה וזכה בפרס נובל לרפואה | https://www.nobelprize.org/prizes/medicine/1945/chain/facts/ |
| 46 | `b4a73c52-9660-4429-84ec-7ef1aa91a56d` | קרל לנדשטיינר גילה את סוגי הדם האנושיים וזכה בפרס נובל לרפואה | https://www.nobelprize.org/prizes/medicine/1930/landsteiner/facts/ |
| 47 | `d142bb87-2de2-4c8a-b7e8-466312ec8010` | אריק קנדל חשף כיצד המוח שומר זיכרונות וזכה בפרס נובל לרפואה | https://www.nobelprize.org/prizes/medicine/2000/kandel/facts/ |
| 48 | `36f4bd0c-3901-4f8d-80ee-0697a5bab8c8` | הפסיכולוג הישראלי דניאל כהנמן זכה בנובל לכלכלה על חקר קבלת ההחלטות | https://www.nobelprize.org/prizes/economic-sciences/2002/kahneman/facts/ |
| 49 | `fc854986-9a7f-44f4-a5a9-04ee356b5741` | האנטומולוג שלמה נברו פיתח שק אטום שמציל יבולי דגן במאה מדינות | http://www.thetower.org/7159-israeli-invention-saves-grain-and-by-putting-a-ziploc-on-it |
| 50 | `b468a1e2-f9e0-47f4-8f3b-a7760e778c6b` | מדעני מכון ויצמן פיתחו את קופקסון — תרופה ישראלית לטרשת נפוצה שאישרה ה-FDA | https://wis-wander.weizmann.ac.il/life-sciences/new-drug-multiple-sclerosis-approved-us-food-and-drug-administration |
| 51 | `a841f813-f715-463e-a21b-25a79e1cd087` | אמנון ששוע ועמיתיו פיתחו מצלמה לבישה שמקריאה טקסט לעיוורים ומזהה פנים | https://abilitymagazine.com/orcam-point-way |
| 52 | `1763d745-4bd0-4078-972e-d8baa50f27b8` | הישראלי רוברט אומן זכה בנובל על ניתוח סכסוך ושיתוף פעולה בתורת המשחקים | https://www.nobelprize.org/prizes/economic-sciences/2005/press-release/ |
| 53 | `4e3ddeb3-b7b2-4152-8a69-f6d80c45a8e2` | צ'חנובר והרשקו מהטכניון גילו את מנגנון פירוק החלבונים בתא — וזכו בפרס נובל | https://www.nobelprize.org/prizes/chemistry/2004/press-release/ |
| 54 | `988815b9-3564-4d60-9fcc-3f41bff6de29` | דן שכטמן גילה קריסטלים שנחשבו בלתי אפשריים — ושינה את תפיסת מדע החומרים | https://www.nobelprize.org/prizes/chemistry/2011/shechtman/facts/ |
| 55 | `e0e08e62-d737-4b08-b89c-86070a0af725` | צה"ל מקים בית חולים שדה בנפאל — ומטפל באלף וארבע מאות פצועים | https://www.jta.org/2015/05/10/israel/israel-closes-field-hospital-in-nepal |
| 56 | `9c987db2-706e-452a-956a-7148b901288f` | עדה יונת פיצחה את מבנה הריבוזום — ופתחה פתח לאנטיביוטיקות חדשות שמצילות חיים | https://www.nobelprize.org/prizes/chemistry/2009/yonath/facts/ |
| 57 | `f867ac24-5a87-47c7-8135-e71b4acc04d1` | ישראל פותחת שעריה לסורים פצועים — ארבעת אלפים אזרחים מחלימים בבתי החולים הישראליים | https://www.idf.il/en/mini-sites/wars-and-operations/operation-good-neighbor-idf-aid-to-syrians |
| 58 | `17f87f35-b83f-400c-bf3f-8752f52448e7` | קיבוץ ישראלי ממציא השקיה בטפטוף ועוזר לחקלאים ב-110 מדינות לגדל יותר ממים פחות | https://www.solutions-site.org/node/919 |
| 59 | `9bd005b9-c330-48f0-b59d-40d744780b3c` | הצבא הישראלי הקים בית חולים שדה בהאיטי — 89 שעות אחרי רעידת האדמה | https://pubmed.ncbi.nlm.nih.gov/20442270 |
| 60 | `63d62fcb-4b07-4ebc-815a-0846fc08bb18` | חיילי צה"ל חילצו 19 ניצולים מהריסות טורקיה — ילד בן עשר בין הניצולים | https://www.jpost.com/middle-east/article-731301 |
| 61 | `c1bab11d-1a73-40e9-ac6b-bad2ec1c478e` | גבריאל אידן ממציא גלולה עם מצלמה — מיליון וחצי בדיקות מעיים ב-75 מדינות | https://www.epo.org/en/news-events/european-inventor-award/meet-the-finalists/gavriel-iddan |
| 62 | `11d9733b-0b53-414a-82de-f9c86935a1b4` | ווטרג'ן הישראלית מפיקה מי שתייה מהאוויר לכפרים מרוחקים ולבתי חולים | https://www.bbc.com/news/business-57847654 |
| 63 | `8a0e4e88-cedb-44f1-af19-a4c6deee7fbe` | עמית גופר יצר שלד חיצוני רובוטי שמחזיר לנכי עמוד שדרה את ההליכה | https://www.theguardian.com/sustainable-business/2015/jun/02/the-bionic-suit-helping-wheelchair-users-get-back-on-their-feet |
| 64 | `676c6376-a249-445e-a303-4f90365945fc` | מתנדבי זאקה ולוחמי פיקוד העורף מגיעים לטורקיה — שלושה ימים בדרכים סבוכות | https://www.timesofisrael.com/bodies-of-leader-of-tiny-turkish-jewish-community-and-wife-found-in-quake-ruins |
| 65 | `f0ca86ec-0a88-4963-b340-ad2e4f790c2b` | צה"ל הקים בית-חולים שדה בטורקיה וחילץ פצועים מתחת להריסות | https://pmc.ncbi.nlm.nih.gov/articles/PMC10450639/ |
| 66 | `f7f31cc8-9485-4b44-af02-491a647dff07` | רופאים ישראלים מנתחים לבבות של ילדים מכל העולם — בחינם | https://press.un.org/en/2011/ecosoc6476.doc.htm |
| 67 | `cd441e22-4e56-482c-ae5f-a0be9a47a13f` | IsraAID — הארגון הישראלי שהגיע ראשון להאיטי אחרי רעידת האדמה | https://www.jpost.com/international/israeli-ngo-israaid-sends-emergency-response-team-to-haiti-676816 |

### 6ג. תקינים יחסית (2 מקורות, לא Wikipedia-only) — 9 ערכים

| id | כותרת | מקורות |
|---|---|---|
| `d7dbd456-b39e-4549-98a8-c5653bfbf02a` | איסראייד שלח לסרי לנקה צוות בן 14 שהקים מרפאה ומטבחים לניצולי הצונאמי | https://unwatch.org/issue-136-diplomatic-conference-will-vote-admitting-magen-david-adom-red-cross<br>https://reliefweb.int/report/sri-lanka/tsunami-crisis-relief-israeli-relief-team-14-arrives-sri-lanka |
| `5a7a40d4-95ac-493c-908c-c9aeac25c1fc` | ישראל שלחה 50 חיילים למקסיקו סיטי לסייע בחילוץ אחרי רעידת האדמה | https://www.jta.org/2017/09/20/israel/israel-to-send-search-and-rescue-team-to-mexico-in-wake-of-severe-earthquake<br>https://www.i24news.tv/en/news/israel/156567-170928-israeli-soldiers-return-home-after-grueling-mexico-quake-recovery-mission |
| `50fabcf3-eef9-4b4f-abd0-9886bc11b7db` | צוות חילוץ ישראלי הגיע ראשון לניירובי וחילץ שלושה לכודים מהריסות השגרירות | https://jewishvirtuallibrary.org/idf-terror-relief-efforts-in-kenya<br>https://2017-2021.state.gov/remembering-the-1998-embassy-bombings-2 |
| `4750f6c8-00de-444c-9734-855e66309a2c` | מרתה ויינשטוק-רוזין פיתחה באוניברסיטה העברית את אקסלון, תרופה לחולי אלצהיימר | https://www.lgcstandards.com/US/en/Resources/Articles/Pharma-roots-rivastigmine<br>https://en.wikipedia.org/wiki/Marta_Weinstock-Rosin |
| `f20cc45d-35f4-4fdd-89e0-6a6d6964c753` | בני הזוג ברוניצקי מיבנה מפעילים בקניה תחנת חשמל גיאותרמית של 150 מגהוואט | https://en.wikipedia.org/wiki/Olkaria_III_Geothermal_Power_Station<br>https://www.encyclopedia.com/books/politics-and-business-magazines/ormat-technologies-inc |
| `10da5666-5b73-4e50-b572-ac3a9e077c92` | שני אסירים נמלטו מאושוויץ וכתבו דוח שהזהיר את העולם מפני ההשמדה | https://www.fdrlibrary.org/vrba-wetzler-report<br>https://hmd.org.uk/resource/rudolf-vrba |
| `b13b8edb-2d39-4b54-992d-6c440e57a2c0` | סטנלי פרוזינר מגלה את הפריונים אף שרעיונו נחשב לכפירה מדעית | https://www.nobelprize.org/prizes/medicine/1997/summary/<br>https://en.wikipedia.org/wiki/Stanley_B._Prusiner |
| `aeeec254-f001-45b2-885d-d568327e54b7` | ג'ושוע לדרברג מגלה שחיידקים מחליפים גנים וזוכה בפרס נובל בגיל 33 | https://www.nobelprize.org/prizes/medicine/1958/summary/<br>https://en.wikipedia.org/wiki/Joshua_Lederberg |
| `8c54a9dc-ce5a-460b-bfc7-355051053a65` | גרטי קורי מגלה את מסלול המרת הגליקוגן וזוכה ראשונה בנשים בנובל לרפואה | https://www.nobelprize.org/prizes/medicine/1947/summary/<br>https://en.wikipedia.org/wiki/Gerty_Cori |

## 7. פילוח דומיינים (על פני כל ה-URLים הייחודיים לכל ערך)

| כמות | דומיין |
|---|---|
| 139 | wikipedia.org (all langs) |
| 25 | nobelprize.org |
| 3 | jta.org |
| 3 | jpost.com |
| 2 | pubmed.ncbi.nlm.nih.gov |
| 2 | fruitnet.com |
| 2 | timesofisrael.com |
| 1 | israelnationalnews.com |
| 1 | eng.buffalo.edu |
| 1 | english.tau.ac.il |
| 1 | unwatch.org |
| 1 | reliefweb.int |
| 1 | i24news.tv |
| 1 | jewishvirtuallibrary.org |
| 1 | 2017-2021.state.gov |
| 1 | lgcstandards.com |
| 1 | encyclopedia.com |
| 1 | fdrlibrary.org |
| 1 | hmd.org.uk |
| 1 | encyclopedia.ushmm.org |
| 1 | jns.org |
| 1 | innovationisrael.org.il |
| 1 | ats.org |
| 1 | azom.com |
| 1 | egassociation.org |
| 1 | grow-ny.com |
| 1 | cfhu.org |
| 1 | nocamels.com |
| 1 | foodnavigator-usa.com |
| 1 | collateralgood.eu |
| 1 | insatech.com |
| 1 | jmir.org |
| 1 | newcannabisventures.com |
| 1 | prnewswire.com |
| 1 | fiercebiotech.com |
| 1 | mobihealthnews.com |
| 1 | clinicalpainadvisor.com |
| 1 | thespoon.tech |
| 1 | en.globes.co.il |
| 1 | greenqueen.com.hk |
| 1 | thetower.org |
| 1 | wis-wander.weizmann.ac.il |
| 1 | abilitymagazine.com |
| 1 | idf.il |
| 1 | solutions-site.org |
| 1 | epo.org |
| 1 | bbc.com |
| 1 | theguardian.com |
| 1 | pmc.ncbi.nlm.nih.gov |
| 1 | press.un.org |

סה"כ 219 הפניות-מקור ייחודיות (לאחר דדופ בתוך כל ערך). ויקיפדיה = 139 (63%) — כמעט כולה he/en.wikipedia.org. nobelprize.org (25) הוא המקור האיכותי הנפוץ היחיד.

---

## שורה תחתונה

- 131/207 (63%) מפרים את הכלל "ויקיפדיה רק כמקור משני" — אין להם שום מקור אחר.
- 195/207 (94%) עם מקור יחיד — כמעט כל האתר עומד על רגל אחת לכל ערך.
- הסכימה כבר תומכת בריבוי מקורות סדורים (`citations` jsonb) — צנרת ההעשרה יכולה לכתוב ישר אליה, בלי מיגרציה. מומלץ: לכל ערך Wikipedia-only, לאתר מקור ראשוני/עיתונאי (למשל דרך ה-References של ערך הוויקיפדיה עצמו), להוסיף אותו כ-citation ראשון ולהעביר את הוויקיפדיה לסוף; ואז לעדכן את `source_url` הראשי למקור החזק.
