#!/bin/bash
# =============================================================================
# IPTV One SEO Machine — Overnight Content Generation Script
# =============================================================================
# Generates all blog articles: research → write → optimize → translate → optimize
#
# By default, translates into PRIORITY languages only (FR DE SV NL ES NO AR PT TR IT DA FI).
# Pass --all-languages to also translate into the 16 remaining languages.
#
# AUTOMATIC RESUME: Every completed step is recorded in scripts/state.log
# If the script crashes or is interrupted, just relaunch it — it picks up
# exactly where it left off.
#
# Usage:
#   ./scripts/generate-all-content.sh                    # Run/resume (priority langs)
#   ./scripts/generate-all-content.sh --all-languages    # Run/resume (all 28 langs)
#   ./scripts/generate-all-content.sh --only 7           # Run only article #7
#   ./scripts/generate-all-content.sh --reset            # Wipe state, start fresh
#   ./scripts/generate-all-content.sh --reset-article 5  # Reset one article
# =============================================================================

set -o pipefail

# --- Configuration ---
BASE_DIR="/Users/juliendev/projects/www_iptv-one_app/seomachine"
SCRIPTS_DIR="$BASE_DIR/scripts"
DRAFTS_DIR="$BASE_DIR/drafts"
RESEARCH_DIR="$BASE_DIR/research"
LOG_DIR="$BASE_DIR/scripts/logs"
STATE_FILE="$SCRIPTS_DIR/state.log"
CALENDAR_FILE="$SCRIPTS_DIR/content-calendar.json"

MAX_PARALLEL_TRANSLATIONS=3

PRIORITY_LANGS="fr de sv nl es no ar pt tr it da fi"
REMAINING_LANGS="af bn cs el es_419 fa hi hu ko ms pl ro ru sr tl vi"

# Default: priority languages only
ACTIVE_LANGS="$PRIORITY_LANGS"
ALL_LANGUAGES=false

# --- Language name lookup (bash 3.2 compatible) ---
lang_name() {
  case "$1" in
    af) echo "Afrikaans" ;; ar) echo "Arabic" ;; bn) echo "Bengali" ;;
    cs) echo "Czech" ;; da) echo "Danish" ;; de) echo "German" ;;
    el) echo "Greek" ;; en) echo "English" ;; es) echo "Spanish" ;;
    es_419) echo "Latin American Spanish" ;; fa) echo "Persian/Farsi" ;;
    fi) echo "Finnish" ;; fr) echo "French" ;; hi) echo "Hindi" ;;
    hu) echo "Hungarian" ;; it) echo "Italian" ;; ko) echo "Korean" ;;
    ms) echo "Malay" ;; nl) echo "Dutch" ;; no) echo "Norwegian" ;;
    pl) echo "Polish" ;; pt) echo "Portuguese" ;; ro) echo "Romanian" ;;
    ru) echo "Russian" ;; sr) echo "Serbian" ;; sv) echo "Swedish" ;;
    tl) echo "Filipino/Tagalog" ;; tr) echo "Turkish" ;; vi) echo "Vietnamese" ;;
    *) echo "$1" ;;
  esac
}

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Setup ---
mkdir -p "$LOG_DIR" "$DRAFTS_DIR" "$RESEARCH_DIR"
touch "$STATE_FILE"

# --- Parse arguments ---
ONLY_ARTICLE=""
RESET_ALL=false
RESET_ARTICLE=""

while [ $# -gt 0 ]; do
  case $1 in
    --only) ONLY_ARTICLE="$2"; shift 2 ;;
    --reset) RESET_ALL=true; shift ;;
    --reset-article) RESET_ARTICLE="$2"; shift 2 ;;
    --all-languages) ALL_LANGUAGES=true; ACTIVE_LANGS="$PRIORITY_LANGS $REMAINING_LANGS"; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [ "$RESET_ALL" = true ]; then
  echo "Resetting all progress..."
  : > "$STATE_FILE"
  echo "Done. State cleared."
fi

if [ -n "$RESET_ARTICLE" ]; then
  echo "Resetting progress for article #$RESET_ARTICLE..."
  grep -v "^${RESET_ARTICLE}:" "$STATE_FILE" > "${STATE_FILE}.tmp" 2>/dev/null || true
  mv "${STATE_FILE}.tmp" "$STATE_FILE"
  echo "Done."
fi

# =============================================================================
# STATE MANAGEMENT
# =============================================================================
# State file: one line per completed step, format "article_id:step_name"
# Examples: 1:research  1:write_en  1:optimize_en  1:translate_fr  1:optimize_fr

is_done() {
  grep -qx "${1}:${2}" "$STATE_FILE" 2>/dev/null
}

mark_done() {
  echo "${1}:${2}" >> "$STATE_FILE"
}

