#!/usr/bin/env python3
"""Generate Delixio landing pages from JSON content configs.

Usage:
  python3 scripts/build_landings.py

Reads:  content/landings/<locale>/*.json
Writes: <slug>/index.html (landing pages)
        guides/index.html (editorial hub)
        guides/<category>/index.html (category listing pages)
        sitemap.xml
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "landings"
GUIDES_DIR = ROOT / "content" / "guides"
CSS_VERSION = "92"
GA_ID = "G-89YMNXP5XF"
SITE = "https://delixioapp.com"
APP_STORE = "https://apps.apple.com/us/app/delixio/id6774958116"
PLAY_STORE = "https://play.google.com/store/apps/details?id=com.fridgemeal.fridgemeal"
OG_IMAGE = f"{SITE}/assets/hero-phones.webp"


def site_header(asset_prefix: str, current: str | None = None) -> str:
    """Full site nav matching homepage / how-it-works chrome."""

    def item(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if current == key else ""
        return f'          <li><a href="{href}"{cur}>{label}</a></li>'

    return f"""  <header class="site-header">
    <div class="container">
      <a href="/" class="logo" aria-label="Delixio home">
        <img src="{asset_prefix}logo.webp?v=45" alt="Delixio" width="208" height="77">
      </a>
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="main-nav">
        <span></span><span></span><span></span>
      </button>
      <nav class="main-nav" id="main-nav">
        <ul class="nav-links">
{item("/how-it-works/", "How it works", "how-it-works")}
{item("/guides/", "Explore", "guides")}
{item("/faq/", "FAQ", "faq")}
{item("/download/", "Download", "download")}
        </ul>
        <a href="/go/" class="btn btn-primary btn-nav">GET THE APP</a>
      </nav>
    </div>
  </header>
"""


def site_footer(asset_prefix: str, js_prefix: str) -> str:
    return f"""  <footer class="site-footer">
    <div class="container">
      <a href="/" class="logo" aria-label="Delixio home">
        <img src="{asset_prefix}logo.webp?v=45" alt="Delixio" width="208" height="77">
      </a>
      <div class="footer-end">
        <ul class="footer-links">
          <li><a href="/download/">Download</a></li>
          <li><a href="/privacy/">Privacy Policy</a></li>
          <li><a href="/terms/">Terms of Use</a></li>
          <li><a href="/support/">Support</a></li>
        </ul>
        <div class="footer-social">
          <a href="#" aria-label="Instagram"><img src="{asset_prefix}social-instagram.png?v=45" alt=""></a>
          <a href="#" aria-label="Facebook"><img class="small" src="{asset_prefix}social-facebook.png?v=45" alt=""></a>
          <a href="https://www.tiktok.com/@delixioapp" aria-label="TikTok" target="_blank" rel="noopener noreferrer"><img class="small" src="{asset_prefix}social-tiktok.png?v=45" alt=""></a>
        </div>
      </div>
    </div>
  </footer>

  <script src="{js_prefix}main.js"></script>
