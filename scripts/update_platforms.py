#!/usr/bin/env python3
"""
Update all non-English draft files to reflect new platform support:
- Android TV and Fire TV via sideloading
- Downloader code 1411180
- Direct APK link
- Platform count: 8 (was 6)
"""

import os
import re
import glob

DRAFTS_DIR = "/Users/juliendev/projects/www_iptv-one_app/seomachine/drafts"
TARGET_LANGS = {"fr", "de", "sv", "nl", "es", "no", "ar", "pt", "tr", "it", "da", "fi"}

def get_lang(filename):
    """Extract language code from filename like 'something-fr-2026-03-17.md'"""
    # Match patterns like -fr-, -de-, -es_419-, etc.
    m = re.search(r'-([a-z]{2}(?:_[0-9A-Za-z]+)?)-\d{4}-', filename)
    if m:
        return m.group(1)
    return None

def should_process(filepath):
    """Check if file should be processed"""
    basename = os.path.basename(filepath)
    lang = get_lang(basename)
    if lang not in TARGET_LANGS:
        return False
    if "optimization-report" in basename:
        return False
    if "firestick" in basename:
        return False
    return True

def update_content(content, lang):
    """Apply all platform updates to content"""
    modified = False
    original = content

    # === REPLACEMENT 1: Platform lists with Apple TV ===
    # "Android, iOS, macOS, Windows, Linux, Apple TV" -> "Android, Android TV, Fire TV, iOS, macOS, Windows, Linux, Apple TV"
    # But NOT if already contains "Android, Android TV"
    if "Android, Android TV" not in content:
        # With comma before Apple TV
        content = content.replace(
            "Android, iOS, macOS, Windows, Linux, Apple TV",
            "Android, Android TV, Fire TV, iOS, macOS, Windows, Linux, Apple TV"
        )

        # Various connectors before Apple TV in different languages
        for connector in [" et ", " und ", " och ", " en ", " og ", " e ", " y ", " ve ", " ja ", " و"]:
            old = f"Android, iOS, macOS, Windows, Linux{connector}Apple TV"
            new = f"Android, Android TV, Fire TV, iOS, macOS, Windows, Linux{connector}Apple TV"
            content = content.replace(old, new)

        # === REPLACEMENT 2: Platform lists WITHOUT Apple TV ===
        # "Android, iOS, macOS, Windows, Linux" -> "Android, Android TV, Fire TV, iOS, macOS, Windows, Linux"
        # But avoid replacing inside already-replaced strings (check no "Apple TV" immediately after)
        # Use a regex to be careful
        content = re.sub(
            r'Android, iOS, macOS, Windows, Linux(?!, Apple TV| et Apple| und Apple| och Apple| en Apple| og Apple| e Apple| y Apple| ve Apple| ja Apple)',
            'Android, Android TV, Fire TV, iOS, macOS, Windows, Linux',
            content
        )

        # "Android, iOS, macOS, Windows et Linux" (French connector)
        for connector in [" et ", " und ", " och ", " en ", " og ", " e ", " y ", " ve ", " ja ", " و"]:
            old = f"Android, iOS, macOS, Windows{connector}Linux"
            new = f"Android, Android TV, Fire TV, iOS, macOS, Windows{connector}Linux"
            content = content.replace(old, new)

    # === REPLACEMENT 3: Platform count 6 -> 8 ===
    # Various language patterns
    count_patterns = [
        # French
        (r'6 plateformes', '8 plateformes'),
        (r'six plateformes', 'huit plateformes'),
        # German
        (r'6-Plattformen', '8-Plattformen'),
        (r'6 Plattformen', '8 Plattformen'),
        (r'sechs Plattformen', 'acht Plattformen'),
        # Swedish
        (r'6-plattform', '8-plattform'),
        (r'6 plattform', '8 plattform'),
        # Norwegian
        (r'6-plattform', '8-plattform'),
        (r'6 plattform', '8 plattform'),
        # Dutch
        (r'6 platformen', '8 platformen'),
        # Spanish
        (r'6 plataformas', '8 plataformas'),
        (r'seis plataformas', 'ocho plataformas'),
        # Portuguese
        (r'6 plataformas', '8 plataformas'),
        (r'seis plataformas', 'oito plataformas'),
        # Italian
        (r'6 piattaforme', '8 piattaforme'),
        (r'sei piattaforme', 'otto piattaforme'),
        (r'Sei piattaforme', 'Otto piattaforme'),
        # Turkish
        (r'6 platform', '8 platform'),
        # Danish
        (r'6-platform', '8-platform'),
        (r'6 platform', '8 platform'),
        # Finnish
        (r'6 alustaa', '8 alustaa'),
        (r'6 alustan', '8 alustan'),
        # Arabic
        (r'6 منصات', '8 منصات'),
        (r'ست منصات', 'ثماني منصات'),
    ]

    for old_pat, new_pat in count_patterns:
        content = re.sub(old_pat, new_pat, content, flags=re.IGNORECASE if old_pat[0].islower() else 0)

    # Also handle "Cobertura en/em 6 plataformas"
    content = re.sub(r'Cobertura en 6 plataformas', 'Cobertura en 8 plataformas', content)
    content = re.sub(r'Cobertura em 6 plataformas', 'Cobertura em 8 plataformas', content)
    content = re.sub(r'Copertura su 6 piattaforme', 'Copertura su 8 piattaforme', content)

    # === REPLACEMENT 4: "(bientôt disponible)" / "(coming soon)" etc after Apple TV ===
    # Remove "coming soon" type phrases next to Apple TV since it's now available
    coming_soon_patterns = [
        r' \(bientôt disponible\)',
        r' \(bald verfügbar\)',
        r' \(kommer snart\)',
        r' \(binnenkort beschikbaar\)',
        r' \(próximamente\)',
        r' \(em breve\)',
        r' \(in arrivo\)',
        r' \(yakında\)',
        r' \(tulossa pian\)',
        r' \(قريباً\)',
        r' \(kommer snart\)',
    ]
    for pat in coming_soon_patterns:
        content = re.sub(pat, '', content)

    if content != original:
        modified = True

    return content, modified


def main():
    processed = 0
    modified_files = []

    # Get all .md files in drafts
    all_files = glob.glob(os.path.join(DRAFTS_DIR, "*.md"))

    for filepath in sorted(all_files):
        if not should_process(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Only process files that mention the platform list
        if "Android, iOS, macOS, Windows" not in content:
            continue

        processed += 1
        new_content, was_modified = update_content(content, get_lang(os.path.basename(filepath)))

        if was_modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified_files.append(os.path.basename(filepath))

    print(f"Processed {processed} files")
    print(f"Modified {len(modified_files)} files")
    print()
    for f in modified_files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
