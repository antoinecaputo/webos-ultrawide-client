#!/usr/bin/env python3
"""Generate the original Ultrawide Client artwork (requires Pillow)."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "frontend" / "assets"
PALETTE = ["#3b63d6", "#9b55c6", "#f648ac", "#eb6a7c", "#e28f48"]
INK = "#10122d"
FONT = next(str(path) for path in (
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
) if path.exists())
FONT_REGULAR = next(str(path) for path in (
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
) if path.exists())


def rgb(value):
    return tuple(bytes.fromhex(value.lstrip("#")))


def mix(a, b, t):
    return tuple(round(x * (1 - t) + y * t) for x, y in zip(a, b))


def gradient(size, stops, horizontal=True):
    width, height = size
    length = width if horizontal else height
    strip = Image.new("RGB", (length, 1))
    pixels = strip.load()
    for i in range(length):
        position = i / max(1, length - 1) * (len(stops) - 1)
        section = min(int(position), len(stops) - 2)
        pixels[i, 0] = mix(rgb(stops[section]), rgb(stops[section + 1]), position - section)
    return strip.resize(size) if horizontal else strip.transpose(Image.Transpose.ROTATE_90).resize(size)


def text_center(draw, box, label, font, color):
    left, top, right, bottom = box
    bounds = draw.textbbox((0, 0), label, font=font)
    x = (left + right - bounds[2] + bounds[0]) / 2
    y = (top + bottom - bounds[3] - bounds[1]) / 2
    draw.text((x, y), label, font=font, fill=color)


def emblem(size=400, transparent=False):
    scale = size / 400
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    def box(*coords):
        return tuple(round(v * scale) for v in coords)
    if not transparent:
        base = gradient((size, size), ["#171945", "#251b50", "#3b2256"], horizontal=False).convert("RGBA")
        mask = Image.new("L", (size, size))
        ImageDraw.Draw(mask).rounded_rectangle(box(0, 0, 399, 399), radius=round(72 * scale), fill=255)
        canvas.paste(base, (0, 0), mask)
        draw = ImageDraw.Draw(canvas)
        draw.ellipse(box(275, 38, 460, 223), fill="#9b55c6")
        draw.ellipse(box(302, 55, 447, 200), fill="#f648ac")
        draw.ellipse(box(321, 73, 432, 184), fill="#e28f48")
    # Wide screen silhouette: the 2.35:1 frame is the product mark.
    frame_box = box(28, 120, 372, 280)
    glow = Image.new("RGBA", (size, size))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(frame_box, radius=round(30 * scale), outline=(246, 72, 172, 235), width=max(1, round(19 * scale)))
    glow = glow.filter(ImageFilter.GaussianBlur(max(1, round(25 * scale))))
    canvas = Image.alpha_composite(canvas, glow)
    draw = ImageDraw.Draw(canvas)
    frame_mask = Image.new("L", (size, size))
    ImageDraw.Draw(frame_mask).rounded_rectangle(frame_box, radius=round(30 * scale), fill=255)
    colorful = gradient((size, size), PALETTE).convert("RGBA")
    canvas.paste(colorful, (0, 0), frame_mask)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(box(40, 132, 360, 268), radius=round(20 * scale), fill=INK)
    draw.rounded_rectangle(box(31, 123, 369, 277), radius=round(27 * scale), outline=(255, 222, 245, 190), width=max(1, round(3 * scale)))
    font = ImageFont.truetype(FONT, round(92 * scale))
    text_center(draw, box(40, 135, 360, 265), "21:9", font, "#fff5fa")
    return canvas


def backdrop(size):
    width, height = size
    image = gradient(size, ["#141a4e", "#29225a", "#48265d", "#67375d"]).convert("RGBA")
    glow = Image.new("RGBA", size)
    g = ImageDraw.Draw(glow)
    radius = round(height * 0.55)
    cx, cy = round(width * 0.86), round(height * 0.85)
    g.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(246, 72, 172, 125))
    image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(round(height * 0.11))))
    draw = ImageDraw.Draw(image)
    draw.ellipse((cx-radius//2, cy-radius//2, cx+radius//2, cy+radius//2), fill="#e28f48")
    draw.ellipse((cx-radius//2, cy-radius//2 + round(height * 0.1), cx+radius//2, cy+radius//2 + round(height * 0.1)), fill="#eb6a7c")
    # The small layered arcs echo the wide display without copying game imagery.
    for i, color in enumerate(PALETTE):
        y = round(height * (0.76 + i * 0.038))
        draw.line((0, y, width, y - round(height * 0.14)), fill=color, width=max(2, round(height * 0.012)))
    return image


def wordmark(size, icon_size, title_size, subtitle_size):
    width, height = size
    image = backdrop(size)
    icon = emblem(icon_size)
    x = round(width * 0.07)
    y = (height - icon_size) // 2
    image.alpha_composite(icon, (x, y))
    draw = ImageDraw.Draw(image)
    label_x = x + icon_size + round(width * 0.045)
    title_y = round(height * 0.39)
    draw.text((label_x, title_y), "ULTRAWIDE", font=ImageFont.truetype(FONT, title_size), fill="#fff6fc", stroke_width=1)
    draw.text((label_x + 4, title_y + title_size * 1.25), "CLIENT FOR webOS", font=ImageFont.truetype(FONT_REGULAR, subtitle_size), fill="#ffd6ea")
    return image.convert("RGB")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for size in (80, 130):
        emblem(400).resize((size, size), Image.Resampling.LANCZOS).save(ASSETS / f"icon-{size}.png")
        emblem(400, transparent=True).resize((size, size), Image.Resampling.LANCZOS).save(ASSETS / f"icon-transparent{size}.png")
    emblem().save(ROOT / "frontend" / "submission-icon.png")
    wordmark((1920, 640), 380, 116, 44).save(ASSETS / "banner-dark.png")
    wordmark((1920, 1080), 500, 130, 53).save(ASSETS / "splash.png")


if __name__ == "__main__":
    main()
