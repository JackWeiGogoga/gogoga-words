#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render short-vowel CVC cards and an eight-page foldable mini-book."""

import re
from pathlib import Path

from worksheet import A4, ACTIVITY_MARGIN, MUTED, Page, activity_page, argument_parser, render_cli, wrap


WIDTH, HEIGHT = A4
MARGIN = ACTIVITY_MARGIN
CONTENT = WIDTH - 2 * MARGIN
ACCENT, BORDER = "#355c92", "#bacadf"
VOCABULARY = Path(__file__).resolve().parents[1] / "references" / "cvc-words.txt"
TOP_PAGES = (5, 4, 3, 2)
BOTTOM_PAGES = (6, 7, 8, 1)


def validate(spec):
    vowel = spec["vowel"]
    letters = spec["known_letters"]
    if vowel not in ("a", "e", "i", "o", "u") or not re.fullmatch(r"[a-z]+", letters) or vowel not in letters:
        raise ValueError("Choose a short vowel and include it in the lowercase known_letters string")
    known = set(letters)
    words = set(VOCABULARY.read_text(encoding="utf-8").split())
    allowed = {word for word in words if word[1] == vowel and set(word) <= known}
    helper_words = spec.get("helper_words", [])
    if not isinstance(helper_words, list) or any(not re.fullmatch(r"[a-z]+", word) for word in helper_words):
        raise ValueError("List helper words as individual lowercase words")
    helpers = set(helper_words)
    cards = [item["word"] for item in spec["cards"]]
    if not 3 <= len(cards) <= 12 or len(set(cards)) != len(cards):
        raise ValueError("Provide 3–12 distinct CVC cards")
    for word in cards:
        if word not in allowed:
            raise ValueError(f"Card {word!r} is outside the approved short-{vowel} words and known letters")
    if len(spec["pages"]) != 8:
        raise ValueError("Provide exactly eight book pages in reading order, including the covers")
    for number, entry in enumerate(spec["pages"], 1):
        text = entry["text"]
        tokens = re.findall(r"[a-z]+", text.lower())
        if not tokens or not re.fullmatch(r"[A-Za-z ,.?!]+", text):
            raise ValueError(f"Page {number} needs simple English words and punctuation")
        for token in tokens:
            if token not in allowed and token not in helpers:
                raise ValueError(f"Page {number} uses {token!r} outside the taught sounds and helper words")


def card_page(spec, assets):
    page = activity_page(spec, "Sound & Blend", ACCENT)
    page.text("Say each sound, then blend the whole word.", MARGIN, 211, 29, "strong", ACCENT)
    page.text("先说每个字母的音，再连起来读整词。", MARGIN, 246, 25, "zh", MUTED)
    gap = 16
    cards = spec["cards"]
    rows = (len(cards) + 2) // 3
    width = (CONTENT - 2 * gap) / 3
    height = min(530, (1260 - (rows - 1) * gap) / rows)
    for index, item in enumerate(cards):
        row, column = divmod(index, 3)
        x, y = MARGIN + column * (width + gap), 281 + row * (height + gap)
        page.rect(x, y, width, height, "#ffffff", BORDER, 18, dash="8 8")
        page.art(assets, item["asset"], x + 24, y + 20, width - 48, height - 185)
        center = x + width / 2
        page.text(item["word"], center, y + height - 109, 47, "strong", anchor="middle")
        for letter_index, letter in enumerate(item["word"]):
            left = center + (letter_index - 1) * 73 - 31
            vowel = letter_index == 1
            page.rect(left, y + height - 85, 62, 62, "#e8f0fb" if vowel else "#ffffff", BORDER, 10)
            page.text(letter, left + 31, y + height - 40, 36, "strong", ACCENT, "middle")
    page.text("Book sheet: dashed lines are folds. Cut only the solid centre line.", MARGIN, 1686, 22,
              color=MUTED, max_width=CONTENT)
    page.text("小书页的虚线用来折叠，只剪中间的实线。", MARGIN, 1720, 22, "zh", MUTED)
    return page


def booklet_page(spec, assets):
    width, height = HEIGHT, WIDTH
    panel_w, panel_h = width / 4, height / 2
    page = Page(width, height, f'{spec["title"]} | Foldable reader', "#ffffff")
    for row, order in enumerate((TOP_PAGES, BOTTOM_PAGES)):
        for column, number in enumerate(order):
            entry = spec["pages"][number - 1]
            x, y = column * panel_w, row * panel_h
            transform = f"translate({x + panel_w} {y + panel_h}) rotate(180)" if row == 0 else f"translate({x} {y})"
            page.markup.append(f'<g transform="{transform}">')
            page.art(assets, entry["asset"], 29, 55, panel_w - 58, 326)
            size, style = (58, "display") if number == 1 else (47, "strong")
            baseline = 418 if number == 1 else 437
            lines = wrap(entry["text"], panel_w - 62, size, style)
            if len(lines) > 3:
                raise ValueError(f"Shorten the text on book page {number}")
            for i, line in enumerate(lines):
                page.text(line, panel_w / 2, baseline + i * (size + 8), size, style, ACCENT, "middle")
            page.text(str(number), panel_w / 2, 584, 23, color=MUTED, anchor="middle")
            page.markup.append("</g>")
    guide = "#8793a4"
    for column in (1, 2, 3):
        x = column * panel_w
        page.line(x, 18, x, height - 18, guide, 1.5, dash="9 9")
    page.line(18, panel_h, panel_w, panel_h, guide, 1.5, dash="9 9")
    page.line(3 * panel_w, panel_h, width - 18, panel_h, guide, 1.5, dash="9 9")
    page.line(panel_w, panel_h, 3 * panel_w, panel_h, "#a13336", 2.6)
    return page


def render(spec, assets):
    validate(spec)
    return [card_page(spec, assets), booklet_page(spec, assets)]


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    render_cli(parser, parser.parse_args(), render)