count_done() {
  local c
  c=$(grep -c "^${1}:" "$STATE_FILE" 2>/dev/null) || c=0
  echo "$c"
}

# =============================================================================
# UTILITY
# =============================================================================

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log() {
  local level="$1"; shift
  local color="$NC"
  case "$level" in
    INFO) color="$GREEN" ;; WARN) color="$YELLOW" ;; ERROR) color="$RED" ;;
    STEP) color="$CYAN" ;; ARTICLE) color="$BLUE" ;;
  esac
  echo -e "${color}[$(timestamp)] [$level] $*${NC}"
  echo "[$(timestamp)] [$level] $*" >> "$LOG_DIR/generation-$(date +%Y-%m-%d).log"
}

get_article_field() {
  python3 -c "
import json, sys
with open('$CALENDAR_FILE') as f:
    data = json.load(f)
for a in data['articles']:
    if a['id'] == $1:
        print(a.get('$2', ''))
        break
"
}

get_total_articles() {
  python3 -c "
import json
with open('$CALENDAR_FILE') as f:
    print(len(json.load(f)['articles']))
"
}

# =============================================================================
# DISK SYNC — auto-detect existing files and mark steps as done in state.log
# =============================================================================
# Handles articles written manually or from previous script runs not recorded
# in state.log. Runs once at startup, idempotent (never duplicates entries).

sync_state_from_disk() {
  local synced=0
  while IFS= read -r step; do
    [ -z "$step" ] && continue
    if ! grep -qx "$step" "$STATE_FILE" 2>/dev/null; then
      echo "$step" >> "$STATE_FILE"
      synced=$((synced + 1))
    fi
  done < <(python3 "$SCRIPTS_DIR/detect-existing.py" "$ACTIVE_LANGS" 2>/dev/null)
  if [ "$synced" -gt 0 ]; then
    log INFO "Synced $synced steps from existing files on disk"
  fi
}

# =============================================================================
# CLAUDE RUNNER
# =============================================================================

CLAUDE_BIN="/Users/juliendev/.local/bin/claude"
CLAUDE_MODEL="claude-sonnet-4-6"

run_claude() {
  local prompt="$1"
  local log_file="$2"
  local timeout_secs="${3:-600}"

  # Start claude in background (cd into project dir first)
  (cd "$BASE_DIR" && "$CLAUDE_BIN" -p "$prompt" \
    --model "$CLAUDE_MODEL" \
    --dangerously-skip-permissions \
    --verbose) \
    >> "$log_file" 2>&1 &
  local pid=$!

  # Wait with timeout
  local elapsed=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 5
    elapsed=$((elapsed + 5))
    if [ $elapsed -ge $timeout_secs ]; then
      kill "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null
      log WARN "Claude timed out after ${timeout_secs}s"
      return 124
    fi
  done

  wait "$pid"
  return $?
}

# =============================================================================
# PIPELINE STEPS
# =============================================================================

step_research() {
  local id="$1"
  is_done "$id" "research" && return 0

  local topic keyword slug
  topic=$(get_article_field "$id" "topic_en")
  keyword=$(get_article_field "$id" "keyword")
  slug=$(get_article_field "$id" "slug_en")

  log STEP "  [1/5 Research] $keyword"

  local prompt="Run /research for the following topic.

Topic: $topic
Primary keyword: $keyword
Target slug: $slug

Do thorough keyword research and SERP analysis. Save the research brief to the research/ folder following the standard naming convention."

  if run_claude "$prompt" "$LOG_DIR/research-${id}-${slug}.log" 600; then
    mark_done "$id" "research"
  else
    log ERROR "  Research failed for article #$id"
    return 1
  fi
}

step_write_en() {
  local id="$1"
  is_done "$id" "write_en" && return 0

  local topic keyword slug publish_date
  topic=$(get_article_field "$id" "topic_en")
  keyword=$(get_article_field "$id" "keyword")
  slug=$(get_article_field "$id" "slug_en")
  publish_date=$(get_article_field "$id" "publish_date")
  local today
  today=$(date +%Y-%m-%d)

  log STEP "  [2/5 Write EN] $topic"

  local prompt="Run /write to create a comprehensive SEO-optimized article in English.

Topic: $topic
Primary keyword: $keyword
Target slug: $slug
Language: en

IMPORTANT — add these fields to the article's YAML frontmatter:
  publish_date: \"$publish_date\"
  lang: \"en\"
  slug: \"$slug\"
  article_id: $id

Use any research brief available in the research/ folder for this topic.
Save the article to drafts/${slug}-en-${today}.md

After writing, run /scrub on the saved file to remove AI patterns."

  if run_claude "$prompt" "$LOG_DIR/write-${id}-${slug}.log" 900; then
    mark_done "$id" "write_en"
  else
    log ERROR "  Write failed for article #$id"
    return 1
  fi
}

