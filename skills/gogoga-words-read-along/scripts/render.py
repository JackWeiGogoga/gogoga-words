#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render bilingual picture questions, read-aloud guides, or illustrated scenes."""

from worksheet import ACCENT, LINE, MUTED, PAPER, Page, argument_parser, batches, render_cli, wrap


WIDTH, HEIGHT = 1240, 1754
MARGIN, TOP, BOTTOM, GAP = 62, 185, 1653, 12
TEXT_X, TEXT_WIDTH = 94, 555
ART_X, ART_WIDTH = 686, 470
THEMES = {
    "default": (PAPER, ACCENT, LINE),
    "engineering": ("#ffffff", "#245387", "#b8cce0"),
    "pattern-search": ("#ffffff", "#793b70", "#dbc6dc"),
}


def prepare(section, mode):
    if mode == "qa":
        fields = [
            ("Q  " + section["question"]["en"], "strong", 29, 37),
            (section["question"]["zh"], "zh", 25, 34),
            ("A  " + section["answer"]["en"], "en", 29, 37),
            (section["answer"]["zh"], "zh", 25, 34),
        ]
    else:
        fields = [(section["read"]["en"], "en", 31, 43), (section["read"]["zh"], "zh", 26, 36)]
    if not 1 <= len(section["images"]) <= 6:
        raise ValueError(f'Use 1–6 illustrations in section {section["title"]!r}')
    lines, offset = [], 88
    for value, style, size, line_height in fields:
        for line in wrap(value, TEXT_WIDTH, size, style):
            lines.append((line, style, size, offset))
            offset += line_height
        offset += 4
    return lines, max(268, offset)


def section_art(page, assets, images, y, height):
    rows = batches(images, 3)
    row_h = (height - 60) / len(rows)
    for index, row in enumerate(rows):
        slot = ART_WIDTH / len(row)
        top = y + 50 + index * row_h
        for column, item in enumerate(row):
            center = ART_X + (column + 0.5) * slot
            width = min(slot - 18, 245)
            page.art(assets, item["asset"], center - width / 2, top, width, row_h - 37)
            if item.get("label"):
                page.text(item["label"], center, top + row_h - 10, 22, color=MUTED, anchor="middle", max_width=slot - 16)


def header(spec, name, paper, accent):
    page = Page(WIDTH, HEIGHT, f'{spec["title"]} | {name}', paper)
    page.text(name, WIDTH - MARGIN, 79, 32, "strong", accent, "end")
    page.text(spec["title"], MARGIN, 94, 70, "display", max_width=WIDTH - 2 * MARGIN - 325)
    page.text(spec["zh_title"], MARGIN + 3, 144, 33, "zh", max_width=WIDTH - 2 * MARGIN)
    page.line(MARGIN, 162, WIDTH - MARGIN, 162, accent, 2)
    return page


def footer(page, note, number, total):
    page.text(note, MARGIN, 1705, 22, color=MUTED)
    page.text(f"{number:02} / {total:02}", WIDTH - MARGIN, 1705, 22, color=MUTED, anchor="end")


