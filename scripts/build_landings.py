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
CSS_VERSION = "97"
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
          <li><a href="/privacy/">Privacy</a></li>
          <li><a href="/terms/">Terms</a></li>
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

  <script src="{js_prefix}main.js?v=2"></script>
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
    "/terms/es/",
    "/terms/fr/",
    "/terms/it/",
    "/support/",
    "/delete-account/",
    "/it/ricette-con-ingredienti/",
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


def _safe_href(href: str) -> str | None:
    h = href.strip()
    if h.startswith("/") or h.startswith("https://") or h.startswith("http://") or h.startswith("#"):
        return h
    return None


def rich_text(text: str) -> str:
    """Render allowed inline Markdown into HTML (escaped otherwise).

    Supported:
    - [[/path/|label]] internal/wiki links
    - [label](url) Markdown links (http(s), /, # only)
    - **bold** / __bold__
    - *italic* / _italic_
    - `inline code`
    """
    placeholders: list[str] = []

    def stash(fragment: str) -> str:
        placeholders.append(fragment)
        return f"@@DELIXIOPH{len(placeholders) - 1}@@"

    def wiki_link(m: re.Match[str]) -> str:
        href = _safe_href(m.group(1).strip())
        if not href:
            return m.group(0)
        return stash(f'<a href="{esc(href)}">{esc_text(m.group(2))}</a>')

    def md_link(m: re.Match[str]) -> str:
        href = _safe_href(m.group(2).strip())
        if not href:
            return m.group(0)
        return stash(f'<a href="{esc(href)}">{esc_text(m.group(1))}</a>')

    def bold(m: re.Match[str]) -> str:
        return stash(f"<strong>{esc_text(m.group(1))}</strong>")

    def italic(m: re.Match[str]) -> str:
        return stash(f"<em>{esc_text(m.group(1))}</em>")

    def code(m: re.Match[str]) -> str:
        return stash(f"<code>{esc_text(m.group(1))}</code>")

    s = text
    s = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", wiki_link, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", md_link, s)
    s = re.sub(r"`([^`]+)`", code, s)
    s = re.sub(r"\*\*([^*]+)\*\*", bold, s)
    s = re.sub(r"__([^_]+)__", bold, s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", italic, s)
    s = re.sub(r"(?<!_)_([^_]+)_(?!_)", italic, s)
    out = esc_text(s)
    for i, fragment in enumerate(placeholders):
        out = out.replace(f"@@DELIXIOPH{i}@@", fragment)
    return out


def linkify(text: str) -> str:
    """Backward-compatible alias for rich_text."""
    return rich_text(text)


def _is_md_table_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.count("|") >= 2


def _is_md_table_separator(line: str) -> bool:
    s = line.strip().strip("|")
    if not s:
        return False
    cells = [c.strip() for c in s.split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells)


def _split_md_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def parse_md_table_lines(lines: list[str]) -> dict | None:
    """Parse GitHub-flavored markdown table lines into headers + rows."""
    body = [ln for ln in lines if ln.strip()]
    if len(body) < 2:
        return None
    headers = _split_md_row(body[0])
    if not headers:
        return None
    start = 1
    if _is_md_table_separator(body[1]):
        start = 2
    rows = [_split_md_row(ln) for ln in body[start:]]
    rows = [r for r in rows if any(cell for cell in r)]
    if not rows:
        return None
    width = len(headers)
    norm_rows = []
    for row in rows:
        padded = (row + [""] * width)[:width]
        norm_rows.append(padded)
    return {"headers": headers, "rows": norm_rows}


def render_table_html(table: dict) -> str:
    headers = table.get("headers") or []
    rows = table.get("rows") or []
    if not headers or not rows:
        return ""
    parts = ['      <div class="guide-table-wrap">', '        <table class="guide-table">']
    parts.append("          <thead>")
    parts.append("            <tr>")
    for cell in headers:
        parts.append(f"              <th>{rich_text(cell)}</th>")
    parts.append("            </tr>")
    parts.append("          </thead>")
    parts.append("          <tbody>")
    for row in rows:
        parts.append("            <tr>")
        for cell in row:
            parts.append(f"              <td>{rich_text(str(cell))}</td>")
        parts.append("            </tr>")
    parts.append("          </tbody>")
    parts.append("        </table>")
    parts.append("      </div>")
    return "\n".join(parts)


def flow_paragraphs(items: list[str]) -> list[str]:
    """Render paragraph strings, coalescing markdown pipe-tables into HTML tables."""
    parts: list[str] = []
    i = 0
    while i < len(items):
        line = items[i]
        if _is_md_table_line(line):
            block = []
            while i < len(items) and _is_md_table_line(items[i]):
                block.append(items[i])
                i += 1
            parsed = parse_md_table_lines(block)
            if parsed:
                html_table = render_table_html(parsed)
                if html_table:
                    parts.append(html_table)
                    continue
            for raw in block:
                parts.append(f"      <p>{rich_text(raw)}</p>")
            continue
        parts.append(f"      <p>{rich_text(line)}</p>")
        i += 1
    return parts


def paragraphs(items: list[str]) -> str:
    return "\n".join(flow_paragraphs(items))


def render_section_body(section: dict) -> list[str]:
    """Shared section body for landings and guides (paragraphs, table, list, steps)."""
    parts: list[str] = []
    parts.extend(flow_paragraphs(section.get("paragraphs") or []))
    table = section.get("table")
    if isinstance(table, dict):
        html_table = render_table_html(table)
        if html_table:
            parts.append(html_table)
    parts.extend(flow_paragraphs(section.get("paragraphs_after") or []))
    if section.get("list"):
        parts.append("      <ul>")
        for item in section["list"]:
            parts.append(f"        <li>{rich_text(item)}</li>")
        parts.append("      </ul>")
    if section.get("examples"):
        parts.append('      <div class="landing-examples">')
        for ex in section["examples"]:
            parts.append('        <article class="landing-example">')
            parts.append(f'          <h3>{esc_text(ex["title"])}</h3>')
            parts.append(f"          <p>{rich_text(ex['text'])}</p>")
            parts.append("        </article>")
        parts.append("      </div>")
    if section.get("steps"):
        parts.append('      <ol class="landing-steps">')
        for step in section["steps"]:
            parts.append(f"        <li>{rich_text(step)}</li>")
        parts.append("      </ol>")
    return parts


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
    raw_hero = data.get("hero") if isinstance(data.get("hero"), dict) else {}
    hero_file = str(raw_hero.get("file") or "").strip()
    if hero_file and not re.fullmatch(r"[a-z0-9][a-z0-9._-]*\.webp", hero_file):
        raise ValueError(f"Invalid landing hero filename for {slug}: {hero_file}")
    hero_alt = str(raw_hero.get("alt") or "").strip()
    hero_width = int(raw_hero.get("width") or 1440)
    hero_height = int(raw_hero.get("height") or 810)
    hero_image_url = f"{SITE}/assets/landings/{hero_file}" if hero_file else OG_IMAGE
    hero_html = ""
    hero_css = ""
    if hero_file:
        hero_html = (
            '      <figure class="landing-hero">\n'
            f'        <img src="../assets/landings/{esc(hero_file)}" alt="{esc(hero_alt)}" '
            f'width="{hero_width}" height="{hero_height}" fetchpriority="high">\n'
            "      </figure>\n"
        )
        hero_css = """  <style>
    .landing-hero { margin: clamp(20px, 3vw, 32px) 0; overflow: hidden; border-radius: 24px; background: var(--color-primary-light); }
    .landing-hero img { display: block; width: 100%; height: auto; aspect-ratio: 16 / 9; object-fit: cover; }
  </style>
"""

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
        parts.extend(render_section_body(section))
        sections_html.append("\n".join(parts))

    faq_html = []
    for item in data.get("faq", []):
        faq_html.append("      <article class=\"faq-item\">")
        faq_html.append(f'        <h3 class="faq-question">{esc_text(item["q"])}</h3>')
        faq_html.append(f'        <p class="faq-answer">{rich_text(item["a"])}</p>')
        faq_html.append("      </article>")

    related_html = []
    for rel in data.get("related", []):
        related_html.append(
            f'        <li><a href="/{rel["slug"]}/">{esc_text(rel["label"])}</a></li>'
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
    delixio_parts = [f'      <h2>{esc_text(delixio.get("heading", "How Delixio helps"))}</h2>']
    for p in delixio.get("paragraphs", []):
        delixio_parts.append(f"      <p>{rich_text(p)}</p>")

    faq_jsonld = ""
    if data.get("faq"):
        faq_jsonld = (
            '  <script type="application/ld+json">\n'
            + render_faq_jsonld(data.get("faq", []))
            + "\n  </script>"
        )

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
  <meta property="og:image" content="{hero_image_url}">
  <meta property="og:locale" content="{meta['og_locale']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{hero_image_url}">
{hero_css}  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Quicksand:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/main.css?v={CSS_VERSION}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png?v=1">
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png?v=1">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png?v=1">
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(webpage, ensure_ascii=False, indent=2)}
  </script>
{faq_jsonld}
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
{hero_html}{paragraphs(data.get("intro", []))}

{chr(10).join(sections_html)}

{chr(10).join(delixio_parts)}
{related_block}
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


def guide_image_meta(data: dict) -> dict | None:
    """Optional guide hero image. Files live under assets/guides/.

    JSON shape:
      "image": {
        "file": "my-slug.webp",
        "alt": "Descriptive alt text",
        "credit": "optional credit line"
      }
    """
    image = data.get("image")
    if not image:
        return None
    filename = (image.get("file") or "").strip()
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        return None
    alt = (image.get("alt") or data.get("h1") or "Cooking guide").strip()
    credit = (image.get("credit") or "").strip()
    web_path = f"/assets/guides/{filename}"
    return {
        "filename": filename,
        "web_path": web_path,
        "abs_url": f"{SITE}{web_path}",
        "alt": alt,
        "credit": credit,
        "disk_path": ROOT / "assets" / "guides" / filename,
    }


def guide_hero_html(image: dict | None) -> str:
    if not image:
        return ""
    credit = ""
    if image["credit"]:
        credit = (
            f'\n      <p class="guide-hero-credit">{esc_text(image["credit"])}</p>'
        )
    return f"""      <figure class="guide-hero">
        <img src="{image["web_path"]}" alt="{esc(image["alt"])}" width="1200" height="675" loading="eager">
      </figure>{credit}
"""


def guide_card_html(page: dict) -> str:
    blurb = page.get("card_blurb") or page.get("description") or ""
    image = guide_image_meta(page)
    thumb = ""
    if image and image["disk_path"].exists():
        thumb = (
            f'<span class="explore-card-thumb">'
            f'<img src="{image["web_path"]}" alt="" width="640" height="360" loading="lazy">'
            f"</span>"
        )
    return (
        f'        <a class="explore-link{" explore-link--with-image" if thumb else ""}" '
        f'href="/guides/{page["slug"]}/">'
        f"{thumb}"
        f'<strong>{esc_text(page["h1"])}</strong>'
        f"<span>{esc_text(blurb)}</span></a>"
    )


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
    category = str(data.get("category") or "")
    cat_meta = GUIDE_CATEGORY_META.get(category)

    crumb_items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {
            "@type": "ListItem",
            "position": 2,
            "name": "Cooking Guides",
            "item": f"{SITE}/guides/",
        },
    ]
    if cat_meta:
        crumb_items.append(
            {
                "@type": "ListItem",
                "position": 3,
                "name": cat_meta["label"],
                "item": f"{SITE}/guides/{category}/",
            }
        )
        crumb_items.append(
            {"@type": "ListItem", "position": 4, "name": breadcrumb_name, "item": url}
        )
        cat_crumb_html = (
            f'        <a href="/guides/{category}/">{esc_text(cat_meta["label"])}</a>\n'
            '        <span aria-hidden="true">/</span>\n'
        )
        eyebrow_html = (
            f'<a href="/guides/{category}/">{esc_text(eyebrow)}</a>'
        )
    else:
        crumb_items.append(
            {"@type": "ListItem", "position": 3, "name": breadcrumb_name, "item": url}
        )
        cat_crumb_html = ""
        eyebrow_html = esc_text(eyebrow)

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": crumb_items,
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "name": title,
        "url": url,
        "description": description,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "isPartOf": {"@type": "WebSite", "name": "Delixio", "url": f"{SITE}/"},
        "publisher": {
            "@type": "Organization",
            "name": "Delixio",
            "url": f"{SITE}/",
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE}/assets/logo.webp",
            },
        },
        "about": {
            "@type": "SoftwareApplication",
            "name": "Delixio",
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "iOS, Android",
        },
    }
    author = (data.get("author") or "").strip()
    if author:
        webpage["author"] = {"@type": "Organization", "name": author}
    if data.get("datePublished"):
        webpage["datePublished"] = data["datePublished"]
    if data.get("dateModified"):
        webpage["dateModified"] = data["dateModified"]
    elif data.get("datePublished"):
        webpage["dateModified"] = data["datePublished"]

    image = guide_image_meta(data)
    og_image = image["abs_url"] if image else OG_IMAGE
    if image:
        webpage["image"] = [image["abs_url"]]

    sections_html = []
    for section in data.get("sections", []):
        parts = [f'      <h2>{esc_text(section["heading"])}</h2>']
        parts.extend(render_section_body(section))
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
            delixio_parts.append(f"      <p>{rich_text(p)}</p>")

    faq_items = [item for item in data.get("faq", []) if isinstance(item, dict) and item.get("q") and item.get("a")]
    faq_html = []
    for item in faq_items:
        faq_html.append("      <article class=\"faq-item\">")
        faq_html.append(f'        <h3 class="faq-question">{esc_text(item["q"])}</h3>')
        faq_html.append(f'        <p class="faq-answer">{rich_text(item["a"])}</p>')
        faq_html.append("      </article>")
    faq_block = ""
    if faq_html:
        faq_block = "\n      <h2>FAQ</h2>\n" + "\n".join(faq_html) + "\n"
    faq_jsonld = ""
    if faq_items:
        faq_jsonld = (
            "\n  <script type=\"application/ld+json\">\n"
            + render_faq_jsonld(faq_items)
            + "\n  </script>"
        )

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
  <meta property="og:image" content="{og_image}">
  <meta property="og:locale" content="{meta['og_locale']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Quicksand:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../css/main.css?v={CSS_VERSION}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png?v=1">
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png?v=1">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png?v=1">
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(webpage, ensure_ascii=False, indent=2)}
  </script>{faq_jsonld}
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
{cat_crumb_html}        <span>{esc_text(breadcrumb_name)}</span>
      </nav>
      <p class="legal-eyebrow">{eyebrow_html}</p>
      <h1>{esc_text(h1)}</h1>
{guide_hero_html(image)}
{paragraphs(data.get("intro", []))}

