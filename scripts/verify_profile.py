#!/usr/bin/env python3

from __future__ import annotations

import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

text = README.read_text(encoding="utf-8")

errors: list[str] = []

image_sources = re.findall(
    r'(?:src|srcset)="([^"]+)"',
    text,
)

if not image_sources:
    errors.append("README contains no images.")

for source in image_sources:
    if source.startswith(
        (
            "http://",
            "https://",
            "data:",
        )
    ):
        errors.append(
            f"External image dependency is forbidden: {source}"
        )
        continue

    path = ROOT / source

    if not path.is_file():
        errors.append(
            f"Missing local image: {source}"
        )
        continue

    if path.suffix.lower() != ".png":
        errors.append(
            f"Primary image is not PNG: {source}"
        )
        continue

    data = path.read_bytes()

    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        errors.append(
            f"Invalid PNG signature: {source}"
        )
        continue

    if len(data) < 24:
        errors.append(
            f"Truncated PNG: {source}"
        )
        continue

    width, height = struct.unpack(
        ">II",
        data[16:24],
    )

    if width < 500 or height < 150:
        errors.append(
            f"Image is unexpectedly small: "
            f"{source} ({width}x{height})"
        )

required_text = [
    "AI Station",
    "ramtin.karbaschi@gmail.com",
    "## Featured work",
    "## Engineering approach",
    "## Collaboration",
]

for fragment in required_text:
    if fragment not in text:
        errors.append(
            f"README is missing required content: {fragment}"
        )

if errors:
    for error in errors:
        print(f"FAIL: {error}")

    raise SystemExit(
        f"Profile validation failed with "
        f"{len(errors)} error(s)."
    )

print(
    f"OK: Local image references checked: "
    f"{len(image_sources)}"
)

print("OK: No external image service is used.")
print("OK: All committed visuals are valid PNG files.")
print("OK: Required profile content is present.")
print("PROFILE VALIDATION PASSED")
