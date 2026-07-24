#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PROJECTS = ASSETS / "projects"

ASSETS.mkdir(parents=True, exist_ok=True)
PROJECTS.mkdir(parents=True, exist_ok=True)

FONT_ROOT = Path("/usr/share/fonts/truetype/dejavu")

FONT_REGULAR = FONT_ROOT / "DejaVuSans.ttf"
FONT_BOLD = FONT_ROOT / "DejaVuSans-Bold.ttf"
FONT_MONO = FONT_ROOT / "DejaVuSansMono.ttf"
FONT_MONO_BOLD = FONT_ROOT / "DejaVuSansMono-Bold.ttf"

for font_path in (
    FONT_REGULAR,
    FONT_BOLD,
    FONT_MONO,
    FONT_MONO_BOLD,
):
    if not font_path.is_file():
        raise SystemExit(f"Required font is missing: {font_path}")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def rgb(hex_value: str) -> tuple[int, int, int]:
    value = hex_value.removeprefix("#")
    return tuple(
        int(value[index:index + 2], 16)
        for index in (0, 2, 4)
    )


def interpolate(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    return tuple(
        round(a + (b - a) * amount)
        for a, b in zip(first, second)
    )


def gradient(
    size: tuple[int, int],
    first: str,
    second: str,
) -> Image.Image:
    width, height = size
    start = rgb(first)
    end = rgb(second)

    image = Image.new("RGBA", size)

    drawing = ImageDraw.Draw(image)

    for y in range(height):
        amount = y / max(height - 1, 1)
        color = interpolate(start, end, amount)

        drawing.line(
            [(0, y), (width, y)],
            fill=(*color, 255),
        )

    return image


def add_glow(
    image: Image.Image,
    center: tuple[int, int],
    radius: int,
    color: str,
    opacity: int,
) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    drawing = ImageDraw.Draw(overlay)

    x, y = center

    drawing.ellipse(
        (
            x - radius,
            y - radius,
            x + radius,
            y + radius,
        ),
        fill=(*rgb(color), opacity),
    )

    overlay = overlay.filter(
        ImageFilter.GaussianBlur(radius // 2)
    )

    image.alpha_composite(overlay)


def add_grid(
    image: Image.Image,
    spacing: int,
    color: str,
    opacity: int,
) -> None:
    drawing = ImageDraw.Draw(image)
    width, height = image.size
    fill = (*rgb(color), opacity)

    for x in range(0, width, spacing):
        drawing.line(
            [(x, 0), (x, height)],
            fill=fill,
            width=1,
        )

    for y in range(0, height, spacing):
        drawing.line(
            [(0, y), (width, y)],
            fill=fill,
            width=1,
        )


def rounded_panel(
    drawing: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    outline: str,
    radius: int = 24,
    width: int = 2,
) -> None:
    drawing.rounded_rectangle(
        box,
        radius=radius,
        fill=rgb(fill),
        outline=rgb(outline),
        width=width,
    )


def draw_text(
    drawing: ImageDraw.ImageDraw,
    position: tuple[int, int],
    value: str,
    selected_font: ImageFont.FreeTypeFont,
    fill: str,
    anchor: str | None = None,
) -> None:
    drawing.text(
        position,
        value,
        font=selected_font,
        fill=rgb(fill),
        anchor=anchor,
    )


def wrap_text(
    drawing: ImageDraw.ImageDraw,
    text: str,
    selected_font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        candidate = " ".join([*current, word])

        left, top, right, bottom = drawing.textbbox(
            (0, 0),
            candidate,
            font=selected_font,
        )

        if right - left <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))

            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


def save_png(image: Image.Image, path: Path) -> None:
    image.convert("RGB").save(
        path,
        format="PNG",
        optimize=True,
    )

    print(f"CREATED: {path.relative_to(ROOT)}")


def draw_network_icon(
    drawing: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    accent: str,
    secondary: str,
) -> None:
    ox, oy = origin

    nodes = [
        (ox, oy),
        (ox + 78, oy - 44),
        (ox + 160, oy + 4),
        (ox + 82, oy + 76),
    ]

    lines = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (0, 2),
    ]

    for first, second in lines:
        drawing.line(
            [nodes[first], nodes[second]],
            fill=rgb("#475569"),
            width=4,
        )

    for index, (x, y) in enumerate(nodes):
        color = accent if index % 2 == 0 else secondary

        drawing.ellipse(
            (x - 11, y - 11, x + 11, y + 11),
            fill=rgb(color),
        )

        drawing.ellipse(
            (x - 4, y - 4, x + 4, y + 4),
            fill=rgb("#F8FAFC"),
        )


