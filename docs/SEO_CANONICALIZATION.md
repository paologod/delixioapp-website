# SEO Canonicalization (Phase 1.2)

This document defines the canonical URL policy for the Delixio static website hosted on GitHub Pages with custom domain `delixioapp.com`.

## Preferred canonical domain

- **HTTPS apex:** `https://delixioapp.com`
- **Not canonical:** `http://`, `www.`, `/index.html` paths, or query-parameter variants

## Preferred URL style

| Page | Canonical URL |
|------|---------------|
| Homepage | `https://delixioapp.com/` |
| Download | `https://delixioapp.com/download/` |
| Privacy | `https://delixioapp.com/privacy/` |
| Terms | `https://delixioapp.com/terms/` |
| Support | `https://delixioapp.com/support/` |
| Delete account | `https://delixioapp.com/delete-account/` |

Rules:

- Use trailing-slash directory URLs for folder pages.
- Do not use `/index.html` in canonical URLs, sitemap entries, or internal links.
- Each public HTML page has exactly one self-referencing `<link rel="canonical">` in `<head>`.
- Each public HTML page has `og:url` matching the canonical URL exactly.

## Sitemap policy

`sitemap.xml` lists **canonical URLs only** — no `http://`, no `www`, no `/index.html`, no duplicates, no query strings.

`robots.txt` references:

```
Sitemap: https://delixioapp.com/sitemap.xml
```

## Internal link policy

Use root-relative clean paths:

- `/` (homepage)
- `/download/`
- `/privacy/`
- `/terms/`
- `/support/`
- `/delete-account/`

Do **not** link internally to `/index.html`, `/download/index.html`, or other `*/index.html` variants.

## Redirect policy

### In the repository

Root-level stub files (`download.html`, `privacy.html`, etc.) redirect to clean directory URLs via `<meta http-equiv="refresh">` and declare the canonical destination URL in `<link rel="canonical">`.

These stubs may appear in Search Console as **“Page with redirect”** — that is expected and acceptable when they redirect to the correct canonical URL.

### Hosting / CDN (manual configuration required)

GitHub Pages **cannot** issue server-side 301 redirects for all duplicate variants from repository files alone. Configure permanent redirects at the DNS/CDN layer (recommended: Cloudflare in front of GitHub Pages).

#### GitHub Pages settings

In the repository **Settings → Pages**:

- Custom domain: `delixioapp.com`
- **Enforce HTTPS:** enabled

#### Cloudflare redirect rules (recommended)

Create **301** redirect rules:

| Source | Target |
|--------|--------|
| `http://delixioapp.com/*` | `https://delixioapp.com/$1` |
| `http://www.delixioapp.com/*` | `https://delixioapp.com/$1` |
| `https://www.delixioapp.com/*` | `https://delixioapp.com/$1` |
| `https://delixioapp.com/index.html` | `https://delixioapp.com/` |
| `https://delixioapp.com/download/index.html` | `https://delixioapp.com/download/` |
| `https://delixioapp.com/privacy/index.html` | `https://delixioapp.com/privacy/` |
| `https://delixioapp.com/terms/index.html` | `https://delixioapp.com/terms/` |
| `https://delixioapp.com/support/index.html` | `https://delixioapp.com/support/` |
| `https://delixioapp.com/delete-account/index.html` | `https://delixioapp.com/delete-account/` |

Optional: redirect legacy `.html` stubs if accessed directly (e.g. `/privacy.html` → `/privacy/`).

#### Without Cloudflare

If DNS points directly to GitHub Pages without a redirect-capable CDN:

- Canonical tags, sitemap consistency, and internal links still signal the preferred URL to Google.
- Server-side 301s for `www` and `/index.html` variants must be configured wherever DNS terminates (registrar, proxy, etc.).

## Search Console notes

- **“Page with redirect”** — acceptable for non-canonical variants (e.g. `www`, `http`, legacy `.html` stubs) when they redirect to the canonical HTTPS apex URL.
- **“Duplicate without user-selected canonical”** — fixed by self-referencing canonical tags on every public page, consistent `og:url`, sitemap entries, and internal links.

After deployment:

1. Inspect affected URLs in Google Search Console.
2. Use **URL Inspection** on representative canonical URLs.
3. Click **Validate fix** once production canonical tags and redirects are live.

## What we do not use

- `noindex` on public pages to fix duplicate canonical issues.
- Fake App Store URLs, ratings, reviews, or statistics.
- Framework migration (site remains static HTML/CSS).
