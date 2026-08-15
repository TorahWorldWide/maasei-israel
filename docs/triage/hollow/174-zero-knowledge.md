# 174 — שלושה ישראלים פיתחו שיטה להוכיח זהות בלי לחשוף את הסוד עצמו

**מזהה:** `c73a0339-e4f8-4872-99bd-f133e542ee70` · **נבדק:** 15.8.2026 · **פעולות רשת:** 15

**הפסק:** stands
**בשורה אחת:** המעש התממש בעולם בקטגוריה **"עבודה שפורסמה והשפיעה — עם שרשרת סיבתית מתועדת"**, ובצורה החזקה ביותר שקטגוריה זו יכולה לקבל: **שני תקנים רשמיים נוקבים בשם הבנייה הזאת בגוף התקן.** תקן בין-לאומי **ISO/IEC 9798-5:2009** — "אימות ישות: מנגנונים המשתמשים בטכניקות אפס-ידיעה" — קובע בסעיף 4 ש"מנגנונים אלה ממשים סכמות שמקורן ב-Fiat ו-Shamir", ותקן פדרלי אמריקני **NIST FIPS 204** (13.8.2024), תקן החתימה הדיגיטלית הפוסט-קוונטית, קובע ש"סכמת ML-DSA משתמשת בבנייה Fiat-Shamir With Aborts". **אבל — וזו הנקודה החדה שהדף חייב לדעת: שני התקנים נוקבים בשני שמות, לא בשלושה, ומצטטים את העבודה מ-1986, לא זו מ-1988.** הכותרת מדברת על שלושה ישראלים ועל 1988; מה שנכנס לתקנים הוא **פיאט ושמיר, 1986**. הסכמה בת שלושת השמות (Feige–Fiat–Shamir 1988) **כן** התממשה — 1,015 ציטוטים בספרות — אך היא לא זו שמופיעה בתקנים.

## מה קרה בעולם בפועל

צריך להפריד **שלוש** תרומות שהדף (וגם רוב הכתיבה הפופולרית) מכווץ לאחת:

**(א) הרעיון עצמו — הוכחת אפס-ידיעה — אינו שלהם.** המושג zero-knowledge proof הומצא בידי **Goldwasser, Micali & Rackoff** (STOC 1985 / SICOMP 1989). הדף לא טוען אחרת, אבל הציטוט הראשון שעליו ("Like all zero-knowledge proofs, it allows one party, the Prover, to prove to another party, the Verifier...") מתאר בדיוק את **תרומתם של השלושה ההם**, לא של שלושת הישראלים. זהו ציטוט הגדרה גנרי, וזו בדיוק הסיבה שהטריאז' סימן שהוא "רק מגדיר".

