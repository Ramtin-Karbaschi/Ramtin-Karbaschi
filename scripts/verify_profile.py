#!/usr/bin/env python3

from __future__ import annotations

import re
import struct
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

errors: list[str] = []

if not README.is_file():
    errors.append("README.md is missing.")
    text = ""
else:
    text = README.read_text(encoding="utf-8")

image_sources = re.findall(
    r'src="([^"]+)"',
    text,
)

for source in image_sources:
    if source.startswith(
        (
            "http://",
            "https://",
            "data:",
        )
    ):
        errors.append(
            f"External image dependency: {source}"
        )
        continue

    path = (ROOT / source).resolve()

    try:
        path.relative_to(ROOT)
    except ValueError:
        errors.append(
            f"Image escapes repository: {source}"
        )
        continue

    if not path.is_file():
        errors.append(
            f"Missing image: {source}"
        )

required_assets = [
    "assets/hero.gif",
    "assets/engineering-loop.gif",
    "assets/capabilities.png",
    "assets/projects/ai-station.png",
    "assets/projects/contentfusion.png",
    "assets/projects/plate-sentiment.png",
    "assets/projects/behavior-market.png",
    "assets/projects/ollama-template.png",
]

for relative in required_assets:
    path = ROOT / relative

    if not path.is_file():
        errors.append(
            f"Required visual is missing: {relative}"
        )

for relative in [
    "assets/hero.gif",
    "assets/engineering-loop.gif",
]:
    path = ROOT / relative

    if not path.is_file():
        continue

    with Image.open(path) as image:
        frames = getattr(image, "n_frames", 1)

        if frames < 10:
            errors.append(
                f"Animation has too few frames: "
                f"{relative} ({frames})"
            )

project_dimensions = set()

for relative in [
    "assets/projects/contentfusion.png",
    "assets/projects/plate-sentiment.png",
    "assets/projects/behavior-market.png",
    "assets/projects/ollama-template.png",
]:
    path = ROOT / relative

    if not path.is_file():
        continue

    with Image.open(path) as image:
        project_dimensions.add(image.size)

if len(project_dimensions) != 1:
    errors.append(
        "Secondary project cards do not have equal dimensions: "
        f"{sorted(project_dimensions)}"
    )

for badge in sorted(
    (ROOT / "assets/badges").rglob("*.svg")
):
    content = badge.read_text(
        encoding="utf-8",
        errors="replace",
    )

    if "<svg" not in content.lower():
        errors.append(
            f"Invalid SVG badge: {badge.relative_to(ROOT)}"
        )

required_text = [
    "ramtin.karbaschi@gmail.com",
    "## Building now",
    "## Capability map",
    "## Selected systems",
    "## Technical stack",
    "## Engineering loop",
    "## Collaboration",
]

for fragment in required_text:
    if fragment not in text:
        errors.append(
            f"README is missing: {fragment}"
        )

if errors:
    for error in errors:
        print(f"FAIL: {error}")

    print()
    print(f"Profile errors: {len(errors)}")
    raise SystemExit(1)

print(f"OK: README image references: {len(image_sources)}")
print("OK: All README images are repository-local.")
print("OK: Animated GIF assets are valid.")
print("OK: Secondary project cards are perfectly aligned.")
print("OK: Contact and technology badges are valid.")
print("PROFILE VALIDATION PASSED")
