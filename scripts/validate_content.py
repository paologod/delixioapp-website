#!/usr/bin/env python3
"""Run structural content quality checks without rebuilding HTML.

Usage:
  python3 scripts/validate_content.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_landings import (  # noqa: E402
    CONTENT_DIR,
    GUIDES_DIR,
    run_content_quality_checks,
)


def main() -> None:
    landings: list[dict] = []
    en = CONTENT_DIR / "en"
    if en.exists():
        for path in sorted(en.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("status", "published") != "published":
                continue
            data["type"] = "landing"
            landings.append(data)

    guides: list[dict] = []
    guides_en = GUIDES_DIR / "en"
    if guides_en.exists():
        for path in sorted(guides_en.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("status", "published") != "published":
                continue
            data["type"] = "guide"
            guides.append(data)

    run_content_quality_checks(landings, guides)


if __name__ == "__main__":
    main()
