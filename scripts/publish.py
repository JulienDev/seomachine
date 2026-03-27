#!/usr/bin/env python3
"""
Publish draft articles to the React site.

Copies .md files from seomachine/drafts/ to public/blog/{lang}/{slug}.md
and updates public/blog/manifest.json.

By default, only publishes articles with publish_date <= today.

Usage:
  python3 publish.py                 # publish due articles (publish_date <= today)
  python3 publish.py --all           # publish everything regardless of date
  python3 publish.py --article 2     # publish all languages of article #2
  python3 publish.py --dry-run       # preview without writing
"""

import json, os, re, glob, sys, shutil
from datetime import date
from collections import defaultdict

# Headings that mark internal optimization artifacts — strip from this point on
STRIP_PATTERNS = re.compile(
    r'^##+ .*(checklist|checkliste|chekliste|tjekliste|kontrolliste'
    r'|tarkistuslista|checklist de seo|lista de verificaci'
    r'|lista de controle|elenco di controllo|controlelijst'
    r'|engagement|engasjement|engasjeringssjekkliste'
    r'|engagementstjekliste|betrokkenheid).*$',
    re.IGNORECASE | re.MULTILINE
)


def strip_artifacts(raw):
    """Remove internal checklist sections from article content."""
    m = STRIP_PATTERNS.search(raw)
    if m:
        raw = raw[:m.start()].rstrip() + '\n'
    return raw

# --- Paths ---
SEOMACHINE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE        = os.path.dirname(SEOMACHINE)
DRAFTS      = os.path.join(SEOMACHINE, "drafts")
PUBLIC_BLOG = os.path.join(SITE, "public", "blog")
MANIFEST    = os.path.join(PUBLIC_BLOG, "manifest.json")

SKIP_PATS   = ["report", "analysis", "meta-options", "link-suggestion",
               "keyword-analysis", "optimization", "seo-report", "content-analysis"]

# --- Args ---
DRY_RUN     = "--dry-run" in sys.argv
PUBLISH_ALL = "--all" in sys.argv
ONLY_ART    = None
for i, arg in enumerate(sys.argv):
    if arg == "--article" and i + 1 < len(sys.argv):
        ONLY_ART = sys.argv[i + 1]

TODAY = date.today().isoformat()


def parse_fm(path):
    """Parse YAML frontmatter from a markdown file."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        m = re.match(r"^---\n(.*?)\n---", raw, re.DOTALL)
        if not m:
            return {}, raw
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip("\"'")
        return fm, raw
    except Exception:
        return {}, ""


def tags_from_fm(fm):
    raw = fm.get("tags", "")
    return [t.strip() for t in raw.split(",") if t.strip()]


# --- Collect all valid drafts ---
all_drafts = []
for path in sorted(glob.glob(os.path.join(DRAFTS, "*.md"))):
    bn = os.path.basename(path)
    if any(p in bn for p in SKIP_PATS):
        continue
    fm, raw = parse_fm(path)
    lang        = fm.get("lang", "").strip()
    slug        = fm.get("slug", "").strip()
    article_id  = fm.get("article_id", "").strip()
    publish_date = fm.get("publish_date", fm.get("date", "")).strip()
    title       = fm.get("title", "").strip()
    if not (lang and slug and article_id and publish_date and title):
        continue
    all_drafts.append({
        "path":         path,
        "lang":         lang,
        "slug":         slug,
        "article_id":   article_id,
        "publish_date": publish_date,
        "title":        title,
        "meta_title":   fm.get("meta_title", title).strip(),
        "meta_description": fm.get("meta_description", "").strip(),
        "category":     fm.get("category", "Guide").strip(),
        "tags":         tags_from_fm(fm),
        "reading_time": int(fm.get("reading_time", 8)),
        "raw":          raw,
    })

# --- Keep only one file per (article_id, lang): newest publish_date ---
best = {}
for d in all_drafts:
    key = (d["article_id"], d["lang"])
    if key not in best or d["publish_date"] > best[key]["publish_date"]:
        best[key] = d
candidates = list(best.values())

# --- Apply filters ---
if ONLY_ART:
    candidates = [d for d in candidates if d["article_id"] == ONLY_ART]

if not PUBLISH_ALL and not ONLY_ART:
    candidates = [d for d in candidates if d["publish_date"] <= TODAY]

if not candidates:
    print(f"Nothing to publish (today={TODAY}, use --all to override).")
    sys.exit(0)

# --- Build translations map (group by article_id, only published langs) ---
published_ids = {d["article_id"] for d in candidates}
by_article = defaultdict(list)
for d in candidates:
    by_article[d["article_id"]].append(d)

def get_translations(article_id, current_lang):
    return {
        d["lang"]: d["slug"]
        for d in by_article[article_id]
        if d["lang"] != current_lang
    }

# --- Load existing manifest ---
existing_manifest = {"articles": []}
if os.path.exists(MANIFEST):
    with open(MANIFEST) as f:
        existing_manifest = json.load(f)

# Index existing entries by (lang, slug)
existing_index = {
    (a["lang"], a["slug"]): a
    for a in existing_manifest["articles"]
}

# --- Publish ---
published = 0
updated   = 0

for d in sorted(candidates, key=lambda x: (x["article_id"], x["lang"])):
    lang = d["lang"]
    slug = d["slug"]
    dest_dir  = os.path.join(PUBLIC_BLOG, lang)
    dest_file = os.path.join(dest_dir, f"{slug}.md")

    translations = get_translations(d["article_id"], lang)

    manifest_entry = {
        "slug":             slug,
        "lang":             lang,
        "article_id":       int(d["article_id"]),
        "publish_date":     d["publish_date"],
        "title":            d["title"],
        "meta_title":       d["meta_title"],
        "meta_description": d["meta_description"],
        "category":         d["category"],
        "tags":             d["tags"],
        "reading_time":     d["reading_time"],
        "translations":     translations,
    }

    is_new = (lang, slug) not in existing_index
    label  = "PUB " if is_new else "UPD "
    print(f"{'[DRY] ' if DRY_RUN else ''}{label} [{lang}] {slug}")

    if not DRY_RUN:
        os.makedirs(dest_dir, exist_ok=True)
        clean_content = strip_artifacts(d["raw"])
        with open(dest_file, "w", encoding="utf-8") as out:
            out.write(clean_content)
        existing_index[(lang, slug)] = manifest_entry

    if is_new:
        published += 1
    else:
        updated += 1

# --- Write manifest ---
if not DRY_RUN:
    # Rebuild translations for ALL existing entries (cross-link new ones)
    all_entries = list(existing_index.values())
    by_art_all  = defaultdict(list)
    for e in all_entries:
        by_art_all[str(e["article_id"])].append(e)

    for e in all_entries:
        e["translations"] = {
            x["lang"]: x["slug"]
            for x in by_art_all[str(e["article_id"])]
            if x["lang"] != e["lang"]
        }

    manifest_out = {
        "generated": TODAY,
        "articles":  sorted(all_entries, key=lambda x: (x["publish_date"], x["lang"]))
    }
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest_out, f, ensure_ascii=False, indent=2)

mode = "ALL" if PUBLISH_ALL else f"due by {TODAY}"
print(f"\n{'[DRY-RUN] ' if DRY_RUN else ''}Published: {published} new, {updated} updated ({mode})")
print(f"Manifest: {MANIFEST}")
