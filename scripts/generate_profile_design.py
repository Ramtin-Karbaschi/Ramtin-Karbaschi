#!/usr/bin/env python3

from __future__ import annotations

import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PROJECTS = ASSETS / "projects"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_SANS = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
FONT_MONO = FONT_DIR / "DejaVuSansMono.ttf"
FONT_MONO_BOLD = FONT_DIR / "DejaVuSansMono-Bold.ttf"

PALETTE = {
    "background": "#070A0F",
    "surface": "#0D131D",
    "surface_high": "#111A27",
    "border": "#263244",
    "text": "#F8FAFC",
    "secondary": "#C3CFDB",
    "muted": "#7F91A5",
    "cyan": "#2DD4BF",
    "blue": "#38BDF8",
    "violet": "#8B5CF6",
    "amber": "#F59E0B",
    "rose": "#FB7185",
}


def rgb(value: str) -> tuple[int, int, int]:
    value = value.removeprefix("#")
    return tuple(
        int(value[index:index + 2], 16)
        for index in (0, 2, 4)
    )


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*rgb(value), alpha)


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.is_file():
        raise RuntimeError(f"Missing font: {path}")

    return ImageFont.truetype(str(path), size=size)


def vertical_gradient(
    width: int,
    height: int,
    top: str,
    bottom: str,
) -> Image.Image:
    image = Image.new("RGBA", (width, height))
    drawing = ImageDraw.Draw(image)
    top_rgb = rgb(top)
    bottom_rgb = rgb(bottom)

    for y in range(height):
        ratio = y / max(height - 1, 1)

        color = tuple(
            round(
                top_rgb[channel]
                + (
                    bottom_rgb[channel]
                    - top_rgb[channel]
                )
                * ratio
            )
            for channel in range(3)
        )

        drawing.line(
            [(0, y), (width, y)],
            fill=(*color, 255),
        )

    return image


def add_grid(
    image: Image.Image,
    spacing: int = 36,
    opacity: int = 6,
) -> None:
    drawing = ImageDraw.Draw(image)
    width, height = image.size
    line = rgba("#94A3B8", opacity)

    for x in range(0, width, spacing):
        drawing.line(
            [(x, 0), (x, height)],
            fill=line,
            width=1,
        )

    for y in range(0, height, spacing):
        drawing.line(
            [(0, y), (width, y)],
            fill=line,
            width=1,
        )


def add_glow(
    image: Image.Image,
    x: int,
    y: int,
    radius: int,
    color: str,
    opacity: int,
) -> None:
    layer = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0),
    )

    drawing = ImageDraw.Draw(layer)

    drawing.ellipse(
        (
            x - radius,
            y - radius,
            x + radius,
            y + radius,
        ),
        fill=rgba(color, opacity),
    )

    layer = layer.filter(
        ImageFilter.GaussianBlur(radius // 2)
    )

    image.alpha_composite(layer)


def rounded_panel(
    drawing: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str = PALETTE["surface"],
    outline: str = PALETTE["border"],
    radius: int = 26,
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
    text: str,
    selected_font: ImageFont.FreeTypeFont,
    fill: str,
    anchor: str | None = None,
) -> None:
    drawing.text(
        position,
        text,
        font=selected_font,
        fill=rgb(fill),
        anchor=anchor,
    )


def text_width(
    drawing: ImageDraw.ImageDraw,
    text: str,
    selected_font: ImageFont.FreeTypeFont,
) -> int:
    left, top, right, bottom = drawing.textbbox(
        (0, 0),
        text,
        font=selected_font,
    )

    return right - left


def wrapped_lines(
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

        if text_width(
            drawing,
            candidate,
            selected_font,
        ) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))

            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


