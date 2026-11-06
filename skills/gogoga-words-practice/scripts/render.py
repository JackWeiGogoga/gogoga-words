#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render wordless speaking worksheets or cut-out illustration sheets."""

from worksheet import ACCENT, LINE, MUTED, Page, argument_parser, batches, render_cli


WIDTH, HEIGHT = 1240, 1754
MARGIN = 66


def blank_pages(spec, assets):
    pages, groups = [], batches(spec["sections"], 5)
    index = 0
    for group in groups:
        page = Page(WIDTH, HEIGHT, f'{spec["title"]} | Wordless practice', "#ffffff")
        for row, section in enumerate(group):
            index += 1
            y = 78 + row * 319
            page.text(f"{index:02}", MARGIN + 26, y + 58, 26, "strong", ACCENT)
            page.line(MARGIN, y, WIDTH - MARGIN, y, LINE, 2)
            items = section["images"]
            slot = (WIDTH - 2 * MARGIN - 88) / len(items)
            for column, item in enumerate(items):
                center = MARGIN + 88 + slot * (column + 0.5)
                width = min(253, slot - 26)
                page.art(assets, item["asset"], center - width / 2, y + 26, width, 213)
                line_w = min(188, width - 20)
                page.line(center - line_w / 2, y + 273, center + line_w / 2, y + 273, MUTED)
        pages.append(page)
    return pages


def sticker_pages(spec, assets):
    keys = list(dict.fromkeys(item["asset"] for section in spec["sections"] for item in section["images"]))
    groups, pages = batches(keys, 16), []
    gap = 17
    card_w = (WIDTH - 2 * MARGIN - 3 * gap) / 4
    card_h = 337
    for number, group in enumerate(groups, 1):
        page = Page(WIDTH, HEIGHT, f'{spec["title"]} | Cut-out pictures', "#ffffff")
        page.text(spec["title"], MARGIN, 95, 66, "display", max_width=WIDTH - 2 * MARGIN - 350)
        page.text("Cut & Say", WIDTH - MARGIN, 78, 32, "strong", ACCENT, "end")
        page.text("沿虚线剪下，选一张图说一说。", MARGIN + 3, 141, 28, "zh", MUTED)
        page.line(MARGIN, 163, WIDTH - MARGIN, 163, ACCENT, 2)
        for index, key in enumerate(group):
            row, column = divmod(index, 4)
            x = MARGIN + column * (card_w + gap)
            y = 188 + row * (card_h + gap)
            page.rect(x, y, card_w, card_h, "#ffffff", "#9b8a7f", 22, dash="8 8")
            page.art(assets, key, x + 24, y + 24, card_w - 48, card_h - 48)
        page.text(f"{number:02} / {len(groups):02}", WIDTH - MARGIN, 1692, 22, color=MUTED, anchor="end")
        pages.append(page)
    return pages


def render(spec, assets, mode):
    if not spec["sections"]:
        raise ValueError("Add at least one practice section")
    for section in spec["sections"]:
        if not 1 <= len(section["images"]) <= 6:
            raise ValueError(f'Use 1–6 illustrations in section {section["title"]!r}')
    return blank_pages(spec, assets) if mode == "blank" else sticker_pages(spec, assets)


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    parser.add_argument("--mode", choices=("blank", "stickers"), required=True)
    args = parser.parse_args()
    render_cli(parser, args, lambda spec, assets: render(spec, assets, args.mode))
