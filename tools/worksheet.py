"""Shared drawing and export helpers bundled with each worksheet skill."""

import argparse
import base64
from functools import cache
from html import escape
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
from unicodedata import east_asian_width

from PIL import Image, ImageFont, ImageOps


INK = "#322722"
MUTED = "#66574e"
ACCENT = "#925748"
PAPER = "#fffdfa"
LINE = "#ded4c9"
A4 = (1240, 1754)
ACTIVITY_MARGIN = 64
FONTS = {
    "display": ("Chalkboard SE, Comic Sans MS, sans-serif", "ChalkboardSE.ttc", 2),
    "en": ("Arial, sans-serif", "Arial.ttf", 0),
    "strong": ("Arial, sans-serif", "Arial Bold.ttf", 0),
    "zh": ("PingFang SC, Noto Sans CJK SC, Microsoft YaHei, Arial Unicode MS, sans-serif", "Arial Unicode.ttf", 0),
}


@cache
def font(size, style):
    _, name, index = FONTS[style]
    path = Path("/System/Library/Fonts/Supplemental") / name
    if path.is_file():
        return ImageFont.truetype(str(path), size, index=index)
    return None if style == "zh" else ImageFont.load_default(size=size)


def measure(value, size, style):
    face = font(size, style)
    if face is not None:
        return face.getlength(value)
    return sum(size if east_asian_width(ch) in "WF" else size * 0.65 for ch in value)


def wrap(value, width, size, style):
    tokens = list(value) if style == "zh" else re.findall(r"\S+\s*", value)
    lines, current = [], ""
    for token in tokens:
        if measure(token.rstrip(), size, style) > width:
            raise ValueError(f"Text cannot fit the available width: {token.strip()!r}")
        if current and measure((current + token).rstrip(), size, style) > width:
            lines.append(current.rstrip())
            current = token.lstrip()
        else:
            current += token
    if current.strip():
        lines.append(current.rstrip())
    return lines


@cache
def source(path):
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGBA")


class Assets:
    def __init__(self, entries, use_line_art=False):
        self.entries = entries
        self.use_line_art = use_line_art

    def line_art(self):
        return Assets(self.entries, use_line_art=True)

    @cache
    def image(self, key):
        if key not in self.entries:
            raise ValueError(f"Unknown illustration: {key!r}")
        directory, entry = self.entries[key]
        if self.use_line_art:
            if "line_art" not in entry:
                raise ValueError(f"Missing line_art artwork for {key!r}")
            entry = entry["line_art"]
        image = source((directory / entry["file"]).resolve())
        if "crop" in entry:
            x1, y1, x2, y2 = entry["crop"]
            if not all(type(v) is int for v in (x1, y1, x2, y2)) or not (
                0 <= x1 < x2 <= image.width and 0 <= y1 < y2 <= image.height
            ):
                raise ValueError(f"Invalid crop for illustration {key!r}")
            image = image.crop((x1, y1, x2, y2))
        alpha = image.getchannel("A")
        if alpha.getbbox() is None:
            raise ValueError(f"Empty illustration: {key!r}")
        if self.use_line_art:
            image = ImageOps.grayscale(image)
            image.putalpha(alpha)
        data = BytesIO()
        image.save(data, "PNG")
        uri = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode("ascii")
        return image.size, uri


def load_document(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    entries = {}
    if "assets_from" in document:
        parent = (path.parent / document["assets_from"]).resolve()
        original = json.loads(parent.read_text(encoding="utf-8"))
        entries.update({key: (parent.parent, art) for key, art in original["assets"].items()})
    entries.update({key: (path.parent, art) for key, art in document.get("assets", {}).items()})
    return document, Assets(entries)


class Page:
    def __init__(self, width, height, title, background=PAPER):
        self.width, self.height = width, height
        self.markup = [
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f"<title>{escape(title)}</title>",
        ]
        self.rect(0, 0, width, height, background)

    def rect(self, x, y, w, h, fill, stroke="none", radius=0, dash=None):
        dashes = f' stroke-dasharray="{dash}"' if dash else ""
        self.markup.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dashes}/>'
        )

    def line(self, x1, y1, x2, y2, color=LINE, width=1.6, dash=None):
        dashes = f' stroke-dasharray="{dash}"' if dash else ""
        self.markup.append(
            f'<path d="M {x1:.2f} {y1:.2f} L {x2:.2f} {y2:.2f}" '
            f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{dashes}/>'
        )

    def text(self, value, x, y, size, style="en", color=INK, anchor="start", max_width=None):
        if max_width is not None:
            minimum = max(18, round(size * 0.72))
            while size > minimum and measure(value, size, style) > max_width:
                size -= 1
            if measure(value, size, style) > max_width:
                raise ValueError(f"Label is too long for its slot: {value!r}")
        weight = 700 if style in {"display", "strong"} else 400
        self.markup.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONTS[style][0]}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">'
            f"{escape(value)}</text>"
        )

    def art(self, assets, key, x, y, width, height):
        (src_w, src_h), uri = assets.image(key)
        scale = min(width / src_w, height / src_h)
        w, h = src_w * scale, src_h * scale
        left, top = x + (width - w) / 2, y + (height - h) / 2
        self.markup.append(
            f'<image x="{left:.2f}" y="{top:.2f}" '
            f'width="{w:.2f}" height="{h:.2f}" xlink:href="{uri}"/>'
        )
        return left, top, w, h

    def svg(self):
        return "\n".join((*self.markup, "</svg>", ""))


def activity_page(spec, label, accent=ACCENT):
    width, height = A4
    margin = ACTIVITY_MARGIN
    page = Page(width, height, f'{spec["title"]} | {label}', "#ffffff")
    page.text(label, width - margin, 72, 26, "strong", accent, "end", max_width=310)
    page.text(spec["title"], margin, 90, 62, "display", max_width=width - 2 * margin - 334)
    page.text(spec["zh_title"], margin, 137, 30, "zh", MUTED, max_width=width - 2 * margin)
    page.line(margin, 159, width - margin, 159, accent, 2)
    return page


def batches(items, count):
    return [items[index:index + count] for index in range(0, len(items), count)]


def argument_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--png", type=Path, help="Export PNG with macOS sips")
    return parser


def render_cli(parser, args, render):
    if args.png and not shutil.which("sips"):
        parser.error("PNG export requires macOS sips. Omit --png to save SVG.")
    try:
        document, assets = load_document(args.manifest.resolve())
        pages = render(document, assets)
        export(pages, args.svg, args.png)
    except (KeyError, ValueError, OSError, TypeError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


def export(pages, svg, png):
    if svg.suffix.lower() != ".svg" or (png and png.suffix.lower() != ".png"):
        raise ValueError("Use .svg for the SVG output and .png for the PNG output")

    def numbered(path, number):
        if len(pages) == 1:
            return path
        return path.with_name(f"{path.stem}-{number:02}{path.suffix}")

    with TemporaryDirectory(prefix="gogoga-worksheet-") as temporary:
        staged = []
        for index, page in enumerate(pages, 1):
            temp_svg = Path(temporary) / f"{index}.svg"
            temp_svg.write_text(page.svg(), encoding="utf-8")
            staged.append((temp_svg, numbered(svg, index)))
            if png:
                temp_png = temp_svg.with_suffix(".png")
                subprocess.run(
                    ["sips", "-s", "format", "png", str(temp_svg), "--out", str(temp_png)],
                    check=True, capture_output=True, text=True,
                )
                staged.append((temp_png, numbered(png, index)))
        for source_file, destination in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, destination)
