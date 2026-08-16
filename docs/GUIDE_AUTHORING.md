# Delixio guide authoring (agents + UI tools)

How to add editorial cooking guides to the static site, including optional images.

## Mental model

```text
brief → write guide JSON → (optional) generate image file → validate → build → preview → push develop
```

Guides teach a **kitchen problem**. Delixio appears only in the `delixio` block and `related` links. Do not invent app features.

Sources of truth:

- Product claims: app repo `DELIXIO_CONTENT_KNOWLEDGE.md`
- Architecture: [`CONTENT_ARCHITECTURE.md`](CONTENT_ARCHITECTURE.md)
- Schema notes: [`content/guides/README.md`](../content/guides/README.md)

## Categories

| Key | Hub card | Listing URL |
|-----|----------|-------------|
| `dinner` | Getting dinner on the table | `/guides/dinner/` |
| `leftovers` | Leftovers and food waste | `/guides/leftovers/` |
| `pantry` | Pantry and ingredients | `/guides/pantry/` |
| `planning` | Planning | `/guides/planning/` |

Reserved: do not use `dinner`, `leftovers`, `pantry`, or `planning` as article slugs.

## Required JSON fields (Ava / publishing)

Include at minimum:

- `type`: `"guide"`
- `status`: `"published"` or `"draft"` (drafts are **not** built into public HTML)
- `language`: e.g. `"en"`
- `category`, `slug`, `title`, `description`, `h1`, `card_blurb`
- `primary_intent`: the educational question this guide owns
- `delixio_capability`: which Delixio capability it should hand off to
- `datePublished`, `dateModified`, `author` (e.g. `"Delixio Editorial Team"`)
- `related`: 2–4 items mixing relevant guides and intent landings
- `intro`, `sections`, `delixio`

Do **not** target a landing-page keyword as the guide’s primary intent.

Path: `content/guides/en/<slug>.json` → public URL `/guides/<slug>/`.

Inline links in paragraphs: `[[/path/|label]]`.

### Optional image

**Do not put base64 or binary in JSON.**

1. Generate or export an image.
2. Save it as `assets/guides/<slug>.webp` (preferred) or `.jpg` / `.png`.
3. Reference it in JSON:

```json
"image": {
  "file": "how-to-turn-leftovers-into-another-meal.webp",
  "alt": "Concrete description of what is in the image",
  "credit": ""
}
```

| Rule | Detail |
|------|--------|
| `file` | Filename only under `assets/guides/` |
| Aspect | 16:9 (~1200×675) |
| Weight | Aim under 300 KB |
| Style | Warm, realistic food / kitchen atmosphere; no fake UI screenshots; no Delixio phone mockups unless you have approved assets |
| `alt` | Required if `image` is present |
| Omit `image` | Article still publishes without a hero |

The build fails if JSON references a missing file.

## Product claim rules (hard)

Allowed only if present in the KB, including:

- Ideas free; 1 credit = 1 full recipe; 1 free full recipe / day; packs 6 / 28 / 90; no subscription; credits do not expire
- Strict / Flexible / Creative modes
- Grocery list, saved recipes/lists, meal calendar, one-way device calendar export
- My Kitchen pantry staples
- Type ingredients; **no** barcode scanner or fridge camera
- EN / FR / IT / ES

Never invent features (e.g. “match meal format”, camera fridge scan, subscription tiers that do not exist).

Copy style: no em dashes (`—`). Prefer commas, colons, periods, or `|` in titles.

## Agent workflow

1. Receive brief: category, slug, angle, target related landing(s).
2. Read KB + this doc + schema.
3. Write `content/guides/en/<slug>.json`.
4. If image requested: generate image → save to `assets/guides/<slug>.webp` → add `image` object with `file` + `alt`.
5. Run:

```bash
python3 scripts/validate_guide.py content/guides/en/<slug>.json
python3 scripts/build_landings.py
```

6. Preview locally; wait for human approval before publishing.

## UI software checklist

Your tool should:

1. Collect brief (category, slug, angle, optional “include image”).
2. Call the writing agent with KB + schema attached.
3. Write JSON to `content/guides/en/<slug>.json`.
4. If image: call image generator → write bytes to `assets/guides/<file>` → set `image.file` / `image.alt` in JSON.
5. Run `validate_guide.py` then `build_landings.py`.
6. Show local preview URL `/guides/<slug>/`.
7. On approve: commit on `develop` (do not auto-push `main`).

Suggested commit message style:

```text
Add cooking guide: <slug>.

Editorial article for the <category> section.
```

## Related landing pages (for `related`)

Prefer linking to these root landings when relevant:

- `/recipe-generator-from-ingredients/`
- `/what-can-i-cook-with-these-ingredients/`
- `/fridge-recipe-app/`
- `/ai-recipe-generator/`
- `/leftover-recipe-generator/`
- `/quick-dinner-ideas/`
- `/use-ingredients-before-they-expire/`
- `/reduce-food-waste/`
- `/meal-planner-app/`
- `/grocery-list-recipe-app/`

Also link `/how-it-works/`, `/faq/`, `/download/` when useful.

## Do not

- Publish thin placeholder guides
- Put intent landings under `/guides/`
- Embed images inside JSON
- Skip human review for product claims
