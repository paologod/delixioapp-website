# Intent landing pages

Search / AI intent **landing** pages are data-driven. They are **not** editorial Cooking Guides.

User-facing Cooking Guides hub: `/guides/` (editorial only).  
Intent landings keep stable **root** URLs.

## Layout

```text
content/landings/en/<slug>.json   # landing source of truth
content/guides/en/<slug>.json     # editorial guides (separate)
scripts/build_landings.py         # generator
<slug>/index.html                 # generated landing pages
guides/index.html                 # editorial hub
guides/<slug>/index.html          # generated guide articles (when present)
explore/index.html                # redirect → /guides/
sitemap.xml                       # landings + guides + product pages
```

## Build

```bash
python3 scripts/build_landings.py
```

Do not hand-edit generated landing/guide HTML for copy changes. Update JSON and rebuild.

## Site architecture

```text
product pages     /  /about/  /how-it-works/  /faq/  /download/
landing pages     /ai-recipe-generator/  /meal-planner-app/  … (root)
guide hub         /guides/
guide articles    /guides/<slug>/   (when published)
```

Header: How it works · Explore (`/guides/`) · FAQ · Download.

Do **not** dump all landings into nav or homepage.

## Landing JSON fields

| Field | Purpose |
|-------|---------|
| `type` | Always `landing` |
| `slug` | URL segment (`/slug/`) — must match filename |
| `cluster` | Internal grouping: `discovery`, `waste`, or `planning` |
| `intent` | Primary user intent (docs / QA) |
| `title` | Unique `<title>` |
| `description` | Unique meta description |
| `h1` | Unique H1 |
| `breadcrumb` | Short breadcrumb label (`Home / …`) |
| `eyebrow` | Small label above H1 |
| `intro` | Opening answer paragraphs |
| `sections` | Headings, paragraphs, lists, steps |
| `delixio` | Natural product integration |
| `related` | 2–4 related landings `{slug, label}` — vary by page |
| `faq` | Visible FAQs + FAQPage JSON-LD |

Inline links: `[[/path/|Label]]`.

`card_blurb` is unused for `/guides/` (landings are not listed there).

## Adding a landing

1. Create `content/landings/en/my-new-page.json` with `"type": "landing"`
2. Unique title / description / H1 / intent
3. Curated `related` (2–4; not identical across all pages)
4. Run `python3 scripts/build_landings.py`
5. Add contextual links from FAQ / How it works / About / guides where natural
6. Do **not** add to header Explore or list all landings on the homepage

## Taxonomy

See `docs/CONTENT_ARCHITECTURE.md` for `product` / `landing` / `guide`.