step_optimize() {
  local id="$1"
  local lang="$2"
  local step_key="optimize_${lang}"

  is_done "$id" "$step_key" && return 0

  local slug
  slug=$(get_article_field "$id" "slug_en")

  # Find the draft by article_id + lang in frontmatter (handles localized slugs)
  local draft_file
  draft_file=$(python3 -c "
import glob, re, os
drafts = '$DRAFTS_DIR'
skip = ['report','analysis','meta-options','link-suggestion',
        'keyword-analysis','optimization','seo-report','content-analysis']
for path in sorted(glob.glob(os.path.join(drafts, '*.md'))):
    bn = os.path.basename(path)
    if any(p in bn for p in skip):
        continue
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            head = f.read(1000)
        m = re.match(r'^---\n(.*?)\n---', head, re.DOTALL)
        if not m: continue
        fm = dict(line.split(':',1) for line in m.group(1).splitlines() if ':' in line)
        aid = fm.get('article_id','').strip().strip('\"\'')
        lng = fm.get('lang','').strip().strip('\"\'')
        if aid == '$id' and lng == '$lang':
            print(path)
            break
    except: pass
" 2>/dev/null)

  if [ -z "$draft_file" ]; then
    log WARN "  No draft for $slug ($lang), skip optimize"
    mark_done "$id" "$step_key"
    return 0
  fi

  local filename
  filename=$(basename "$draft_file")
  local today
  today=$(date +%Y-%m-%d)

  log STEP "  [Optimize] $filename"

  local prompt="Run /optimize on the article file: drafts/${filename}

Perform a full SEO optimization pass:
1. Check keyword density and placement
2. Validate internal and external links
3. Optimize meta title and description
4. Check heading structure
5. Verify readability score
6. Apply all recommended fixes directly to the article

Save the optimization report to drafts/optimization-report-${slug}-${lang}-${today}.md"

  if run_claude "$prompt" "$LOG_DIR/optimize-${id}-${slug}-${lang}.log" 600; then
    mark_done "$id" "$step_key"
  else
    log WARN "  Optimize failed for $slug ($lang), marking done anyway"
    mark_done "$id" "$step_key"
  fi
}

step_translate() {
  local id="$1"
  local target_lang="$2"
  local step_key="translate_${target_lang}"

  is_done "$id" "$step_key" && return 0

  local slug publish_date
  slug=$(get_article_field "$id" "slug_en")
  publish_date=$(get_article_field "$id" "publish_date")
  local lname
  lname=$(lang_name "$target_lang")

  # Find EN source
  local en_file
  en_file=$(find "$DRAFTS_DIR" -name "*${slug}*en*" \
    -not -name "*report*" -not -name "*analysis*" -not -name "*meta*" \
    -not -name "*link*" -not -name "*keyword*" -not -name "*optimization*" \
    2>/dev/null | head -1)

  if [ -z "$en_file" ]; then
    log ERROR "  No EN source for $slug, cannot translate to $target_lang"
    return 1
  fi

  local en_filename
  en_filename=$(basename "$en_file")
  local today
  today=$(date +%Y-%m-%d)

  log STEP "  [Translate → $target_lang] $slug"

  local prompt="Translate the article at drafts/${en_filename} into ${lname} (language code: ${target_lang}).

CRITICAL TRANSLATION RULES:
1. This is NOT a word-for-word translation. Adapt the content naturally for ${lname}-speaking readers.
2. Translate the slug naturally into ${lname} (e.g., 'best-iptv-player' → 'meilleur-lecteur-iptv' in French, 'bester-iptv-player' in German).
3. Translate the meta title and meta description for ${lname} SEO.
4. Keep all technical terms that are universally used (IPTV, M3U, EPG, Xtream Codes, Stalker Portal, 4K, HDR, etc.).
5. Translate keyword and heading text naturally — do NOT keep English headings.
6. Adapt any cultural references or examples if needed.
7. Keep all internal links but update the language prefix and slug: /${target_lang}/blog/[translated-slug].
8. Keep all store links (Google Play, App Store, etc.) unchanged.
9. Maintain the same markdown structure and formatting.

REQUIRED FRONTMATTER — update these fields:
  lang: \"${target_lang}\"
  publish_date: \"${publish_date}\"
  slug: [translated-slug-in-${target_lang}]
  article_id: ${id}

The article_id field is critical — it allows the site's language switcher to find all translations of the same article.

Save the translated article to the drafts/ folder with the naming convention: [translated-slug]-${target_lang}-${today}.md

After saving, run /scrub on the file to remove AI patterns."

  if run_claude "$prompt" "$LOG_DIR/translate-${id}-${slug}-${target_lang}.log" 600; then
    mark_done "$id" "$step_key"
  else
    log WARN "  Translate failed for $slug → $target_lang (will retry on next run)"
  fi
}

# =============================================================================
# PARALLEL TRANSLATION BATCH
# =============================================================================

translate_batch() {
  local id="$1"
  shift
  local langs="$*"

  local pids=""
  local running=0

  for lang in $langs; do
    [ "$lang" = "en" ] && continue
    is_done "$id" "translate_${lang}" && continue

    step_translate "$id" "$lang" &
    pids="$pids $!"
    running=$((running + 1))

    if [ $running -ge $MAX_PARALLEL_TRANSLATIONS ]; then
      # Wait for oldest
      local first_pid
      first_pid=$(echo "$pids" | awk '{print $1}')
      wait "$first_pid" 2>/dev/null || true
      pids=$(echo "$pids" | awk '{$1=""; print $0}' | sed 's/^ //')
      running=$((running - 1))
    fi
  done

  # Wait for remaining
  for pid in $pids; do
    wait "$pid" 2>/dev/null || true
  done
}

# =============================================================================
# ARTICLE PIPELINE
# =============================================================================

process_article() {
  local id="$1"
  local topic publish_date slug article_type
  topic=$(get_article_field "$id" "topic_en")
  publish_date=$(get_article_field "$id" "publish_date")
  slug=$(get_article_field "$id" "slug_en")
  article_type=$(get_article_field "$id" "type")

  local done_count
  done_count=$(count_done "$id")
  # Total steps: 1 research + 1 write + 1 optimize_en + N translate + N optimize
  local lang_count
  lang_count=$(echo "$ACTIVE_LANGS" | wc -w | tr -d ' ')
  local total_steps=$((3 + lang_count * 2))

  if [ "$done_count" -ge "$total_steps" ]; then
    log INFO "Article #${id} already complete ($done_count/$total_steps), skipping"
    return 0
  fi

  log ARTICLE "=========================================="
  log ARTICLE "Article #${id}: $topic"
  log ARTICLE "Publish: $publish_date | Type: $article_type | Progress: $done_count/$total_steps"
  log ARTICLE "=========================================="

  # Step 1: Research
  step_research "$id" || true

  # Step 2: Write EN
  step_write_en "$id" || {
    log ERROR "Cannot continue article #$id without EN draft"
    return 1
  }

  # Step 3: Optimize EN
  step_optimize "$id" "en"

  # Step 4: Translate
  log STEP "  [4/5 Translate] $ACTIVE_LANGS"
  translate_batch "$id" $ACTIVE_LANGS

  # Step 5: Optimize all translations
  log STEP "  [5/5 Optimize] All translations"
  for lang in $ACTIVE_LANGS; do
    step_optimize "$id" "$lang"
  done

  done_count=$(count_done "$id")
  log ARTICLE "Article #${id} done ($done_count/$total_steps): $topic"
  echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
  local total
  total=$(get_total_articles)

  local total_done
  total_done=$(wc -l < "$STATE_FILE" | tr -d ' ')
  local lang_count
  lang_count=$(echo "$ACTIVE_LANGS" | wc -w | tr -d ' ')
  local steps_per_article=$((3 + lang_count * 2))
  local grand_total=$((total * steps_per_article))

  log INFO "=============================================="
  log INFO "IPTV One SEO Machine — Content Generation"
  log INFO "=============================================="
  local mode="priority languages ($(echo "$PRIORITY_LANGS" | wc -w | tr -d ' '))"
  [ "$ALL_LANGUAGES" = true ] && mode="all languages (28)"
  log INFO "Articles: $total | Mode: $mode | Steps: $total_done / $grand_total"
  log INFO "=============================================="

  # Auto-detect existing files and mark steps as done
  log INFO "Scanning disk for existing drafts..."
  sync_state_from_disk

  # Recount after sync
  total_done=$(wc -l < "$STATE_FILE" | tr -d ' ')
  log INFO "Steps after disk sync: $total_done / $grand_total"
  if [ "$total_done" -gt 0 ]; then
    log INFO "Resuming — skipping completed steps automatically"
  fi
  log INFO "=============================================="
  echo ""

  local start_time
  start_time=$(date +%s)

  if [ -n "$ONLY_ARTICLE" ]; then
    process_article "$ONLY_ARTICLE"
  else
    local article_id=1
    while [ "$article_id" -le "$total" ]; do
      process_article "$article_id"
      article_id=$((article_id + 1))
    done
  fi

  local end_time
  end_time=$(date +%s)
  local duration=$(( (end_time - start_time) / 60 ))

  total_done=$(wc -l < "$STATE_FILE" | tr -d ' ')
  log INFO "=============================================="
  log INFO "DONE — ${duration} min — $total_done / $grand_total steps complete"
  log INFO "=============================================="
}

main
