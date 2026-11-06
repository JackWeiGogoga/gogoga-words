#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Render a picture menu, two role cards, and a shopping mission."""

from worksheet import A4, ACTIVITY_MARGIN, MUTED, activity_page, argument_parser, render_cli


WIDTH, _ = A4
MARGIN = ACTIVITY_MARGIN
CONTENT = WIDTH - 2 * MARGIN
ACCENT, BORDER = "#85452f", "#d9c3ad"


def coins(count):
    return f"{count} coin{'s' if count != 1 else ''}"


def validate(spec):
    items = spec["items"]
    by_asset = {item["asset"]: item for item in items}
    if not 3 <= len(items) <= 9 or len(by_asset) != len(items):
        raise ValueError("Provide 3–9 distinct things to buy")
    for item in items:
        if type(item["price"]) is not int or not 1 <= item["price"] <= 99:
            raise ValueError("Each price must be 1–99 play coins")
        if type(item["stock"]) is not int or not 0 <= item["stock"] <= 99:
            raise ValueError("Each stock count must be 0–99")
    task = spec["task"]
    budget, requests = task["budget"], task["items"]
    if type(budget) is not int or not 1 <= budget <= 999 or not 1 <= len(requests) <= 6:
        raise ValueError("Use a budget of 1–999 coins and 1–6 things on the shopping list")
    if len({request["asset"] for request in requests}) != len(requests):
        raise ValueError("Combine repeated shopping list items into one quantity")
    total = 0
    for request in requests:
        quantity = request["quantity"]
        item = by_asset[request["asset"]]
        if type(quantity) is not int or not 1 <= quantity <= item["stock"]:
            raise ValueError(f"Check stock for the shopping task: {item['en']}")
        if quantity > 1 and not item.get("plural"):
            raise ValueError(f"Provide a plural label for {item['en']!r}")
        total += item["price"] * quantity
    if total > budget:
        raise ValueError(f"The shopping list costs {coins(total)}; increase the budget or adjust the list")
    for role in ("buyer", "seller"):
        if not 1 <= len(spec["roles"][role]["lines"]) <= 4:
            raise ValueError(f"Give the {role} 1–4 short phrases")
    return by_asset


def menu_page(spec, assets):
    page = activity_page(spec, "Picture Menu", ACCENT)
    page.text("Choose something and ask its price.", MARGIN, 212, 29, "strong", ACCENT)
    page.text("选一样东西，向店员问价。", MARGIN, 248, 26, "zh", MUTED)
    items = spec["items"]
    rows = (len(items) + 2) // 3
    gap = 17
    width = (CONTENT - 2 * gap) / 3
    height = min(480, (1230 - (rows - 1) * gap) / rows)
    for index, item in enumerate(items):
        row, column = divmod(index, 3)
        x, y = MARGIN + column * (width + gap), 284 + row * (height + gap)
        page.rect(x, y, width, height, "#fffdf9", BORDER, 18)
        page.art(assets, item["asset"], x + 29, y + 22, width - 58, height - 166)
        center = x + width / 2
        page.text(item["en"], center, y + height - 104, 33, "strong", anchor="middle", max_width=width - 30)
        page.text(item["zh"], center, y + height - 68, 25, "zh", MUTED, "middle", max_width=width - 30)
        page.text(coins(item["price"]), center, y + height - 24, 27, "strong", ACCENT, "middle")
    page.text("Use play coins, then swap roles.", MARGIN, 1690, 24, color=MUTED)
    return page


def role_page(spec):
    page = activity_page(spec, "Role Cards", ACCENT)
    for key, y in (("buyer", 208), ("seller", 928)):
        role = spec["roles"][key]
        x = MARGIN + 32
        page.rect(MARGIN, y, CONTENT, 676, "#ffffff", BORDER, 19, dash="8 8")
        page.text(role["title"], x, y + 67, 52, "display", ACCENT, max_width=CONTENT - 64)
        page.text(role["zh_title"], x + 2, y + 107, 28, "zh", MUTED, max_width=CONTENT - 64)
        page.line(x, y + 128, WIDTH - x, y + 128, BORDER)
        for index, line in enumerate(role["lines"]):
            baseline = y + 186 + index * 78
            page.text(line["en"], x, baseline, 31, "strong", max_width=CONTENT - 64)
            page.text(line["zh"], x, baseline + 33, 24, "zh", MUTED, max_width=CONTENT - 64)
        if key == "seller":
            page.text("Stock list / 库存", x, y + 505, 24, "zh", ACCENT)
            for index, item in enumerate(spec["items"]):
                row, column = divmod(index, 3)
                page.text(f'{item["en"]} × {item["stock"]}', x + column * 352, y + 543 + row * 38,
                          23, max_width=331)
        else:
            page.text("Take the mission sheet. Tick each item after you buy it.", x, y + 535, 26,
                      color=ACCENT, max_width=CONTENT - 64)
            page.text("拿任务单。每买到一样东西，就打一个勾。", x, y + 576, 24, "zh", MUTED)
    page.text("Cut the role cards apart and give one to each player.", MARGIN, 1690, 24, color=MUTED)
    return page


def mission_page(spec, assets, by_asset):
    page = activity_page(spec, "Shopping Mission", ACCENT)
    task = spec["task"]
    page.rect(MARGIN, 191, CONTENT, 83, "#fff7eb", BORDER, 16)
    page.text("Your shopping list", MARGIN + 23, 243, 31, "display", ACCENT)
    page.text(f'Budget / 预算 {coins(task["budget"])}', WIDTH - MARGIN - 24, 243, 26,
              "zh", ACCENT, "end", max_width=510)
    for index, request in enumerate(task["items"]):
        item = by_asset[request["asset"]]
        quantity = request["quantity"]
        noun = item["en"] if quantity == 1 else item["plural"]
        y = 311 + index * 179
        page.rect(MARGIN, y, CONTENT, 153, "#ffffff", BORDER, 16)
        page.art(assets, item["asset"], MARGIN + 24, y + 12, 204, 129)
        page.text(f"{quantity} {noun}", MARGIN + 252, y + 68, 36, "strong", max_width=CONTENT - 370)
        page.text(item["zh"], MARGIN + 252, y + 109, 26, "zh", MUTED, max_width=CONTENT - 370)
        page.rect(WIDTH - MARGIN - 84, y + 53, 45, 45, "#ffffff", ACCENT, 4)
    y = 328 + len(task["items"]) * 179
    page.text("I spent __________.", MARGIN, y + 31, 31, "strong", ACCENT)
    page.text("问价、付钱，最后把花了多少枚游戏币写下来。", MARGIN, y + 74, 25, "zh", MUTED)
    return page


def render(spec, assets):
    by_asset = validate(spec)
    return [menu_page(spec, assets), role_page(spec), mission_page(spec, assets, by_asset)]


if __name__ == "__main__":
    parser = argument_parser(__doc__)
    render_cli(parser, parser.parse_args(), render)