def scene_pages(spec, assets, paper, accent, border):
    scenes = spec["scenes"]
    if not scenes:
        raise ValueError("Add at least one illustrated scene")
    content_width = WIDTH - 2 * MARGIN
    legend_width = content_width / 3
    pages = []
    for number, scene in enumerate(scenes, 1):
        points, sentences = scene["points"], scene["lines"]
        if not 1 <= len(points) <= 8 or not 1 <= len(sentences) <= 6:
            raise ValueError(f"Use 1–8 picture points and 1–6 short sentences in scene {number}")
        show_markers = scene.get("show_markers", True)
        if type(show_markers) is not bool:
            raise ValueError(f"Scene {number} needs true or false for show_markers")
        page = header(spec, "Scene Read", paper, accent)
        (image_w, image_h), _ = assets.image(scene["asset"])
        art_height = min(802, max(460, (content_width - 32) * image_h / image_w + 32))
        page.rect(MARGIN, TOP, content_width, art_height, "#ffffff", border, 18)
        left, top, width, height = page.art(
            assets, scene["asset"], MARGIN + 16, TOP + 16, content_width - 32, art_height - 32,
        )
        legend_y = TOP + art_height + 46
        page.text("Find & Say", MARGIN, legend_y, 30, "display", accent)
        for index, item in enumerate(points, 1):
            if not item["en"].strip() or not item["zh"].strip():
                raise ValueError(f"Scene {number}, point {index} needs English and Chinese labels")
            px, py = item["point"]
            if any(type(value) not in (int, float) or not 0 <= value <= 1 for value in (px, py)):
                raise ValueError(f"Scene {number}, point {index} must have two coordinates in [0, 1]")
            if show_markers:
                cx, cy = left + width * px, top + height * py
                page.rect(cx - 18, cy - 18, 36, 36, "#ffffff", accent, 18)
                page.text(str(index), cx, cy + 8, 24, "strong", accent, "middle")
            row, column = divmod(index - 1, 3)
            x = MARGIN + legend_width * column
            y = legend_y + 18 + row * 63
            page.rect(x + 4, y + 4, 29, 29, accent, radius=15)
            page.text(str(index), x + 18.5, y + 26, 20, "strong", "#ffffff", "middle")
            page.text(item["en"], x + 46, y + 25, 27, "strong", max_width=legend_width - 56)
            page.text(item["zh"], x + 46, y + 52, 22, "zh", MUTED, max_width=legend_width - 56)

        y = legend_y + 18 + 63 * ((len(points) + 2) // 3) + 18
        page.line(MARGIN, y, WIDTH - MARGIN, y, border)
        y += 37
        page.text("Read Along", MARGIN, y, 30, "display", accent)
        y += 40
        for sentence in sentences:
            for language, style, size, leading in (("en", "en", 29, 36), ("zh", "zh", 23, 30)):
                lines = wrap(sentence[language], content_width, size, style)
                if not lines:
                    raise ValueError(f"Scene {number} has an empty {language} sentence")
                for line in lines:
                    if y > BOTTOM:
                        raise ValueError(f"Scene {number} text does not fit. Use fewer words or a second scene.")
                    page.text(line, MARGIN, y, size, style, MUTED if language == "zh" else "#322722")
                    y += leading
            y += 4
        note = "Point to a number, say the word, then read." if show_markers else "Find each picture, say the word, then read."
        footer(page, note, number, len(scenes))
        pages.append(page)
    return pages


def render(spec, assets, mode, style=None):
    style = style if style is not None else spec.get("style", "default")
    if style not in THEMES:
        raise ValueError(f"Use one of these read-along styles: {', '.join(THEMES)}")
    paper, accent, border = THEMES[style]
    if mode == "scene":
        return scene_pages(spec, assets, paper, accent, border)
    sections = spec["sections"]
    if not sections:
        raise ValueError("Add at least one reading section")
    groups, group, used = [], [], 0
    for index, section in enumerate(sections, 1):
        lines, height = prepare(section, mode)
        if height > BOTTOM - TOP:
            raise ValueError(f'Section is too long for one page: {section["title"]!r}')
        if group and used + GAP + height > BOTTOM - TOP:
            groups.append(group)
            group, used = [], 0
        used += height + (GAP if group else 0)
        group.append((index, section, lines, height))
    groups.append(group)

    pages = []
    for number, items in enumerate(groups, 1):
        name = "Picture Q&A" if mode == "qa" else "Read Along"
        page = header(spec, name, paper, accent)
        y = TOP
        for index, section, lines, height in items:
            page.rect(MARGIN, y, WIDTH - 2 * MARGIN, height, "#ffffff", border, 22)
            page.text(f'{index:02}   {section["title"]}', TEXT_X, y + 48, 31, "display", accent, max_width=TEXT_WIDTH)
            page.line(667, y + 28, 667, y + height - 26)
            for line, style, size, offset in lines:
                page.text(line, TEXT_X, y + offset, size, style, MUTED if style == "zh" else "#322722")
            section_art(page, assets, section["images"], y, height)
            y += height + GAP
        note = "Point to a picture. Ask and answer." if mode == "qa" else "Point to the pictures as you read."
        footer(page, note, number, len(groups))
        pages.append(page)
    return pages


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    parser.add_argument("--mode", choices=("qa", "read", "scene"), required=True)
    parser.add_argument("--style", choices=THEMES, help="Override the style specified by the manifest")
    args = parser.parse_args()
    render_cli(parser, args, lambda spec, assets: render(spec, assets, args.mode, args.style))
