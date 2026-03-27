#!/usr/bin/env python3
"""
Scans drafts/ and research/ folders and prints "article_id:step_name" for every
step that can be considered done based on files already present on disk.
Reads frontmatter lang/slug fields to reliably match translated files even when
the translated slug has reordered or localized words.

Usage: python3 detect-existing.py <active_langs_space_separated>
"""

import json, os, re, glob, sys

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDAR = os.path.join(BASE, "scripts", "content-calendar.json")
DRAFTS   = os.path.join(BASE, "drafts")
RESEARCH = os.path.join(BASE, "research")
ACTIVE   = sys.argv[1].split() if len(sys.argv) > 1 else []

SKIP_PATS = ["report", "analysis", "meta-options", "link-suggestion",
             "keyword-analysis", "optimization", "seo-report", "content-analysis"]
COMMON    = {"best","iptv","player","for","and","the","how","set","up","what",
             "is","guide","to","vs","in","of","complete","on","your","one","use",
             "with","from","into","that","this"}


def parse_fm(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            head = f.read(2000)
        m = re.match(r"^---\n(.*?)\n---", head, re.DOTALL)
        if not m:
            return {}
        out = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip().strip("\"'")
        return out
    except Exception:
        return {}


def key_words(slug, keyword=""):
    words = set()
    for w in re.split(r"[-\s]+", (slug + " " + keyword).lower()):
        if len(w) >= 4 and w not in COMMON:
            words.add(w)
    return words


with open(CALENDAR) as f:
    articles = json.load(f)["articles"]

# Scan all draft files once — parse frontmatter
draft_index = []
for path in sorted(glob.glob(os.path.join(DRAFTS, "*.md"))):
    bn = os.path.basename(path)
    if any(p in bn for p in SKIP_PATS):
        continue
    fm = parse_fm(path)
    lang = fm.get("lang", "")
    slug = fm.get("slug", "")
    if lang:
        draft_index.append({"path": path, "lang": lang, "slug": slug, "bn": bn})

research_basenames = [os.path.basename(f) for f in glob.glob(os.path.join(RESEARCH, "*.md"))]

done = set()

for art in articles:
    aid   = art["id"]
    sl_en = art["slug_en"]
    kw    = art["keyword"]
    words = key_words(sl_en, kw)

    # --- Research ---
    if any(sl_en in rb for rb in research_basenames):
        done.add(f"{aid}:research")

    # --- Write EN ---
    # File whose frontmatter lang=en AND (slug matches OR slug_en in filename)
    for d in draft_index:
        if d["lang"] == "en" and (d["slug"] == sl_en or sl_en in d["bn"]):
            done.add(f"{aid}:write_en")
            break

    # --- Optimize EN ---
    for path in (glob.glob(os.path.join(DRAFTS, f"*optimization*{sl_en}*en*.md")) +
                 glob.glob(os.path.join(DRAFTS, f"*optimization*en*{sl_en}*.md"))):
        done.add(f"{aid}:optimize_en")
        break

    # --- Translations ---
    for lang in ACTIVE:
        trans_step = f"{aid}:translate_{lang}"
        opt_step   = f"{aid}:optimize_{lang}"

        if trans_step not in done:
            matched = False

            # Strategy 1: frontmatter lang matches AND frontmatter slug contains
            # a key word from the article. Handles reordered/translated slugs.
            for d in draft_index:
                if d["lang"] != lang:
                    continue
                file_slug = d["slug"].lower()
                if any(w in file_slug for w in words):
                    done.add(trans_step)
                    matched = True
                    break

            # Strategy 2: filename contains -lang- AND a key word (fallback)
            if not matched:
                pat = f"-{lang}-"
                for d in draft_index:
                    if d["lang"] != lang:
                        continue
                    if pat in d["bn"] and any(w in d["bn"] for w in words):
                        done.add(trans_step)
                        break

        # Optimize translation
        if opt_step not in done:
            for path in (glob.glob(os.path.join(DRAFTS, f"*optimization*{sl_en}*{lang}*.md")) +
                         glob.glob(os.path.join(DRAFTS, f"*optimization*{lang}*{sl_en}*.md"))):
                done.add(opt_step)
                break

for step in sorted(done):
    print(step)
