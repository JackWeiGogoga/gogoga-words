#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Lay out an illustrated theme map and export a self-contained SVG."""

import argparse
import base64
from dataclasses import dataclass
from functools import cache
from html import escape
from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess
from unicodedata import east_asian_width

from PIL import Image, ImageFont


WIDTH, HEIGHT = 1080, 1440
STYLES = {
    "watercolor": ("#2b201c", "#ad6255", ()),
    "flat": ("#263249", "#4276be", ("#4276be", "#20846a", "#ba5b29", "#a55b26", "#397b98", "#a35173", "#496eb5")),
    "diagram": ("#20334a", "#6d8399", ()),
    "engineering": ("#253446", "#245387", ()),
}
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
PAPER_PATH = Path(__file__).resolve().parents[1] / "assets" / "paper-texture.jpg"
NUMBER_X = 354
HEADING_X = 380
CONTENT_RIGHT = 1037
NOTE_STEP = 24
IPA_MODES = ("off", "key", "all")
ACCENTS = ("uk", "us")
NOTE_FONTS = {
    "ipa": ("Arial, DejaVu Sans, sans-serif", "Arial.ttf"),
    "zh": ("PingFang SC, Noto Sans CJK SC, Microsoft YaHei, Arial Unicode MS, sans-serif", "Arial Unicode.ttf"),
}


@dataclass(frozen=True)
class Display:
    zh: bool = False
    zh_headings: bool = False
    ipa: str = "off"
    accent: str = "uk"
    qa: bool = False

    def __post_init__(self):
        if any(type(value) is not bool for value in (self.zh, self.zh_headings, self.qa)):
            raise ValueError("Use true or false for zh, zh_headings, and qa")
        if self.ipa not in IPA_MODES or self.accent not in ACCENTS:
            raise ValueError("Use ipa off/key/all and accent uk/us")

    def notes(self, entry, *, title=False):
        notes = []
        if self.ipa == "all" or (self.ipa == "key" and (title or entry.get("key", False))):
            readings = entry.get("title_ipa" if title else "ipa", {})
            if not isinstance(readings, dict):
                raise ValueError("Provide IPA as an object with uk and/or us readings")
            if reading := readings.get(self.accent):
                notes.append(("ipa", reading))
        if self.zh and (gloss := entry.get("zh_title" if title else "zh")):
            notes.append(("zh", gloss))
        return notes


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


def lettering(value, x, y, size, color, anchor="start", bold=False, kind=None):
    weight = "700" if bold else "400"
    family = ("Chalkboard SE" if bold else "Chalkboard") + ", Comic Sans MS, sans-serif"
    if kind:
        family = NOTE_FONTS[kind][0]
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
        f'fill="{color}">{escape(value)}</text>'
    )


