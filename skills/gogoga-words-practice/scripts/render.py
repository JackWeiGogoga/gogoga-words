#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render wordless practice, cut-out pictures, or matching mats and cards."""

from itertools import zip_longest

from worksheet import ACCENT, INK, LINE, MUTED, Page, argument_parser, batches, render_cli


WIDTH, HEIGHT = 1240, 1754
MARGIN = 66


def colors(line_art):
    return ("#222222", "#b8b8b8", "#4b4b4b", "#777777") if line_art else (ACCENT, LINE, MUTED, "#9b8a7f")


def blank_pages(spec, assets, line_art):
    accent, rule, muted, _ = colors(line_art)
    pages, groups = [], batches(spec["sections"], 5)
    index = 0
    for group in groups:
        page = Page(WIDTH, HEIGHT, f'{spec["title"]} | Wordless practice', "#ffffff")
        for row, section in enumerate(group):
            index += 1
            y = 78 + row * 319
            page.text(f"{index:02}", MARGIN + 26, y + 58, 26, "strong", accent)
            page.line(MARGIN, y, WIDTH - MARGIN, y, rule, 2)
            items = section["images"]
            slot = (WIDTH - 2 * MARGIN - 88) / len(items)
            for column, item in enumerate(items):
                center = MARGIN + 88 + slot * (column + 0.5)
                width = min(253, slot - 26)
                page.art(assets, item["asset"], center - width / 2, y + 26, width, 213)
                line_w = min(188, width - 20)
                page.line(center - line_w / 2, y + 273, center + line_w / 2, y + 273, muted)
        pages.append(page)
    return pages


def sticker_pages(spec, assets, line_art):
    accent, _, muted, border = colors(line_art)
    keys = list(dict.fromkeys(item["asset"] for section in spec["sections"] for item in section["images"]))
    groups, pages = batches(keys, 16), []
    gap = 17
    card_w = (WIDTH - 2 * MARGIN - 3 * gap) / 4
    card_h = 337
    for number, group in enumerate(groups, 1):
        page = Page(WIDTH, HEIGHT, f'{spec["title"]} | Cut-out pictures', "#ffffff")
        page.text(spec["title"], MARGIN, 95, 66, "display", accent if line_art else INK, max_width=WIDTH - 2 * MARGIN - 350)
        page.text("Cut & Say", WIDTH - MARGIN, 78, 32, "strong", accent, "end")
        page.text("沿虚线剪下，选一张图说一说。", MARGIN + 3, 141, 28, "zh", muted)
        page.line(MARGIN, 163, WIDTH - MARGIN, 163, accent, 2)
        for index, key in enumerate(group):
            row, column = divmod(index, 4)
            x = MARGIN + column * (card_w + gap)
            y = 188 + row * (card_h + gap)
            page.rect(x, y, card_w, card_h, "#ffffff", border, 22, dash="8 8")
            page.art(assets, key, x + 24, y + 24, card_w - 48, card_h - 48)
        page.text(f"{number:02} / {len(groups):02}", WIDTH - MARGIN, 1692, 22, color=muted, anchor="end")
        pages.append(page)
    return pages


def match_header(title, label, instruction, part, total, accent, muted):
    page = Page(WIDTH, HEIGHT, f"{title} | {label}", "#ffffff")
    page.text(title, MARGIN, 95, 66, "display", accent, max_width=WIDTH - 2 * MARGIN - 335)
    page.text(label, WIDTH - MARGIN, 78, 30, "strong", accent, "end")
    page.text(instruction, MARGIN, 145, 28, "zh", muted, max_width=WIDTH - 2 * MARGIN)
    page.line(MARGIN, 169, WIDTH - MARGIN, 169, accent, 2)
    page.text(f"Set {part:02} / {total:02}", WIDTH - MARGIN, 1692, 22, color=muted, anchor="end")
    return page


def match_pages(spec, assets, line_art):
    accent, rule, muted, border = colors(line_art)
    sets = batches(spec["sections"], 3)
    pages = []
    gap, card_h = 16, 240
    for index, group in enumerate(sets, 1):
        # Interleave the groups so their solutions are not printed together.
        columns = max(3, max(len(section["images"]) for section in group))
        items = [item for row in zip_longest(*(s["images"] for s in reversed(group))) for item in row if item is not None]
        if len({item["asset"] for item in items}) != len(items):
            raise ValueError(f"Each picture must have one matching slot in set {index}")
        card_w = (WIDTH - 2 * MARGIN - (columns - 1) * gap) / columns
        board = match_header(spec["title"], "Matching Mat", "把图卡贴到对应的空格里，再说一遍英文。", index, len(sets), accent, muted)
        cards = match_header(spec["title"], "Cut-out Cards", "沿虚线剪下图卡，找到它所属的一组。", index, len(sets), accent, muted)
        for row, section in enumerate(group):
            y = 250 + row * 422
            board.text(section["title"], MARGIN, y, 38, "display", accent, max_width=WIDTH - 2 * MARGIN)
            if section.get("zh_title"):
                board.text(section["zh_title"], MARGIN, y + 38, 26, "zh", muted, max_width=WIDTH - 2 * MARGIN)
            for column in range(len(section["images"])):
                x = MARGIN + column * (card_w + gap)
                board.rect(x, y + 62, card_w, card_h, "#ffffff", border, 15)
            board.line(MARGIN, y + 336, WIDTH - MARGIN, y + 336, rule)
        for position, item in enumerate(items):
            row, column = divmod(position, columns)
            x = MARGIN + column * (card_w + gap)
            y = 229 + row * (card_h + gap)
            cards.rect(x, y, card_w, card_h, "#ffffff", border, 15, dash="8 8")
            cards.art(assets, item["asset"], x + 13, y + 13, card_w - 26, card_h - 26)
        pages.extend((board, cards))
    return pages


def render(spec, assets, mode, line_art=False):
    if not spec["sections"]:
        raise ValueError("Add at least one practice section")
    for section in spec["sections"]:
        if not 1 <= len(section["images"]) <= 6:
            raise ValueError(f'Use 1–6 illustrations in section {section["title"]!r}')
    if line_art:
        assets = assets.line_art()
    draw = {"blank": blank_pages, "stickers": sticker_pages, "match": match_pages}[mode]
    return draw(spec, assets, line_art)


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    parser.add_argument("--mode", choices=("blank", "stickers", "match"), required=True)
    parser.add_argument("--line-art", action="store_true", help="Print using the matching line_art illustrations")
    args = parser.parse_args()
    render_cli(parser, args, lambda spec, assets: render(spec, assets, args.mode, args.line_art))
