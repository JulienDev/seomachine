Publish an article to the PrivAlert blog. This command replaces the WordPress publishing workflow.

## Input

The user will specify either:
- A file path from `published/` or `drafts/`
- A topic name to search for in those directories

## Steps

1. **Find the article**: Look in `published/` first, then `drafts/` for a matching markdown file
2. **Extract metadata**: Read the file and ensure it has valid frontmatter with all required fields:
   - `title`, `meta_title`, `meta_description`, `slug`, `date`, `category`, `tags`, `primary_keyword`, `excerpt`
3. **Validate the slug**: Ensure the slug uses only lowercase letters, numbers, and hyphens (no accents, no spaces)
4. **Copy to blog directory**: Copy the file to `../privalert-api/resources/blog/[slug].md`
5. **Verify**: Read the copied file to confirm it's in place

## Required frontmatter format

```yaml
---
title: "Article title"
meta_title: "SEO title | PrivAlert"
meta_description: "Meta description under 160 chars"
slug: article-slug-without-accents
date: 2026-03-15
category: guides
tags: [tag1, tag2, tag3]
primary_keyword: main keyword
excerpt: "Short excerpt for the blog listing page."
---
```

## After publishing

Tell the user:
1. The article has been copied to `privalert-api/resources/blog/[slug].md`
2. To make it live, they need to deploy:
   - Commit and push `privalert-api`
   - Run `git pull` on Hostinger
3. The article will be accessible at `https://www.privalert.app/blog/[slug]`
4. Remind them to run `composer install` on the server if this is the first blog article (to install Parsedown)
