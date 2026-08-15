# Localization plan for Delixio marketing pages

## Current state

- English marketing pages live at the **site root** (no `/en/` prefix):  
  `https://delixioapp.com/about/`, `https://delixioapp.com/faq/`, landing pages, etc.
- Privacy policy already has localized paths:  
  `/privacy/`, `/privacy/fr/`, `/privacy/es/`, `/privacy/it/` with `hreflang` tags.
- App languages today: English, French, Spanish, Italian.

Do **not** migrate English pages to `/en/` unless there is a deliberate SEO migration with redirects.

## Recommended URL pattern for future localized landings

| Locale | Pattern | Example |
|--------|---------|---------|
| English (default) | `/{slug}/` | `/leftover-recipe-generator/` |
| French | `/fr/{slug}/` | `/fr/leftover-recipe-generator/` |
| Spanish | `/es/{slug}/` | `/es/leftover-recipe-generator/` |
| Italian | `/it/{slug}/` | `/it/leftover-recipe-generator/` |

This matches the privacy convention and keeps English URLs stable.

Alternative if you later prefer language folders for everything including English: `/en/{slug}/` with 301s from old English URLs. That is a larger migration — not recommended now.

## Content source layout

```text
content/landings/en/<slug>.json
content/landings/fr/<slug>.json
content/landings/es/<slug>.json
content/landings/it/<slug>.json
```

`scripts/build_landings.py` already understands locale folders and writes:

- English → `/{slug}/index.html`
- Other locales → `/{locale}/{slug}/index.html`

## hreflang mapping (when translations exist)

On each translated page set:

```html
<link rel="alternate" hreflang="en" href="https://delixioapp.com/{slug}/">
<link rel="alternate" hreflang="fr" href="https://delixioapp.com/fr/{slug}/">
<link rel="alternate" hreflang="es" href="https://delixioapp.com/es/{slug}/">
<link rel="alternate" hreflang="it" href="https://delixioapp.com/it/{slug}/">
<link rel="alternate" hreflang="x-default" href="https://delixioapp.com/{slug}/">
```

Rules:

- Only emit `hreflang` for locales that actually exist.
- Canonical must be self-referencing for that locale URL.
- Sitemap should list every localized URL.
- Do not machine-translate and publish all pages in bulk without editorial review.

## What not to do in this phase

- Do not auto-generate hundreds of localized doorway pages.
- Do not change English root URLs.
- Do not put translated marketing pages under `/privacy/` or other unrelated trees.
