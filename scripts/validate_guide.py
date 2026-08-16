#!/usr/bin/env python3
"""Validate a Delixio editorial guide JSON file.

Usage:
  python3 scripts/validate_guide.py content/guides/en/<slug>.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {"dinner", "leftovers", "pantry", "planning"}
REQUIRED = {
    "type",
    "slug",
    "category",
    "card_blurb",
    "breadcrumb",
    "eyebrow",
    "title",
    "description",
    "h1",
    "intro",
    "sections",
    "delixio",
    "related",
}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: python3 scripts/validate_guide.py content/guides/en/<slug>.json")

    path = Path(sys.argv[1])
    if not path.is_file():
        fail(f"file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED - set(data))
    if missing:
        fail(f"missing fields: {', '.join(missing)}")

    if data.get("type") != "guide":
        fail('type must be "guide"')

    slug = data["slug"]
    if slug != path.stem:
        fail(f'slug "{slug}" must match filename stem "{path.stem}"')
    if slug in CATEGORIES:
        fail(f'slug "{slug}" is reserved for category listing pages')

    if data["category"] not in CATEGORIES:
        fail(f'category must be one of: {", ".join(sorted(CATEGORIES))}')

    if not isinstance(data["intro"], list) or not data["intro"]:
        fail("intro must be a non-empty array of strings")

    if not isinstance(data["sections"], list) or not data["sections"]:
        fail("sections must be a non-empty array")

    delixio = data["delixio"]
    if not isinstance(delixio, dict) or not delixio.get("paragraphs"):
        fail("delixio.paragraphs is required")

    if not isinstance(data["related"], list) or len(data["related"]) < 1:
        fail("related must include at least one item")

    text_blob = json.dumps(data, ensure_ascii=False)
    if "—" in text_blob:
        fail("em dash (—) found; use commas, colons, periods, or | instead")

    image = data.get("image")
    if image is not None:
        if not isinstance(image, dict):
            fail("image must be an object when present")
        filename = (image.get("file") or "").strip()
        alt = (image.get("alt") or "").strip()
        if not filename:
            fail("image.file is required when image is set")
        if "/" in filename or "\\" in filename or ".." in filename:
            fail("image.file must be a filename only (no directories)")
        if not alt:
            fail("image.alt is required when image is set")
        disk = ROOT / "assets" / "guides" / filename
        if not disk.is_file():
            fail(f"image file missing: {disk}")

    print(f"OK: {path}")


if __name__ == "__main__":
    main()