def stroke(path, color, width=2.6):
    return (
        f'<path d="{path}" fill="none" stroke="{color}" '
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


def branch_curve(end_y, hero_top, hero_bottom, accent):
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
    return stroke(curve, accent, 2.7)


def heading(title, zh, number, y, hero_top, hero_bottom, ink, accent, ring):
    output = [
        branch_curve(y - 10, hero_top, hero_bottom, accent),
        f'<ellipse cx="{NUMBER_X}" cy="{y-11:.2f}" rx="15.4" ry="15.9" '
        f'fill="none" stroke="{ring}" stroke-width="2.55"/>',
        lettering(str(number), NUMBER_X, y - 3, 22, ink, "middle", True),
        lettering(title, HEADING_X, y, 35, ink, bold=True),
    ]
    if zh:
        output.append(lettering(zh, HEADING_X, y + NOTE_STEP, 22, ink, kind="zh"))
    return output


def arrow(x1, x2, y, accent):
    center = (x1 + x2) / 2
    return stroke(
        f"M {x1:.2f} {y+3:.2f} Q {center:.2f} {y-8:.2f} {x2:.2f} {y:.2f} "
        f"M {x2-8:.2f} {y-8:.2f} L {x2:.2f} {y:.2f} L {x2-9:.2f} {y+7:.2f}", accent,
    )


@cache
def note_font(size, kind):
    path = FONT_DIR / NOTE_FONTS[kind][1]
    return ImageFont.truetype(str(path), size) if path.is_file() else None


def note_width(value, size, kind):
    if face := note_font(size, kind):
        return face.getlength(value)
    return sum(size if east_asian_width(ch) in "WF" else size * 0.68 for ch in value)


def fit_label(label, width, maximum=27, minimum=19, kind=None):
    for size in range(maximum, minimum - 1, -1):
        measured = note_width(label, size, kind) if kind else text_width(label, size)
        if measured <= width:
            return size
    raise ValueError(f"Label is too long for its slot: {label!r}")


def note_lines(notes, x, y, width, ink, anchor):
    return [
        lettering(value, x, y + index * NOTE_STEP, fit_label(value, width, 22, 16, kind), ink, anchor, kind=kind)
        for index, (kind, value) in enumerate(notes, 1)
    ]


def item_row(branch, art, y, height, left, ink, accent, notes, heading_extra):
    items = branch["items"]
    sequence = branch.get("layout") == "sequence"
    if not items:
        raise ValueError(f"No items in branch {branch['title']!r}")
    label_y = y + height - 6 - NOTE_STEP * max(map(len, notes))
    visual_y = y + (37 + heading_extra if sequence else 2)
    visual_height = label_y - 31 - visual_y
    if visual_height <= 0:
        raise ValueError(f"Not enough room in {branch['title']!r}. Reduce annotations or adjust branch weights.")
    slot = (CONTENT_RIGHT - left) / len(items)
    art_padding = 34 if sequence else 13
    if slot <= art_padding:
        raise ValueError(f"Not enough room in {branch['title']!r}. Shorten the heading or use fewer items.")
    output = []
    for index, item in enumerate(items):
        center = left + slot * (index + 0.5)
        scale = item.get("scale", 1.0)
        if not 0 < scale <= 1:
            raise ValueError(f"Scale must be above 0 and at most 1 for {item['asset']!r}")
        asset_width, asset_height = (slot - art_padding) * scale, visual_height * scale
        art_box = (center - asset_width / 2, visual_y + visual_height - asset_height,
                   asset_width, asset_height)
        output.append(art(item["asset"], art_box, bottom=True)[0])
        label = item["label"]
        output.append(lettering(label, center, label_y, fit_label(label, slot - 10), ink, "middle"))
        output.extend(note_lines(notes[index], center, label_y, slot - 10, ink, "middle"))
        if sequence and index < len(items) - 1:
            boundary = left + slot * (index + 1)
            output.append(arrow(boundary - 13, boundary + 13, visual_y + visual_height * 0.59, accent))
    return output


def callout_baselines(labels, notes, y, height):
    positions = [y + height * label["y"] for label in labels]
    if not any(notes):
        return positions
    for side in ("left", "right"):
        indices = sorted((i for i, label in enumerate(labels) if label["side"] == side), key=positions.__getitem__)
        lower = y + 26
        for i in indices:
            positions[i] = max(positions[i], lower)
            lower = positions[i] + NOTE_STEP * len(notes[i]) + 29
        upper = y + height - 6
        for i in reversed(indices):
            positions[i] = min(positions[i], upper - NOTE_STEP * len(notes[i]))
            upper = positions[i] - 29
        if indices and positions[indices[0]] < y + 25:
            raise ValueError("Not enough room for the callouts. Reduce annotations or increase the branch weight.")
    return positions


def callout_row(branch, art, y, height, left, ink, accent, points, notes):
    center = (left + CONTENT_RIGHT) / 2
    width = branch.get("art_width", 212)
    picture, (x, picture_y, w, h) = art(branch["asset"], (center - width / 2, y, width, height))
    output = [picture]
    positions = callout_baselines(branch["labels"], notes, y, height)
    for label, label_y, details in zip(branch["labels"], positions, notes):
        ax, ay = points.get(label["text"], label["point"])
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
            f"{target_x:.1f} {target_y:.1f}", accent, 2.15
        ))
        anchor = "end" if side == "left" else "start"
        slot = label_x - left + 8 if side == "left" else CONTENT_RIGHT - label_x
        size = fit_label(label["text"], slot, 26) if details else 26
        output.append(lettering(label["text"], label_x, label_y, size, ink, anchor))
        output.extend(note_lines(details, label_x, label_y, slot, ink, anchor))
    return output


def branch_annotations(branch, display):
    zh = branch.get("zh_title") if display.zh_headings else None
    layout = branch.get("layout", "items")
    if layout == "callouts":
        labels = branch["labels"]
        notes = [display.notes(label) for label in labels]
        depth = max(sum(len(note) for label, note in zip(labels, notes) if label["side"] == side)
                    for side in ("left", "right"))
    else:
        notes = [display.notes(item) for item in branch["items"]]
        depth = max(map(len, notes), default=0) + bool(zh and layout == "sequence")
    return zh, notes, NOTE_STEP * depth


def speaking_footer(spec, display, ink, accent):
    if not display.qa:
        return [], HEIGHT - 55
    speaking = spec.get("speaking", {})
    entries = [(speaking.get(key), speaking.get(f"zh_{key}") if display.zh else None)
               for key in ("question", "answer")]
    if any(not isinstance(line, str) or not line.strip() for line, _ in entries):
        raise ValueError("Provide speaking.question and speaking.answer to show a Q&A")
    height = 100 if any(zh for _, zh in entries) else 76
    y = HEIGHT - height - 32
    output = [
        f'<rect x="32" y="{y}" width="1016" height="{height}" rx="17" fill="#ffffff" '
        f'stroke="{accent}" stroke-width="1.5"/>',
        stroke(f"M 540 {y + 15} V {y + height - 15}", accent, 1.0),
    ]
    for (english, zh), x, caption in zip(entries, (53, 562), ("ASK", "SAY")):
        output.append(lettering(caption, x, y + 24, 16, accent, bold=True))
        output.append(lettering(english, x, y + 51, fit_label(english, 463, 25), ink))
        if zh:
            output.extend(note_lines([("zh", zh)], x, y + 51, 463, ink, "start"))
    return output, y - 24


