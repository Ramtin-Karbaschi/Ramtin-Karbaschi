#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

text = README.read_text(encoding="utf-8")

errors: list[str] = []

for forbidden in [
    "&nbsp;",
    "&#160;",
    "### AI and model systems",
    "### Platform and inference infrastructure",
    "### Data, retrieval and operations",
]:
    if forbidden in text:
        errors.append(
            f"Forbidden README fragment remains: {forbidden}"
        )

stack_match = re.search(
    r"## Technical stack\s+(.*?)"
    r"## Engineering loop",
    text,
    re.DOTALL,
)

if not stack_match:
    errors.append(
        "Unified Technical Stack section was not found."
    )
else:
    stack_section = stack_match.group(1)

    if "### " in stack_section:
        errors.append(
            "Technical Stack still contains subcategories."
        )

    badge_references = re.findall(
        r'assets/badges/stack/[^"]+\.svg',
        stack_section,
    )

    if len(badge_references) < 35:
        errors.append(
            "Technical Stack contains too few Badges: "
            f"{len(badge_references)}"
        )

    if len(badge_references) != len(
        set(badge_references)
    ):
        errors.append(
            "Duplicate Technical Stack Badge references found."
        )

for badge_path in sorted(
    (ROOT / "assets/badges").rglob("*.svg")
):
    if not badge_path.is_file():
        errors.append(
            f"Badge is missing: {badge_path}"
        )

        continue

    content = badge_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    if "<svg" not in content.lower():
        errors.append(
            f"Invalid SVG Badge: {badge_path}"
        )

    visible_text = " ".join(
        re.findall(
            r"<text[^>]*>(.*?)</text>",
            content,
            re.DOTALL,
        )
    )

    visible_text = re.sub(
        r"<[^>]+>",
        "",
        visible_text,
    )

    if "_" in visible_text:
        errors.append(
            "Visible underscore in Badge: "
            f"{badge_path.relative_to(ROOT)}"
        )

if errors:
    for error in errors:
        print(f"FAIL: {error}")

    print()
    print(f"Layout errors: {len(errors)}")
    raise SystemExit(1)

print("OK: No artificial Badge spacers remain.")
print("OK: Technical Stack subcategories were removed.")
print("OK: Technical Stack contains at least 35 Badges.")
print("OK: Badge labels contain no visible underscores.")
print("STACK LAYOUT VALIDATION PASSED")