def save_png(
    image: Image.Image,
    destination: Path,
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image.convert("RGB").save(
        destination,
        "PNG",
        optimize=True,
    )

    print(f"CREATED: {destination.relative_to(ROOT)}")


def save_gif(
    frames: list[Image.Image],
    destination: Path,
    duration: int,
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rgb_frames = [
        frame.convert("RGB")
        for frame in frames
    ]

    rgb_frames[0].save(
        destination,
        "GIF",
        save_all=True,
        append_images=rgb_frames[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )

    print(
        f"CREATED: {destination.relative_to(ROOT)} "
        f"({len(frames)} frames)"
    )


def build_hero() -> None:
    width = 1200
    height = 410
    frame_count = 28
    frames: list[Image.Image] = []

    title_font = font(FONT_BOLD, 58)
    surname_font = font(FONT_BOLD, 58)
    role_font = font(FONT_MONO_BOLD, 21)
    body_font = font(FONT_SANS, 17)
    small_font = font(FONT_MONO_BOLD, 13)
    terminal_font = font(FONT_MONO, 16)
    terminal_bold = font(FONT_MONO_BOLD, 16)

    for frame_index in range(frame_count):
        progress = frame_index / frame_count
        phase = progress * math.tau

        image = vertical_gradient(
            width,
            height,
            "#06090E",
            "#0A111B",
        )

        add_grid(image, spacing=38, opacity=6)

        glow_x = round(
            930 + math.sin(phase) * 95
        )

        glow_y = round(
            75 + math.cos(phase * 0.75) * 25
        )

        add_glow(
            image,
            glow_x,
            glow_y,
            260,
            PALETTE["cyan"],
            50,
        )

        add_glow(
            image,
            1080,
            390,
            210,
            PALETTE["violet"],
            32,
        )

        drawing = ImageDraw.Draw(image)

        drawing.rounded_rectangle(
            (1, 1, width - 2, height - 2),
            radius=32,
            outline=rgb(PALETTE["border"]),
            width=2,
        )

        rounded_panel(
            drawing,
            (54, 43, 279, 79),
            fill="#0A1721",
            outline="#224655",
            radius=18,
        )

        drawing.ellipse(
            (71, 56, 81, 66),
            fill=rgb(PALETTE["cyan"]),
        )

        draw_text(
            drawing,
            (91, 54),
            "OPEN TO COLLABORATION",
            small_font,
            PALETTE["cyan"],
        )

        draw_text(
            drawing,
            (54, 117),
            "RAMTIN",
            title_font,
            PALETTE["text"],
        )

        draw_text(
            drawing,
            (54, 180),
            "KARBASCHI",
            surname_font,
            PALETTE["text"],
        )

        drawing.rounded_rectangle(
            (57, 257, 468, 262),
            radius=3,
            fill=rgb(PALETTE["cyan"]),
        )

        draw_text(
            drawing,
            (54, 288),
            "AI SYSTEMS ARCHITECT",
            role_font,
            PALETTE["secondary"],
        )

        draw_text(
            drawing,
            (54, 329),
            "Local AI  ·  Agentic Systems  ·  Engineering Intelligence",
            body_font,
            PALETTE["muted"],
        )

        draw_text(
            drawing,
            (54, 369),
            "Private by design. Evidence-driven by practice.",
            font(FONT_MONO, 14),
            PALETTE["cyan"],
        )

        panel = (650, 49, 1147, 356)

        rounded_panel(
            drawing,
            panel,
            fill="#0B111A",
            outline="#2A384A",
            radius=26,
        )

        drawing.ellipse(
            (677, 70, 689, 82),
            fill=rgb("#FB7185"),
        )

        drawing.ellipse(
            (698, 70, 710, 82),
            fill=rgb("#F59E0B"),
        )

        drawing.ellipse(
            (719, 70, 731, 82),
            fill=rgb(PALETTE["cyan"]),
        )

        draw_text(
            drawing,
            (756, 67),
            "ramtin@systems",
            font(FONT_MONO_BOLD, 13),
            PALETTE["muted"],
        )

        drawing.line(
            [(672, 100), (1124, 100)],
            fill=rgb(PALETTE["border"]),
            width=1,
        )

        terminal_lines = [
            (
                "$ identity",
                PALETTE["blue"],
                terminal_bold,
            ),
            (
                "AI systems architect",
                PALETTE["text"],
                terminal_font,
            ),
            (
                "$ current_focus",
                PALETTE["blue"],
                terminal_bold,
            ),
            (
                "local inference · agents · RAG",
                PALETTE["secondary"],
                terminal_font,
            ),
            (
                "$ engineering_mode",
                PALETTE["blue"],
                terminal_bold,
            ),
            (
                "benchmark → build → verify",
                PALETTE["cyan"],
                terminal_font,
            ),
        ]

        y = 124

        for line, color, selected_font in terminal_lines:
            draw_text(
                drawing,
                (679, y),
                line,
                selected_font,
                color,
            )

            y += 34

        cursor_visible = frame_index % 8 < 5

        if cursor_visible:
            drawing.rounded_rectangle(
                (679, 328, 689, 346),
                radius=2,
                fill=rgb(PALETTE["cyan"]),
            )

        signal_start = 659
        signal_end = 1136
        signal_y = 378

        drawing.line(
            [(signal_start, signal_y), (signal_end, signal_y)],
            fill=rgb("#1F2B38"),
            width=2,
        )

        dot_x = round(
            signal_start
            + (signal_end - signal_start) * progress
        )

        add_glow(
            image,
            dot_x,
            signal_y,
            25,
            PALETTE["cyan"],
            90,
        )

        drawing = ImageDraw.Draw(image)

        drawing.ellipse(
            (
                dot_x - 5,
                signal_y - 5,
                dot_x + 5,
                signal_y + 5,
            ),
            fill=rgb(PALETTE["cyan"]),
        )

        frames.append(image)

    save_gif(
        frames,
        ASSETS / "hero.gif",
        duration=90,
    )


def build_workflow() -> None:
    width = 1200
    height = 150
    frames: list[Image.Image] = []
    stages = [
        "RESEARCH",
        "ARCHITECT",
        "BENCHMARK",
        "BUILD",
        "VERIFY",
    ]

    positions = [
        100,
        350,
        600,
        850,
        1100,
    ]

    label_font = font(FONT_MONO_BOLD, 15)
    small_font = font(FONT_MONO, 12)

    frame_count = 40

    for frame_index in range(frame_count):
        progress = frame_index / frame_count

        image = vertical_gradient(
            width,
            height,
            "#090D13",
            "#0C131D",
        )

        drawing = ImageDraw.Draw(image)

        drawing.rounded_rectangle(
            (1, 1, width - 2, height - 2),
            radius=26,
            outline=rgb(PALETTE["border"]),
            width=2,
        )

        drawing.line(
            [(positions[0], 70), (positions[-1], 70)],
            fill=rgb("#2A3746"),
            width=4,
        )

        segment_count = len(positions) - 1
        full_progress = progress * segment_count
        segment = min(
            int(full_progress),
            segment_count - 1,
        )

        local_progress = (
            full_progress - segment
        )

        active_x = round(
            positions[segment]
            + (
                positions[segment + 1]
                - positions[segment]
            )
            * local_progress
        )

        add_glow(
            image,
            active_x,
            70,
            34,
            PALETTE["cyan"],
            100,
        )

        drawing = ImageDraw.Draw(image)

        for index, (stage, x) in enumerate(
            zip(stages, positions)
        ):
            distance = abs(x - active_x)
            active = distance < 90

            node_color = (
                PALETTE["cyan"]
                if active
                else "#344252"
            )

            drawing.ellipse(
                (x - 9, 61, x + 9, 79),
                fill=rgb(node_color),
            )

            draw_text(
                drawing,
                (x, 99),
                stage,
                label_font,
                (
                    PALETTE["text"]
                    if active
                    else PALETTE["muted"]
                ),
                anchor="mm",
            )

        drawing.ellipse(
            (
                active_x - 6,
                64,
                active_x + 6,
                76,
            ),
            fill=rgb(PALETTE["text"]),
        )

        draw_text(
            drawing,
            (600, 128),
            "A disciplined loop for dependable AI systems",
            small_font,
            PALETTE["muted"],
            anchor="mm",
        )

        frames.append(image)

    save_gif(
        frames,
        ASSETS / "engineering-loop.gif",
        duration=80,
    )


def build_capabilities() -> None:
    width = 1200
    height = 320

    image = vertical_gradient(
        width,
        height,
        "#080D14",
        "#0B121B",
    )

    add_grid(image, 40, 5)
    add_glow(
        image,
        1100,
        20,
        230,
        PALETTE["violet"],
        28,
    )

    drawing = ImageDraw.Draw(image)

    draw_text(
        drawing,
        (47, 38),
        "CAPABILITY MAP",
        font(FONT_MONO_BOLD, 19),
        PALETTE["cyan"],
    )

    draw_text(
        drawing,
        (47, 69),
        "Four connected domains. One engineering system.",
        font(FONT_SANS, 16),
        PALETTE["muted"],
    )

    cards = [
        (
            "01",
            "LOCAL AI",
            "Inference, model serving and reusable private infrastructure.",
            PALETTE["cyan"],
        ),
        (
            "02",
            "AGENTIC SYSTEMS",
            "Tool-using workflows with controlled human oversight.",
            PALETTE["blue"],
        ),
        (
            "03",
            "KNOWLEDGE SYSTEMS",
            "RAG, retrieval, OCR and auditable evidence pipelines.",
            PALETTE["violet"],
        ),
        (
            "04",
            "ENGINEERING AI",
            "Deterministic review and decision-support systems.",
            PALETTE["amber"],
        ),
    ]

    gap = 18
    card_width = 270
    start_x = 47
    top = 111

    for index, (
        number,
        title,
        description,
        accent,
    ) in enumerate(cards):
        x1 = start_x + index * (card_width + gap)
        x2 = x1 + card_width

        rounded_panel(
            drawing,
            (x1, top, x2, 282),
            fill=PALETTE["surface"],
            outline=PALETTE["border"],
            radius=22,
        )

        drawing.rounded_rectangle(
            (x1 + 19, top + 20, x1 + 24, top + 151),
            radius=3,
            fill=rgb(accent),
        )

        draw_text(
            drawing,
            (x1 + 42, top + 22),
            number,
            font(FONT_MONO_BOLD, 15),
            accent,
        )

        draw_text(
            drawing,
            (x1 + 42, top + 54),
            title,
            font(FONT_BOLD, 18),
            PALETTE["text"],
        )

        lines = wrapped_lines(
            drawing,
            description,
            font(FONT_SANS, 14),
            card_width - 68,
        )

        for line_index, line in enumerate(lines[:4]):
            draw_text(
                drawing,
                (
                    x1 + 42,
                    top + 91 + line_index * 23,
                ),
                line,
                font(FONT_SANS, 14),
                PALETTE["secondary"],
            )

    save_png(
        image,
        ASSETS / "capabilities.png",
    )


def build_project_card(
    filename: str,
    title: str,
    category: str,
    description: str,
    tags: list[str],
    accent: str,
    wide: bool = False,
) -> None:
    width = 1200 if wide else 570
    height = 280 if wide else 245

    image = vertical_gradient(
        width,
        height,
        "#080D14",
        "#0C1420",
    )

    add_grid(image, 38, 4)

    add_glow(
        image,
        width - 25,
        25,
        190 if wide else 140,
        accent,
        40,
    )

    drawing = ImageDraw.Draw(image)

    drawing.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=26,
        outline=rgb(PALETTE["border"]),
        width=2,
    )

    category_font = font(FONT_MONO_BOLD, 13)

    category_width = text_width(
        drawing,
        category.upper(),
        category_font,
    ) + 34

    drawing.rounded_rectangle(
        (28, 25, 28 + category_width, 58),
        radius=16,
        fill=rgb("#101C29"),
        outline=rgb(accent),
        width=1,
    )

    draw_text(
        drawing,
        (
            28 + category_width // 2,
            41,
        ),
        category.upper(),
        category_font,
        accent,
        anchor="mm",
    )

    title_size = 34 if wide else 25

    draw_text(
        drawing,
        (28, 83),
        title,
        font(FONT_BOLD, title_size),
        PALETTE["text"],
    )

    description_font = font(
        FONT_SANS,
        16 if wide else 14,
    )

    max_description_width = (
        width - 450
        if wide
        else width - 56
    )

    lines = wrapped_lines(
        drawing,
        description,
        description_font,
        max_description_width,
    )

    for line_index, line in enumerate(lines[:3]):
        draw_text(
            drawing,
            (28, 134 + line_index * 24),
            line,
            description_font,
            PALETTE["secondary"],
        )

    x = 28
    tag_y = height - 49
    tag_font = font(FONT_MONO_BOLD, 11)

    for tag in tags:
        tag_width = text_width(
            drawing,
            tag,
            tag_font,
        ) + 25

        drawing.rounded_rectangle(
            (
                x,
                tag_y,
                x + tag_width,
                tag_y + 27,
            ),
            radius=13,
            fill=rgb("#101C29"),
            outline=rgb("#28384A"),
            width=1,
        )

        draw_text(
            drawing,
            (
                x + tag_width // 2,
                tag_y + 13,
            ),
            tag,
            tag_font,
            PALETTE["secondary"],
            anchor="mm",
        )

        x += tag_width + 8

    if wide:
        box = (
            width - 385,
            45,
            width - 38,
            height - 45,
        )

        rounded_panel(
            drawing,
            box,
            fill="#0B121C",
            outline="#253649",
            radius=24,
        )

        bx1, by1, bx2, by2 = box

        nodes = [
            (bx1 + 62, by1 + 56),
            (bx1 + 176, by1 + 37),
            (bx1 + 279, by1 + 73),
            (bx1 + 102, by1 + 135),
            (bx1 + 242, by1 + 141),
        ]

        edges = [
            (0, 1),
            (1, 2),
            (0, 3),
            (1, 3),
            (1, 4),
            (2, 4),
            (3, 4),
        ]

        for first, second in edges:
            drawing.line(
                [nodes[first], nodes[second]],
                fill=rgb("#344356"),
                width=3,
            )

        node_colors = [
            PALETTE["cyan"],
            PALETTE["blue"],
            PALETTE["violet"],
            PALETTE["amber"],
            PALETTE["rose"],
        ]

        for (node_x, node_y), node_color in zip(
            nodes,
            node_colors,
        ):
            drawing.ellipse(
                (
                    node_x - 9,
                    node_y - 9,
                    node_x + 9,
                    node_y + 9,
                ),
                fill=rgb(node_color),
            )

        draw_text(
            drawing,
            (
                bx2 - 20,
                by2 - 23,
            ),
            "OPEN REPOSITORY  →",
            font(FONT_MONO_BOLD, 12),
            accent,
            anchor="ra",
        )
    else:
        draw_text(
            drawing,
            (width - 27, height - 29),
            "VIEW  →",
            font(FONT_MONO_BOLD, 11),
            accent,
            anchor="ra",
        )

    save_png(
        image,
        PROJECTS / filename,
    )


build_hero()
build_workflow()
build_capabilities()

build_project_card(
    filename="ai-station.png",
    title="AI STATION",
    category="Flagship · Open source",
    description=(
        "A reproducible local-first AI workstation for private inference, "
        "multi-project APIs, RAG, document intelligence and dependable operations."
    ),
    tags=[
        "LOCAL AI",
        "WSL2",
        "DOCKER",
        "LLM",
        "RAG",
    ],
    accent=PALETTE["cyan"],
    wide=True,
)

build_project_card(
    filename="contentfusion.png",
    title="ContentFusion-LLM",
    category="Multimodal AI",
    description=(
        "A unified content-analysis project spanning text, image, "
        "audio and video workflows."
    ),
    tags=[
        "MULTIMODAL",
        "RAG",
        "LLM",
    ],
    accent=PALETTE["violet"],
)

build_project_card(
    filename="plate-sentiment.png",
    title="ANPR + Sentiment",
    category="Vision and NLP",
    description=(
        "Automatic plate recognition combined with "
        "natural-language sentiment analysis."
    ),
    tags=[
        "YOLO",
        "OCR",
        "NLP",
    ],
    accent=PALETTE["blue"],
)

build_project_card(
    filename="behavior-market.png",
    title="Behavior + Market",
    category="Applied ML",
    description=(
        "Behavioral pattern analysis and mobile-market segmentation "
        "using statistical and unsupervised methods."
    ),
    tags=[
        "ML",
        "STATISTICS",
        "CLUSTERING",
    ],
    accent=PALETTE["amber"],
)

build_project_card(
    filename="ollama-template.png",
    title="Ollama Web Template",
    category="Local AI interface",
    description=(
        "A lightweight web template for interacting with "
        "locally hosted Ollama models."
    ),
    tags=[
        "OLLAMA",
        "WEB UI",
        "LOCAL LLM",
    ],
    accent=PALETTE["rose"],
)