**(ב) העבודה מ-1986 — פיאט ושמיר, שניים.**
"How to Prove Yourself: Practical Solutions to Identification and Signature Problems" (CRYPTO '86). היא נתנה שני דברים: סכמת זיהוי מעשית מבוססת פירוק לגורמים, **ואת ההיוריסטיקה שהופכת כל פרוטוקול אינטראקטיבי לחתימה לא-אינטראקטיבית** (הטרנספורם המכונה Fiat-Shamir). **זו התרומה שהתממשה בברזל.** 4,929 ציטוטים.

**(ג) העבודה מ-1988 — פייגה, פיאט ושמיר, שלושה.**
"Zero-knowledge proofs of identity", *Journal of Cryptology*. היא הפכה את סכמת הזיהוי להוכחת אפס-ידיעה במובן החזק ובגרסה מקבילית. **זו העבודה שהדף מתאר, והיא אמנם עבודה שפורסמה והשפיעה** — 1,015 ציטוטים — **אבל היא לא זו שמצוטטת בתקנים.**

**ומה שהתממש בעולם, בשלוש שכבות של קושיוּת עולה:**

1. **תקן בין-לאומי שמממש את סכמת הזיהוי בשמה.** ISO/IEC 9798-5:2009, מהדורה שלישית, 15.12.2009. **זהו התקן שעוסק בדיוק בנושא הכותרת** — אימות ישות באמצעות טכניקות אפס-ידיעה — וסעיף 4 שלו, "Mechanisms based on identities", אומר במפורש שהמנגנונים מממשים את הסכמה של פיאט ושמיר, ומכנה אותה **FS**.
2. **תקן פדרלי אמריקני שבנוי על ההיוריסטיקה.** NIST FIPS 204, "Module-Lattice-Based Digital Signature Standard", פורסם 13.8.2024 — אחד משלושת תקני הקריפטוגרפיה הפוסט-קוונטית שלפיהם תיבנה תשתית החתימות של ממשלת ארה"ב. הוא בנוי על "Fiat-Shamir With Aborts", ומקדיש חצי עמוד להסברת "the Fiat-Shamir heuristic".
3. **מערכת חיה שרצה על זה מאז 2018.** מטבע הקריפטו Monero הפעיל את Bulletproofs — הוכחות אפס-ידיעה לא-אינטראקטיביות שנעשות לא-אינטראקטיביות **בדיוק בעזרת ההיוריסטיקה הזאת** — בעדכון הרשת של **18.10.2018**. זו לא הצעה ולא פיילוט: זה עדכון קונצנזוס בכוח בבלוקצ'יין ציבורי, ומאז כל עסקה במטבע הזה נושאת אותו.

## הראיות

### הראיה המכריעה מס' 1 — תקן בין-לאומי לאימות זהות באפס-ידיעה, שנוקב בשם הסכמה
- **ציטוט (מילה במילה, סעיף 4.1):** "NOTE        These mechanisms implement schemes due either to Fiat and Shamir [4] and denoted FS, or to Guillou and Quisquater [11] and denoted GQ1."
- **ציטוט (Scope, סעיף 1):** "This part of ISO/IEC 9798 specifies entity authentication mechanisms using zero-knowledge techniques: ⎯ mechanisms based on identities and providing unilateral authentication; ⎯ mechanisms based on integer factorization and providing unilateral authentication;"
- **ציטוט (עמוד השער):** "INTERNATIONAL STANDARD ISO/IEC 9798-5 Third edition 2009-12-15 — Information technology — Security techniques — Entity authentication — Part 5: Mechanisms using zero-knowledge techniques"
- **מקור:** ISO/IEC 9798-5:2009 — עותק תצוגה מוקדמת רשמי של iTeh/ISO: https://cdn.standards.iteh.ai/samples/50456/1be410dfedb64046a197e4fb90a0e05a/ISO-IEC-9798-5-2009.pdf · דף הקטלוג: https://www.iso.org/standard/50456.html
- **תאריך פרסום:** 15.12.2009 · **נמשך:** 15.8.2026 (PDF גולמי, הומר ב-pdftotext, אומת מילה במילה)
- **הערה — למה זו הראיה החזקה ביותר בתיק, וגם היכן היא נעצרת:**
  - **זה בדיוק המעש שעל הכותרת.** לא "קריפטוגרפיה בכלל" ולא "פרטיות בכלל", אלא **תקן בין-לאומי שכל נושאו הוא הוכחת זהות בטכניקת אפס-ידיעה**, ושמו של פיאט-שמיר כתוב בגופו כמנגנון שהוא מממש. בלשון התדריך: לא "סלל את הדרך", אלא **הדרך עצמה נסללה ונחתמה כתקן ISO.**
  - **מגבלה שיש לרשום:** התקן נוקב ב**"Fiat and Shamir"** — שניים. **השם Feige אינו מופיע בקובץ התצוגה המוקדמת כלל** (חיפשתי; אפס תוצאות). כלומר התקן מיישם את סכמת 1986, לא את גרסת 1988 בת שלושת המחברים.
  - **מגבלה נוספת:** קובץ התצוגה המוקדמת מכיל את עמודי הפתיחה ואת פרקים 1–4, **ולא את הביבליוגרפיה שבעמ' 52**. לכן לא יכולתי לאמת שההפניה `[4]` היא אכן ל-CRYPTO '86 (זה כמעט ודאי, אבל לא אומת). **אבן להפוך:** רכישת התקן המלא, או גישה מוסדית.
  - **ISO/IEC DIS 9798-5 החדש** (https://www.iso.org/standard/89516.html) בעבודה — כלומר התקן לא נזנח, הוא בעדכון.

### הראיה המכריעה מס' 2 — תקן פדרלי אמריקני משנת 2024 בנוי על הבנייה הזאת
- **ציטוט (מילה במילה, סעיף 3):** "ML-DSA is a digital signature scheme based on CRYSTALS-DILITHIUM [6]. It consists of three main algorithms: ML-DSA.KeyGen (Algorithm 1), ML-DSA.Sign (Algorithm 2), and ML-DSA.Verify (Algorithm 3). The ML-DSA scheme uses the Fiat-Shamir With Aborts construction [10, 11] and bears the most resemblance to the schemes proposed in [12, 13]."
- **ציטוט (סעיף 3.3, "ML-DSA Construction"):** "ML-DSA is a Schnorr-like signature with several optimizations. The Schnorr signature scheme applies the Fiat-Shamir heuristic to an interactive protocol between a verifier who knows 𝑔 (the generator of a group in which discrete logs are believed to be difficult) and the value 𝑦 = 𝑔𝑥 and a prover who knows 𝑔 and 𝑥. The interactive protocol, where the prover demonstrates knowledge of 𝑥 to the verifier, consists of three steps:"
- **ציטוט (סעיף 7, "Signing"):** "The rejection sampling loop follows the Fiat-Shamir With Aborts paradigm [10]"
- **ציטוט (עמוד השער):** "FIPS 204 Federal Information Processing Standards Publication — Module-Lattice-Based Digital Signature Standard ... Published August 13, 2024"
- **מקור:** National Institute of Standards and Technology, FIPS 204 — https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf (DOI: https://doi.org/10.6028/NIST.FIPS.204)
- **תאריך פרסום:** 13.8.2024 · **נמשך:** 15.8.2026 (PDF גולמי, 3.2MB, הומר ב-pdftotext, אומת מילה במילה)
- **הערה:** **המילה "Fiat" מופיעה בגוף התקן שש פעמים.** זהו התקן שעליו תיבנה מערכת החתימות של ממשלת ארה"ב בעידן הפוסט-קוונטי — כלומר הבנייה של 1986 לא רק שרדה ארבעים שנה, היא נבחרה לשמש **בסיס לתקן הדור הבא**.
  - **מגבלה מדויקת:** התקן מפנה ל-`[10] Lyubashevsky V (2009) Fiat-Shamir with aborts` ול-`[16] Kiltz, Lyubashevsky, Schaffner (2018) A concrete treatment of Fiat-Shamir signatures in the quantum random-oracle model` — כלומר הוא מצטט את **העבודות שהרחיבו** את הבנייה, ולא את מאמר 1986 עצמו. **השם מופיע; ההפניה הביבליוגרפית — לא.** זו הסתייגות אמיתית וצריך לרשום אותה. (מנגד: תקנים בדרך כלל מפנים למקור הטכני הישיר שממנו נלקח האלגוריתם, לא לאב הקדמון; והשימוש בשם כשם קנוני של הבנייה הוא עצמו עדות להשפעה.)

### הראיה מס' 3 — מערכת חיה: Monero הפעיל Bulletproofs ב-18.10.2018
- **ציטוט (הודעת השחרור, מילה במילה):** "This is the v0.13.0 release of the Monero software. This major release is due to the October 18th network update, which in turn enabled Bulletproofs for reduced transaction sizes, sets the ringsize globally to 11 for uniformity of transactions, updated the PoW algorithm to CNv2, and finally sets the max transaction size at half of the penalty free block size."
- **מקור:** getmonero.org, "Monero 0.13.0 'Beryllium Bullet' Release", Posted by: Riccardo Spagni (fluffypony) — https://www.getmonero.org/2018/10/11/monero-0.13.0-released.html
- **תאריך פרסום:** 11.10.2018 (העדכון עצמו: 18.10.2018) · **נמשך:** 15.8.2026 (HTML גולמי, אומת מילה במילה)
- **החוליה שמחברת את Bulletproofs להיוריסטיקה — מהמאמר המקורי, מילה במילה:**
  - "We present Bulletproofs, a new zero-knowledge argument of knowledge system, to prove that a secret committed value lies in a given interval. Bulletproofs do not require a trusted setup. They rely only on the discrete logarithm assumption, and are made non-interactive using the Fiat-Shamir heuristic."
  - כותרת סעיף 4.4 בגוף המאמר: "4.4   Non-Interactive Proof through Fiat-Shamir"
  - "The verifier is a public coin verifier, as all the honest verifier's messages are random elements from Z‹p . We can therefore convert the protocol into a non-interactive protocol that is secure and full zero-knowledge in the random oracle model using the Fiat-Shamir transform [BR93]."
- **מקור:** Bünz, Bootle, Boneh, Poelstra, Wuille, Maxwell, "Bulletproofs: Short Proofs for Confidential Transactions and More", IACR ePrint 2017/1066 (גם IEEE S&P 2018) — https://eprint.iacr.org/2017/1066.pdf
- **תאריך פרסום:** 2017 (מעודכן) · **נמשך:** 15.8.2026 (PDF גולמי, אומת מילה במילה; "Fiat" מופיע 11 פעמים)
- **הערה — יש כאן חוליה חזקה ופגם קטן, ושניהם צריכים להיאמר:**
  - **החזק:** זו שרשרת סיבתית שלמה משיטה למערכת: מאמר → מימוש → ביקורת אבטחה חיצונית → עדכון קונצנזוס בתאריך נקוב → מיליוני עסקאות מאז. **מכשיר שנבנה והופעל**, בלשון התדריך.
  - **הפגם:** מחברי Bulletproofs נוקבים בשם **"Fiat-Shamir"** לאורך המאמר, אבל ההפניה שהם נותנים במקום הקריטי היא **[BR93]** (Bellare–Rogaway, מודל האורקל האקראי) — **לא [FS86]**. כלומר גם כאן: **השם נשאר, ההפניה נודדת.** זו תופעה שחוזרת בכל המקורות בתיק הזה, והיא מספרת משהו אמיתי: הבנייה הפכה לשם עצם כללי בתחום, כמו "אלגוריתם דייקסטרה". זו עדות להשפעה עמוקה **ובו בזמן** מקשה על ציטוט שרשרת ביבליוגרפית ישירה.
  - **⚠️ אישוש שלא אומת גולמית:** ביקורת האבטחה של Quarkslab (22.10.2018) מתארת: "Three senior engineers reviewed Monero's implementation of Bulletproof, a new non-interactive zero-knowledge proof protocol." — **הובא מתקציר מנוע חיפוש בלבד**, לא מ-HTML גולמי (נגמר התקציב). פסול לציטוט על הדף עד אימות. כתובת: https://blog.quarkslab.com/security-audit-of-monero-bulletproofs.html

### מדד ההשפעה: 4,929 ציטוטים למאמר 1986, 1,015 למאמר 1988
- **ציטוט (התשובה הגולמית של ה-API, מאמר 1986):** `{"paperId": "b9046d002da153a6fe9b06d469da4efffdfcb9c6", "externalIds": {"DBLP": "conf/crypto/FiatS86", "MAG": "1589034595", "DOI": "10.1007/3-540-47721-7_12", "CorpusId": 4838652}, "title": "How to Prove Yourself: Practical Solutions to Identification and Signature Problems", "venue": "Annual International Cryptology Conference", "year": 1986, "citationCount": 4929, "authors": [{"authorId": "1742404", "name": "A. Fiat"}, {"authorId": "1706216", "name": "A. Shamir"}]}`
- **ציטוט (התשובה הגולמית של ה-API, מאמר 1988):** `{"paperId": "f982d95a9177088bb7cc3d0cccf06187251457ce", "externalIds": {"MAG": "2152005134", "DBLP": "journals/joc/FeigeFS88", "DOI": "10.1007/BF02351717", "CorpusId": 2950602}, "title": "Zero-knowledge proofs of identity", "venue": "Journal of Cryptology", "year": 1987, "citationCount": 1015, "authors": [{"authorId": "1684495", "name": "U. Feige"}, {"authorId": "1742404", "name": "A. Fiat"}, {"authorId": "1706216", "name": "A. Shamir"}]}`
- **מקור:** Semantic Scholar Graph API (Allen Institute for AI) — `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/3-540-47721-7_12` · `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/BF02351717`
- **תאריך פרסום:** 1986 / 1988 · **נמשך:** 15.8.2026 (JSON גולמי משתי שאילתות נפרדות)
- **הערה:**
  - **שני המאמרים חוצים בקלות את סף "עבודה שפורסמה והשפיעה".** 4,929 ציטוטים הוא מספר יוצא דופן גם בקנה מידה של קריפטוגרפיה; 1,015 הוא מספר חזק מאוד לכשעצמו.
  - **⚠️ סתירה קטנה בתאריך:** Semantic Scholar רושם `"year": 1987` למאמר של פייגה-פיאט-שמיר, אבל מפתח ה-DBLP שלו הוא `journals/joc/FeigeFS88` והוא הופיע ב-*Journal of Cryptology* כרך 1 חוברת 2 — **1988**. ההסבר: הגרסה הראשונה הוצגה ב-STOC 1987, וגרסת כתב העת היא 1988. **השנה 1988 שעל הדף נכונה** לגרסה שהדף מתאר.

### שרשרת אפס-ידיעה שכן נפרסה בעולם — אבל היא לא עוברת דרכם, וחשוב לומר זאת
- **ציטוט (הכרזת ההשקה, מילה במילה):** "The Zcash blockchain is live! We released the genesis block this morning, and people all around our planet have begun mining and transacting on it." · "This is the first protocol of its kind. It is the product of years of scientific research, advanced engineering, and diligent security work."
- **מקור:** Zooko Wilcox, "Zcash begins", Electric Coin Company — https://electriccoin.co/blog/zcash-begins/
- **תאריך פרסום:** 28.10.2016 · **נמשך:** 15.8.2026 (HTML גולמי, אומת מילה במילה)
- **⚠️ הערה קריטית — ממצא שלילי, ואני מדגיש אותו כדי שלא ייעשה בו שימוש שגוי:** משכתי את **מפרט הפרוטוקול הרשמי של Zcash** (`https://zips.z.cash/protocol/protocol.pdf`, 920,358 תווי טקסט לאחר המרה) וחיפשתי בו. **המילים "Fiat" ו-"Shamir" מופיעות בו אפס פעמים.** מערכות ההוכחה של Zcash הן BCTV14, Groth16 ו-Halo 2, וסעיף Halo 2 במפרט מפנה החוצה למסמך אחר ואינו מפרט. **מסקנה: אסור לתלות את Zcash בשלושת הישראלים.** Zcash הוא צאצא של הוכחות אפס-ידיעה במובן של Goldwasser–Micali–Rackoff, לא של סכמת הזיהוי או של הטרנספורם. הבאתי אותו כאן **רק כדי לסמן את הגבול** — זו בדיוק הטעות שהתדריך נועד למנוע.

## הפגם שבדף עצמו — סעיף נפרד

**זהו הדף עם הבעיה החמורה ביותר במקורות מכל אלה שבדקתי, ולא בגלל תוכן שגוי אלא בגלל שהמקור היחיד שלו אינו מקור.**

1. **הציטוט השני קטוע באמצע משפט, וקטיעתו משנה את המשמעות.** הדף מצטט: `"is a type of parallel zero-knowledge proof developed by Uriel Feige"`. משכתי את הטקסט הגולמי של הערך ומצאתי שהמשפט המלא הוא:
   - **ציטוט (מילה במילה, ויקיטקסט גולמי):** `In [[cryptography]], the '''Feige–Fiat–Shamir identification scheme''' is a type of parallel [[zero-knowledge proof]] developed by [[Uriel Feige]], [[Amos Fiat]], and [[Adi Shamir]] in 1988.`
   - **מקור:** https://en.wikipedia.org/w/index.php?title=Feige%E2%80%93Fiat%E2%80%93Shamir_identification_scheme&action=raw · **נמשך:** 15.8.2026
   - **כלומר:** הקטיעה נעצרה **בדיוק** אחרי השם הראשון והשמיטה את שני האחרים ואת השנה. הדף עצמו סותר את כותרתו ("שלושה ישראלים") בגוף הציטוט שהוא מביא. **זה פגם טכני, לא פגם עובדתי** — העובדה שעל הכותרת נכונה, והציטוט שמאחוריה פשוט חתוך לרעתה.
2. **⚠️ והחמור באמת: הערך בוויקיפדיה מסומן זה 12 שנה כערך ללא מקורות כלל.** השורה הראשונה בקוד המקור של הערך היא:
   - **ציטוט (מילה במילה):** `{{no footnotes|date=January 2014}}`
   - **המשמעות:** בוויקיפדיה עצמה סימנו את הערך הזה בינואר 2014 כערך **חסר הערות שוליים** — כלומר אין בו ולו מקור אחד. **המקור היחיד של הדף במאסעי הוא ערך שאין לו מקורות.** לפי כלל 2 בתדריך ויקיפדיה אינה מקור גם במקרה הטוב; כאן היא אפילו לא מפת דרכים, כי אין לאן להפנות.
3. **שני הציטוטים רק מגדירים — הטריאז' צדק לחלוטין.** אחד מהם ("Like all zero-knowledge proofs...") מגדיר בכלל את **הקטגוריה** ולא את הסכמה, כלומר הוא מתאר את תרומתם של Goldwasser–Micali–Rackoff.
4. **התמונה היא של אדי שמיר בלבד** (`Adi_Shamir_Royal_Society.jpg`) בדף שכותרתו "שלושה ישראלים". הטיה חזותית קלה, שווה ציון.
5. **הטענה "זהו אחד היסודות של הגנת הפרטיות במחשוב המודרני" — נכונה, אבל בדף היא חסרת מקור לחלוטין.** אחרי המחקר הזה יש לה שני מקורות ראשוניים מסדר ראשון (ISO/IEC 9798-5, FIPS 204), ואין שום סיבה שתישאר טענה יתומה.

## מה שחיפשתי ולא מצאתי

- **הפניה ביבליוגרפית ישירה למאמר 1986 בתוך תקן — לא נמצאה, בשני התקנים, מסיבות שונות.** ב-FIPS 204 השם מופיע אך ההפניות הן ל-Lyubashevsky 2009/2012 ול-Kiltz et al. 2018. ב-ISO/IEC 9798-5 קיימת הפניה מפורשת `[4]` **בדיוק במקום הנכון**, אבל **הביבליוגרפיה (עמ' 52) אינה כלולה בקובץ התצוגה המוקדמת החינמי.** זו האבן החשובה ביותר שנשארה להפוך בתיק הזה, והיא זולה: **התקן המלא ISO/IEC 9798-5:2009, עמ' 52, הפניה [4].** אם היא ל-CRYPTO '86 — ואין לי ספק שכן — יש כאן שרשרת ביבליוגרפית מושלמת מהמאמר הישראלי אל תקן ISO חי.
- **השם "Feige" בתקנים — אפס תוצאות.** חיפשתי `Feige` בטקסט המלא של FIPS 204 (175KB) ובקובץ ISO/IEC 9798-5 (46KB). לא מופיע באף אחד מהם. **הסכמה בת שלושת השמות אינה מתועדת כמתוקננת בשום מקום שהגעתי אליו.**
- **Zcash — שרשרת שנבדקה ונפסלה.** מפרט הפרוטוקול המלא (920KB טקסט) — אפס אזכורים ל-Fiat או Shamir. ראה למעלה. **אבן שנותרה:** הספר `[Zcash-halo2]`, שאליו המפרט מפנה בסעיף 5.4.10.3 — סביר מאוד שהוא כן נוקב ב-Fiat-Shamir (Halo 2 הוא פרוטוקול אינטראקטיבי שהופך ללא-אינטראקטיבי בדיוק כך), ולא הספקתי לבדוק. אם ייבדק ויימצא, זו חוליה נוספת ל**מערכת חיה** נוספת.
- **פרס גדל 1993 (Goldwasser, Micali, Rackoff) — לא הצלחתי להביא מקור רשמי בתקציב.** `https://sigact.org/prizes/godel/1993.html` ו-`https://sigact.org/prizes/godel.html` — **שניהם החזירו דף 404 של SIGACT.** `https://eatcs.org/index.php/goedel-prize` — **כשל SSL (curl exit 60).** לא הוספתי ציטוט שאיני יכול לאמת. **הערה מהותית: הפרס הזה גם ממילא שייך לשלושה אחרים** (גולדווסר, מיקאלי, רקוף), ולא לשלושת הישראלים שעל הדף. הוא רלוונטי להקשר, **ואסור להשתמש בו כהוכחת השפעה של המעש הזה** — זו בדיוק הטעות שהתדריך פוסל.
- **EdDSA/RFC 8032 — לא נבדק.** נגמר התקציב. חתימות Schnorr/EdDSA (Ed25519, בשימוש ב-TLS 1.3, SSH, Signal, Tor) הן בנייה מסוג Fiat-Shamir, ו-FIPS 204 עצמו אומר זאת במפורש ("The Schnorr signature scheme applies the Fiat-Shamir heuristic"). **אבן להפוך:** RFC 8032 — אם הוא נוקב בשם, זו חוליה שלישית לתקן.
- **DAA/TPM — לא נבדק.** Direct Anonymous Attestation, המנגנון שבשבבי TPM ומבוסס על ההיוריסטיקה הזאת, הוא לכאורה הפריסה הרחבה ביותר שקיימת (מאות מיליוני מחשבים). לא הגעתי אליו. **אבן להפוך:** ISO/IEC 11889 / מפרט TCG TPM 2.0.
- **ויקיפדיה — נמשכה, אך לא כמקור.** משכתי את הוויקיטקסט הגולמי **אך ורק כדי לבדוק את הפגם שבציטוט שעל הדף** (כלומר לביקורת הדף, כפי שעשה הטריאז'), ולא לצורך שום עובדה על העולם. כל העובדות בקובץ מגיעות מ-ISO, NIST, IACR ePrint, getmonero.org, Electric Coin Company ו-Semantic Scholar.

## מה זה אומר לדף כפי שהוא כתוב היום

**המעש עומד. הטענה שעל הדף נתמכת בעיקרה, ואף חלשה מהמציאות. הבעיה בדף היא לא התוכן — היא המקור, והדיוק בשאלת מי ומתי.**

1. **הכותרת נתמכת, בהסתייגות אחת.** "שלושה ישראלים פיתחו שיטה להוכיח זהות בלי לחשוף את הסוד עצמו" — נכון: הם אכן פיתחו את הסכמה ב-1988 ופרסמו אותה ב-*Journal of Cryptology*. **מה שאינו מדויק הוא הקישור הסמוי בין המשולש הזה לבין ההשפעה.** ההשפעה שנכנסה לתקנים היא של **שניים** מהשלושה, ומעבודה **שנתיים קודם לכן**.
2. **ה-`ripple` נתמך — ולראשונה יש לו הוכחה.** "תשתית להגנת פרטיות בזיהוי דיגיטלי ובקריפטוגרפיה מודרנית" הוא בדיוק מה שתקן ISO/IEC 9798-5 (זיהוי דיגיטלי) ותקן FIPS 204 (קריפטוגרפיה מודרנית) מוכיחים. **ה-`ripple` היה נכון; הוא פשוט היה חסר-מקור לגמרי.** עכשיו יש לו שני תקנים.
3. **המקור חייב להתחלף — וזו הנקודה הדחופה ביותר בדף.** המקור היחיד היום הוא ערך ויקיפדיה **שוויקיפדיה עצמה מסמנת כחסר מקורות מאז ינואר 2014**, וממנו נלקחו שני ציטוטים שאחד מהם קטוע באמצע משפט. יש שלוש חלופות ראשוניות, חינמיות וזמינות מיידית:
   - **ISO/IEC 9798-5:2009** — התקן שנושאו הוא בדיוק נושא הדף.
   - **NIST FIPS 204 (13.8.2024)** — התקן הפדרלי שבנוי על הבנייה.
   - **Feige, Fiat & Shamir, "Zero-knowledge proofs of identity", *Journal of Cryptology* 1988** (DOI 10.1007/BF02351717) — המאמר עצמו, המקור הראשוני של המעש.
4. **השנה 1988 — נכונה** לגרסת כתב העת בת שלושת המחברים. **אבל שווה לשקול אם המעש שכדאי לספר הוא זה.** אם הדף רוצה לספר את הסיפור שהתממש בברזל, השנה היא **1986** והשמות הם **פיאט ושמיר**. אם הוא רוצה לספר את הסיפור בת שלושת הישראלים — 1988 נכון, וההשפעה שיש לו היא 1,015 ציטוטים בספרות, לא תקן ISO. **שתי האפשרויות לגיטימיות; מה שאסור הוא לערבב, כלומר לכתוב 1988 ושלושה שמות ואז לתלות בהם את התקנים.**
5. **התמונה.** דף על שלושה, ותמונה של אחד.

**המלצה לתומר (אינה הוראה):** **לא רק לא להסיר — זה אחד המעשים החזקים ביותר שראיתי בכל התיקים האלה, והדף מוכר אותו בחסר.** יש כאן ישראלים ששמם כתוב בגוף שני תקנים רשמיים — אחד בין-לאומי ואחד פדרלי אמריקני — ומערכת פיננסית חיה שרצה על הבנייה שלהם מאז 2018. שלוש פעולות מתבקשות: **(א)** להחליף את מקור הוויקיפדיה (חסר-המקורות) בתקנים ובמאמר עצמו; **(ב)** לתקן את הציטוט הקטוע, או פשוט למחוק אותו ולהביא במקומו את ה-NOTE מתוך ISO/IEC 9798-5; **(ג)** להכריע בין "1986, פיאט ושמיר, הבנייה שנכנסה לתקנים" לבין "1988, שלושתם, הסכמה עצמה" — ולנסח בהתאם. **בכל שלוש הדרכים המעש עומד.**