"""


STATIC_SITEMAP = [
    "/",
    "/about/",
    "/how-it-works/",
    "/faq/",
    "/guides/",
    "/download/",
    "/privacy/",
    "/privacy/es/",
    "/privacy/fr/",
    "/privacy/it/",
    "/terms/",
    "/support/",
    "/delete-account/",
]

CLUSTER_ORDER = ["discovery", "waste", "planning"]
CLUSTER_LABELS = {
    "discovery": "Recipe discovery",
    "waste": "Leftovers & food waste",
    "planning": "Planning",
}

# Editorial guide categories for /guides/ (not landing-page SEO clusters).
# Category slugs are reserved under /guides/<category>/, do not use as guide article slugs.
GUIDE_CATEGORY_ORDER = ["dinner", "leftovers", "pantry", "planning"]
GUIDE_CATEGORY_META = {
    "dinner": {
        "label": "Getting dinner on the table",
        "blurb": "Ideas and frameworks for weeknights when you need a meal from what you already have.",
        "icon": "icon-chef-hat.png",
        "icon_w": 48,
        "icon_h": 41,
    },
    "leftovers": {
        "label": "Leftovers and food waste",
        "blurb": "Practical ways to reuse cooked food and use ingredients before they go to waste.",
        "icon": "icon-basket.png",
        "icon_w": 44,
        "icon_h": 48,
    },
    "pantry": {
        "label": "Pantry and ingredients",
        "blurb": "How to combine staples and small ingredient lists into complete meals.",
        "icon": "icon-grocery.png",
        "icon_w": 48,
        "icon_h": 48,
    },
    "planning": {
        "label": "Planning",
        "blurb": "Plan meals and grocery lists around ingredients you already own.",
        "icon": "icon-calendar.png",
        "icon_w": 42,
        "icon_h": 46,
    },
}

LOCALE_META = {
    "en": {"html_lang": "en", "og_locale": "en_US", "dir_prefix": ""},
    "fr": {"html_lang": "fr", "og_locale": "fr_FR", "dir_prefix": "fr/"},
    "es": {"html_lang": "es", "og_locale": "es_ES", "dir_prefix": "es/"},
    "it": {"html_lang": "it", "og_locale": "it_IT", "dir_prefix": "it/"},
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def esc_text(text: str) -> str:
    return html.escape(text, quote=False)


def linkify(text: str) -> str:
    """Allow simple [[/path/|label]] markdown-ish links in content."""
    def repl(m: re.Match[str]) -> str:
        href, label = m.group(1), m.group(2)
        return f'<a href="{esc(href)}">{esc_text(label)}</a>'

    return re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", repl, esc_text(text))


def paragraphs(items: list[str]) -> str:
    return "\n".join(f"      <p>{linkify(p)}</p>" for p in items)


def page_url(slug: str, locale: str = "en") -> str:
    prefix = LOCALE_META[locale]["dir_prefix"]
    return f"{SITE}/{prefix}{slug}/"


def output_dir(slug: str, locale: str = "en") -> Path:
    prefix = LOCALE_META[locale]["dir_prefix"]
    return ROOT / prefix / slug if prefix else ROOT / slug


def render_faq_jsonld(faqs: list[dict]) -> str:
    entities = []
    for item in faqs:
        entities.append(
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
            }
        )
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_page(data: dict, locale: str = "en") -> str:
    slug = data["slug"]
    meta = LOCALE_META[locale]
    url = page_url(slug, locale)
    title = data["title"]
    description = data["description"]
    h1 = data["h1"]
    eyebrow = data.get("eyebrow", "Guide")
    breadcrumb_name = data.get("breadcrumb", h1)

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": breadcrumb_name, "item": url},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": h1,
        "url": url,
        "description": description,
        "isPartOf": {"@type": "WebSite", "name": "Delixio", "url": f"{SITE}/"},
        "about": {
            "@type": "SoftwareApplication",
            "name": "Delixio",
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "iOS, Android",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        },
    }

    sections_html = []
    for section in data.get("sections", []):
        parts = [f'      <h2>{esc_text(section["heading"])}</h2>']
        for p in section.get("paragraphs", []):
            parts.append(f"      <p>{linkify(p)}</p>")
        if section.get("list"):
            parts.append("      <ul>")
            for li in section["list"]:
                parts.append(f"        <li>{linkify(li)}</li>")
            parts.append("      </ul>")
        if section.get("examples"):
            parts.append('      <div class="landing-examples">')
            for ex in section["examples"]:
                parts.append('        <article class="landing-example">')
                parts.append(f'          <h3>{esc_text(ex["title"])}</h3>')
                parts.append(f"          <p>{linkify(ex['text'])}</p>")
                parts.append("        </article>")
            parts.append("      </div>")
        if section.get("steps"):
            parts.append('      <ol class="landing-steps">')
            for step in section["steps"]:
                parts.append(f"        <li>{linkify(step)}</li>")
            parts.append("      </ol>")
        sections_html.append("\n".join(parts))

    faq_html = []
    for item in data.get("faq", []):
        faq_html.append("      <article class=\"faq-item\">")
        faq_html.append(f'        <h3 class="faq-question">{esc_text(item["q"])}</h3>')
        faq_html.append(f'        <p class="faq-answer">{linkify(item["a"])}</p>')
        faq_html.append("      </article>")

    related_html = []
    for rel in data.get("related", []):
        related_html.append(
            f'        <li><a href="/{rel["slug"]}/">{esc_text(rel["label"])}</a></li>'
        )

    delixio = data.get("delixio", {})
    delixio_parts = [f'      <h2>{esc_text(delixio.get("heading", "How Delixio helps"))}</h2>']
    for p in delixio.get("paragraphs", []):
        delixio_parts.append(f"      <p>{linkify(p)}</p>")

    return f"""<!DOCTYPE html>
