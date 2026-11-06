#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Lay out an illustrated theme map and export a self-contained SVG."""

import argparse
import base64
from functools import cache
from html import escape
from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageFont


WIDTH, HEIGHT = 1080, 1440
INK, BRICK = "#2b201c", "#ad6255"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
PAPER_PATH = Path(__file__).resolve().parents[1] / "assets" / "paper-texture.jpg"
NUMBER_X = 354
HEADING_X = 380
CONTENT_RIGHT = 1037


def encoded(image, format_name="PNG", **options):
    stream = BytesIO()
    image.save(stream, format_name, **options)
    return base64.b64encode(stream.getvalue()).decode("ascii")


def paper():
    return "data:image/jpeg;base64," + base64.b64encode(PAPER_PATH.read_bytes()).decode("ascii")


@cache
def font(size, bold):
    path = FONT_DIR / ("ChalkboardSE.ttc" if bold else "Chalkboard.ttc")
    if path.is_file():
        return ImageFont.truetype(str(path), size, index=2 if bold else 0)
    return ImageFont.load_default(size=size)


def text_width(value, size, bold=False):
    return font(size, bold).getlength(value)


def lettering(value, x, y, size, anchor="start", bold=False):
    weight = "700" if bold else "400"
    family = "Chalkboard SE" if bold else "Chalkboard"
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}, Comic Sans MS, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
        f'fill="{INK}">{escape(value)}</text>'
    )


