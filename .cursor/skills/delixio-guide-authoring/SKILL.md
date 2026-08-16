---
name: delixio-guide-authoring
description: >-
  Write or update Delixio editorial cooking guides as JSON under
  content/guides/en/, optionally with a hero image in assets/guides/.
  Use when creating guide articles, guide images, validating guides, or
  publishing cooking guides for dinner, leftovers, pantry, or planning.
---

# Delixio guide authoring

## Read first

1. `docs/GUIDE_AUTHORING.md`
2. `content/guides/README.md`
3. `content/guides/guide.schema.json`
4. Product KB: `DELIXIO_CONTENT_KNOWLEDGE.md` in the Delixio app docs (approved claims only)

## Output

- Write **one** file: `content/guides/en/<slug>.json`
- `type` must be `"guide"`
- `slug` must match the filename
- `category`: `dinner` | `leftovers` | `pantry` | `planning`
- Never use reserved slugs: `dinner`, `leftovers`, `pantry`, `planning`

## Optional image

If an image is requested:

1. Generate a warm, realistic kitchen/food scene (16:9).
2. Save bytes to `assets/guides/<slug>.webp` (preferred).
3. Add to JSON:

```json
"image": {
  "file": "<slug>.webp",
  "alt": "Concrete description of the scene",
  "credit": ""
}
```

Do **not** embed image data in JSON. Omit `image` if none.

## Claims and style

- Only KB-approved Delixio features and pricing
- No invented features
- No em dashes (`—`)
- Kitchen problem first; Delixio only in `delixio` + `related`
- Link landings with `[[/path/|label]]` and `related` entries

## After writing

```bash
python3 scripts/validate_guide.py content/guides/en/<slug>.json
python3 scripts/build_landings.py
```

Do not push to `main` unless the user asks. Prefer `develop` after human review.
