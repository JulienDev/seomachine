#!/usr/bin/env python3
"""
Update non-English TiviMate comparison drafts with Android TV / Fire TV sideloading info.
"""
import os
import glob
import re

DRAFTS_DIR = "/Users/juliendev/projects/www_iptv-one_app/seomachine/drafts"

# Already handled files (EN files + already manually updated)
SKIP_FILES = {
    "iptv-one-vs-tivimate-en-2026-03-16.md",
    "iptv-one-vs-tivimate-en-2026-03-17.md",
    "tivimate-alternative-en-2026-03-16.md",
    "tivimate-alternative-en-2026-03-17.md",
    "iptv-one-vs-tivimate-comparatif-fr-2026-03-17.md",  # already done manually
    "iptv-one-vs-tivimate-vergleich-de-2026-03-17.md",   # already done manually
}

# Language-specific translations for sideloading text
SIDELOADING_TEXTS = {
    "fr": {
        "sideloading_platform": "Sur Fire TV et Android TV, vous pouvez installer IPTV One via sideloading avec l'application Downloader (code **1411180**) ou en t\u00e9l\u00e9chargeant directement l'APK depuis `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "Sur Fire TV, utilisez l'application Downloader avec le code **1411180** (ou rendez-vous sur [aftv.news/1411180](https://aftv.news/1411180)) pour installer l'APK directement.",
        "firetv_faq": "Oui. IPTV One est disponible pour Fire TV et Fire TV Stick via sideloading. Utilisez l'application Downloader avec le code **1411180** (ou t\u00e9l\u00e9chargez l'APK depuis `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One est d\u00e9sormais disponible sur Fire TV, le terrain de pr\u00e9dilection de TiviMate, via sideloading avec Downloader (code **1411180**).",
        "six": "Six", "eight": "Huit",
        "six_lower": "six", "eight_lower": "huit",
    },
    "de": {
        "sideloading_platform": "Auf Fire TV und Android TV k\u00f6nnen Sie IPTV One per Sideloading mit der Downloader-App installieren (Code **1411180**) oder das APK direkt von `https://www.iptv-one.app/downloads/onetv/latest.apk` herunterladen.",
        "firetv_cta": "Auf Fire TV nutzen Sie die Downloader-App mit dem Code **1411180** (oder besuchen Sie [aftv.news/1411180](https://aftv.news/1411180)), um das APK direkt zu installieren.",
        "firetv_faq": "Ja. IPTV One ist f\u00fcr Fire TV und Fire TV Stick per Sideloading verf\u00fcgbar. Nutzen Sie die Downloader-App mit dem Code **1411180** (oder laden Sie das APK direkt von `https://www.iptv-one.app/downloads/onetv/latest.apk` herunter).",
        "verdict_extra": "IPTV One ist jetzt auch auf Fire TV verf\u00fcgbar, dem Heimatgebiet von TiviMate, per Sideloading mit Downloader (Code **1411180**).",
        "six": "Sechs", "eight": "Acht",
        "six_lower": "sechs", "eight_lower": "acht",
    },
    "es": {
        "sideloading_platform": "En Fire TV y Android TV, puedes instalar IPTV One mediante sideloading con la aplicaci\u00f3n Downloader (c\u00f3digo **1411180**) o descargando directamente el APK desde `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "En Fire TV, usa la aplicaci\u00f3n Downloader con el c\u00f3digo **1411180** (o visita [aftv.news/1411180](https://aftv.news/1411180)) para instalar el APK directamente.",
        "firetv_faq": "S\u00ed. IPTV One est\u00e1 disponible para Fire TV y Fire TV Stick mediante sideloading. Usa la aplicaci\u00f3n Downloader con el c\u00f3digo **1411180** (o descarga el APK desde `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One ahora tambi\u00e9n est\u00e1 disponible en Fire TV, el terreno de TiviMate, mediante sideloading con Downloader (c\u00f3digo **1411180**).",
        "six": "Seis", "eight": "Ocho",
        "six_lower": "seis", "eight_lower": "ocho",
    },
    "nl": {
        "sideloading_platform": "Op Fire TV en Android TV kun je IPTV One installeren via sideloading met de Downloader-app (code **1411180**) of door de APK rechtstreeks te downloaden van `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "Op Fire TV gebruik je de Downloader-app met code **1411180** (of ga naar [aftv.news/1411180](https://aftv.news/1411180)) om de APK direct te installeren.",
        "firetv_faq": "Ja. IPTV One is beschikbaar voor Fire TV en Fire TV Stick via sideloading. Gebruik de Downloader-app met code **1411180** (of download de APK van `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One is nu ook beschikbaar op Fire TV, het thuisterrein van TiviMate, via sideloading met Downloader (code **1411180**).",
        "six": "Zes", "eight": "Acht",
        "six_lower": "zes", "eight_lower": "acht",
    },
    "sv": {
        "sideloading_platform": "P\u00e5 Fire TV och Android TV kan du installera IPTV One via sideloading med Downloader-appen (kod **1411180**) eller genom att ladda ner APK:n direkt fr\u00e5n `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "P\u00e5 Fire TV anv\u00e4nder du Downloader-appen med kod **1411180** (eller bes\u00f6k [aftv.news/1411180](https://aftv.news/1411180)) f\u00f6r att installera APK:n direkt.",
        "firetv_faq": "Ja. IPTV One finns tillg\u00e4nglig f\u00f6r Fire TV och Fire TV Stick via sideloading. Anv\u00e4nd Downloader-appen med kod **1411180** (eller ladda ner APK:n fr\u00e5n `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One finns nu \u00e4ven p\u00e5 Fire TV, TiviMates hemmaplan, via sideloading med Downloader (kod **1411180**).",
        "six": "Sex", "eight": "\u00c5tta",
        "six_lower": "sex", "eight_lower": "\u00e5tta",
    },
    "no": {
        "sideloading_platform": "P\u00e5 Fire TV og Android TV kan du installere IPTV One via sideloading med Downloader-appen (kode **1411180**) eller ved \u00e5 laste ned APK-en direkte fra `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "P\u00e5 Fire TV bruker du Downloader-appen med kode **1411180** (eller g\u00e5 til [aftv.news/1411180](https://aftv.news/1411180)) for \u00e5 installere APK-en direkte.",
        "firetv_faq": "Ja. IPTV One er tilgjengelig for Fire TV og Fire TV Stick via sideloading. Bruk Downloader-appen med kode **1411180** (eller last ned APK-en fra `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One er n\u00e5 ogs\u00e5 tilgjengelig p\u00e5 Fire TV, TiviMates hjemmebane, via sideloading med Downloader (kode **1411180**).",
        "six": "Seks", "eight": "\u00c5tte",
        "six_lower": "seks", "eight_lower": "\u00e5tte",
    },
    "it": {
        "sideloading_platform": "Su Fire TV e Android TV, puoi installare IPTV One tramite sideloading con l'app Downloader (codice **1411180**) o scaricando direttamente l'APK da `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "Su Fire TV, usa l'app Downloader con il codice **1411180** (o visita [aftv.news/1411180](https://aftv.news/1411180)) per installare l'APK direttamente.",
        "firetv_faq": "S\u00ec. IPTV One \u00e8 disponibile per Fire TV e Fire TV Stick tramite sideloading. Usa l'app Downloader con il codice **1411180** (o scarica l'APK da `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One \u00e8 ora disponibile anche su Fire TV, il territorio di TiviMate, tramite sideloading con Downloader (codice **1411180**).",
        "six": "Sei", "eight": "Otto",
        "six_lower": "sei", "eight_lower": "otto",
    },
    "da": {
        "sideloading_platform": "P\u00e5 Fire TV og Android TV kan du installere IPTV One via sideloading med Downloader-appen (kode **1411180**) eller ved at downloade APK'en direkte fra `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "P\u00e5 Fire TV bruger du Downloader-appen med kode **1411180** (eller bes\u00f8g [aftv.news/1411180](https://aftv.news/1411180)) for at installere APK'en direkte.",
        "firetv_faq": "Ja. IPTV One er tilg\u00e6ngelig til Fire TV og Fire TV Stick via sideloading. Brug Downloader-appen med kode **1411180** (eller download APK'en fra `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One er nu ogs\u00e5 tilg\u00e6ngelig p\u00e5 Fire TV, TiviMates hjemmebane, via sideloading med Downloader (kode **1411180**).",
        "six": "Seks", "eight": "Otte",
        "six_lower": "seks", "eight_lower": "otte",
    },
    "fi": {
        "sideloading_platform": "Fire TV:ll\u00e4 ja Android TV:ll\u00e4 voit asentaa IPTV Onen sivulatauksella Downloader-sovelluksella (koodi **1411180**) tai lataamalla APK:n suoraan osoitteesta `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "Fire TV:ll\u00e4 k\u00e4yt\u00e4 Downloader-sovellusta koodilla **1411180** (tai vieraile osoitteessa [aftv.news/1411180](https://aftv.news/1411180)) asentaaksesi APK:n suoraan.",
        "firetv_faq": "Kyll\u00e4. IPTV One on saatavilla Fire TV:lle ja Fire TV Stickille sivulatauksella. K\u00e4yt\u00e4 Downloader-sovellusta koodilla **1411180** (tai lataa APK osoitteesta `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One on nyt saatavilla my\u00f6s Fire TV:ll\u00e4, TiviMaten kotikent\u00e4ll\u00e4, sivulatauksella Downloader-sovelluksella (koodi **1411180**).",
        "six": "Kuusi", "eight": "Kahdeksan",
        "six_lower": "kuusi", "eight_lower": "kahdeksan",
    },
    "tr": {
        "sideloading_platform": "Fire TV ve Android TV'de IPTV One'\\u0131 Downloader uygulamas\\u0131 ile sideloading yaparak (kod **1411180**) veya APK'y\\u0131 do\\u011frudan `https://www.iptv-one.app/downloads/onetv/latest.apk` adresinden indirerek y\\u00fckleyebilirsiniz.",
        "firetv_cta": "Fire TV'de Downloader uygulamas\\u0131n\\u0131 **1411180** koduyla kullan\\u0131n (veya [aftv.news/1411180](https://aftv.news/1411180) adresini ziyaret edin) ve APK'y\\u0131 do\\u011frudan y\\u00fckleyin.",
        "firetv_faq": "Evet. IPTV One, Fire TV ve Fire TV Stick i\\u00e7in sideloading ile kullan\\u0131labilir. Downloader uygulamas\\u0131n\\u0131 **1411180** koduyla kullan\\u0131n (veya APK'y\\u0131 `https://www.iptv-one.app/downloads/onetv/latest.apk` adresinden indirin).",
        "verdict_extra": "IPTV One art\\u0131k TiviMate'in ev sahas\\u0131 olan Fire TV'de de mevcut; Downloader ile sideloading yap\\u0131labilir (kod **1411180**).",
        "six": "Alt\\u0131", "eight": "Sekiz",
        "six_lower": "alt\\u0131", "eight_lower": "sekiz",
    },
    "ar": {
        "sideloading_platform": "\\u0639\\u0644\\u0649 Fire TV \\u0648Android TV\\u060c \\u064a\\u0645\\u0643\\u0646\\u0643 \\u062a\\u062b\\u0628\\u064a\\u062a IPTV One \\u0639\\u0628\\u0631 \\u0627\\u0644\\u062a\\u062d\\u0645\\u064a\\u0644 \\u0627\\u0644\\u062c\\u0627\\u0646\\u0628\\u064a \\u0628\\u0627\\u0633\\u062a\\u062e\\u062f\\u0627\\u0645 \\u062a\\u0637\\u0628\\u064a\\u0642 Downloader (\\u0627\\u0644\\u0631\\u0645\\u0632 **1411180**) \\u0623\\u0648 \\u0628\\u062a\\u062d\\u0645\\u064a\\u0644 \\u0645\\u0644\\u0641 APK \\u0645\\u0628\\u0627\\u0634\\u0631\\u0629 \\u0645\\u0646 `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "\\u0639\\u0644\\u0649 Fire TV\\u060c \\u0627\\u0633\\u062a\\u062e\\u062f\\u0645 \\u062a\\u0637\\u0628\\u064a\\u0642 Downloader \\u0628\\u0627\\u0644\\u0631\\u0645\\u0632 **1411180** (\\u0623\\u0648 \\u0642\\u0645 \\u0628\\u0632\\u064a\\u0627\\u0631\\u0629 [aftv.news/1411180](https://aftv.news/1411180)) \\u0644\\u062a\\u062b\\u0628\\u064a\\u062a APK \\u0645\\u0628\\u0627\\u0634\\u0631\\u0629.",
        "firetv_faq": "\\u0646\\u0639\\u0645. IPTV One \\u0645\\u062a\\u0627\\u062d \\u0644\\u0623\\u062c\\u0647\\u0632\\u0629 Fire TV \\u0648Fire TV Stick \\u0639\\u0628\\u0631 \\u0627\\u0644\\u062a\\u062d\\u0645\\u064a\\u0644 \\u0627\\u0644\\u062c\\u0627\\u0646\\u0628\\u064a. \\u0627\\u0633\\u062a\\u062e\\u062f\\u0645 \\u062a\\u0637\\u0628\\u064a\\u0642 Downloader \\u0628\\u0627\\u0644\\u0631\\u0645\\u0632 **1411180** (\\u0623\\u0648 \\u062d\\u0645\\u0651\\u0644 APK \\u0645\\u0646 `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "IPTV One \\u0645\\u062a\\u0627\\u062d \\u0627\\u0644\\u0622\\u0646 \\u0623\\u064a\\u0636\\u0627\\u064b \\u0639\\u0644\\u0649 Fire TV\\u060c \\u0645\\u0644\\u0639\\u0628 TiviMate\\u060c \\u0639\\u0628\\u0631 \\u0627\\u0644\\u062a\\u062d\\u0645\\u064a\\u0644 \\u0627\\u0644\\u062c\\u0627\\u0646\\u0628\\u064a \\u0628\\u0627\\u0633\\u062a\\u062e\\u062f\\u0627\\u0645 Downloader (\\u0627\\u0644\\u0631\\u0645\\u0632 **1411180**).",
        "six": "\\u0633\\u062a", "eight": "\\u062b\\u0645\\u0627\\u0646\\u064a",
        "six_lower": "\\u0633\\u062a", "eight_lower": "\\u062b\\u0645\\u0627\\u0646\\u064a",
    },
    "pt": {
        "sideloading_platform": "No Fire TV e Android TV, pode instalar o IPTV One via sideloading com a aplica\\u00e7\\u00e3o Downloader (c\\u00f3digo **1411180**) ou descarregando diretamente o APK de `https://www.iptv-one.app/downloads/onetv/latest.apk`.",
        "firetv_cta": "No Fire TV, utilize a aplica\\u00e7\\u00e3o Downloader com o c\\u00f3digo **1411180** (ou visite [aftv.news/1411180](https://aftv.news/1411180)) para instalar o APK diretamente.",
        "firetv_faq": "Sim. O IPTV One est\\u00e1 dispon\\u00edvel para Fire TV e Fire TV Stick via sideloading. Utilize a aplica\\u00e7\\u00e3o Downloader com o c\\u00f3digo **1411180** (ou descarregue o APK de `https://www.iptv-one.app/downloads/onetv/latest.apk`).",
        "verdict_extra": "O IPTV One est\\u00e1 agora tamb\\u00e9m dispon\\u00edvel no Fire TV, o territ\\u00f3rio do TiviMate, via sideloading com Downloader (c\\u00f3digo **1411180**).",
        "six": "Seis", "eight": "Oito",
        "six_lower": "seis", "eight_lower": "oito",
    },
}


def detect_lang(filename):
    """Detect language from filename."""
    # Check for known language patterns in filename
    lang_patterns = {
        "comparatif-fr": "fr", "-fr-": "fr",
        "vergleich-de": "de", "-de-": "de",
        "comparativa-es": "es", "comparacion-es": "es", "-es-": "es", "es_419": "es",
        "vergelijking-nl": "nl", "-nl-": "nl",
        "jamforelse-sv": "sv", "-sv-": "sv",
        "sammenligning-no": "no", "-no-": "no",
        "confronto-it": "it", "-it-": "it",
        "sammenligning-da": "da", "-da-": "da",
        "vertailu-fi": "fi", "-fi-": "fi",
        "karsilastirma-tr": "tr", "-tr-": "tr",
        "muqarana-ar": "ar", "-ar-": "ar",
        "comparacao-pt": "pt", "-pt-": "pt",
    }
    for pattern, lang in lang_patterns.items():
        if pattern in filename:
            return lang
    return None


def update_file(filepath):
    """Apply Android TV / Fire TV sideloading updates to a file."""
    filename = os.path.basename(filepath)
    lang = detect_lang(filename)

    if lang not in SIDELOADING_TEXTS:
        print(f"  SKIP (no translations for lang={lang}): {filename}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    texts = SIDELOADING_TEXTS[lang]

    # 1. Update platform line in overview table
    # Pattern: IPTV One platforms in table (without Android TV, Fire TV)
    content = re.sub(
        r'(\| \*\*(?:Platt?form(?:e[nrs]?|ar)?|Piattaforme|Platt?forme?s?|Alustat|Platformlar|المنصات)\*\* \| )(Android, iOS, macOS, Windows, Linux)( \|)',
        r'\1Android, iOS, macOS, Windows, Linux, Android TV, Fire TV\3',
        content
    )

    # 2. Add sideloading info after IPTV One platform description
    # Look for the pattern where IPTV One platforms are listed in body text
    # This varies by language but follows pattern: "IPTV One runs on Android, iOS, macOS, Windows and Linux"
    platform_patterns = [
        # French
        (r'(\*\*IPTV One\*\* fonctionne sur Android, iOS, macOS, Windows et Linux)',
         r'\1, Android TV et Fire TV'),
        # German
        (r'(\*\*IPTV One\*\* läuft auf Android, iOS, macOS, Windows und Linux)',
         r'\1, Android TV und Fire TV'),
        # Spanish
        (r'(\*\*IPTV One\*\* funciona en Android, iOS, macOS, Windows y Linux)',
         r'\1, Android TV y Fire TV'),
        # Dutch
        (r'(\*\*IPTV One\*\* (?:draait|werkt) op Android, iOS, macOS, Windows en Linux)',
         r'\1, Android TV en Fire TV'),
        # Swedish
        (r'(\*\*IPTV One\*\* (?:körs|fungerar) på Android, iOS, macOS, Windows och Linux)',
         r'\1, Android TV och Fire TV'),
        # Norwegian
        (r'(\*\*IPTV One\*\* kjører på Android, iOS, macOS, Windows og Linux)',
         r'\1, Android TV og Fire TV'),
        # Italian
        (r'(\*\*IPTV One\*\* funziona su Android, iOS, macOS, Windows e Linux)',
         r'\1, Android TV e Fire TV'),
        # Danish
        (r'(\*\*IPTV One\*\* kører på Android, iOS, macOS, Windows og Linux)',
         r'\1, Android TV og Fire TV'),
        # Finnish
        (r'(\*\*IPTV One\*\* toimii Android(?:ill)?a, iOS)',
         None),  # Complex, handle separately
        # Turkish
        (r'(\*\*IPTV One\*\* Android, iOS, macOS, Windows ve Linux\'ta çalışır)',
         r'\1, Android TV ve Fire TV'),
        # Portuguese
        (r'(\*\*IPTV One\*\* funciona em Android, iOS, macOS, Windows e Linux)',
         r'\1, Android TV e Fire TV'),
    ]

    for pattern, replacement in platform_patterns:
        if replacement:
            content = re.sub(pattern, replacement, content)

    # Add sideloading sentence after the platform mention if not already present
    if "Downloader" not in content and "1411180" not in content:
        # Find the paragraph about IPTV One platforms and add sideloading info
        sideloading_text = texts["sideloading_platform"]

        # Try to insert after "Apple TV" mention in the IPTV One platform paragraph
        apple_tv_patterns = [
            r'(avec le support Apple TV (?:à venir|qui arrive prochainement)\. )',
            r'(mit Apple-TV-Unterstützung (?:in Kürze|folgt in Kürze)\. )',
            r'(con soporte para Apple TV próximamente\. )',
            r'(met Apple TV-ondersteuning (?:die binnenkort beschikbaar komt|die eraan komt)\. )',
            r'(med Apple TV-stöd (?:på väg|som snart blir tillgängligt)\. )',
            r'(med Apple TV-støtte (?:like rundt hjørnet|på vei)\. )',
            r'(con il supporto Apple TV in arrivo\. )',
            r'(med Apple TV-understøttelse lige om hjørnet\. )',
            r'(ja Apple TV -tuki on tulossa pian\. )',
            r'(Apple TV desteği de çok yakında geliyor\. )',
            r'(com suporte para Apple TV a caminho\. )',
            r'(مع دعم Apple TV في الطريق\. )',
        ]
        for pattern in apple_tv_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, r'\1' + sideloading_text + ' ', content)
                break

    # 3. Update "six platforms" -> "eight platforms" in verdict section
    six = texts["six"]
    eight = texts["eight"]
    six_lower = texts["six_lower"]
    eight_lower = texts["eight_lower"]

    # Replace in verdict numbered list (capitalized)
    content = content.replace(f"**{six} ", f"**{eight} ")

    # Replace in FAQ answers (lowercase)
    content = re.sub(
        rf'{six_lower} (?:platt?form(?:e[nrs]?|ar)?|piattaforme|platt?forme?s?|alustaa|platform(?:u|lar)?|منصات)',
        lambda m: m.group(0).replace(six_lower, eight_lower),
        content
    )

    # Also update platform lists in verdict: add Android TV, Fire TV
    verdict_platform_patterns = [
        ("Android, iOS, macOS, Windows, Linux und bald Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV und bald Apple TV"),
        ("Android, iOS, macOS, Windows, Linux, et bientôt Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, et bientôt Apple TV"),
        ("Android, iOS, macOS, Windows, Linux y próximamente Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV y próximamente Apple TV"),
        ("Android, iOS, macOS, Windows, Linux en binnenkort Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV en binnenkort Apple TV"),
        ("Android, iOS, macOS, Windows, Linux och snart Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV och snart Apple TV"),
        ("Android, iOS, macOS, Windows, Linux og snart Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV og snart Apple TV"),
        ("Android, iOS, macOS, Windows, Linux e presto Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV e presto Apple TV"),
        ("Android, iOS, macOS, Windows, Linux e em breve Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV e em breve Apple TV"),
        ("Android, iOS, macOS, Windows, Linux ve yakında Apple TV", "Android, iOS, macOS, Windows, Linux, Android TV, Fire TV ve yakında Apple TV"),
    ]
    for old, new in verdict_platform_patterns:
        content = content.replace(old, new)

    # Add verdict extra sentence about Fire TV being TiviMate's turf
    verdict_extra = texts["verdict_extra"]
    if verdict_extra and verdict_extra not in content:
        # Insert after the first point in the verdict list
        # Look for the line ending with "TiviMate" works only on Android
        tivimate_only_patterns = [
            "TiviMate se limite à Android.",
            "TiviMate funktioniert nur auf Android.",
            "TiviMate läuft nur auf Android.",
            "TiviMate solo funciona en Android.",
            "TiviMate werkt alleen op Android.",
            "TiviMate fungerar bara på Android.",
            "TiviMate fungerer bare på Android.",
            "TiviMate kjører bare på Android.",
            "TiviMate funziona solo su Android.",
            "TiviMate fungerer kun på Android.",
            "TiviMate toimii vain Androidilla.",
            "TiviMate yalnızca Android'de çalışıyor.",
            "TiviMate funciona apenas em Android.",
        ]
        for pattern in tivimate_only_patterns:
            if pattern in content:
                content = content.replace(pattern, f"{pattern} {verdict_extra}")
                break

    # 4. Update Fire TV FAQ answer
    firetv_faq = texts["firetv_faq"]
    # Replace the existing Fire TV FAQ answer
    faq_patterns = [
        # French
        (r'Oui\. IPTV One est disponible pour Fire TV et Fire TV Stick via Google Play\.[^*]+?(?=\n\n---)',
         firetv_faq + " Il fonctionne de concert avec les versions Android, iOS, macOS, Windows et Linux, avec synchronisation cloud complète entre tous les appareils."),
        # German
        (r'Ja\. IPTV One ist für Fire TV und Fire TV Stick über Google Play verfügbar\.[^*]+?(?=\n\n---)',
         firetv_faq + " Es funktioniert nahtlos mit den Android-, iOS-, macOS-, Windows- und Linux-Versionen, mit vollem Cloud-Sync zwischen allen Geräten."),
    ]
    # Generic approach: find the Fire TV FAQ section and update it
    # This is complex with regex, so let's do targeted replacements

    # Update Fire TV FAQ - look for "via Google Play" or "via Amazon Appstore" and replace
    google_play_faq_replacements = [
        ("via Google Play. Il fonctionne de concert", "via sideloading. Utilisez l'application Downloader avec le code **1411180** (ou téléchargez l'APK depuis `https://www.iptv-one.app/downloads/onetv/latest.apk`). Il fonctionne de concert"),
        ("via Google Play. Il fonctionne de pair", "via sideloading. Utilisez l'application Downloader avec le code **1411180** (ou téléchargez l'APK depuis `https://www.iptv-one.app/downloads/onetv/latest.apk`). Il fonctionne de pair"),
        ("über Google Play verfügbar. Es funktioniert", "per Sideloading verfügbar. Nutzen Sie die Downloader-App mit dem Code **1411180** (oder laden Sie das APK direkt von `https://www.iptv-one.app/downloads/onetv/latest.apk` herunter). Es funktioniert"),
        ("über Google Play verfügbar. Es läuft", "per Sideloading verfügbar. Nutzen Sie die Downloader-App mit dem Code **1411180** (oder laden Sie das APK direkt von `https://www.iptv-one.app/downloads/onetv/latest.apk` herunter). Es läuft"),
        ("a través de Google Play. Funciona", "mediante sideloading. Usa la aplicación Downloader con el código **1411180** (o descarga el APK desde `https://www.iptv-one.app/downloads/onetv/latest.apk`). Funciona"),
        ("via Google Play. Het werkt", "via sideloading. Gebruik de Downloader-app met code **1411180** (of download de APK van `https://www.iptv-one.app/downloads/onetv/latest.apk`). Het werkt"),
        ("via Google Play. Den fungerar", "via sideloading. Använd Downloader-appen med kod **1411180** (eller ladda ner APK:n från `https://www.iptv-one.app/downloads/onetv/latest.apk`). Den fungerar"),
        ("via Google Play. Den fungerer", "via sideloading. Bruk Downloader-appen med kode **1411180** (eller last ned APK-en fra `https://www.iptv-one.app/downloads/onetv/latest.apk`). Den fungerer"),
        ("tramite Google Play. Funziona", "tramite sideloading. Usa l'app Downloader con il codice **1411180** (o scarica l'APK da `https://www.iptv-one.app/downloads/onetv/latest.apk`). Funziona"),
        ("via Google Play. Den fungerer sammen", "via sideloading. Brug Downloader-appen med kode **1411180** (eller download APK'en fra `https://www.iptv-one.app/downloads/onetv/latest.apk`). Den fungerer sammen"),
        ("Google Playn kautta. Se toimii", "sivulatauksella. Käytä Downloader-sovellusta koodilla **1411180** (tai lataa APK osoitteesta `https://www.iptv-one.app/downloads/onetv/latest.apk`). Se toimii"),
        ("Google Play üzerinden Fire TV", "sideloading ile Fire TV"),
        ("Fire TV ve Fire TV Stick için mevcut. Android", "Fire TV ve Fire TV Stick için sideloading ile kullanılabilir. Downloader uygulamasını **1411180** koduyla kullanın (veya APK'yı `https://www.iptv-one.app/downloads/onetv/latest.apk` adresinden indirin). Android"),
        ("via Amazon Appstore. Funciona", "via sideloading. Utilize a aplicação Downloader com o código **1411180** (ou descarregue o APK de `https://www.iptv-one.app/downloads/onetv/latest.apk`). Funciona"),
        ("via Google Play. Funciona junto", "via sideloading. Utilize a aplicação Downloader com o código **1411180** (ou descarregue o APK de `https://www.iptv-one.app/downloads/onetv/latest.apk`). Funciona junto"),
    ]
    for old, new in google_play_faq_replacements:
        content = content.replace(old, new)

    # Arabic Fire TV FAQ
    if lang == "ar":
        content = content.replace(
            "عبر Google Play. يعمل جنباً إلى جنب",
            "عبر التحميل الجانبي. استخدم تطبيق Downloader بالرمز **1411180** (أو حمّل APK من `https://www.iptv-one.app/downloads/onetv/latest.apk`). يعمل جنباً إلى جنب"
        )

    # 5. Update download CTA at the end
    cta_additions = {
        "fr": (" C'est gratuit pour commencer.", f" {texts['firetv_cta']} C'est gratuit pour commencer."),
        "de": (" Der Einstieg ist kostenlos.", f" {texts['firetv_cta']} Der Einstieg ist kostenlos."),
        "es": (" Empieza gratis.", f" {texts['firetv_cta']} Empieza gratis."),
        "nl": (" Gratis om te starten.", f" {texts['firetv_cta']} Gratis om te starten."),
        "sv": (" Det är gratis att börja.", f" {texts['firetv_cta']} Det är gratis att börja."),
        "no": (" Det er gratis å starte.", f" {texts['firetv_cta']} Det er gratis å starte."),
        "it": (" Si inizia gratis.", f" {texts['firetv_cta']} Si inizia gratis."),
        "da": (" Det er gratis at starte.", f" {texts['firetv_cta']} Det er gratis at starte."),
        "fi": (" Aloittaminen on ilmaista.", f" {texts['firetv_cta']} Aloittaminen on ilmaista."),
        "tr": (" Başlamak ücretsiz.", f" {texts['firetv_cta']} Başlamak ücretsiz."),
        "pt": (" É grátis para começar.", f" {texts['firetv_cta']} É grátis para começar."),
    }
    if lang in cta_additions:
        old_cta, new_cta = cta_additions[lang]
        # Only replace the first occurrence (the main CTA, not FAQ)
        if old_cta in content and texts['firetv_cta'] not in content:
            content = content.replace(old_cta, new_cta, 1)

    # Arabic CTA
    if lang == "ar" and "1411180" not in content.split("البدء مجاني")[0] if "البدء مجاني" in content else True:
        content = content.replace(
            " البدء مجاني.",
            f" {texts['firetv_cta']} البدء مجاني.",
            1
        )

    # Also handle Norwegian variant
    content = content.replace(
        " Det er gratis å komme i gang.",
        f" {texts.get('firetv_cta', '')} Det er gratis å komme i gang." if lang == "no" else " Det er gratis å komme i gang."
    )
    # Swedish variant
    content = content.replace(
        " Kom igång gratis.",
        f" {texts.get('firetv_cta', '')} Kom igång gratis." if lang == "sv" else " Kom igång gratis."
    )
    # Dutch variant
    content = content.replace(
        " Starten is gratis.",
        f" {texts.get('firetv_cta', '')} Starten is gratis." if lang == "nl" else " Starten is gratis."
    )

    # Also update FAQ platform counts
    # Replace "sechs/seis/sei/etc. Plattformen/plataformas/etc." in FAQ
    faq_platform_replacements = [
        ("six plateformes (Android, iOS, macOS, Windows, Linux, Apple TV)", "huit plateformes (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("sechs Plattformen (Android, iOS, macOS, Windows, Linux, Apple TV)", "acht Plattformen (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("seis plataformas (Android, iOS, macOS, Windows, Linux, Apple TV)", "ocho plataformas (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("zes platforms (Android, iOS, macOS, Windows, Linux, Apple TV)", "acht platforms (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("sex plattformar (Android, iOS, macOS, Windows, Linux, Apple TV)", "åtta plattformar (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("seks plattformer (Android, iOS, macOS, Windows, Linux, Apple TV)", "åtte plattformer (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("sei piattaforme (Android, iOS, macOS, Windows, Linux, Apple TV)", "otto piattaforme (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("seks platforme (Android, iOS, macOS, Windows, Linux, Apple TV)", "otte platforme (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("kuutta alustaa (Android, iOS, macOS, Windows, Linux, Apple TV)", "kahdeksaa alustaa (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("altı platformu destekliyor (Android, iOS, macOS, Windows, Linux, Apple TV)", "sekiz platformu destekliyor (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("seis plataformas (Android, iOS, macOS, Windows, Linux, Apple TV)", "oito plataformas (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV, Apple TV)"),
        ("ست منصات (Android وiOS وmacOS وWindows وLinux وApple TV)", "ثماني منصات (Android وiOS وmacOS وWindows وLinux وAndroid TV وFire TV وApple TV)"),
        # Swedish variant with "fem" (five)
        ("fem plattformar idag (Android, iOS, macOS, Windows, Linux) med Apple TV-stöd på väg", "åtta plattformar (Android, iOS, macOS, Windows, Linux, Android TV, Fire TV) med Apple TV-stöd på väg"),
    ]
    for old, new in faq_platform_replacements:
        content = content.replace(old, new)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  UPDATED: {filename}")
        return True
    else:
        print(f"  NO CHANGES: {filename}")
        return False


def main():
    patterns = [
        os.path.join(DRAFTS_DIR, "iptv-one-vs-tivimate-*.md"),
        os.path.join(DRAFTS_DIR, "tivimate-alternative-*.md"),
    ]

    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern))

    # Filter out EN files and already-handled files
    files_to_update = []
    for f in sorted(all_files):
        basename = os.path.basename(f)
        if basename in SKIP_FILES:
            continue
        if "-en-" in basename or basename.endswith("-en.md"):
            continue
        files_to_update.append(f)

    print(f"Found {len(files_to_update)} files to update:")
    updated = 0
    for f in files_to_update:
        result = update_file(f)
        if result:
            updated += 1

    print(f"\nDone. Updated {updated}/{len(files_to_update)} files.")


if __name__ == "__main__":
    main()
