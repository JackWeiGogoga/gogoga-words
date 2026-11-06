#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render a four-panel story, shuffled picture cards, and a retelling guide."""

from worksheet import A4, ACTIVITY_MARGIN, INK, MUTED, activity_page, argument_parser, render_cli, wrap


WIDTH, _ = A4
MARGIN = ACTIVITY_MARGIN
CONTENT = WIDTH - 2 * MARGIN
ACCENT, BORDER = "#37665a", "#b8cfc5"
TRANSITIONS = ("First", "Next", "Then", "Finally")
CUT_ORDER = (2, 0, 3, 1)
POSITIONS = ("top left", "top right", "bottom left", "bottom right")


def bilingual_text(page, entry, x, baseline, width, size=28, limit=2):
    for key, style, font_size, color in (("en", "en", size, INK), ("zh", "zh", 24, MUTED)):
        lines = wrap(entry[key], width, font_size, style)
        if not 1 <= len(lines) <= limit:
            raise ValueError(f"Shorten the {key} text to fit: {entry[key]!r}")
        for line in lines:
            page.text(line, x, baseline, font_size, style, color)
            baseline += font_size + 8
    return baseline


def story_page(spec, assets):
    page = activity_page(spec, "Four-panel Story", ACCENT)
    page.text("Read the pictures in order.", MARGIN, 210, 28, "strong", ACCENT)
    page.text("按顺序看图，跟读每一格。", MARGIN, 245, 25, "zh", MUTED)
    gap, height = 18, 638
    width = (CONTENT - gap) / 2
    for index, scene in enumerate(spec["scenes"]):
        row, column = divmod(index, 2)
        x, y = MARGIN + column * (width + gap), 280 + row * (height + gap)
        page.rect(x, y, width, height, "#ffffff", BORDER, 17)
        page.text(f"{index + 1:02}  {TRANSITIONS[index]}", x + 20, y + 50, 30, "display", ACCENT)
        page.art(assets, scene["asset"], x + 19, y + 70, width - 38, 384)
        bilingual_text(page, scene, x + 23, y + 493, width - 46)
    page.text("Point to the picture as you read.", MARGIN, 1690, 24, color=MUTED)
    return page


def sorting_page(spec, assets):
    page = activity_page(spec, "Story Cards", ACCENT)
    page.text("Cut the pictures apart. Put them in story order.", MARGIN, 210, 28, "strong", ACCENT)
    page.text("沿虚线剪图，排出故事顺序，再自己讲一遍。", MARGIN, 245, 25, "zh", MUTED)
    gap, height = 20, 540
    width = (CONTENT - gap) / 2
    for index, scene_index in enumerate(CUT_ORDER):
        row, column = divmod(index, 2)
        x, y = MARGIN + column * (width + gap), 300 + row * (height + gap)
        page.rect(x, y, width, height, "#ffffff", BORDER, 17, dash="8 8")
        page.art(assets, spec["scenes"][scene_index]["asset"], x + 18, y + 18, width - 36, height - 36)
    return page


def guide_page(spec):
    page = activity_page(spec, "Retell Together", ACCENT)
    page.rect(MARGIN, 195, CONTENT, 104, "#f3f8f5", BORDER, 15)
    page.text("Sorting key / 排序答案", MARGIN + 18, 233, 25, "zh", ACCENT)
    order = " → ".join(POSITIONS[CUT_ORDER.index(index)] for index in range(4))
    page.text(order, MARGIN + 18, 273, 27, "strong", max_width=CONTENT - 36)
    for index, scene in enumerate(spec["scenes"]):
        y = 325 + index * 321
        page.rect(MARGIN, y, CONTENT, 300, "#ffffff", BORDER, 17)
        x = MARGIN + 23
        page.text(f"{index + 1:02}  {TRANSITIONS[index]}", x, y + 45, 31, "display", ACCENT)
        baseline = bilingual_text(page, scene["prompt"], x, y + 91, CONTENT - 46, limit=1)
        page.line(x, baseline + 2, WIDTH - x, baseline + 2, BORDER)
        page.text("One way to tell it", x, baseline + 36, 22, "strong", ACCENT)
        bilingual_text(page, scene, x, baseline + 76, CONTENT - 46, size=26, limit=1)
    page.text("Let the child tell the whole story in their own words.", MARGIN, 1690, 24, color=MUTED)
    return page


def render(spec, assets):
    scenes = spec["scenes"]
    if len(scenes) != 4 or len({scene["asset"] for scene in scenes}) != 4:
        raise ValueError("Provide four different scenes in story order")
    return [story_page(spec, assets), sorting_page(spec, assets), guide_page(spec)]


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    render_cli(parser, parser.parse_args(), render)
