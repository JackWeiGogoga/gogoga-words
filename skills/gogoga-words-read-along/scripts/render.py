#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render bilingual picture questions or a read-aloud guide."""

from worksheet import ACCENT, LINE, MUTED, Page, argument_parser, batches, render_cli, wrap


WIDTH, HEIGHT = 1240, 1754
MARGIN, TOP, BOTTOM, GAP = 62, 185, 1653, 12
TEXT_X, TEXT_WIDTH = 94, 555
ART_X, ART_WIDTH = 686, 470


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


def render(spec, assets, mode):
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
        page = Page(WIDTH, HEIGHT, f'{spec["title"]} | {name}')
        page.text(name, WIDTH - MARGIN, 79, 32, "strong", ACCENT, "end")
        page.text(spec["title"], MARGIN, 94, 70, "display", max_width=WIDTH - 2 * MARGIN - 325)
        page.text(spec["zh_title"], MARGIN + 3, 144, 33, "zh", max_width=WIDTH - 2 * MARGIN)
        page.line(MARGIN, 162, WIDTH - MARGIN, 162, ACCENT, 2)
        y = TOP
        for index, section, lines, height in items:
            page.rect(MARGIN, y, WIDTH - 2 * MARGIN, height, "#ffffff", LINE, 22)
            page.text(f'{index:02}   {section["title"]}', TEXT_X, y + 48, 31, "display", ACCENT, max_width=TEXT_WIDTH)
            page.line(667, y + 28, 667, y + height - 26)
            for line, style, size, offset in lines:
                page.text(line, TEXT_X, y + offset, size, style, MUTED if style == "zh" else "#322722")
            section_art(page, assets, section["images"], y, height)
            y += height + GAP
        note = "Point to a picture. Ask and answer." if mode == "qa" else "Point to the pictures as you read."
        page.text(note, MARGIN, 1705, 22, color=MUTED)
        page.text(f"{number:02} / {len(groups):02}", WIDTH - MARGIN, 1705, 22, color=MUTED, anchor="end")
        pages.append(page)
    return pages


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    parser.add_argument("--mode", choices=("qa", "read"), required=True)
    args = parser.parse_args()
    render_cli(parser, args, lambda spec, assets: render(spec, assets, args.mode))