{chr(10).join(sections_html)}

{chr(10).join(delixio_parts)}
{related_block}{faq_block}
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
    for key in by_category:
        by_category[key].sort(key=_guide_list_sort_key, reverse=True)
    other.sort(key=_guide_list_sort_key, reverse=True)
    return by_category, other


def _guide_list_sort_key(page: dict) -> tuple[str, str]:
    return (str(page.get("datePublished") or ""), str(page.get("slug") or ""))


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
            cards.append(guide_card_html(page))
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
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png?v=1">
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png?v=1">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png?v=1">
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
            other_parts.append(guide_card_html(page))
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
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png?v=1">
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png?v=1">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png?v=1">
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


def write_redirects() -> list[str]:
    """Write soft redirect HTML for retired URLs. Returns paths to exclude from sitemap."""
    redirects_path = ROOT / "content" / "redirects.json"
    if not redirects_path.exists():
        return []
    redirects = json.loads(redirects_path.read_text(encoding="utf-8"))
    excluded: list[str] = []
    for item in redirects:
        src = item["from"].rstrip("/") + "/"
        dest = item["to"]
        excluded.append(src)
        # Map /guides/slug/ -> guides/slug/index.html
        rel = src.strip("/")
        out_dir = ROOT / rel
        out_dir.mkdir(parents=True, exist_ok=True)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="{SITE}{dest}">
  <meta http-equiv="refresh" content="0; url={dest}">
  <title>Redirecting…</title>
