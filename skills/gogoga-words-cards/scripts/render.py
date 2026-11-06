#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render illustrated vocabulary cards from a JSON word list."""

from worksheet import ACCENT, LINE, MUTED, PAPER, Page, argument_parser, batches, render_cli


WIDTH, HEIGHT = 1080, 1440
MARGIN, GAP = 52, 14
THEMES = {
    "watercolor": (PAPER, ACCENT, LINE, MUTED, "display"),
    "flat": ("#ffffff", "#17645d", "#ccded9", "#455c58", "strong"),
    "photo": ("#ffffff", "#29486c", "#d6e0e9", "#485a6c", "strong"),
    "paper-collage": ("#ffffff", "#8e4337", "#e7cfc1", "#6d534a", "display"),
}


def render(spec, assets, style=None):
    style = style if style is not None else spec.get("style", "watercolor")
    if style not in THEMES:
        raise ValueError(f"Use one of these card styles: {', '.join(THEMES)}")
    paper, accent, border, muted, heading = THEMES[style]
    columns, rows = spec.get("columns", 5), spec.get("rows", 4)
    if type(columns) is not int or type(rows) is not int or not (2 <= columns <= 5 and 2 <= rows <= 5):
        raise ValueError("Use 2–5 columns and 2–5 rows")
    if not spec["items"]:
        raise ValueError("Add at least one vocabulary item")

    groups = batches(spec["items"], columns * rows)
    card_w = (WIDTH - 2 * MARGIN - (columns - 1) * GAP) / columns
    card_h = (1169 - (rows - 1) * GAP) / rows
    pages = []
    for number, items in enumerate(groups, 1):
        page = Page(WIDTH, HEIGHT, f'{spec["title"]} | Vocabulary cards', paper)
        page.text("PICTURE WORDS", WIDTH - MARGIN, 62, 19, "strong", accent, "end")
        page.text(spec["title"], MARGIN, 91, 64, heading, max_width=WIDTH - 2 * MARGIN - 220)
        page.text(spec["zh_title"], MARGIN + 3, 140, 34, "zh", max_width=WIDTH - 2 * MARGIN)
        page.line(MARGIN, 162, WIDTH - MARGIN, 162, accent, 2)

        for index, item in enumerate(items):
            if any(not item[key].strip() for key in ("en", "ipa", "zh")):
                raise ValueError(f"Incomplete labels for card {index + 1} on page {number}")
            row, column = divmod(index, columns)
            x = MARGIN + column * (card_w + GAP)
            y = 183 + row * (card_h + GAP)
            center = x + card_w / 2
            page.rect(x, y, card_w, card_h, "#ffffff", border, 17)
            page.art(assets, item["asset"], x + 14, y + 13, card_w - 28, card_h * 0.52)
            page.text(item["en"], center, y + card_h * 0.70, 30, "strong", anchor="middle", max_width=card_w - 20)
            page.text(item["ipa"], center, y + card_h * 0.81, 24, color=muted, anchor="middle", max_width=card_w - 20)
            page.text(item["zh"], center, y + card_h * 0.93, 26, "zh", anchor="middle", max_width=card_w - 20)

        page.text(spec.get("pronunciation", ""), MARGIN, 1400, 21, color=muted, max_width=WIDTH - 2 * MARGIN - 120)
        page.text(f"{number:02} / {len(groups):02}", WIDTH - MARGIN, 1400, 21, color=muted, anchor="end")
        pages.append(page)
    return pages


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    parser.add_argument("--style", choices=THEMES, help="Override the style specified by the manifest")
    args = parser.parse_args()
    render_cli(parser, args, lambda spec, assets: render(spec, assets, args.style))