def build_hero(
    mode: str,
    output: Path,
) -> None:
    size = (1600, 520)

    if mode == "dark":
        image = gradient(size, "#06111F", "#0A2B3A")
        background_grid = "#94A3B8"
        primary = "#F8FAFC"
        secondary = "#CBD5E1"
        muted = "#8291A7"
        panel = "#0C2133"
        panel_border = "#1D4A5A"
    else:
        image = gradient(size, "#F8FBFD", "#E8F3F5")
        background_grid = "#1E3A4C"
        primary = "#10202D"
        secondary = "#334E5F"
        muted = "#607787"
        panel = "#FFFFFF"
        panel_border = "#B8D5DC"

    add_grid(image, 42, background_grid, 18)
    add_glow(image, (1340, 40), 310, "#14B8A6", 65)
    add_glow(image, (950, 540), 260, "#0EA5E9", 45)

    drawing = ImageDraw.Draw(image)

    drawing.rounded_rectangle(
        (0, 0, 1599, 519),
        radius=34,
        outline=rgb("#14B8A6"),
        width=2,
    )

    drawing.rounded_rectangle(
        (74, 64, 315, 105),
        radius=20,
        fill=rgb(panel),
        outline=rgb(panel_border),
        width=2,
    )

    draw_text(
        drawing,
        (194, 85),
        "LOCAL-FIRST AI SYSTEMS",
        font(FONT_MONO_BOLD, 20),
        "#14B8A6",
        anchor="mm",
    )

    draw_text(
        drawing,
        (74, 176),
        "RAMTIN",
        font(FONT_BOLD, 76),
        primary,
    )

    draw_text(
        drawing,
        (74, 257),
        "KARBASCHI",
        font(FONT_BOLD, 76),
        primary,
    )

    drawing.rounded_rectangle(
        (76, 352, 600, 359),
        radius=4,
        fill=rgb("#14B8A6"),
    )

    draw_text(
        drawing,
        (74, 390),
        "AI SYSTEMS ARCHITECT",
        font(FONT_MONO_BOLD, 27),
        secondary,
    )

    draw_text(
        drawing,
        (74, 436),
        "Private infrastructure · Agentic platforms · Engineering intelligence",
        font(FONT_REGULAR, 20),
        muted,
    )

    cards = [
        (
            (1010, 72, 1507, 167),
            "INFERENCE",
            "Local models and provider-neutral APIs",
            "#14B8A6",
        ),
        (
            (1010, 190, 1507, 285),
            "KNOWLEDGE",
            "RAG, search and document intelligence",
            "#38BDF8",
        ),
        (
            (1010, 308, 1507, 403),
            "OPERATIONS",
            "Reproducible, observable and recoverable",
            "#A78BFA",
        ),
    ]

    for box, title, description, accent in cards:
        drawing.rounded_rectangle(
            box,
            radius=24,
            fill=rgb(panel),
            outline=rgb(panel_border),
            width=2,
        )

        x1, y1, x2, y2 = box

        drawing.rounded_rectangle(
            (x1 + 18, y1 + 19, x1 + 25, y2 - 19),
            radius=4,
            fill=rgb(accent),
        )

        draw_text(
            drawing,
            (x1 + 48, y1 + 22),
            title,
            font(FONT_MONO_BOLD, 20),
            accent,
        )

        draw_text(
            drawing,
            (x1 + 48, y1 + 56),
            description,
            font(FONT_REGULAR, 16),
            secondary,
        )

    draw_network_icon(
        drawing,
        (800, 230),
        "#14B8A6",
        "#38BDF8",
    )

    draw_text(
        drawing,
        (1524, 475),
        "github.com/Ramtin-Karbaschi",
        font(FONT_MONO, 15),
        muted,
        anchor="ra",
    )

    save_png(image, output)