def render(spec, base, style=None, display_overrides=None):
    style = style if style is not None else spec.get("style", "watercolor")
    if style not in STYLES:
        raise ValueError(f"Use one of these mind map styles: {', '.join(STYLES)}")
    ink, accent, branch_colors = STYLES[style]
    display = Display(**(spec.get("display", {}) | (display_overrides or {})))
    footer, map_bottom = speaking_footer(spec, display, ink, accent)
    asset_specs = spec["assets"] | spec.get("style_assets", {}).get(style, {})
    assets = load_assets(asset_specs, base)

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
    title_notes = display.notes(spec, title=True)
    annotations = [branch_annotations(branch, display) for branch in branches]
    background = (image_markup(paper(), (0, 0, WIDTH, HEIGHT)) if style == "watercolor" else
                  f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>')
    page = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<title>{escape(spec["title"])} | English theme map</title>',
        background,
        hero,
        lettering(spec["title"], 150, hero_bottom + 48, fit_title(spec["title"]), ink, "middle", True),
    ]
    page.extend(note_lines(title_notes, 150, hero_bottom + 48, 226, ink, "middle"))
    if any(kind == "ipa" for kind, _ in title_notes) or any(
        kind == "ipa" for _, rows, _ in annotations for notes in rows for kind, _ in notes
    ):
        page.append(lettering(f"IPA · {display.accent.upper()}", 33, 58, 19, ink, kind="ipa"))

    gap = 16
    available = map_bottom - 32 - gap * (len(branches) - 1) - sum(reserve for _, _, reserve in annotations)
    if available <= 0:
        raise ValueError("Not enough room on one page. Reduce the number of annotations or branches.")
    y = 32.0
    for number, (branch, weight, (zh, notes, reserve)) in enumerate(zip(branches, weights, annotations), 1):
        height = available * weight / sum(weights) + reserve
        title, layout = branch["title"], branch.get("layout", "items")
        heading_y = y + (33 if layout == "sequence" else height * 0.43)
        branch_accent = branch_colors[(number - 1) % len(branch_colors)] if branch_colors else accent
        ring = ink if style == "watercolor" else branch_accent
        page.extend(heading(title, zh, number, heading_y, hero_top, hero_bottom + NOTE_STEP * len(title_notes),
                            ink, branch_accent, ring))
        heading_width = max(text_width(title, 35, True), note_width(zh, 22, "zh") if zh else 0)
        left = max(486, HEADING_X + heading_width + 23)
        if layout == "callouts":
            points = asset_specs[branch["asset"]].get("callout_points", {})
            page.extend(callout_row(branch, art, y, height, left, ink, accent, points, notes))
        elif layout in {"items", "sequence"}:
            if layout == "sequence" and y > 910:
                left = 321
            page.extend(item_row(branch, art, y, height, left, ink, accent, notes, NOTE_STEP if zh else 0))
        else:
            raise ValueError(f"Unknown branch layout {layout!r}")
        y += height + gap
    page.extend(footer)
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
    parser.add_argument("--style", choices=STYLES, help="Override the style specified by the manifest")
    parser.add_argument("--zh", action=argparse.BooleanOptionalAction, help="Show Chinese glosses")
    parser.add_argument("--zh-headings", action=argparse.BooleanOptionalAction, help="Show Chinese branch headings")
    parser.add_argument("--ipa", nargs="?", const="key", choices=IPA_MODES, help="Show IPA for key words or all supplied readings")
    parser.add_argument("--accent", choices=ACCENTS, help="Select the IPA accent")
    parser.add_argument("--qa", action=argparse.BooleanOptionalAction, help="Show the speaking question and answer")
    parser.add_argument("--png", type=Path, help="Rasterize the SVG with macOS sips")
    args = parser.parse_args()
    if args.png and not shutil.which("sips"):
        parser.error("--png requires macOS sips; omit it to save an SVG")
    spec = json.loads(args.manifest.read_text(encoding="utf-8"))
    overrides = {key: getattr(args, key) for key in ("zh", "zh_headings", "ipa", "accent", "qa")
                 if getattr(args, key) is not None}
    try:
        content = render(spec, args.manifest.parent, args.style, overrides)
    except (ValueError, TypeError) as error:
        parser.error(str(error))
    args.svg.write_text(content, encoding="utf-8")
    if args.png:
        subprocess.run(
            ["sips", "-s", "format", "png", str(args.svg), "--out", str(args.png)],
            check=True, capture_output=True, text=True,
        )


if __name__ == "__main__":
    main()
