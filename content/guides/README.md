# Editorial cooking guides

Place genuine editorial guide articles here as `en/<slug>.json`.

These are **not** search/AI intent landing pages.

| Content | Path | URL |
|---------|------|-----|
| Guides | `content/guides/` | `/guides/<slug>/` |
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

Category listing URLs (reserved, do not use as guide article slugs):

| Category | URL |
|----------|-----|
| dinner | `/guides/dinner/` |
| leftovers | `/guides/leftovers/` |
| pantry | `/guides/pantry/` |
| planning | `/guides/planning/` |

Then run:

```bash
python3 scripts/build_landings.py
```

Do not publish thin placeholder guides. See `docs/CONTENT_ARCHITECTURE.md`.
