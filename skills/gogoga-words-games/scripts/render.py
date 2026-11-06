#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render picture Bingo boards and matching caller cards."""

from itertools import permutations
from random import Random

from worksheet import A4, ACTIVITY_MARGIN, MUTED, activity_page, argument_parser, batches, render_cli


WIDTH, _ = A4
MARGIN = ACTIVITY_MARGIN
ACCENT, BORDER = "#17645d", "#a4c3bc"
CONTENT = WIDTH - 2 * MARGIN


def layouts(items, size, count, seed):
    cells = size * size
    if not cells <= len(items) <= cells * count:
        raise ValueError("Use at least one board's worth of words and enough boards to include every word")
    rng = Random(seed)
    pool = list(range(len(items)))
    rng.shuffle(pool)
    used = set()
    for board in range(count):
        selection = [pool[(board * cells + offset) % len(pool)] for offset in range(cells)]
        rng.shuffle(selection)
        layout = next(order for order in permutations(selection) if order not in used)
        used.add(layout)
        yield [items[index] for index in layout]


def bingo_board(spec, assets, items, size, number, total):
    page = activity_page(spec, "Picture Bingo", ACCENT)
    page.text("Listen for the word. Cover the matching picture.", MARGIN, 209, 29, "strong", ACCENT)
    page.text("听到单词，盖住对应的图片。", MARGIN, 244, 26, "zh", MUTED)
    gap = 12
    side = (CONTENT - (size - 1) * gap) / size
    for index, item in enumerate(items):
        row, column = divmod(index, size)
        x, y = MARGIN + column * (side + gap), 285 + row * (side + gap)
        page.rect(x, y, side, side, "#ffffff", BORDER, 18)
        padding = side * 0.13
        page.art(assets, item["asset"], x + padding, y + padding, side - 2 * padding, side - 2 * padding)
    y = 285 + CONTENT + 70
    page.text(f"Cover {size} in a row to call Bingo!", MARGIN, y, 29, "display", ACCENT)
    page.text("横、竖或斜线连满一排，就喊 Bingo。", MARGIN, y + 38, 25, "zh", MUTED)
    page.text(f"Board {number:02} / {total:02}", WIDTH - MARGIN, 1690, 24, color=MUTED, anchor="end")
    return page


def caller_pages(spec, assets, items):
    groups = batches(items, 16)
    gap, height = 16, 300
    width = (CONTENT - 3 * gap) / 4
    for number, group in enumerate(groups, 1):
        page = activity_page(spec, "Caller Cards", ACCENT)
        page.text("Cut, shuffle, then say one word at a time.", MARGIN, 209, 28, "strong", ACCENT)
        page.text("剪下并打乱叫词卡。抽一张，只念英文。", MARGIN, 244, 26, "zh", MUTED)
        for index, item in enumerate(group):
            row, column = divmod(index, 4)
            x, y = MARGIN + column * (width + gap), 285 + row * (height + gap)
            page.rect(x, y, width, height, "#ffffff", BORDER, 14, dash="8 8")
            page.art(assets, item["asset"], x + 18, y + 18, width - 36, 178)
            page.text(item["en"], x + width / 2, y + 229, 28, "strong", anchor="middle", max_width=width - 28)
            if item.get("zh"):
                page.text(item["zh"], x + width / 2, y + 264, 23, "zh", MUTED, "middle", max_width=width - 28)
        page.text(f"Caller cards {number:02} / {len(groups):02}", WIDTH - MARGIN, 1690, 24, color=MUTED, anchor="end")
        yield page


def render(spec, assets, size=None, boards=None, seed=None):
    size = spec.get("board_size", 3) if size is None else size
    boards = spec.get("board_count", 4) if boards is None else boards
    seed = spec.get("seed", 0) if seed is None else seed
    if type(size) is not int or size not in (2, 3, 4) or type(boards) is not int or not 1 <= boards <= 12:
        raise ValueError("Use board sizes 2–4 and 1–12 boards")
    if type(seed) is not int:
        raise ValueError("Use an integer seed")
    items = spec["items"]
    words = [item["en"].strip().casefold() for item in items]
    if not all(words) or len(set(words)) != len(items) or len({item["asset"] for item in items}) != len(items):
        raise ValueError("Each Bingo item needs a distinct English word and illustration")
    pages = [bingo_board(spec, assets, board, size, number, boards)
             for number, board in enumerate(layouts(items, size, boards, seed), 1)]
    return pages + list(caller_pages(spec, assets, items))


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    parser.add_argument("--size", type=int, choices=(2, 3, 4), help="Number of squares per side")
    parser.add_argument("--boards", type=int, help="Number of different boards")
    parser.add_argument("--seed", type=int, help="Change the board layout reproducibly")
    args = parser.parse_args()
    render_cli(parser, args, lambda spec, assets: render(spec, assets, args.size, args.boards, args.seed))
