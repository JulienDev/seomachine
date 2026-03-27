#!/usr/bin/env python3
"""
Patches existing draft files to add article_id to frontmatter.
Uses the same key-word matching logic as detect-existing.py.

Usage: python3 patch-article-ids.py [--dry-run]
"""

import json, os, re, glob, sys

DRY_RUN   = "--dry-run" in sys.argv
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDAR  = os.path.join(BASE, "scripts", "content-calendar.json")
DRAFTS    = os.path.join(BASE, "drafts")

SKIP_PATS = ["report", "analysis", "meta-options", "link-suggestion",
             "keyword-analysis", "optimization", "seo-report", "content-analysis"]
COMMON    = {"best","iptv","player","for","and","the","how","set","up","what",
             "is","guide","to","vs","in","of","complete","on","your","one","use",
             "with","from","into","that","this"}


def parse_fm(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        m = re.match(r"^---\n(.*?)\n---", raw, re.DOTALL)
        if not m:
            return {}, raw
        out = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip().strip("\"'")
        return out, raw
    except Exception:
        return {}, ""


def key_words(slug, keyword=""):
    words = set()
    for w in re.split(r"[-\s]+", (slug + " " + keyword).lower()):
        if len(w) >= 4 and w not in COMMON:
            words.add(w)
    return words


def inject_article_id(raw, article_id):
    """Insert article_id after the lang: line in frontmatter."""
    # Already present — update it
    if re.search(r"^article_id:", raw, re.MULTILINE):
        return re.sub(r"^article_id:.*$", f"article_id: {article_id}", raw, flags=re.MULTILINE)
    # Insert after lang: line
    return re.sub(r"(^lang:.*$)", rf"\1\narticle_id: {article_id}", raw, count=1, flags=re.MULTILINE)


with open(CALENDAR) as f:
    articles = json.load(f)["articles"]

# Build keyword sets per article
article_words = {}
for art in articles:
    article_words[art["id"]] = (art, key_words(art["slug_en"], art["keyword"]))

# Scan all draft files
draft_files = [
    p for p in sorted(glob.glob(os.path.join(DRAFTS, "*.md")))
    if not any(pat in os.path.basename(p) for pat in SKIP_PATS)
]

patched = 0
skipped_already = 0
unmatched = []

for path in draft_files:
    fm, raw = parse_fm(path)
    if not raw:
        continue

    lang = fm.get("lang", "")
    slug = fm.get("slug", "")

    if not lang:
        continue

    # Already has article_id — skip unless it needs updating
    if "article_id" in fm:
        skipped_already += 1
        continue

    # Find matching article
    matched_id = None
    file_slug_lower = slug.lower()
    bn = os.path.basename(path)

    for art_id, (art, words) in article_words.items():
        # Strategy 1: frontmatter slug contains a key word from the article
        if words and any(w in file_slug_lower for w in words):
            matched_id = art_id
            break
        # Strategy 2: filename contains a key word from the article
        if words and any(w in bn.lower() for w in words):
            matched_id = art_id
            break

    if matched_id is None:
        unmatched.append((path, lang, slug))
        continue

    new_raw = inject_article_id(raw, matched_id)
    if new_raw == raw:
        skipped_already += 1
        continue

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_raw)

    art_slug = article_words[matched_id][0]["slug_en"]
    print(f"{'[DRY]' if DRY_RUN else '[OK] '} article_id={matched_id} ({art_slug}) → {os.path.basename(path)}")
    patched += 1

print(f"\n{'[DRY-RUN] ' if DRY_RUN else ''}Patched: {patched} | Already had article_id: {skipped_already} | Unmatched: {len(unmatched)}")

if unmatched:
    print("\nUnmatched files (no article found):")
    for p, lang, slug in unmatched:
        print(f"  [{lang}] slug={slug!r}  {os.path.basename(p)}")