</head>
<body>
  <p>This page has moved to <a href="{esc(dest)}">{esc_text(dest)}</a>.</p>
</body>
</html>
"""
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"Wrote redirect {out_dir / 'index.html'} -> {dest}")
    return excluded


def run_content_quality_checks(
    landing_pages: list[dict],
    guide_pages: list[dict],
) -> None:
    """Warn about structural content issues (non-fatal)."""
    warnings: list[str] = []
    titles: dict[str, list[str]] = {}
    slugs: dict[str, list[str]] = {}

    def note_title(title: str, url: str) -> None:
        titles.setdefault(title.strip().lower(), []).append(url)

    def note_slug(slug: str, kind: str) -> None:
        slugs.setdefault(slug, []).append(kind)

    for page in landing_pages:
        slug = page["slug"]
        note_slug(slug, "landing")
        note_title(page.get("title", ""), f"/{slug}/")
        if not page.get("description"):
            warnings.append(f"landing {slug}: missing description")
        if not page.get("h1"):
            warnings.append(f"landing {slug}: missing h1")
        related = page.get("related") or []
        if not related:
            warnings.append(f"landing {slug}: empty related")
        elif len(related) < 2:
            warnings.append(f"landing {slug}: related has fewer than 2 links")

    for page in guide_pages:
        slug = page["slug"]
        note_slug(slug, "guide")
        note_title(page.get("title", ""), f"/guides/{slug}/")
        if page.get("type") not in (None, "guide") and page.get("content_type") == "landing":
            warnings.append(f"guide {slug}: landing content_type on guide path")
        if not page.get("description"):
            warnings.append(f"guide {slug}: missing description")
        if not page.get("h1"):
            warnings.append(f"guide {slug}: missing h1")
        if not page.get("datePublished"):
            warnings.append(f"guide {slug}: missing datePublished")
        if not page.get("author"):
            warnings.append(f"guide {slug}: missing author")
        related = page.get("related") or []
        if not related:
            warnings.append(f"guide {slug}: empty related")

    for slug, kinds in slugs.items():
        if len(kinds) > 1:
            warnings.append(f"duplicate slug across types: {slug} ({', '.join(kinds)})")

    for title, urls in titles.items():
        if title and len(urls) > 1:
            warnings.append(f"duplicate title '{title}' on {', '.join(urls)}")

    # Broken related targets
    landing_slugs = {p["slug"] for p in landing_pages}
    guide_slugs = {p["slug"] for p in guide_pages}
    for page in landing_pages + guide_pages:
        for rel in page.get("related") or []:
            target = rel.get("slug")
            if not target:
                continue
            if rel.get("type") == "guide":
                if target not in guide_slugs:
                    warnings.append(
                        f"{page.get('slug')}: related guide missing: {target}"
                    )
            else:
                if target not in landing_slugs and not rel.get("href"):
                    warnings.append(
                        f"{page.get('slug')}: related landing missing: {target}"
                    )

    if warnings:
        print("Content quality warnings:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("Content quality checks: OK")


def main() -> None:
    landing_paths: list[str] = []
    guide_paths: list[str] = []
    landing_pages: list[dict] = []
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
            if data.get("status", "published") != "published":
                print(f"Skipping unpublished landing {path}")
                continue
            data["type"] = "landing"
            html_out = render_page(data, locale=locale)
            out_dir = output_dir(slug, locale)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html_out, encoding="utf-8")
            prefix = LOCALE_META[locale]["dir_prefix"]
            landing_paths.append(f"/{prefix}{slug}/")
            if locale == "en":
                landing_pages.append(data)
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
            if data.get("status", "published") != "published":
                print(f"Skipping unpublished guide {path}")
                continue
            image = guide_image_meta(data)
            if data.get("image") and not image:
                raise SystemExit(f"{path}: invalid image.file (use filename only under assets/guides/)")
            if image and not image["disk_path"].exists():
                raise SystemExit(
                    f"{path}: image file missing: {image['disk_path']} "
                    f"(save the asset before building)"
                )
            if image and not (image.get("alt") or "").strip():
                raise SystemExit(f"{path}: image.alt is required when image is set")
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
    redirect_paths = write_redirects()

    all_extra = landing_paths + guide_paths + category_paths
    # redirects are written but excluded from sitemap
    write_sitemap(all_extra)
    print(f"Updated sitemap.xml ({len(STATIC_SITEMAP) + len(all_extra)} URLs)")
    if redirect_paths:
        print(f"Redirect pages excluded from sitemap: {', '.join(redirect_paths)}")
    run_content_quality_checks(landing_pages, en_guides)


if __name__ == "__main__":
    main()