def build_focus_board(
    mode: str,
    output: Path,
) -> None:
    size = (1600, 345)

    if mode == "dark":
        image = gradient(size, "#071522", "#0A2431")
        primary = "#F8FAFC"
        secondary = "#B9C7D5"
        muted = "#8192A5"
        card = "#0C2130"
        border = "#1B4353"
    else:
        image = gradient(size, "#F7FAFC", "#EDF5F6")
        primary = "#12212C"
        secondary = "#3C5565"
        muted = "#6B7E8A"
        card = "#FFFFFF"
        border = "#C4DADF"

    add_glow(image, (1500, 20), 260, "#14B8A6", 38)

    drawing = ImageDraw.Draw(image)

    draw_text(
        drawing,
        (70, 52),
        "WHAT I BUILD",
        font(FONT_MONO_BOLD, 26),
        "#14B8A6",
    )

    draw_text(
        drawing,
        (70, 91),
        "Four connected disciplines, one engineering mindset.",
        font(FONT_REGULAR, 18),
        muted,
    )

    items = [
        (
            "01",
            "LOCAL AI PLATFORMS",
            "Inference, model serving and reusable private infrastructure.",
            "#14B8A6",
        ),
        (
            "02",
            "AGENTIC SYSTEMS",
            "Tool-using workflows with controlled human oversight.",
            "#38BDF8",
        ),
        (
            "03",
            "KNOWLEDGE SYSTEMS",
            "RAG, retrieval, OCR and auditable evidence pipelines.",
            "#A78BFA",
        ),
        (
            "04",
            "ENGINEERING AI",
            "Deterministic review and decision-support systems.",
            "#F59E0B",
        ),
    ]

    card_width = 350
    gap = 24
    start_x = 70
    top = 136

    for index, (number, title, description, accent) in enumerate(items):
        x1 = start_x + index * (card_width + gap)
        x2 = x1 + card_width

        drawing.rounded_rectangle(
            (x1, top, x2, 304),
            radius=24,
            fill=rgb(card),
            outline=rgb(border),
            width=2,
        )

        draw_text(
            drawing,
            (x1 + 24, top + 24),
            number,
            font(FONT_MONO_BOLD, 18),
            accent,
        )

        draw_text(
            drawing,
            (x1 + 24, top + 58),
            title,
            font(FONT_BOLD, 20),
            primary,
        )

        lines = wrap_text(
            drawing,
            description,
            font(FONT_REGULAR, 16),
            card_width - 48,
        )

        for line_index, line in enumerate(lines[:3]):
            draw_text(
                drawing,
                (x1 + 24, top + 98 + line_index * 25),
                line,
                font(FONT_REGULAR, 16),
                secondary,
            )

    save_png(image, output)


