# Content architecture audit report (2026-08-16)

Cleanup and strengthening pass after production manual audit. IA preserved.

## 1. Issues found

| Area | Finding |
|------|---------|
| Related | Landing template always emitted `<h2>Related</h2>` even if `related` were empty (latent). Live pages already had 2–4 links in JSON/HTML. Guides gated Related correctly. Guide Related lists were landing-only (weak guide↔guide linking). |
| Quick dinner overlap | Landing `/quick-dinner-ideas/` and guide `/guides/quick-dinner-ideas-with-what-you-already-have-at-home/` answered nearly the same “quick dinner ideas” question. |
| Leftovers overlap | Guide `how-a-leftover-recipe-generator-helps-you-waste-less-food` targeted “leftover recipe generator” (landing keyword). |
| Pantry overlap | Two pantry guides shared the same “pantry staples → dinner” purpose. |
| Food safety | `/use-ingredients-before-they-expire/` suggested sensory checks when unsure about date labels, without separating use-by vs best-before clearly enough. |
| Article schema | Guides used `Article` but lacked `datePublished`, `dateModified`, `author`, `publisher`, `mainEntityOfPage`. |
| Drafts | No `status` gate; any JSON was published. `content/blog/*.md` exists but is not built (not public). |
| Ava metadata | Guides lacked `primary_intent`, `delixio_capability`, `language`, `status`, dates, author. |
| Extra landing | `/recipe-app-without-subscription/` exists beyond the original 10 intent pages (kept; listed in inventory). |

## 2. Issues fixed

- Related: landings omit empty Related block; guides get mixed guide+landing Related lists.
- Quick dinner: landing = Delixio solution; guide = educational framework (metadata/H1/intro differentiated; cross-links added).
- Leftovers: new educational guide slug; old generator-keyword URL becomes redirect.
- Pantry: differentiated into staples-to-stock vs meal templates (URLs kept).
- Food safety: corrected best-before / use-by wording.
- Article JSON-LD enriched; unpublished `status` skipped by build.
- Build quality warnings + `scripts/validate_content.py`.
- Redirects via `content/redirects.json` (excluded from sitemap).
- `llms.txt` updated to match published guides.

## 3. Redirects introduced

| From | To | Mechanism |
|------|-----|-----------|
| `/guides/how-a-leftover-recipe-generator-helps-you-waste-less-food/` | `/guides/how-to-turn-leftovers-into-a-completely-different-dinner/` | Static HTML `meta refresh` + canonical + `noindex`; **recommend Cloudflare 301** for a true permanent redirect |

## 4. Content overlap table

| Cluster | Landing (owns solution intent) | Guide (owns educational intent) | Status |
|---------|--------------------------------|----------------------------------|--------|
| Quick dinner | `/quick-dinner-ideas/` — generate timed ideas in Delixio | `/guides/quick-dinner-ideas-with-what-you-already-have-at-home/` — framework for building a fast dinner | Differentiated |
| Leftovers / generator | `/leftover-recipe-generator/` | `/guides/how-to-turn-leftovers-into-a-completely-different-dinner/` — remix method | Differentiated + redirect from old guide URL |
| Fridge leftovers examples | (landing above) | `/guides/leftover-recipes-that-start-with-what-is-already-in-your-fridge/` | Kept; complementary |
| Pantry staples | — | `/guides/meals-from-pantry-staples-…` — what to stock | Differentiated |
| Pantry templates | — | `/guides/pantry-meal-ideas-…` — 7 templates | Differentiated |
| Tonight / no plan | `/what-can-i-cook-with-these-ingredients/` | `/guides/what-to-cook-tonight-…` | Distinct enough (decision vs method); monitor |
| Meal planning | `/meal-planner-app/` | planning guides | Distinct (product vs education) |

## 5. Related links

All published landings: 2–4 crawlable `<a href>` items (examples match audit: AI / leftovers / meal planner).  
Guides: each has 2–4 links including at least one peer guide where useful and the best intent landing.

## 6. Schema changes

| Type | Schema |
|------|--------|
| Guides | `Article` + `BreadcrumbList` with headline, description, image (when present), datePublished, dateModified, author (Delixio Editorial Team), publisher, mainEntityOfPage |
| Landings | `WebPage` + `BreadcrumbList` + `FAQPage` when FAQ present (unchanged intent) |
| Homepage / FAQ / About / How it works | Unchanged mapping |
| Download | BreadcrumbList only (no fake Review/rating) |

## 7. Sitemap / robots

- Sitemap rebuild includes product pages, landings, published guides, category hubs.
- Redirect URL excluded from sitemap.
- `/go/`, `/explore/` remain noindex and out of sitemap.
- `robots.txt`: OAI-SearchBot, Googlebot, Bingbot, GPTBot allowed; Sitemap declared. No change required to GPTBot policy.

## 8. Cloudflare manual checks

See updated [`CLOUDFLARE_CRAWLER_CHECKLIST.md`](CLOUDFLARE_CRAWLER_CHECKLIST.md). Owner should verify WAF/bot rules and add a **301** for the leftovers guide redirect if possible.

## 9. Remaining editorial judgment

- Whether `/recipe-app-without-subscription/` should stay as a core intent page or be soft-deprecated.
- Whether `/guides/what-to-cook-tonight-…` still overlaps too much with `/what-can-i-cook-with-these-ingredients/` after more editorial polish.
- Hero images are large (~1.7–1.9 MB); compress for Pi disk and performance (editorial/ops, not architecture).
- `content/blog/*.md` is unused by the builder; decide keep-as-draft-source or remove.
- True HTTP 301 for retired guide URL (Cloudflare) vs meta refresh only (GitHub Pages limit).

## 10. Recommendations for Ava / Content Intelligence

1. Write only `content/guides/en/<slug>.json` (+ optional `assets/guides/<file>`).
2. Require: `status`, `language`, `primary_intent`, `delixio_capability`, `related` (2–4), `datePublished`/`dateModified`, `author`.
3. Use `status: "draft"` until approved; build skips non-published.
4. After write: `validate_guide.py` → `validate_content.py` → `build_landings.py`.
5. Never target a landing keyword as a guide’s primary intent (own the educational question).
6. Update `llms.txt` on publish.
7. Prefer WebP under ~300 KB for guide images.
