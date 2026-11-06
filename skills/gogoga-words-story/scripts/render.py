#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render a four-panel retelling pack or a picture book with editable text."""

from worksheet import A4, ACTIVITY_MARGIN, INK, MUTED, Page, activity_page, argument_parser, render_cli, wrap


WIDTH, _ = A4
MARGIN = ACTIVITY_MARGIN
CONTENT = WIDTH - 2 * MARGIN
THEMES = {
    "default": ("#37665a", "#b8cfc5", "#f3f8f5"),
    "engineering": ("#245387", "#b8cce0", "#f1f6fb"),
    "animal-story": ("#85513c", "#dbc4ae", "#fff5e9"),
    "folk-print": ("#983e2d", "#ded5c5", "#fff8ec"),
}
MODES = ("panels", "book")
BOOK_LANGUAGES = {"zh": ("zh",), "en": ("en",), "bilingual": ("zh", "en")}
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


def story_page(spec, assets, accent, border):
    page = activity_page(spec, "Four-panel Story", accent)
    page.text("Read the pictures in order.", MARGIN, 210, 28, "strong", accent)
    page.text("按顺序看图，跟读每一格。", MARGIN, 245, 25, "zh", MUTED)
    gap, height = 18, 638
    width = (CONTENT - gap) / 2
    for index, scene in enumerate(spec["scenes"]):
        row, column = divmod(index, 2)
        x, y = MARGIN + column * (width + gap), 280 + row * (height + gap)
        page.rect(x, y, width, height, "#ffffff", border, 17)
        page.text(f"{index + 1:02}  {TRANSITIONS[index]}", x + 20, y + 50, 30, "display", accent)
        page.art(assets, scene["asset"], x + 19, y + 70, width - 38, 384)
        bilingual_text(page, scene, x + 23, y + 493, width - 46)
    page.text("Point to the picture as you read.", MARGIN, 1690, 24, color=MUTED)
    return page


def sorting_page(spec, assets, accent, border):
    page = activity_page(spec, "Story Cards", accent)
    page.text("Cut the pictures apart. Put them in story order.", MARGIN, 210, 28, "strong", accent)
    page.text("沿虚线剪图，排出故事顺序，再自己讲一遍。", MARGIN, 245, 25, "zh", MUTED)
    gap, height = 20, 540
    width = (CONTENT - gap) / 2
    for index, scene_index in enumerate(CUT_ORDER):
        row, column = divmod(index, 2)
        x, y = MARGIN + column * (width + gap), 300 + row * (height + gap)
        page.rect(x, y, width, height, "#ffffff", border, 17, dash="8 8")
        page.art(assets, spec["scenes"][scene_index]["asset"], x + 18, y + 18, width - 36, height - 36)
    return page


def guide_page(spec, accent, border, key_background):
    page = activity_page(spec, "Retell Together", accent)
    page.rect(MARGIN, 195, CONTENT, 104, key_background, border, 15)
    page.text("Sorting key / 排序答案", MARGIN + 18, 233, 25, "zh", accent)
    order = " → ".join(POSITIONS[CUT_ORDER.index(index)] for index in range(4))
    page.text(order, MARGIN + 18, 273, 27, "strong", max_width=CONTENT - 36)
    for index, scene in enumerate(spec["scenes"]):
        y = 325 + index * 321
        page.rect(MARGIN, y, CONTENT, 300, "#ffffff", border, 17)
        x = MARGIN + 23
        page.text(f"{index + 1:02}  {TRANSITIONS[index]}", x, y + 45, 31, "display", accent)
        baseline = bilingual_text(page, scene["prompt"], x, y + 91, CONTENT - 46, limit=1)
        page.line(x, baseline + 2, WIDTH - x, baseline + 2, border)
        page.text("One way to tell it", x, baseline + 36, 22, "strong", accent)
        bilingual_text(page, scene, x, baseline + 76, CONTENT - 46, size=26, limit=1)
    page.text("Let the child tell the whole story in their own words.", MARGIN, 1690, 24, color=MUTED)
    return page


def book_pages(spec, assets, accent, border, language):
    if language not in BOOK_LANGUAGES:
        raise ValueError("Use zh, en, or bilingual for the picture book language")
    languages = BOOK_LANGUAGES[language]
    titles = {}
    for key in languages:
        field = "zh_title" if key == "zh" else "title"
        title = spec.get(field)
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Provide {field} for the picture book")
        titles[key] = title.strip()
    scenes = spec["scenes"]
    if not scenes:
        raise ValueError("Give the picture book at least one page")

    primary = languages[0]
    bilingual = len(languages) == 2
    width, height = 1440, 1320 if bilingual else 1200
    margin = 48
    art_width = width - 2 * margin
    art_height = art_width * 2 / 3
    art_top = 116 if bilingual else 96
    caption_top = art_top + art_height + 71
    pages = []
    for number, scene in enumerate(scenes, 1):
        page = Page(width, height, f"{titles[primary]} · {number:02}", "#fffdfa")
        page.text(titles[primary], margin, 54 if bilingual else 66, 41, primary, accent, max_width=art_width - 185)
        if bilingual:
            page.text(titles["en"], margin, 90, 29, "en", accent, max_width=art_width - 185)
        page.text(f"{number:02} / {len(scenes):02}", width - margin, 64, 26, "en", MUTED, "end")
        page.line(margin, art_top - 13, width - margin, art_top - 13, border, 1.4)
        page.art(assets, scene["asset"], margin, art_top, art_width, art_height)
        for group, key in enumerate(languages):
            size = 42 if key == "zh" else 38
            caption = scene.get(key)
            if not isinstance(caption, str) or not caption.strip():
                raise ValueError(f"Provide {key} text for picture book page {number}")
            lines = [line for paragraph in caption.splitlines()
                     for line in wrap(paragraph, art_width - 32, size, key)]
            if len(lines) > 2:
                raise ValueError(f"Shorten the {key} text on picture book page {number} to two lines")
            baseline = caption_top + group * 119
            for index, line in enumerate(lines):
                page.text(line, margin + 16, baseline + index * (size + 16), size, key, MUTED if group else INK)
        pages.append(page)
    return pages


def render(spec, assets, style=None, mode=None, language=None):
    style = style if style is not None else spec.get("style", "default")
    if style not in THEMES:
        raise ValueError(f"Use one of these story styles: {', '.join(THEMES)}")
    accent, border, key_background = THEMES[style]
    mode = mode if mode is not None else spec.get("mode", "panels")
    if mode not in MODES:
        raise ValueError("Use panels or book for the story mode")
    if mode == "book":
        language = language if language is not None else spec.get("language", "zh")
        return book_pages(spec, assets, accent, border, language)
    if language is not None:
        raise ValueError("Use --language in book mode")
    scenes = spec["scenes"]
    if len(scenes) != 4 or len({scene["asset"] for scene in scenes}) != 4:
        raise ValueError("Provide four different scenes in story order")
    return [story_page(spec, assets, accent, border), sorting_page(spec, assets, accent, border),
            guide_page(spec, accent, border, key_background)]


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    parser.add_argument("--style", choices=THEMES, help="Override the style specified by the manifest")
    parser.add_argument("--mode", choices=MODES, help="Override the mode specified by the manifest")
    parser.add_argument("--language", choices=BOOK_LANGUAGES, help="Override the text language in book mode")
    args = parser.parse_args()
    render_cli(parser, args, lambda spec, assets: render(spec, assets, args.style, args.mode, args.language))