def build_toolkit(
    mode: str,
    output: Path,
) -> None:
    size = (1600, 220)

    if mode == "dark":
        image = gradient(size, "#07131F", "#0B202C")
        primary = "#E8F2F5"
        muted = "#8294A4"
        chip = "#0F2837"
        border = "#234958"
    else:
        image = gradient(size, "#F8FBFC", "#EEF5F6")
        primary = "#17303B"
        muted = "#607682"
        chip = "#FFFFFF"
        border = "#C3D9DE"

    drawing = ImageDraw.Draw(image)

    draw_text(
        drawing,
        (70, 48),
        "CORE TOOLKIT",
        font(FONT_MONO_BOLD, 25),
        "#14B8A6",
    )

    draw_text(
        drawing,
        (70, 83),
        "Technologies selected for practical AI systems—not collected for decoration.",
        font(FONT_REGULAR, 17),
        muted,
    )

    technologies = [
        "Python",
        "PyTorch",
        "FastAPI",
        "Docker",
        "Linux / WSL2",
        "PostgreSQL",
        "Redis",
        "NVIDIA CUDA",
        "OpenCV",
        "Hugging Face",
    ]

    x = 70
    y = 128

    for technology in technologies:
        selected_font = font(FONT_MONO_BOLD, 16)
        left, top, right, bottom = drawing.textbbox(
            (0, 0),
            technology,
            font=selected_font,
        )

        width = right - left + 42

        if x + width > 1530:
            x = 70
            y += 52

        drawing.rounded_rectangle(
            (x, y, x + width, y + 38),
            radius=19,
            fill=rgb(chip),
            outline=rgb(border),
            width=2,
        )

        draw_text(
            drawing,
            (x + width // 2, y + 19),
            technology,
            selected_font,
            primary,
            anchor="mm",
        )

        x += width + 14

    save_png(image, output)


def build_project_card(
    output: Path,
    title: str,
    category: str,
    description: str,
    tags: Iterable[str],
    accent: str,
    wide: bool = False,
) -> None:
    size = (1600, 330) if wide else (780, 300)
    width, height = size

    image = gradient(size, "#071522", "#0B2533")
    add_grid(image, 38, "#94A3B8", 11)
    add_glow(
        image,
        (width - 40, 30),
        210 if wide else 150,
        accent,
        48,
    )

    drawing = ImageDraw.Draw(image)

    drawing.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=28,
        outline=rgb("#224A59"),
        width=2,
    )

    drawing.rounded_rectangle(
        (38, 35, 215, 72),
        radius=18,
        fill=rgb("#0D2937"),
        outline=rgb(accent),
        width=2,
    )

    draw_text(
        drawing,
        (126, 54),
        category.upper(),
        font(FONT_MONO_BOLD, 15),
        accent,
        anchor="mm",
    )

    title_size = 39 if wide else 28

    draw_text(
        drawing,
        (38, 104),
        title,
        font(FONT_BOLD, title_size),
        "#F8FAFC",
    )

    description_font = font(
        FONT_REGULAR,
        20 if wide else 17,
    )

    max_width = (
        width - 485
        if wide
        else width - 76
    )

    lines = wrap_text(
        drawing,
        description,
        description_font,
        max_width,
    )

    for line_index, line in enumerate(lines[:3]):
        draw_text(
            drawing,
            (38, 165 + line_index * 30),
            line,
            description_font,
            "#B5C5D2",
        )

    x = 38
    tag_y = height - 64

    for tag in tags:
        selected_font = font(FONT_MONO_BOLD, 14)

        left, top, right, bottom = drawing.textbbox(
            (0, 0),
            tag,
            font=selected_font,
        )

        tag_width = right - left + 34

        drawing.rounded_rectangle(
            (x, tag_y, x + tag_width, tag_y + 34),
            radius=17,
            fill=rgb("#0D2937"),
            outline=rgb("#285162"),
            width=1,
        )

        draw_text(
            drawing,
            (x + tag_width // 2, tag_y + 17),
            tag,
            selected_font,
            "#D8E5EA",
            anchor="mm",
        )

        x += tag_width + 12

    if wide:
        panel_x1 = width - 410
        panel_y1 = 58

        drawing.rounded_rectangle(
            (
                panel_x1,
                panel_y1,
                width - 55,
                height - 58,
            ),
            radius=27,
            fill=rgb("#0B2130"),
            outline=rgb("#245164"),
            width=2,
        )

        draw_network_icon(
            drawing,
            (panel_x1 + 65, panel_y1 + 105),
            accent,
            "#38BDF8",
        )

        draw_text(
            drawing,
            (width - 80, height - 82),
            "OPEN REPOSITORY  →",
            font(FONT_MONO_BOLD, 15),
            accent,
            anchor="ra",
        )
    else:
        draw_text(
            drawing,
            (width - 38, height - 42),
            "VIEW  →",
            font(FONT_MONO_BOLD, 14),
            accent,
            anchor="ra",
        )

    save_png(image, output)


build_hero(
    "dark",
    ASSETS / "hero-dark.png",
)

build_hero(
    "light",
    ASSETS / "hero-light.png",
)

build_focus_board(
    "dark",
    ASSETS / "focus-dark.png",
)

build_focus_board(
    "light",
    ASSETS / "focus-light.png",
)

build_toolkit(
    "dark",
    ASSETS / "toolkit-dark.png",
)

build_toolkit(
    "light",
    ASSETS / "toolkit-light.png",
)

build_project_card(
    PROJECTS / "ai-station.png",
    title="AI STATION",
    category="Flagship project",
    description=(
        "A reproducible local-first AI workstation for private inference, "
        "multi-project APIs, RAG, document intelligence and dependable operations."
    ),
    tags=(
        "LOCAL AI",
        "WSL2",
        "DOCKER",
        "LLM",
        "RAG",
    ),
    accent="#14B8A6",
    wide=True,
)

build_project_card(
    PROJECTS / "contentfusion.png",
    title="ContentFusion-LLM",
    category="Multimodal AI",
    description=(
        "A unified content-analysis concept spanning text, image, "
        "audio and video workflows."
    ),
    tags=(
        "GEMINI",
        "RAG",
        "MULTIMODAL",
    ),
    accent="#A78BFA",
)

build_project_card(
    PROJECTS / "plate-sentiment.png",
    title="ANPR + Sentiment",
    category="Vision and NLP",
    description=(
        "Automatic number-plate recognition combined with "
        "natural-language sentiment analysis."
    ),
    tags=(
        "YOLO",
        "OCR",
        "NLP",
    ),
    accent="#38BDF8",
)

build_project_card(
    PROJECTS / "behavior-market.png",
    title="Behavior + Market Analysis",
    category="Applied ML",
    description=(
        "Behavioral pattern analysis and mobile-market segmentation "
        "using statistical and unsupervised methods."
    ),
    tags=(
        "ML",
        "STATISTICS",
        "CLUSTERING",
    ),
    accent="#F59E0B",
)
