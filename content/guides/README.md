# Editorial cooking guides

Place genuine editorial guide articles here as `en/<slug>.json`.

These are **not** search/AI intent landing pages.

| Content | Path | URL |
|---------|------|-----|
| Guides | `content/guides/` | `/guides/<slug>/` |
| Guide images | `assets/guides/` | `/assets/guides/<file>` |
| Landings | `content/landings/` | `/<slug>/` (root) |

## Required fields

```json
{
  "type": "guide",
  "slug": "how-to-turn-leftovers-into-another-meal",
  "category": "leftovers",
  "card_blurb": "Short card text for /guides/ and homepage.",
  "breadcrumb": "Turn leftovers into another meal",
  "eyebrow": "Leftovers",
  "title": "…",
  "description": "…",
  "h1": "How to turn leftovers into another meal",
  "intro": ["…"],
  "sections": [{"heading": "…", "paragraphs": ["…"]}],
  "delixio": {
    "heading": "How Delixio helps",
    "paragraphs": [
      "Use Delixio’s [[/leftover-recipe-generator/|leftover recipe generator]] to…"
    ]
  },
  "related": [
    {"slug": "leftover-recipe-generator", "label": "Leftover recipe generator", "type": "landing"}
  ]
}
```

`category`: `dinner` | `leftovers` | `pantry` | `planning`

## Optional hero image

Do **not** embed image bytes in JSON. Save a file, then reference it:

```json
"image": {
  "file": "how-to-turn-leftovers-into-another-meal.webp",
  "alt": "Leftover roast vegetables reheated in a skillet for a second meal",
  "credit": ""
}
```

| Rule | Detail |
|------|--------|
| Location | `assets/guides/<file>` only |
| `file` | Filename only (no paths, no `..`) |
| Formats | Prefer `.webp`; `.jpg` / `.png` OK |
| Size | ~1200×675 (16:9), under ~300 KB |
| `alt` | Required when `image` is set; describe the scene |
| `credit` | Optional short credit line |

If `image` is omitted, the article still builds (default OG image).

Category listing cards show a thumbnail when the image file exists.

## Category URLs (reserved)

Do not use these as guide article slugs:

| Category | URL |
|----------|-----|
| dinner | `/guides/dinner/` |
| leftovers | `/guides/leftovers/` |
| pantry | `/guides/pantry/` |
| planning | `/guides/planning/` |

## Build / validate

```bash
python3 scripts/validate_guide.py content/guides/en/<slug>.json
python3 scripts/build_landings.py
```

Full agent + UI instructions: [`docs/GUIDE_AUTHORING.md`](../../docs/GUIDE_AUTHORING.md).

Do not publish thin placeholder guides. See `docs/CONTENT_ARCHITECTURE.md`.