<html lang="{meta['html_lang']}">
<head>
  <meta charset="UTF-8">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{GA_ID}');
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(description)}">
  <title>{esc_text(title)}</title>
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:locale" content="{meta['og_locale']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Quicksand:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/main.css?v={CSS_VERSION}">
  <link rel="icon" href="../assets/logo.webp?v=45" type="image/webp">
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(webpage, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{render_faq_jsonld(data.get("faq", []))}
  </script>
</head>
<body class="page-download page-internal">
{site_header("../assets/", current=None)}
  <main class="legal-page legal-page--wide landing-page">
    <div class="legal-page-inner">
      <nav class="landing-breadcrumb" aria-label="Breadcrumb">
        <a href="/">Home</a>
        <span aria-hidden="true">/</span>
        <span>{esc_text(breadcrumb_name)}</span>
      </nav>
      <p class="legal-eyebrow">{esc_text(eyebrow)}</p>
      <h1>{esc_text(h1)}</h1>
{paragraphs(data.get("intro", []))}

{chr(10).join(sections_html)}

{chr(10).join(delixio_parts)}

      <h2>Related</h2>
      <ul class="landing-related">
{chr(10).join(related_html)}
      </ul>

      <div class="landing-download">
        <h2>Try Delixio</h2>
        <p>Delixio is currently available for iPhone and Android. Type the ingredients you already have, explore free recipe ideas, then unlock a full recipe when you want to cook. You get 1 free full recipe every day, plus optional credit packs. No subscription.</p>
        <div class="landing-badges">
          <a href="{APP_STORE}" class="store-badge" aria-label="Download Delixio on the App Store" target="_blank" rel="noopener noreferrer">
            <img src="../assets/badge-app-store.png?v=2" alt="Download Delixio on the App Store" width="472" height="134" loading="lazy">
          </a>
          <a href="{PLAY_STORE}" class="store-badge" aria-label="Get Delixio on Google Play" target="_blank" rel="noopener noreferrer">
            <img src="../assets/badge-google-play.png?v=2" alt="Get Delixio on Google Play" width="472" height="135" loading="lazy">
          </a>
        </div>
        <p class="landing-download-links"><a href="/download/">Download page</a> · <a href="/how-it-works/">How it works</a> · <a href="/faq/">FAQ</a></p>
      </div>

      <h2>FAQ</h2>
{chr(10).join(faq_html)}
    </div>
  </main>

{site_footer("../assets/", "../js/")}
</body>
</html>
"""


def card_blurb(page: dict) -> str:
    if page.get("card_blurb"):
        return page["card_blurb"]
    if page.get("intent"):
        # Intent is written as an infinitive phrase; make it a short card line.
        intent = page["intent"].strip()
        if intent and not intent.endswith("."):
            intent = intent[0].upper() + intent[1:] + "."
        return intent
    desc = page.get("description") or ""
    # Prefer the first sentence; fall back to a short clause.
    first = desc.split(". ")[0].strip()
    if first and not first.endswith("."):
        first += "."
    return first


def append_explore_cards(sections_html: list[str], items: list[dict]) -> None:
    sections_html.append('        <div class="explore-hub-grid">')
    for page in items:
        blurb = card_blurb(page)
        sections_html.append(
            f'          <a class="explore-link" href="/{page["slug"]}/">'
            f'<strong>{esc_text(page["h1"])}</strong>'
            f"<span>{esc_text(blurb)}</span></a>"
        )
    sections_html.append("        </div>")


def write_sitemap(landing_paths: list[str]) -> None:
    urls = STATIC_SITEMAP + sorted(set(landing_paths))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE}{path}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def render_guide_page(data: dict, locale: str = "en") -> str:
    """Editorial guide under /guides/<slug>/, not a search/AI landing page."""
    meta = LOCALE_META[locale]
    slug = data["slug"]
    url = f"{SITE}/guides/{slug}/"
    title = data["title"]
    description = data["description"]
    h1 = data["h1"]
    eyebrow = data.get("eyebrow", "Cooking guide")
    breadcrumb_name = data.get("breadcrumb", h1)

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Cooking Guides",
                "item": f"{SITE}/guides/",
            },
            {"@type": "ListItem", "position": 3, "name": breadcrumb_name, "item": url},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "Article",
        "name": title,
        "url": url,
        "description": description,
        "headline": h1,
        "isPartOf": {"@type": "WebSite", "name": "Delixio", "url": f"{SITE}/"},
        "about": {
            "@type": "SoftwareApplication",
            "name": "Delixio",
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "iOS, Android",
        },
    }

    sections_html = []
    for section in data.get("sections", []):
        parts = [f'      <h2>{esc_text(section["heading"])}</h2>']
        for p in section.get("paragraphs", []):
            parts.append(f"      <p>{linkify(p)}</p>")
        if section.get("list"):
            parts.append("      <ul>")
            for item in section["list"]:
                parts.append(f"        <li>{linkify(item)}</li>")
            parts.append("      </ul>")
        if section.get("steps"):
            parts.append('      <ol class="landing-steps">')
            for step in section["steps"]:
                parts.append(f"        <li>{linkify(step)}</li>")
            parts.append("      </ol>")
        sections_html.append("\n".join(parts))

    related_html = []
    for rel in data.get("related", []):
        if "href" in rel:
            href = rel["href"]
        elif rel.get("type") == "guide":
            href = f"/guides/{rel['slug']}/"
        else:
            # Default: link to a root intent landing page
            href = f"/{rel['slug']}/"
        related_html.append(
            f'        <li><a href="{esc(href)}">{esc_text(rel["label"])}</a></li>'
        )

    related_block = ""
    if related_html:
        related_block = (
            "\n      <h2>Related</h2>\n"
            '      <ul class="landing-related">\n'
            + "\n".join(related_html)
            + "\n      </ul>\n"
        )

    delixio = data.get("delixio", {})
    delixio_parts = []
    if delixio:
        delixio_parts.append(
            f'      <h2>{esc_text(delixio.get("heading", "How Delixio helps"))}</h2>'
        )
        for p in delixio.get("paragraphs", []):
            delixio_parts.append(f"      <p>{linkify(p)}</p>")

    return f"""<!DOCTYPE html>
<html lang="{meta['html_lang']}">
<head>
  <meta charset="UTF-8">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{GA_ID}');
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(description)}">
  <title>{esc_text(title)}</title>
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:locale" content="{meta['og_locale']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Quicksand:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/main.css?v={CSS_VERSION}">
  <link rel="icon" href="../../assets/logo.webp?v=45" type="image/webp">
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(webpage, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="page-download page-internal">
{site_header("../../assets/", current="guides")}
  <main class="legal-page legal-page--wide landing-page guide-page">
    <div class="legal-page-inner">
      <nav class="landing-breadcrumb" aria-label="Breadcrumb">
        <a href="/">Home</a>
        <span aria-hidden="true">/</span>
        <a href="/guides/">Cooking Guides</a>
        <span aria-hidden="true">/</span>
        <span>{esc_text(breadcrumb_name)}</span>
      </nav>
      <p class="legal-eyebrow">{esc_text(eyebrow)}</p>
      <h1>{esc_text(h1)}</h1>
{paragraphs(data.get("intro", []))}

{chr(10).join(sections_html)}

{chr(10).join(delixio_parts)}
{related_block}
      <div class="landing-download">
        <h2>Try Delixio</h2>
        <p>Delixio is currently available for iPhone and Android. Type the ingredients you already have, explore free recipe ideas, then unlock a full recipe when you want to cook. You get 1 free full recipe every day, plus optional credit packs. No subscription.</p>
        <div class="landing-badges">
          <a href="{APP_STORE}" class="store-badge" aria-label="Download Delixio on the App Store" target="_blank" rel="noopener noreferrer">
            <img src="../../assets/badge-app-store.png?v=2" alt="Download Delixio on the App Store" width="472" height="134" loading="lazy">
          </a>
          <a href="{PLAY_STORE}" class="store-badge" aria-label="Get Delixio on Google Play" target="_blank" rel="noopener noreferrer">
            <img src="../../assets/badge-google-play.png?v=2" alt="Get Delixio on Google Play" width="472" height="135" loading="lazy">
          </a>
        </div>
        <p class="landing-download-links"><a href="/download/">Download page</a> · <a href="/guides/">All cooking guides</a> · <a href="/faq/">FAQ</a></p>
      </div>
    </div>
  </main>

{site_footer("../../assets/", "../../js/")}
</body>
</html>
"""


def group_guides_by_category(guide_pages: list[dict]) -> tuple[dict[str, list[dict]], list[dict]]:
    by_category: dict[str, list[dict]] = {key: [] for key in GUIDE_CATEGORY_ORDER}
    other: list[dict] = []
    for page in guide_pages:
        category = page.get("category", "")
        if category in by_category:
            by_category[category].append(page)
        else:
            other.append(page)
    return by_category, other


def category_count_label(count: int) -> str:
    if count == 0:
        return "Coming soon"
    if count == 1:
        return "1 guide"
    return f"{count} guides"


def render_guide_category_page(
    category: str,
    guide_pages: list[dict],
    locale: str = "en",
) -> str:
    """Category listing under /guides/<category>/."""
    meta = LOCALE_META[locale]
    meta_cat = GUIDE_CATEGORY_META[category]
    label = meta_cat["label"]
    blurb = meta_cat["blurb"]
    url = f"{SITE}/guides/{category}/"
    title = f"{label} | Delixio Cooking Guides"
    description = f"{blurb} Browse Delixio cooking guides in this section."

    cards: list[str] = []
    if guide_pages:
        cards.append('      <div class="explore-hub-grid">')
        for page in guide_pages:
            card_blurb = page.get("card_blurb") or page.get("description") or ""
            cards.append(
                f'        <a class="explore-link" href="/guides/{page["slug"]}/">'
                f'<strong>{esc_text(page["h1"])}</strong>'
                f"<span>{esc_text(card_blurb)}</span></a>"
            )
        cards.append("      </div>")
    else:
        cards.append(
            '      <p class="explore-hub-empty">Guides in this section are coming soon. '
            'In the meantime, see <a href="/how-it-works/">how Delixio works</a> '
            'or browse the <a href="/faq/">FAQ</a>.</p>'
        )

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Cooking Guides",
                "item": f"{SITE}/guides/",
            },
            {"@type": "ListItem", "position": 3, "name": label, "item": url},
        ],
    }
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": label,
        "url": url,
        "description": description,
        "isPartOf": {"@type": "WebSite", "name": "Delixio", "url": f"{SITE}/"},
    }

    return f"""<!DOCTYPE html>
<html lang="{meta['html_lang']}">
<head>
  <meta charset="UTF-8">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{GA_ID}');
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(description)}">
  <title>{esc_text(title)}</title>
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:locale" content="{meta['og_locale']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Quicksand:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/main.css?v={CSS_VERSION}">
  <link rel="icon" href="../../assets/logo.webp?v=45" type="image/webp">
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(collection, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="page-download page-internal">
{site_header("../../assets/", current="guides")}
  <main class="legal-page legal-page--wide explore-hub">
    <div class="legal-page-inner">
      <nav class="landing-breadcrumb" aria-label="Breadcrumb">
        <a href="/">Home</a>
        <span aria-hidden="true">/</span>
        <a href="/guides/">Cooking Guides</a>
        <span aria-hidden="true">/</span>
        <span>{esc_text(label)}</span>
      </nav>
      <p class="legal-eyebrow">Cooking Guides</p>
      <h1>{esc_text(label)}</h1>
      <p class="explore-hub-lead">{esc_text(blurb)}</p>

{chr(10).join(cards)}

      <p class="faq-kb-footer-links">
        <a href="/guides/">← All cooking guides</a>
        · See <a href="/how-it-works/">how Delixio works</a>
        · <a href="/faq/">FAQ</a>
        · <a href="/download/">Download</a>
      </p>
    </div>
  </main>

{site_footer("../../assets/", "../../js/")}
</body>
</html>
"""


def render_guides_hub(guide_pages: list[dict], locale: str = "en") -> str:
    """Editorial Cooking Guides hub, category cards linking to listing pages."""
    meta = LOCALE_META[locale]
    url = f"{SITE}/guides/"
    title = "Delixio Cooking Guides"
    description = (
        "Practical Delixio cooking guides for weeknight dinners, leftovers, "
        "pantry cooking, and planning meals around ingredients you already have."
    )

    by_category, other = group_guides_by_category(guide_pages)
    has_any_guides = bool(guide_pages)

    cards_html: list[str] = ['      <div class="explore-hub-grid explore-hub-categories">']
    for category in GUIDE_CATEGORY_ORDER:
        meta_cat = GUIDE_CATEGORY_META[category]
        count = len(by_category[category])
        icon = meta_cat["icon"]
        cards_html.append(
            f'        <a class="explore-link explore-cat-card" href="/guides/{category}/">'
            f'<span class="explore-cat-icon" aria-hidden="true">'
            f'<img src="../assets/icons/{icon}?v=45" alt="" '
            f'width="{meta_cat["icon_w"]}" height="{meta_cat["icon_h"]}">'
            f"</span>"
            f'<strong>{esc_text(meta_cat["label"])}</strong>'
            f'<span>{esc_text(meta_cat["blurb"])}</span>'
            f'<span class="explore-cat-meta">{esc_text(category_count_label(count))}</span>'
            f"</a>"
        )
    cards_html.append("      </div>")

    other_html = ""
    if other:
        other_parts = [
            '      <section class="explore-hub-section" aria-labelledby="guide-cat-other">',
            '        <h2 id="guide-cat-other">More guides</h2>',
            '        <div class="explore-hub-grid">',
        ]
        for page in other:
            card_blurb = page.get("card_blurb") or page.get("description") or ""
            other_parts.append(
                f'          <a class="explore-link" href="/guides/{page["slug"]}/">'
                f'<strong>{esc_text(page["h1"])}</strong>'
                f"<span>{esc_text(card_blurb)}</span></a>"
            )
        other_parts.extend(["        </div>", "      </section>"])
        other_html = "\n" + "\n".join(other_parts)

    if not has_any_guides:
        intro_extra = (
            '      <p class="explore-hub-lead">We are preparing editorial cooking guides for these topics. '
            'In the meantime, see <a href="/how-it-works/">how Delixio works</a> '
            'or browse the <a href="/faq/">FAQ</a>.</p>'
        )
    else:
        intro_extra = ""

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Cooking Guides", "item": url},
        ],
    }
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "url": url,
        "description": description,
        "isPartOf": {"@type": "WebSite", "name": "Delixio", "url": f"{SITE}/"},
    }

    return f"""<!DOCTYPE html>
<html lang="{meta['html_lang']}">
<head>
  <meta charset="UTF-8">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{GA_ID}');
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(description)}">
  <title>{esc_text(title)}</title>
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:locale" content="{meta['og_locale']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Quicksand:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/main.css?v={CSS_VERSION}">
  <link rel="icon" href="../assets/logo.webp?v=45" type="image/webp">
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(collection, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="page-download page-internal">
{site_header("../assets/", current="guides")}
  <main class="legal-page legal-page--wide explore-hub">
    <div class="legal-page-inner">
      <nav class="landing-breadcrumb" aria-label="Breadcrumb">
        <a href="/">Home</a>
        <span aria-hidden="true">/</span>
        <span>Cooking Guides</span>
      </nav>
      <p class="legal-eyebrow">Cooking Guides</p>
      <h1>Delixio cooking guides</h1>
      <p class="explore-hub-lead">Practical articles that help you solve real kitchen problems, from weeknight dinners and leftovers to pantry cooking and simple meal planning.</p>
      <p class="explore-hub-lead explore-hub-lead--second">Start with the problem you're trying to solve.</p>
{intro_extra}

{chr(10).join(cards_html)}
{other_html}

      <p class="faq-kb-footer-links">
        New here? See <a href="/how-it-works/">how Delixio works</a>, read the <a href="/faq/">FAQ</a>, or <a href="/download/">download the app</a>.
      </p>
    </div>
  </main>

{site_footer("../assets/", "../js/")}
</body>
</html>
"""


def write_explore_redirect() -> None:
    """Keep /explore/ as a soft redirect to /guides/ for early bookmarks."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-89YMNXP5XF"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-89YMNXP5XF');
  </script>
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="https://delixioapp.com/guides/">
  <meta http-equiv="refresh" content="0; url=/guides/">
  <title>Redirecting to Cooking Guides | Delixio</title>
</head>
<body>
  <p><a href="/guides/">Delixio cooking guides</a></p>
</body>
</html>
"""
    explore_dir = ROOT / "explore"
    explore_dir.mkdir(parents=True, exist_ok=True)
    (explore_dir / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    landing_paths: list[str] = []
    guide_paths: list[str] = []
    locales = sorted(p.name for p in CONTENT_DIR.iterdir() if p.is_dir())
    if not locales:
        raise SystemExit(f"No locale directories found under {CONTENT_DIR}")

    for locale in locales:
        if locale not in LOCALE_META:
            print(f"Skipping unknown locale: {locale}")
            continue
        for path in sorted((CONTENT_DIR / locale).glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            slug = data["slug"]
            if slug != path.stem:
                raise SystemExit(f"slug mismatch: {path} vs {slug}")
            page_type = data.get("type", "landing")
            if page_type != "landing":
                raise SystemExit(f"{path} must have type=landing (got {page_type})")
            data["type"] = "landing"
            html_out = render_page(data, locale=locale)
            out_dir = output_dir(slug, locale)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html_out, encoding="utf-8")
            prefix = LOCALE_META[locale]["dir_prefix"]
            landing_paths.append(f"/{prefix}{slug}/")
            print(f"Wrote landing {out_dir / 'index.html'}")

    en_guides: list[dict] = []
    guides_en = GUIDES_DIR / "en"
    reserved_category_slugs = set(GUIDE_CATEGORY_ORDER)
    if guides_en.exists():
        for path in sorted(guides_en.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            data["type"] = "guide"
            slug = data["slug"]
            if slug != path.stem:
                raise SystemExit(f"guide slug mismatch: {path} vs {slug}")
            if slug in reserved_category_slugs:
                raise SystemExit(
                    f"guide slug '{slug}' collides with reserved category path /guides/{slug}/"
                )
            html_out = render_guide_page(data, locale="en")
            out_dir = ROOT / "guides" / slug
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html_out, encoding="utf-8")
            en_guides.append(data)
            guide_paths.append(f"/guides/{slug}/")
            print(f"Wrote guide {out_dir / 'index.html'}")

    by_category, _other = group_guides_by_category(en_guides)
    category_paths: list[str] = []
    for category in GUIDE_CATEGORY_ORDER:
        cat_html = render_guide_category_page(
            category, by_category[category], locale="en"
        )
        cat_dir = ROOT / "guides" / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        (cat_dir / "index.html").write_text(cat_html, encoding="utf-8")
        category_paths.append(f"/guides/{category}/")
        print(f"Wrote category {cat_dir / 'index.html'}")

    guides_html = render_guides_hub(en_guides, locale="en")
    guides_dir = ROOT / "guides"
    guides_dir.mkdir(parents=True, exist_ok=True)
    (guides_dir / "index.html").write_text(guides_html, encoding="utf-8")
    print(f"Wrote {guides_dir / 'index.html'}")
    write_explore_redirect()
    print(f"Wrote {ROOT / 'explore' / 'index.html'} (redirect)")

    all_extra = landing_paths + guide_paths + category_paths
    write_sitemap(all_extra)
    print(f"Updated sitemap.xml ({len(STATIC_SITEMAP) + len(all_extra)} URLs)")


if __name__ == "__main__":
    main()
