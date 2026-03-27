# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SEO Machine configured for **IPTV One** (https://www.iptv-one.app) — a premium multi-platform IPTV player available on Android, Android TV, Fire TV, iOS, macOS, Windows, Linux, and Apple TV.

SEO Machine is a Claude Code workspace for creating SEO-optimized blog content. It combines custom commands, specialized agents, and Python-based analytics to research, write, optimize, and publish articles.

### Business Context

- **Product**: IPTV One — IPTV media player (NOT a content/service provider), available on Android, Android TV, Fire TV, iOS, macOS, Windows, Linux, and Apple TV
- **Revenue model**: Freemium with premium subscriptions (RevenueCat)
- **2025 Revenue**: $758K across 170+ countries
- **Top markets**: France, Sweden, Germany, USA, Netherlands, Switzerland, Norway, UK, Spain, Canada
- **Blog integration**: Content will be integrated into the existing React/Vite landing page (not WordPress)
- **Languages**: 28 supported languages; content priority by revenue (French, English, German, Swedish, Dutch, Spanish, Norwegian, Arabic, Portuguese, Turkish, Italian, Danish, Finnish)

### CRITICAL Content Rules

1. **NEVER write content about illegal streaming, piracy, or copyrighted content access**
2. **NEVER mention specific IPTV service providers or resellers**
3. **ALWAYS present IPTV One as the best IPTV player** — never promote competitors
4. **ALWAYS clarify IPTV One is a player, not a content provider**
5. **Content must be safe for app store compliance** (Google Play, App Store policies)

## Setup

```bash
pip install -r data_sources/requirements.txt
```

API credentials are configured in `data_sources/config/.env` (GA4, GSC, DataForSEO). GA4 service account credentials go in `credentials/ga4-credentials.json`.

Note: WordPress publishing is NOT used for IPTV One. Blog content will be integrated into the React site at `https://www.iptv-one.app/{lang}/blog/{slug}`.

## Commands

All commands are defined in `.claude/commands/` and invoked as slash commands:

- `/research [topic]` - Keyword/competitor research, generates brief in `research/`
- `/write [topic]` - Create full article in `drafts/`, auto-triggers optimization agents
- `/rewrite [topic]` - Update existing content, saves to `rewrites/`
- `/optimize [file]` - Final SEO polish pass
- `/analyze-existing [URL or file]` - Content health audit
- `/performance-review` - Analytics-driven content priorities
- `/article [topic]` - Simplified article creation
- `/cluster [topic]` - Build complete topic cluster strategy with pillar + supporting articles + linking map
- `/priorities` - Content prioritization matrix
- `/research-serp`, `/research-gaps`, `/research-trending`, `/research-performance`, `/research-topics` - Specialized research commands
- `/landing-write`, `/landing-audit`, `/landing-research`, `/landing-competitor` - Landing page commands

## Architecture

### Command-Agent Model

**Commands** (`.claude/commands/`) orchestrate workflows. **Agents** (`.claude/agents/`) are specialized roles invoked by commands. After `/write`, these agents auto-run: SEO Optimizer, Meta Creator, Internal Linker, Keyword Mapper.

Key agents: `content-analyzer.md`, `seo-optimizer.md`, `meta-creator.md`, `internal-linker.md`, `keyword-mapper.md`, `editor.md`, `headline-generator.md`, `cro-analyst.md`, `performance.md`, `cluster-strategist.md`.

### Python Analysis Pipeline

Located in `data_sources/modules/`. The Content Analyzer chains:
1. `search_intent_analyzer.py` - Query intent classification
2. `keyword_analyzer.py` - Density, distribution, stuffing detection
3. `content_length_comparator.py` - Benchmarks against top 10 SERP results
4. `readability_scorer.py` - Flesch Reading Ease, grade level
5. `seo_quality_rater.py` - Comprehensive 0-100 SEO score

### Data Integrations

- `google_analytics.py` - GA4 traffic/engagement data (ID: G-JDD6MYXF32)
- `google_search_console.py` - Rankings and impressions (site verified)
- `dataforseo.py` - SERP positions, keyword metrics (to be configured later)
- `data_aggregator.py` - Combines all sources into unified analytics

### Opportunity Scoring

`opportunity_scorer.py` uses 8 weighted factors: Volume (25%), Position (20%), Intent (20%), Competition (15%), Cluster (10%), CTR (5%), Freshness (5%), Trend (5%).

## Content Pipeline

`topics/` (ideas) → `research/` (briefs) → `drafts/` (articles) → `review-required/` (pending review) → `published/` (final)

Rewrites go to `rewrites/`. Landing pages go to `landing-pages/`. Audits go to `audits/`.

## Context Files

`context/` contains brand guidelines configured for IPTV One:
- `brand-voice.md` - Professional, authoritative, premium tone; critical content rules
- `style-guide.md` - Multilingual grammar, formatting, technical terminology
- `seo-guidelines.md` - Multilingual SEO strategy, keyword optimization, legal content rules
- `target-keywords.md` - 6 keyword clusters with multilingual equivalents
- `internal-links-map.md` - Site pages, store links, blog article cross-linking
- `features.md` - 12 key features with benefits and conversion angles
- `competitor-analysis.md` - TiviMate, IPTV Smarters, GSE, OTT Navigator analysis
- `writing-examples.md` - Sample articles showing voice and positioning
- `cro-best-practices.md` - Download and subscription conversion optimization

## Store Links & Install Methods

- Google Play: https://play.google.com/store/apps/details?id=app.iptv.one
- App Store: https://apps.apple.com/app/id6751048813
- Microsoft Store: https://apps.microsoft.com/store/detail/9nc74zd1dtj0
- Snap Store: https://snapcraft.io/iptv-one
- Android TV / Fire TV (Sideload): Downloader app code **1411180** — https://aftv.news/1411180
- Direct APK download: https://www.iptv-one.app/downloads/onetv/latest.apk
