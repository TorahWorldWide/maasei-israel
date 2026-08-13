#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assembles v3/canonical.json from the section files plus the page-level fields."""
import json, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))

sections = []
for path in sorted(glob.glob(os.path.join(HERE, "sections", "*.json"))):
    with open(path, encoding="utf-8") as fh:
        s = json.load(fh)
    sections.append({
        "heading": s["heading"],
        "heading_en": s["heading_en"],
        "body": s["body"],
        "body_en": s["body_en"],
    })

ENGINE = ("שני אנשים שלא היו מהנדסים — שחקנית שלמדה על טורפדואים בשולחן האוכל של בעלה "
          "סוחר הנשק, ומלחין שנכשל שש-עשרה שנה בסנכרון פסנתרים מכניים — לקחו גליל פסנתר "
          "מנוקב והפכו אותו למנגנון שמקפיץ שידור בין 88 תדרים כדי שלא יהיה אפשר לשבש אותו; "
          "ואז נמחק מן הפטנט הסעיף היחיד שדיבר על העיקרון, ונשאר להם פטנט על מכשיר שלא נבנה "
          "מעולם.")

ENGINE_EN = ("Two people who were not engineers — an actress who learned about torpedoes at "
             "her arms-dealer husband's dinner table, and a composer who had spent sixteen years "
             "failing to synchronize player pianos — took a punched piano roll and turned it into a "
             "mechanism that hops a transmission across 88 frequencies so it cannot be jammed; and "
             "then the one claim that spoke about the principle was struck from the patent, leaving "
             "them a patent on a device that was never built.")

PATENT_URL = "https://patents.google.com/patent/US2292387A/en"
PATENT_PDF = "https://patentimages.storage.googleapis.com/e0/dd/4e/0e04d56d1d7604/US2292387.pdf"
MEMOIR = "https://monoskop.org/images/4/4d/Antheil_George_Bad_Boy_of_Music_1947.pdf"
ROTHMAN19 = "https://www.americanscientist.org/article/random-paths-to-frequency-hopping"
ROTHMAN24 = "https://www.americanscientist.org/blog/the-long-view/the-seventh-claim"
WW2 = "https://www.nationalww2museum.org/war/articles/hedy-lamarrs-wwii-invention-helped-shape-modern-tech"
NIHF = "https://www.invent.org/inductees/hedy-lamarr"
EFF = "https://web.archive.org/web/20000522165803/http://www.eff.org/awards/6th_pioneer_awards.announce"
LEHRMAN = "https://acoustics.org/pressroom/httpdocs/140th/lehrman.htm"
NEAMAN = "https://www.neaman.org.il/wp-content/uploads/2024/02/649-Hedy-Lamarr-Dec-19-2011.pdf"
CASEFILE39 = ("https://commons.wikimedia.org/wiki/File:Patent_Case_File_No._2,292,387,_Secret_Communication_"
              "System,_Inventors_Hedy_Kiesler_Markey_and_George_Antheil_-_DPLA_-_"
              "128f022cfd9421aa10de72958a7edf90_(page_39).jpg")

Q_CANCEL = ("In response to the Office action of August 13, 1941, please amend the above identified "
            "application by canceling rejected Claim 7.")
Q_PRIOR = ("The first was U.S. patent 1,869,659 granted to Willem Broertjes in 1932, and a second was "
           "U.S. Patent 2,134,850, granted in 1938 to Martin Baesecke of the German firm Siemens and Halske.")
Q_88 = ("In a conventional player piano record there may be 88 rows of perforations, and in our system "
        "such a record would permit the use of 88 different carrier frequencies, from one to another of "
        "which both the transmitting and receiving station would be changed at intervals.")
Q_APP = "Application June 10, 1941, Serial No. 397,412"
Q_GRANT = "Patented Aug. 11, 1942"
Q_FEE = ("They suggested that the inventors might improve their device by inserting a new claim (for a fee "
         "of $25) that was not limited to a record strip, but the pair never took action.")
Q_BLADES = ("It was tested by 1957 and in 1963 it was installed on the flagship U.S.S. Mount McKinley, where "
            "it successfully thwarted intentional jamming efforts.")
Q_BLADES55 = ("another major effort at developing a secure, jam-proof system was put forth by Sylvania with its "
              "Buffalo Laboratories Application of Digitally Exact Spectra, or BLADES, which began in 1955 as "
              "system for communicating with Polaris submarines.")
Q_DIXON = ("no reference to Lamarr and Antheil's device appears in the patents underlying the first "
           "frequency-hopping system put into action ... or in R.C. Dixon's Spread Spectrum Systems, the first "
           "textbook devoted to the field, which cites nearly 2,000 technical papers.")
Q_16 = ("His crowning glory was to be the Ballet mécanique, which he scored for two grand pianos, three "
        "xylophones, four bass drums, a tam-tam, a siren, three airplane propellors, several electric bells, "
        "and 16 synchronized player pianos, playing four separate parts.")
Q_EXPIRE = "1959-08-11"
Q_ANTHEIL_DEATH = "Antheil died in 1959, at the age of 58."
Q_WILAN = ("A Canadian wireless developer Wi-LAN acquired a 49 per cent claim to the patent from Hedy Lamarr "
           "herself, in 1998, even though the patent had expired long ago and had no economic value.")
