# Delixio content architecture

Three content types. Keep them distinct in data, URLs, navigation, and breadcrumbs.

| Type | Role | Typical URL | Source |
|------|------|-------------|--------|
| **product** | Brand / product explanation | `/`, `/about/`, `/how-it-works/`, `/faq/`, `/download/` | Hand-maintained HTML |
| **landing** | Search / AI intent solution page | `/ai-recipe-generator/`, etc. (root) | `content/landings/<locale>/*.json` |
| **guide** | Editorial cooking article | `/guides/<slug>/` | `content/guides/<locale>/*.json` |

## Mental model

```text
Editorial guide  →  relevant landing (capability)  →  Delixio app download
```

Guides teach a kitchen problem. Landings explain the Delixio solution for a specific intent. Product pages sell and explain the app.

## Rules

1. **Do not** put intent landings under `/guides/`.
2. **Do not** list all landings in header / Explore / homepage menus.
3. Landings stay indexable and in `sitemap.xml`.
4. `/guides/` is only for genuine editorial guides (human-browsable).
5. Discover landings via contextual links (FAQ, How it works, About, guides, related blocks).
6. Landing breadcrumb: `Home / Page title` — never under Cooking Guides.
7. Guide hub: category cards → `/guides/<category>/` listing pages.
8. Guide breadcrumb: `Home / Cooking Guides / Guide title` (category pages: `Home / Cooking Guides / Category`).
9. Product pages: `Home / Page title` visual breadcrumbs (homepage excluded).

## Build

```bash
python3 scripts/build_landings.py
```

Generates landing HTML, guide HTML (when JSON exists), `/guides/` hub, `/guides/<category>/` listings, `/explore/` → `/guides/` redirect, and `sitemap.xml`.

## Navigation

Header Explore → `/guides/` only.

Homepage “Cooking guides” section links to `/guides/` only. Do **not** feature intent landings there. Once editorial guides exist, feature 3–4 selected guides + “View all cooking guides →”.

## Adding an editorial guide

1. Create `content/guides/en/<slug>.json` with `"type": "guide"` and `"category"`: `dinner` | `leftovers` | `pantry` | `planning`
2. Optionally add a hero image file under `assets/guides/` and reference it with `"image": { "file", "alt" }` (never embed bytes in JSON)
3. Link contextually to the best landing page in body/`delixio`/`related`
4. Run `python3 scripts/validate_guide.py content/guides/en/<slug>.json` then `python3 scripts/build_landings.py`
5. Optionally feature it on the homepage (max ~4 cards)

Guide metadata should support at minimum:

* title, slug, description, language
* content type (`guide`)
* category
* primary intent
* related pages
* relevant Delixio capability
* datePublished, dateModified
* author
* publication status (`published` | `draft`)

Draft/unpublished content (`"status": "draft"`) is skipped by `scripts/build_landings.py` and must not become publicly accessible.

See `docs/GUIDE_AUTHORING.md` and `docs/CONTENT_AUDIT_2026-08.md`.

