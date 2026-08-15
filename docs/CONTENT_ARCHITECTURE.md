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
2. Link contextually to the best landing page in body/`delixio`/`related`
3. Run `python3 scripts/build_landings.py`
4. Optionally feature it on the homepage (max ~4 cards)

Do not create thin placeholder guides.

See also `docs/CONTENT_LANDINGS.md`, `content/guides/README.md`, and the product knowledge base `DELIXIO_CONTENT_KNOWLEDGE.md` (in the Delixio app repo) for approved claims.