def stroke(path, width=2.6):
    return (
        f'<path d="{path}" fill="none" stroke="{BRICK}" '
        f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


@cache
def source(path):
    with Image.open(path) as image:
        return image.convert("RGBA")


def load_assets(spec, base):
    assets = {}
    for name, entry in spec.items():
        image = source((base / entry["file"]).resolve())
        if "crop" in entry:
            left, top, right, bottom = entry["crop"]
            if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                raise ValueError(f"Crop outside the source image for {name!r}")
            image = image.crop((left, top, right, bottom))
        if image.getchannel("A").getbbox() is None:
            raise ValueError(f"Empty art for {name!r}")
        assets[name] = image
    return assets


def image_markup(uri, box):
    x, y, w, h = box
    return (
        f'<image x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'preserveAspectRatio="none" xlink:href="{uri}"/>'
    )


def fit(image, x, y, w, h, bottom=False):
    scale = min(w / image.width, h / image.height)
    art_width, art_height = image.width * scale, image.height * scale
    return (
        x + (w - art_width) / 2,
        y + (h - art_height) / (1 if bottom else 2),
        art_width,
        art_height,
    )


def branch_curve(end_y, hero_top, hero_bottom):
    if end_y < 560:
        proportion = (end_y - 90) / 470
        x, y = 154 + 99 * proportion, hero_top - 7 + 16 * proportion
        control_y = min(end_y + 110, y - 6)
        curve = f"M {x:.1f} {y:.1f} Q {x + 14:.1f} {control_y:.1f} 328 {end_y:.1f}"
    elif end_y < 885:
        x, y = 268, 655 + (end_y - 655) * 0.48
        curve = f"M {x} {y:.1f} Q 300 {end_y + 5:.1f} 328 {end_y:.1f}"
    else:
        proportion = (end_y - 885) / 390
        x, y = 229 - 69 * proportion, hero_bottom + 51 + 12 * proportion
        curve = f"M {x:.1f} {y:.1f} Q {x + 35:.1f} {end_y - 75:.1f} 328 {end_y:.1f}"
    return stroke(curve, 2.7)


def heading(title, number, y, hero_top, hero_bottom):
    return [
        branch_curve(y - 10, hero_top, hero_bottom),
        f'<ellipse cx="{NUMBER_X}" cy="{y-11:.2f}" rx="15.4" ry="15.9" '
        f'fill="none" stroke="{INK}" stroke-width="2.55"/>',
        lettering(str(number), NUMBER_X, y - 3, 22, "middle", True),
        lettering(title, HEADING_X, y, 35, bold=True),
    ]


def arrow(x1, x2, y):
    center = (x1 + x2) / 2
    return stroke(
        f"M {x1:.2f} {y+3:.2f} Q {center:.2f} {y-8:.2f} {x2:.2f} {y:.2f} "
        f"M {x2-8:.2f} {y-8:.2f} L {x2:.2f} {y:.2f} L {x2-9:.2f} {y+7:.2f}"
    )


def fit_label(label, width):
    for size in range(27, 18, -1):
        if text_width(label, size) <= width:
            return size
    raise ValueError(f"Label is too long for its slot: {label!r}")


def item_row(branch, art, y, height, left):
    items = branch["items"]
    sequence = branch.get("layout") == "sequence"
    if not items:
        raise ValueError(f"No items in branch {branch['title']!r}")
    label_y = y + height - 6
    visual_y = y + (37 if sequence else 2)
    visual_height = label_y - 31 - visual_y
    slot = (CONTENT_RIGHT - left) / len(items)
    output = []
    for index, item in enumerate(items):
        center = left + slot * (index + 0.5)
        scale = item.get("scale", 1.0)
        if not 0 < scale <= 1:
            raise ValueError(f"Scale must be above 0 and at most 1 for {item['asset']!r}")
        asset_width, asset_height = (slot - (34 if sequence else 13)) * scale, visual_height * scale
        art_box = (center - asset_width / 2, visual_y + visual_height - asset_height,
                   asset_width, asset_height)
        output.append(art(item["asset"], art_box, bottom=True)[0])
        label = item["label"]
        output.append(lettering(label, center, label_y, fit_label(label, slot - 10), "middle"))
        if sequence and index < len(items) - 1:
            boundary = left + slot * (index + 1)
            output.append(arrow(boundary - 13, boundary + 13, visual_y + visual_height * 0.59))
    return output


def callout_row(branch, art, y, height, left):
    center = (left + CONTENT_RIGHT) / 2
    width = branch.get("art_width", 212)
    picture, (x, picture_y, w, h) = art(branch["asset"], (center - width / 2, y, width, height))
    output = [picture]
    for label in branch["labels"]:
        ax, ay = label["point"]
        label_y = y + height * label["y"]
        target_x, target_y = x + ax * w, picture_y + ay * h
        side = label["side"]
        if side not in {"left", "right"} or not all(0 <= v <= 1 for v in (ax, ay, label["y"])):
            raise ValueError(f"Invalid position for callout {label['text']!r}")
        label_x = x - 34 if side == "left" else x + w + 34
        start_x = label_x + (9 if side == "left" else -9)
        start_y = label_y - 8
        midpoint = (start_x + target_x) / 2
        output.append(stroke(
            f"M {start_x:.1f} {start_y:.1f} Q {midpoint:.1f} {start_y:.1f} "
            f"{target_x:.1f} {target_y:.1f}", 2.15
        ))
        output.append(lettering(
            label["text"], label_x, label_y, 26, "end" if side == "left" else "start"
        ))
    return output


def render(spec, base):
    assets = load_assets(spec["assets"], base)

    @cache
    def asset_uri(name):
        return f"data:image/png;base64,{encoded(assets[name])}"

    def art(name, box, bottom=False):
        placement = fit(assets[name], *box, bottom=bottom)
        return image_markup(asset_uri(name), placement), placement

    branches = spec["branches"]
    weights = [branch.get("weight", 1) for branch in branches]
    if not 3 <= len(branches) <= 8 or any(weight <= 0 for weight in weights):
        raise ValueError("Use 3–8 branches with positive weights")

    hero, (_, hero_top, _, hero_height) = art(spec["hero"], (31, 537, 238, 299))
    hero_bottom = hero_top + hero_height
    page = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<title>{escape(spec["title"])} | English theme map</title>',
        image_markup(paper(), (0, 0, WIDTH, HEIGHT)),
        hero,
        lettering(spec["title"], 150, hero_bottom + 48, fit_title(spec["title"]), "middle", True),
    ]

    gap = 16
    available = 1353 - gap * (len(branches) - 1)
    y = 32.0
    for number, (branch, weight) in enumerate(zip(branches, weights), 1):
        height = available * weight / sum(weights)
        title, layout = branch["title"], branch.get("layout", "items")
        heading_y = y + (33 if layout == "sequence" else height * 0.43)
        page.extend(heading(title, number, heading_y, hero_top, hero_bottom))
        left = max(486, HEADING_X + text_width(title, 35, True) + 23)
        if layout == "callouts":
            page.extend(callout_row(branch, art, y, height, left))
        elif layout in {"items", "sequence"}:
            if layout == "sequence" and y > 910:
                left = 321
            page.extend(item_row(branch, art, y, height, left))
        else:
            raise ValueError(f"Unknown branch layout {layout!r}")
        y += height + gap
    page.append("</svg>")
    return "\n".join(page) + "\n"


def fit_title(title):
    for size in range(70, 26, -1):
        if text_width(title, size, True) <= 242:
            return size
    raise ValueError("Use a short title that fits under the hero illustration")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--png", type=Path, help="Rasterize the SVG with macOS sips")
    args = parser.parse_args()
    if args.png and not shutil.which("sips"):
        parser.error("--png requires macOS sips; omit it to save an SVG")
    spec = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.svg.write_text(render(spec, args.manifest.parent), encoding="utf-8")
    if args.png:
        subprocess.run(
            ["sips", "-s", "format", "png", str(args.svg), "--out", str(args.png)],
            check=True, capture_output=True, text=True,
        )


if __name__ == "__main__":
    main()