Q_EFF = ("the Electronic Frontier Foundation (EFF) will honor former movie actress Hedy Lamarr with a special "
         "award this evening for her co-invention of spread-spectrum broadcast communications technologies")
Q_82 = "But in 1997, Hedy Lamarr, age 82 and still gorgeous, along with Antheil (posthumously), were given a Pioneer Award by the Electronic Frontier Foundation."
Q_1940 = ("Later on that evening we began talking about the war, which, in the late summer of 1940, was looking most "
          "extremely black. ... She said that she knew a good deal about new munitions and various secret weapons, some "
          "of which she had invented herself.")

doc = {
    "deed_id": "347192a7-eafd-402f-9216-fb7d27795bd2",
    "canonical_type": "ממציא יחיד",
    "canonical_type_en": "single-inventor",
    "written_by": "canonical/opus-5 · v3",
    "engine_sentence": ENGINE,
    "engine_sentence_en": ENGINE_EN,

    "title": "הדי לאמאר: 88 תדרים, וסעיף אחד שנמחק מן הפטנט",
    "title_en": "Hedy Lamarr: 88 frequencies, and one claim struck from the patent",

    "description": (
        "שחקנית של MGM ומלחין אוונגרדי הגישו ב-1941 בקשת פטנט על מערכת שבה משדר ומקלט קופצים יחד בין 88 "
        "תדרי רדיו לפי גליל פסנתר מנוקב, כדי שאי אפשר יהיה לשבש את ההיגוי של טורפדו. הפטנט אושר ב-1942, "
        "אבל הסעיף היחיד שניסח את העיקרון עצמו נדחה בידי הבוחן חודשיים אחרי ההגשה ונמחק מן הבקשה בידי "
        "עורכי הדין באוקטובר, ובידיהם נשאר פטנט על מכשיר שלא נבנה מעולם."
    ),
    "description_en": (
        "An MGM actress and an avant-garde composer filed a patent application in 1941 for a system in which "
        "transmitter and receiver hop together across 88 radio frequencies, dictated by a punched piano roll, "
        "so that a torpedo's guidance cannot be jammed. The patent was granted in 1942, but the one claim that "
        "stated the principle itself was rejected by the examiner two months after filing and struck from the "
        "application by their attorneys in October, leaving them a patent on a device that was never built."
    ),

    "summary_short": (
        "שחקנית של MGM ומלחין אוונגרדי, שאיש מהם לא היה מהנדס, רשמו פטנט על היגוי טורפדו שאי אפשר לשבש. "
        "הפטנט אושר. הסעיף שדיבר על העיקרון לא.\n\n"
        "היא למדה על נשק ליד שולחנו של בעלה סוחר הנשק, שהיה בטוח שאינה מבינה מילה. ג'ורג' אנתייל נכשל שש-עשרה שנה "
        "בסנכרון שישה-עשר פסנתרים מכניים.\n\n"
        "בפגישתם השנייה, בביתה, הפכו גליל פסנתר מנוקב למנגנון שמקפיץ שידור בין 88 תדרים. קפיצת תדרים כבר הייתה "
        "ידועה, והבוחן דחה את הסעיף היחיד שקשר את שמם לעיקרון. עורכי הדין הציעו סעיף חדש תמורת 25 דולר, "
        "השניים לא עשו דבר, והסעיף נמחק מן הבקשה.\n\n"
        "ב-1963 יצאה לים המערכת הראשונה שקפצה בין תדרים, וסיכלה שיבוש מכוון. אף אחד מן המסמכים שלה לא מזכיר את שמם."
    ),
    "summary_short_en": (
        "An MGM actress and an avant-garde composer, neither of them an engineer, patented a torpedo guidance system "
        "that could not be jammed. The patent was granted. The claim that stated the principle was not.\n\n"
        "She learned about weapons at the table of her arms-dealer husband, who was certain she did not understand a "
        "word. George Antheil had failed for sixteen years to synchronize sixteen player pianos.\n\n"
        "At their second meeting, at her home, they turned a punched piano roll into a mechanism that hops a "
        "transmission across 88 frequencies. Frequency hopping was already known, and the examiner rejected the one "
        "claim that tied their names to the principle. Their attorneys offered a new claim for $25, the pair took no "
        "action, and the claim was struck from the application.\n\n"
        "In 1963 the first frequency-hopping system went to sea and defeated deliberate jamming. Not one of its "
        "documents mentions their names."
    ),

    "origin_story": (
        "הידע הגיע משולחן שסביבו נמכר נשק. לפי אנתייל, שכתב על כך ב-1945, רכשה לאמאר את כישרונה להמצאת נשק בשנים "
        "שבהן הייתה נשואה לפריץ מנדל, בעל מפעלי הנשק הגדולים באוסטריה: שוב ושוב שמעה אותו ואת המומחים שלו דנים "
        "במכשירים חדשים, ושמרה את הרעיונות בצורתם הבסיסית, בעוד שמנדל, בלשונו של אנתייל, לא חשב שהיא יודעת א' מ-ב'. "
        "בשלהי קיץ 1940, בהוליווד, נקבעה לה פגישה עם המלחין ג'ורג' אנתייל, שהתפרנס אז מטור על אנדוקרינולוגיה "
        "יישומית במגזין אסקווייר. היא הגיעה עם פנקס ועיפרון. בפגישתם השנייה, בביתה, עלתה המלחמה, והיא סיפרה "
        "שהיא יודעת לא מעט על תחמושת חדשה ועל נשקים סודיים, שחלקם המציאה בעצמה. אחד הרעיונות נראה לו טוב כל כך "
        "שהציע לרשום עליו פטנט ולמסור אותו לממשלת ארצות הברית."
    ),
    "origin_story_en": (
        "The knowledge came from a table where weapons were sold. According to Antheil, writing in 1945, Lamarr acquired "
        "her flair for inventing weapons during the years she was married to Fritz Mandl, who owned the largest munitions "
        "works in Austria: time and time again she overheard him and his experts discussing new devices and retained the "
        "ideas in basic form, while Mandl, in Antheil's words, did not think she knew A from Z. In the late summer of 1940, "
        "in Hollywood, a meeting was arranged for her with the composer George Antheil, who was then making his living from "
        "a column on applied endocrinology in Esquire. She arrived "
        "with a notebook and a pencil. At their second meeting, at her home, the talk turned to the war, and she said she knew a good deal "
        "about new munitions and secret weapons, some of which she had invented herself. One of her ideas struck him as good "
        "enough that he suggested she patent it and give it to the United States Government."
    ),

    "act": (
        "ההמצאה עצמה הייתה מנגנון סנכרון. גליל של פסנתר מכני, מנוקב ב-88 שורות של חורים שמיקומם אקראי, יונח במשדר וישלוט "
        "בקפיצה בין 88 תדרי רדיו; גליל זהה יונח במקלט; ואת שניהם יש לשחרר באותו רגע ממש. המערכת משדרת גם תדרי דמה, "
        "והמקלט קולט רק את תדרי ההיגוי האמיתיים. אנתייל הביא לעניין שש-עשרה שנות כישלון בסנכרון פסנתרים מכניים ביצירתו "
        "בלט מקניק, והשראה ממכשיר מיסטרי קונטרול של פילקו משנת 1939, השלט הרחוק המסחרי הראשון לרדיו; את התקלות "
        "פתר בעזרת סמואל מקאון, מהנדס ממכון הטכנולוגיה של קליפורניה. הבקשה הוגשה ב-10 ביוני 1941, מספר סידורי 397,412, "
        "על שמה של הדי קיסלר מרקי ועל שמו של ג'ורג' אנתייל, ופטנט מספר 2,292,387 אושר ב-11 באוגוסט 1942."
    ),
    "act_en": (
        "The invention itself was a synchronizing mechanism. A player-piano roll, punched with 88 rows of randomly placed "
        "perforations, is placed in the transmitter and controls the hopping among 88 radio frequencies; an identical roll "
        "is placed in the receiver; and both must be released at the same instant. The system also transmits dummy "
        "frequencies, and the receiver picks up only the true steering frequencies. Antheil brought to it sixteen years of "
        "failure at synchronizing player pianos in his Ballet mécanique, and the influence of Philco's 1939 Mystery Control, "
        "the first commercially available radio remote controller; he worked out the faults with the help of Samuel Mackeown, "
        "an engineer at the California Institute of Technology. The application was filed on 10 June 1941, Serial No. 397,412, "
        "in the names of Hedy Kiesler Markey and George Antheil, and patent number 2,292,387 was granted on 11 August 1942."
    ),

    "ripple": (
        "הסעיף השביעי בבקשה תיאר את העיקרון בלי גליל ובלי פסנתר: שינוי בו-זמני של כוונון המשדר והמקלט לפי דפוס "
        "שרירותי ובלתי חוזר. ב-13 באוגוסט 1941 דחה אותו הבוחן בנימוק שקפיצת תדרים כבר ידועה, וציטט פטנט אמריקאי משנת "
        "1932 של ווילם ברוארטיס ופטנט משנת 1938 של מרטין בזקה מן החברה הגרמנית זימנס והלסקה. השניים לא היו הראשונים "
        "שהגו קפיצת תדרים, והסעיף השביעי היה המקום היחיד בבקשה ששמם נקשר בו לעיקרון עצמו ולא לגליל נייר מנוקב. "
        "עורכי הדין הסכימו עם הבוחן, הציעו תמורת 25 דולר סעיף חדש שאינו כבול לגליל, והשניים לא עשו דבר. ששת הסעיפים "
        "שנותרו כבולים כולם לגליל, והפטנט שנשאר בידיהם הוא על המכשיר ולא על העיקרון. המערכת המבצעית הראשונה שקפצה בין תדרים, BLADES של סילבניה, "
        "החלה ב-1955 והותקנה ב-1963 על ספינת הדגל מאונט מקינלי, שם סיכלה שיבוש מכוון. הפטנטים שבבסיסה אינם "
        "מזכירים את לאמאר ואנתייל, וגם ספר הלימוד הראשון בתחום, המצטט קרוב ל-2,000 מאמרים מקצועיים, אינו מזכיר אותם. "
        "בלשונו של רות'מן: הרעיונות ניצחו, לא האנשים."
    ),
    "ripple_en": (
        "The seventh claim in the application described the principle with no roll and no piano: simultaneously changing the "
        "tuning of the transmitter and receiver according to an arbitrary, nonrecurring pattern. On 13 August 1941 the examiner "
        "rejected it on the grounds that frequency hopping was already known, citing a U.S. patent granted in 1932 to Willem "
        "Broertjes and one granted in 1938 to Martin Baesecke of the German firm Siemens and Halske. The two were not the first "
        "to conceive of frequency hopping, and the seventh claim was the one place in the application where their names were "
        "tied to the principle itself rather than to a punched paper roll. The attorneys agreed with "
        "the examiner, offered for $25 a new claim not limited to a record strip, and the pair took no action. The six "
        "surviving claims are all bound to the roll, and the patent left in their hands is on the device and not on the principle. The first "
        "operational frequency-hopping system, Sylvania's BLADES, began in 1955 and was installed in 1963 on the flagship "
        "U.S.S. Mount McKinley, where it thwarted intentional jamming. The patents underlying it make no mention of Lamarr and "
        "Antheil, and neither does the first textbook in the field, which cites nearly 2,000 technical papers. In Rothman's "
        "words: the ideas prevailed, not the individuals."
    ),

    "aftermath": (
        "חיל הים לא בנה את המכשיר, ולא נמצא מקור ראשוני שאומר מדוע. הפטנט פקע ב-11 באוגוסט 1959, ארבע שנים לפני "
        "שקפיצת תדרים יצאה לים, ובאותה שנה מת ג'ורג' אנתייל בגיל 58. שלושה מוסדות הכרה קובעים שמן ההמצאה לא הגיע "
        "אליהם כסף, ואיש מהם אינו מציג רשומה כספית; תיעוד לתשלום כלשהו לא נמצא. הסייג היחיד הוא מ-1998, כשחברת "
        "התקשורת האלחוטית הקנדית Wi-LAN רכשה מלאמאר עצמה 49 אחוזים מן הזכויות בפטנט ושילמה במניות. הפטנט פקע "
        "כארבעים שנה קודם לכן ולא היה לו ערך כלכלי, ובאותו מועד כבר לא נותרה זכות למכור."
    ),
    "aftermath_en": (
        "The Navy did not build the device, and no primary source saying why has been found. The patent expired on 11 August "
        "1959, four years before frequency hopping went to sea, and in that same year George Antheil died at the age of 58. "
        "Three institutions of record state that no money from the invention ever reached them, and none of them produces a "
        "financial record; no documentation of any payment has been found. The single qualification comes from 1998, when the "
        "Canadian wireless developer Wi-LAN acquired from Lamarr herself a 49 per cent interest in the patent and paid in "
        "shares. The patent had expired some forty years earlier and had no economic value, and by then there was no right "
        "left to sell."
    ),

    "recognition": (
        "ההכרה הראשונה הגיעה ב-1997, אחרי מסע ציבורי שהוביל דייב יוז, פעיל קהילות מקוונות מקולורדו. קרן החזית האלקטרונית "
        "העניקה ללאמאר ולאנתייל המנוח פרס מיוחד בטקס פרסי החלוץ השישי, ולפי ההודעה שלה עצמה ניתן הפרס גם על \"הבערות "
        "הכמעט מוחלטת של הציבור\" ביחס להמצאה. לאמאר הייתה אז בת 82 ולא הגיעה לטקס; בנה קיבל את הפרס והשמיע הקלטה שבה "
        "אמרה שהיא שמחה שההמצאה לא נעשתה לשווא. באותה שנה זכתה גם בפרס BULBIE של כנס ההמצאות, וב-2014 הוכנסה אחרי מותה "
        "להיכל התהילה הלאומי לממציאים יחד עם אנתייל. ההוקרות המאוחרות ממשיכות להגיע: טלסקופ לתקשורת קוונטית בווינה ב-2014, "
        "אסטרואיד ב-2019, ולוויין GPS ב-2021."
    ),
    "recognition_en": (
        "The first recognition came in 1997, after a public campaign led by Dave Hughes, an online community activist from "
        "Colorado. The Electronic Frontier Foundation gave Lamarr and the late Antheil a special award at its sixth Pioneer "
        "Awards ceremony, and according to its own announcement the award was given partly for the public's \"nearly absolute "
        "ignorance about it\". Lamarr was 82 and did not attend; her son accepted the award and played a recording in which she "
        "said she was glad the invention was not done in vain. That same year she also received the BULBIE Gnass Spirit of "
        "Achievement Award at the Invention Convention, and in 2014 she was inducted posthumously into the National Inventors "
        "Hall of Fame together with Antheil. Later honours keep arriving: a quantum-communication telescope in Vienna in 2014, "
        "an asteroid in 2019, and a GPS satellite in 2021."
    ),

    "the_moment": (
        "לשכת הפטנטים בוושינגטון, 13 באוגוסט 1941. על שולחנו של הבוחן מונחת בקשה שהוגשה חודשיים קודם לכן, על שמם של שחקנית "
        "ומלחין. הוא קורא את הסעיף השביעי, זה שאין בו גליל ואין בו פסנתר, רק העיקרון עצמו: שינוי בו-זמני של כוונון המשדר "
        "והמקלט לפי דפוס שרירותי ובלתי חוזר. הוא דוחה אותו, בנימוק שקפיצת תדרים כבר ידועה, ומציב לצדו שני מספרים של פטנטים "
        "קודמים, אחד משנת 1932 ואחד משנת 1938. ב-31 באוקטובר עונים עורכי הדין מלוס אנג'לס בשורה אחת: בתגובה לפעולת הלשכה "
        "מיום 13 באוגוסט 1941, אנא תקנו את הבקשה על ידי מחיקת הסעיף השביעי שנדחה. בבקשה נותרו שישה סעיפים, וכולם "
        "מדברים על גליל נייר מנוקב. העיקרון יצא מן הפטנט ולא חזר אליו."
    ),
    "the_moment_en": (
        "The Patent Office in Washington, 13 August 1941. On the examiner's desk lies an application filed two months earlier, "
        "in the names of an actress and a composer. He reads the seventh claim, the one with no roll and no piano in it, only the "
        "principle itself: simultaneously changing the tuning of the transmitter and receiver according to an arbitrary, "
        "nonrecurring pattern. He rejects it on the grounds that frequency hopping is already known, and sets beside it two "
        "numbers of earlier patents, one from 1932 and one from 1938. On 31 October the attorneys in Los Angeles answer in a "
        "single line: in response to the Office action of August 13, 1941, please amend the application by canceling rejected "
        "Claim 7. Six claims are left in the application, and every one of them speaks of a punched record strip. The "
        "principle left the patent and never came back to it."
    ),

    "infobox": {"rows": [
        {
            "label": "שנים",
            "label_en": "Years",
            "value": "1914–2000",
            "value_en": "1914–2000",
            "source": ("Wien Geschichte Wiki (הלקסיקון ההיסטורי של עיריית וינה): \"Hedy Lamarr (Hedwig Eva Maria Kiesler), "
                       "* 9. November 1914 Wien\" וכן \"† 19. Jänner 2000\" · שנת הלידה שנויה במחלוקת בין המקורות: "
                       "Encyclopaedia Britannica כותבת \"born November 9, 1913/14, Vienna, Austria\", וסוכנות AP וגייל "
                       "נוקבות 1913.")
        },
        {
            "label": "עיסוקים",
            "label_en": "Occupations",
            "value": "שחקנית קולנוע וממציאה. כך, ורק כך, מונות אותה שתי הרשויות הביוגרפיות הגדולות.",
            "value_en": ("Film actress and inventor. That, and only that, is how the two major biographical authorities "
                         "list her."),
            "source": ("Wien Geschichte Wiki: \"Beruf Filmschauspielerin, Erfinderin\" · Deutsche Biographie: "
                       "\"Beruf/Funktion Schauspielerin ; Erfinderin ; Filmschauspielerin\".")
        },
        {
            "label": "הפטנט",
            "label_en": "The patent",
            "value": ("ארצות הברית מספר 2,292,387, \"Secret Communication System\". הוגש ב-10 ביוני 1941 (מספר סידורי "
                      "397,412) על שם הדי קיסלר מרקי וג'ורג' אנתייל, אושר ב-11 באוגוסט 1942, ופקע ב-11 באוגוסט 1959."),
            "value_en": ("United States 2,292,387, \"Secret Communication System\". Filed 10 June 1941 (Serial No. 397,412) "
                         "in the names of Hedy Kiesler Markey and George Antheil, granted 11 August 1942, expired 11 August 1959."),
            "source": ("סריקת הפטנט המודפס: \"Patented Aug. 11, 1942\" · Google Patents, שדה Anticipated expiration: "
                       "\"1959-08-11\" · אנתייל, Bad Boy of Music (1945): \"Number 2,292,387 ... Application, June 10, 1941, "
                       "Serial No. 397,412\" · היכל התהילה הלאומי לממציאים: \"it listed her maiden and married name at the "
                       "time, Hedy Kiesler Markey\".")
        },
        {
            "label": "השותף לפטנט",
            "label_en": "Patent partner",
            "value": ("ג'ורג' אנתייל, מלחין, שכתב ב-1924 את בלט מקניק לשישה-עשר פסנתרים מכניים מסונכרנים. מת "
                      "ב-1959, בגיל 58, בשנה שבה פקע הפטנט. היום המדויק של מותו לא אותר."),
            "value_en": ("George Antheil, composer, who in 1924 wrote the Ballet mécanique for sixteen synchronized player "
                         "pianos. He died in 1959, aged 58, the year the patent expired. The exact day of his death was not found."),
            "source": ("פול לרמן, ASA/NOISE-CON 2000: \"Antheil died in 1959, at the age of 58\" וכן \"16 synchronized player "
                       "pianos, playing four separate parts\" · Google Patents, מועד הפקיעה: \"1959-08-11\".")
        }
    ]},

    "sections": sections,

    "honors": [
        {
            "name": "פרס מיוחד על ההמצאה המשותפת של תקשורת בפריסת ספקטרום",
            "name_en": "Special award for the co-invention of spread-spectrum communications",
            "awarding_body": "קרן החזית האלקטרונית (EFF)",
            "awarding_body_en": "Electronic Frontier Foundation",
            "year": 1997,
            "source_url": EFF,
            "quote": Q_EFF,
            "note": ("הוענק בטקס פרסי החלוץ השישי. ההודעה בת-הזמן מבחינה בין הפרס המיוחד הזה לבין שני פרסי החלוץ שהוענקו "
                     "באותו ערב ליוהאן הלסינגיוס ולמארק רוטנברג; רשימת הזוכים המאוחרת של EFF מאחדת את שלושתם בשורה אחת, "
                     "ומכאן הנוסח הרווח \"זכתה בפרס החלוץ\"."),
            "note_en": ("Given at the sixth Pioneer Awards ceremony. The contemporary announcement distinguishes this special "
                        "award from the two Pioneer Awards given that evening to Johan Helsingius and Marc Rotenberg; EFF's "
                        "later winners list merges all three into one line, which is where the common phrasing \"won the Pioneer "
                        "Award\" comes from.")
        },
        {
            "name": "פרס BULBIE, Gnass Spirit of Achievement",
            "name_en": "BULBIE Gnass Spirit of Achievement Award",
            "awarding_body": "כנס ההמצאות (Invention Convention), ארצות הברית",
            "awarding_body_en": "The Invention Convention, United States",
            "year": 1997,
            "source_url": "https://web.archive.org/web/19980710194658/http://www.inventionconvention.com/awards/bulbie.winlist.html",
            "quote": ("... who in 1942 patented the basis for Spread Spectrum Technology now used in cellular phones ... these "
                      "are the 1997 recipients of the 1997 BULBIE, Gnass Spirit of Achievement Award held on August 31 at the "
                      "11th annual INVENTION CONVENTION trade show."),
            "note": "הטקס נערך ב-31 באוגוסט 1997. הטענה שהייתה האישה הראשונה שזכתה בפרס אינה מופיעה באתר הפרס עצמו.",
            "note_en": ("The ceremony was held on 31 August 1997. The claim that she was the first woman to receive it does not "
                        "appear on the award's own site.")
        },
        {
            "name": "הכנסה להיכל התהילה הלאומי לממציאים, לאחר מותה",
            "name_en": "Induction into the National Inventors Hall of Fame (posthumous)",
            "awarding_body": "היכל התהילה הלאומי לממציאים, ארצות הברית",
            "awarding_body_en": "National Inventors Hall of Fame, United States",
            "year": 2014,
            "source_url": NIHF,
            "quote": "Hedy Lamarr Frequency Hopping Communication System U.S. Patent No. 2,292,387 Inducted in 2014",
            "note": "אנתייל הוכנס באותה שנה עצמה.",
            "note_en": "Antheil was inducted in the same year."
        },
        {
            "name": "טלסקופ לתקשורת קוונטית בווינה נקרא על שמה",
            "name_en": "A quantum-communication telescope in Vienna named after her",
            "awarding_body": "אוניברסיטת וינה והאקדמיה האוסטרית למדעים",
            "awarding_body_en": "University of Vienna and the Austrian Academy of Sciences",
            "year": 2014,
            "source_url": "https://vcm2015.univie.ac.at/uniview/wissenschaft-gesellschaft/detailansicht/artikel/ein-teleskop-namens-hedy-lamarr",
            "quote": ("Nun tauften sie Rektor Heinz W. Engl und ÖAW-Präsident Anton Zeilinger offiziell \"Hedy Lamarr Quantum "
                      "Communication Telescope\". \"Mit dieser Namensgebung ehren wir eine große österreichische Erfinderin\", "
                      "so Anton Zeilinger."),
            "note": "המעניקים בשמם: הרקטור היינץ אנגל ונשיא האקדמיה אנטון ציילינגר. ההודעה מ-12 בדצמבר 2014.",
            "note_en": ("Named by Rector Heinz Engl and Academy President Anton Zeilinger. The announcement is dated 12 December 2014.")
        },
        {
            "name": "אסטרואיד 32730 Lamarr",
            "name_en": "Asteroid 32730 Lamarr",
            "awarding_body": "המרכז לכוכבי לכת מזעריים (IAU)",
            "awarding_body_en": "Minor Planet Center (IAU)",
            "year": 2019,
            "source_url": "https://minorplanetcenter.net/db_search/show_object?object_id=32730",
            "quote": ("(32730) Lamarr = 1951 RX. Hedy Lamarr (1914-2000) was a Austrian-American inventor and actress. Along "
                      "with George Antheil, she developed technology for a radio guidance system to assist the Allied war effort "
                      "in WWII. [Ref: Minor Planet Circ. 115894]"),
            "note": ("נימוק השם אושר באוגוסט 2019, שבעה חודשים אחרי מאמרו של רות'מן שקבע את ההפך. הדף מציג את שתי העמדות זו "
                     "לצד זו ואינו מכריע."),
            "note_en": ("The citation was approved in August 2019, seven months after Rothman's article argued the opposite. The "
                        "page sets the two positions side by side and does not decide between them.")
        },
        {
            "name": "לוויין GPS III SV10 נקרא על שמה",
            "name_en": "GPS III SV10 satellite named after her",
            "awarding_body": "חיל החלל האמריקאי",
            "awarding_body_en": "United States Space Force",
            "year": 2021,
            "source_url": "https://www.lockheedmartin.com/en-us/news/features/2021/core-mate-complete-for-final-gps-iii-sv10.html",
            "quote": ("per tradition at the \"birth\" of a satellite, nicknamed GPS III SV10 \"Hedy Lamarr\" after the actress "
                      "and inventor ... it gets a nickname – chosen by the U.S. Space Force"),
            "note": ("2021 היא שנת ההרכבה ומתן השם ולא שנת השיגור, והמקור הוא הקבלן ולא חיל החלל. באותה הודעה נטען גם שהפטנט "
                     "הניח את היסוד ל-GPS, טענה שרות'מן סותר, שכן GPS השתמש מאז ומתמיד ברצף ישיר."),
            "note_en": ("2021 is the year of assembly and naming, not of launch, and the source is the contractor rather than the "
                        "Space Force. The same release claims the patent laid the foundation for GPS, which Rothman contradicts, "
                        "since GPS has always used direct sequencing.")
        }
    ],

    "writer_questions": [
        "מכתב Lyon and Lyon מ-3 באוקטובר 1941, בשלמותו: המשפט \"the Examiner has found nothing antedating the invention\" אינו מתיישב עם דחיית הסעיף השביעי ב-13 באוגוסט. האם עורכי הדין התכוונו למכשיר בלבד? המקור אצל חוקר אנתייל מאורו פיצ'יניני, ולא נמשך.",
        "האם קיים תיעוד כלשהו לתגובת השניים להצעת 25 הדולר: מכתב, חשבונית, רישום במשרד עורכי הדין? כל המקורות אומרים רק שלא פעלו, ואין מהם ללמוד אם הגיעה אליהם ההצעה ואם השיבו עליה.",
        "ידיעת הניו-יורק טיימס מ-1 באוקטובר 1941 (\"red-hot category\"): לא נמשכה מארכיון העיתון, ומובאת בדף מפי רות'מן בלבד. נדרש עותק.",
        "מקור לאמרה \"קציני חיל הים חשבו שהוא רוצה להכניס פסנתר מכני לטורפדו\": אינה נמצאת באף אחת מ-13,031 השורות של Bad Boy of Music, ורות'מן אינו מציין מניין הגיעה. מכתבים? ראיון? ארכיון פיצ'יניני?",
        "האם קיים בארכיוני חיל הים מסמך כלשהו על ההמצאה או על דחייתה? תיק הבקשה מן הארכיון הלאומי אינו כולל התכתבות עם חיל הים.",
        "תאריך מותו המדויק של ג'ורג' אנתייל ב-1959, ובעיקר אם מת לפני 11 באוגוסט או אחריו. יש בידינו רק \"1959, בגיל 58\" מלרמן.",
        "הודעת Wi-LAN המקורית מ-1998 על רכישת 49% מן הזכויות בפטנט: לא אותרה. כל המקורות חוזרים על אותו ניסוח, ואיש מהם אינו אומר מה בדיוק נמכר בפטנט שכבר פקע.",
        "מי מבני לאמאר עלה לבמה ב-1997 וקיבל את הפרס. המוזיאון כותב \"בנה\" בלי שם, ולא אומת שאנתוני לודר הוא שעלה.",
        "פטנטי ברוארטיס (1,869,659) ובזקה (2,134,850) במקורם: לא נמשכו ישירות, ומצוטטים דרך רות'מן. בזקה רק מתואר אצלו ואינו מצוטט.",
        "האם BLADES (תקשורת בספינת דגל, 1963) והטענה על טורפדואים במשבר הטילים בקובה (אוקטובר 1962) מתייחסות לשני מכשירים שונים? לא נמצא מקור שמכריע.",
        "המרה עצמאית של 25 מיליון דולר מ-1942 לערכי היום: \"כ-343 מיליון\" מגיע מכתבה של 2025 ולא ממקור המרה רשמי, וגם לא ברור לאיזו שנה מתייחס הסכום המומר. חומר אגרות המלחמה הוצא מן הדף בסבב הזה, והשאלה נשארת פתוחה ביומן.",
        "היכל התהילה של הקניין הרוחני (2019): הפריט הגיע דרך כתב-עת מקצועי ולא מן הגוף המעניק, ובלי ציטוט מילה-במילה. נדרשת משיכה ישירה לפני שייכנס לרשימת ההוקרות.",
        "פרס הדי לאמאר לחוקרות פורצות דרך (2018): הוצא מרשימת ההוקרות בסבב הזה, משום שהמקור היחיד הוא המוזיאון היהודי בווינה ולא העירייה המעניקה, ומשום שפרס הנקרא על שמה ומוענק לאחרות אינו הוקרה שניתנה לה על ההמצאה. נדרשת הכרעה עקרונית, ואישור מאתר העירייה."
    ],

    "numbers": [
        {"kind": "quoted", "field": "act", "value": "2292387", "as_written": "2,292,387",
         "quote": "Number 2,292,387 United States Patent Office Application, June 10, 1941, Serial No. 397,412.",
         "quote_en": "Number 2,292,387 United States Patent Office Application, June 10, 1941, Serial No. 397,412.",
         "citation_url": MEMOIR},
        {"kind": "quoted", "field": "act", "value": "397412", "as_written": "397,412",
         "quote": Q_APP, "quote_en": Q_APP, "citation_url": PATENT_URL},
        {"kind": "quoted", "field": "act", "value": "10", "as_written": "10 ביוני 1941",
         "quote": Q_APP, "quote_en": Q_APP, "citation_url": PATENT_URL},
        {"kind": "quoted", "field": "act", "value": "11", "as_written": "11 באוגוסט 1942",
         "quote": Q_GRANT, "quote_en": Q_GRANT, "citation_url": PATENT_PDF},
        {"kind": "quoted", "field": "act", "value": "88", "as_written": "88",
         "quote": Q_88, "quote_en": Q_88, "citation_url": PATENT_URL},
        {"kind": "quoted", "field": "description", "value": "88", "as_written": "88",
         "quote": Q_88, "quote_en": Q_88, "citation_url": PATENT_URL},
        {"kind": "quoted", "field": "summary_short", "value": "88", "as_written": "88",
         "quote": Q_88, "quote_en": Q_88, "citation_url": PATENT_URL},
        {"kind": "quoted", "field": "the_moment", "value": "13", "as_written": "13 באוגוסט 1941",
         "quote": Q_CANCEL, "quote_en": Q_CANCEL, "citation_url": CASEFILE39},
        {"kind": "quoted", "field": "ripple", "value": "13", "as_written": "13 באוגוסט 1941",
         "quote": Q_CANCEL, "quote_en": Q_CANCEL, "citation_url": CASEFILE39},
        {"kind": "quoted", "field": "the_moment", "value": "31", "as_written": "31 באוקטובר",
         "quote": "Los Angeles, Calif.\nOctober 31, 1941", "quote_en": "Los Angeles, Calif.\nOctober 31, 1941",
         "citation_url": CASEFILE39},
        {"kind": "quoted", "field": "ripple", "value": "1932", "as_written": "1932",
         "quote": Q_PRIOR, "quote_en": Q_PRIOR, "citation_url": ROTHMAN24},
        {"kind": "quoted", "field": "ripple", "value": "1938", "as_written": "1938",
         "quote": Q_PRIOR, "quote_en": Q_PRIOR, "citation_url": ROTHMAN24},
        {"kind": "quoted", "field": "the_moment", "value": "1932", "as_written": "1932",
         "quote": Q_PRIOR, "quote_en": Q_PRIOR, "citation_url": ROTHMAN24},
        {"kind": "quoted", "field": "the_moment", "value": "1938", "as_written": "1938",
         "quote": Q_PRIOR, "quote_en": Q_PRIOR, "citation_url": ROTHMAN24},
        {"kind": "quoted", "field": "ripple", "value": "25", "as_written": "25 דולר",
         "quote": Q_FEE, "quote_en": Q_FEE, "citation_url": ROTHMAN24},
        {"kind": "quoted", "field": "summary_short", "value": "25", "as_written": "25 דולר",
         "quote": Q_FEE, "quote_en": Q_FEE, "citation_url": ROTHMAN24},
        {"kind": "quoted", "field": "ripple", "value": "1955", "as_written": "1955",
         "quote": Q_BLADES55, "quote_en": Q_BLADES55, "citation_url": ROTHMAN19},
        {"kind": "quoted", "field": "ripple", "value": "1963", "as_written": "1963",
         "quote": Q_BLADES, "quote_en": Q_BLADES, "citation_url": ROTHMAN19},
        {"kind": "quoted", "field": "summary_short", "value": "1963", "as_written": "1963",
         "quote": Q_BLADES, "quote_en": Q_BLADES, "citation_url": ROTHMAN19},
        {"kind": "quoted", "field": "ripple", "value": "2000", "as_written": "2,000",
         "quote": Q_DIXON, "quote_en": Q_DIXON, "citation_url": ROTHMAN24},
        {"kind": "quoted", "field": "aftermath", "value": "1959", "as_written": "11 באוגוסט 1959",
         "quote": Q_EXPIRE, "quote_en": Q_EXPIRE, "citation_url": PATENT_URL},
        {"kind": "quoted", "field": "aftermath", "value": "58", "as_written": "58",
         "quote": Q_ANTHEIL_DEATH, "quote_en": Q_ANTHEIL_DEATH, "citation_url": LEHRMAN},
        {"kind": "quoted", "field": "aftermath", "value": "49", "as_written": "49 אחוזים",
         "quote": Q_WILAN, "quote_en": Q_WILAN, "citation_url": NEAMAN},
        {"kind": "quoted", "field": "recognition", "value": "1997", "as_written": "1997",
         "quote": Q_EFF, "quote_en": Q_EFF, "citation_url": EFF},
        {"kind": "quoted", "field": "recognition", "value": "82", "as_written": "82",
         "quote": Q_82, "quote_en": Q_82, "citation_url": NEAMAN},
        {"kind": "quoted", "field": "origin_story", "value": "1940", "as_written": "1940",
         "quote": Q_1940, "quote_en": Q_1940, "citation_url": MEMOIR},
        {"kind": "quoted", "field": "act", "value": "16", "as_written": "שש-עשרה",
         "quote": Q_16, "quote_en": Q_16, "citation_url": LEHRMAN},
        {"kind": "quoted", "field": "summary_short", "value": "16", "as_written": "שישה-עשר",
         "quote": Q_16, "quote_en": Q_16, "citation_url": LEHRMAN}
    ],
}

doc["honors"].sort(key=lambda h: h["year"])

out = os.path.join(HERE, "canonical.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print("sections:", len(sections))
for s in sections:
    print("  -", s["heading"] or "(ללא כותרת)")
print("keys:", len(doc))
print("wrote", out)
