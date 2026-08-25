# Content Intelligence: Delixio guide publishing prompt

Copy this into the Content Intelligence / Ava publishing agent (or system prompt for the “publish guide” step).

---

## Goal

When a cooking guide is approved for the Delixio static site, convert the editorial Markdown draft into **guide JSON** that matches `content/guides/guide.schema.json` and renders correctly on delixioapp.com.

The website does **not** render arbitrary Markdown documents. It renders structured JSON to HTML, with a small allowlist of **inline** Markdown inside string fields.

## Hard rules

1. Write one file: `content/guides/en/<slug>.json` (`type: "guide"`).
2. Optional hero: save image bytes to `assets/guides/<slug>.webp` and set `"image": { "file", "alt" }`. Never embed base64 in JSON.
3. Never invent Delixio product features. Use only `DELIXIO_CONTENT_KNOWLEDGE.md`.
4. No em dashes (`—`). Prefer commas, colons, periods, or `|` in titles.
5. Do **not** leave Markdown pipe-tables (`| col | col |`) inside `paragraphs`. Convert them to `table`.
6. Do **not** dump a whole MD document into one paragraph string.
7. Do **not** put raw HTML tags in JSON (`<p>`, `<table>`, `<strong>`, …). Use the mappings below.
8. Drafts use `"status": "draft"`. Approved guides use `"status": "published"`.
9. After writing: `python3 scripts/validate_guide.py <file>` then `python3 scripts/build_landings.py`.
10. Commit/push to **`main`** only after human approval (per product policy).

## Block-level Markdown → JSON (required)

| Markdown in the draft | Put in JSON as |
|------------------------|----------------|
| Title / H1 | `title`, `h1` |
| Opening paragraphs | `intro` (array of strings) |
| `## Section` / `###` used as section title | `sections[].heading` (one section object per H2) |
| Normal paragraphs under a section | `sections[].paragraphs` |
| Prose that must appear **after** a table in the same section | `sections[].paragraphs_after` |
| Bullet list (`-` / `*`) | `sections[].list` (array of strings) |
| Numbered list / method steps | `sections[].steps` (array of strings) |
| Markdown table | `sections[].table` with `headers` + `rows` |
| Delixio CTA block | `delixio.heading` + `delixio.paragraphs` only |
| Related links | `related` (2–4 items): mix peer guides (`type: "guide"`) and intent landings |

Never keep `#` / `##` markers inside paragraph strings. Headings become `heading` fields.

## Inline Markdown allowed inside strings

These may remain inside `intro`, `paragraphs`, `paragraphs_after`, `list`, `steps`, table cells, and `delixio.paragraphs`. The site converts them to HTML.

| Markdown | HTML on site | Notes |
|----------|--------------|--------|
| `**bold**` or `__bold__` | `<strong>` | Preferred emphasis for key terms |
| `*italic*` or `_italic_` | `<em>` | Do not nest awkwardly inside bold |
| `` `inline code` `` | `<code>` | Rare for cooking guides; allowed |
| `[[/path/\|label]]` | `<a href="/path/">label</a>` | **Preferred** for Delixio internal links |
| `[label](url)` | `<a href="url">label</a>` | Allowed when url is `/…`, `https://…`, `http://…`, or `#…` |

Examples:

```text
The useful question is which **dinner shape** fits tonight.
If the fridge looks sparse, see [[/guides/how-to-decide-what-to-cook-when-the-fridge-looks-empty/|deciding what to cook when the fridge looks empty]].
You can also link with [Quick dinner ideas](/quick-dinner-ideas/).
```

## Inline / block Markdown NOT supported (must convert or drop)

Do **not** leave these in published JSON expecting them to render:

| Construct | What to do instead |
|-----------|--------------------|
| Raw HTML (`<b>`, `<em>`, `<ul>`, `<table>`, …) | Use Markdown inline allowlist or structured fields |
| `#` / `##` / `###` inside paragraphs | Map to `sections[].heading` |
| Multi-paragraph blobs with blank lines in one string | Split into separate `paragraphs` entries |
| Images `![](…)` in body | Hero only via `image.file` under `assets/guides/` |
| Blockquotes `>` | Rewrite as normal paragraphs |
| Horizontal rules `---` | Omit |
| Fenced code blocks ` ``` ` | Omit or rewrite as prose |
| Task lists / footnotes / definition lists | Omit |
| Nested lists | Flatten into one `list` or `steps` array |

## Tables (required conversion)

Wrong (do not publish):

```json
"paragraphs": [
  "| If you want… | Make… | Best extra |",
  "|---|---|---|",
  "| Crisp edges | Hash | Onion |"
]
```

Right:

```json
"paragraphs": [
  "Start with potatoes as the filling base, then choose one of these five directions:"
],
"table": {
  "headers": ["If you want…", "Make…", "Best extra to add"],
  "rows": [
    ["Crisp edges and a fast skillet", "Potato-and-egg hash", "Onion or greens"],
    ["A sliceable one-pan dinner", "Tortilla-style potato skillet", "Onion"]
  ]
},
"paragraphs_after": [
  "You only need eggs, potatoes, cooking oil or butter, salt, and pepper to begin."
]
```

Conversion algorithm:

1. Detect a GFM table block (header row, separator `|---|`, body rows).
2. Split cells on `|`, trim whitespace.
3. Set `table.headers` from the header row.
4. Set `table.rows` as an array of string arrays (pad/truncate to header width).
5. Place prose before the table in `paragraphs`, prose after in `paragraphs_after`.
6. Never keep the separator row in JSON.
7. Inline allowlist (`**bold**`, links, etc.) may appear inside header/cell strings.

## Coexistence with the website

The static site also **tolerates**:

- leftover Markdown pipe-tables inside `paragraphs` (fallback HTML table)
- the inline allowlist above

That is a safety net. **Content Intelligence must still emit structured `table` / `list` / `steps`.** Do not rely on fallbacks for block structure.

## Metadata checklist

Include when known:

- `language`: `"en"`
- `status`: `"published"` or `"draft"`
- `category`: `dinner` | `leftovers` | `pantry` | `planning`
- `primary_intent`, `delixio_capability`
- `datePublished`, `dateModified` (ISO dates; do not invent)
- `author`: `"Delixio Editorial Team"` when that is the publishing model
- `card_blurb`, `breadcrumb`, `eyebrow`
- `related` (2–4)

## Intent ownership

- Landing pages own solution keywords (e.g. “leftover recipe generator”).
- Guides own educational questions (e.g. “how to reuse leftovers”).
- Do not target a landing-page keyword as the guide’s primary intent.

## After publish

1. Validate + build.
2. Spot-check `/guides/<slug>/`: real HTML tables (not pipe characters), bold/italic/links as expected.
3. Update `llms.txt` if the site workflow expects it.
4. Prefer WebP hero images under ~300 KB.

---
