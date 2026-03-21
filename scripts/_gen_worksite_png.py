#!/usr/bin/env python3
"""One-off: generate cool-toned worksite illustration PNG, emit base64 to stdout."""
from __future__ import annotations

import base64
import io
import math
import sys

from PIL import Image, ImageDraw, ImageEnhance


def main() -> int:
    w, h = 768, 432
    img = Image.new("RGB", (w, h), (28, 38, 48))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(28 + (42 - 28) * t)
        g = int(38 + (52 - 38) * t)
        b = int(48 + (62 - 48) * t)
        for x in range(w):
            px[x, y] = (r, g, b)

    d = ImageDraw.Draw(img)
    for y in range(h):
        for x in range(w):
            cx, cy = w / 2, h / 2
            dist = math.hypot(x - cx, y - cy) / (math.hypot(w / 2, h / 2) + 1e-6)
            v = min(1.0, dist * 0.35)
            r, g_, b = px[x, y]
            r = max(0, int(r * (1 - v * 0.25)))
            g_ = max(0, int(g_ * (1 - v * 0.25)))
            b = max(0, int(b * (1 - v * 0.2)))
            px[x, y] = (r, g_, b)

    floor = [(0, int(h * 0.72)), (w, int(h * 0.68)), (w, h), (0, h)]
    d.polygon(floor, fill=(22, 30, 38))

    rack_x = 80
    for i in range(5):
        x0 = rack_x + i * 22
        d.rectangle([x0, 120, x0 + 8, 280], fill=(45, 55, 65))
    d.rectangle([rack_x - 15, 115, rack_x + 120, 125], fill=(55, 62, 72))
    d.rectangle([rack_x - 15, 265, rack_x + 120, 275], fill=(55, 62, 72))
    for j in range(4):
        hx = rack_x + 18 + j * 28
        d.ellipse([hx, 135, hx + 18, 153], fill=(210, 215, 220))
        d.arc([hx, 135, hx + 18, 153], 200, 340, fill=(90, 98, 108), width=2)

    vest_hi = (200, 175, 55)
    vest_mid = (175, 155, 48)
    helmet = (235, 238, 242)

    def draw_worker(cx: float, cy: float, scale: float, facing_right: bool, arm_up: bool) -> None:
        s = scale
        d.rectangle([cx - 8 * s, cy + 15 * s, cx - 2 * s, cy + 55 * s], fill=(38, 44, 52))
        d.rectangle([cx + 2 * s, cy + 15 * s, cx + 8 * s, cy + 55 * s], fill=(38, 44, 52))
        d.rounded_rectangle(
            [cx - 14 * s, cy - 5 * s, cx + 14 * s, cy + 18 * s],
            radius=4,
            fill=vest_hi,
            outline=(120, 105, 40),
            width=1,
        )
        d.rectangle([cx - 10 * s, cy + 2 * s, cx + 10 * s, cy + 14 * s], fill=vest_mid)
        d.rectangle([cx - 12 * s, cy + 4 * s, cx + 12 * s, cy + 6 * s], fill=(240, 245, 250))
        d.rectangle([cx - 12 * s, cy + 10 * s, cx + 12 * s, cy + 12 * s], fill=(240, 245, 250))
        d.ellipse([cx - 10 * s, cy - 28 * s, cx + 10 * s, cy - 8 * s], fill=(180, 155, 130))
        d.pieslice([cx - 12 * s, cy - 30 * s, cx + 12 * s, cy - 6 * s], 180, 360, fill=helmet)
        lw = max(1, int(4 * s))
        if arm_up:
            if facing_right:
                d.line([(cx + 12 * s, cy), (cx + 38 * s, cy - 22 * s)], fill=(180, 155, 130), width=lw)
                d.line([(cx + 38 * s, cy - 22 * s), (cx + 48 * s, cy - 18 * s)], fill=(180, 155, 130), width=lw)
                d.line([(cx - 12 * s, cy + 2 * s), (cx - 22 * s, cy + 18 * s)], fill=(180, 155, 130), width=lw)
            else:
                d.line([(cx - 12 * s, cy), (cx - 38 * s, cy - 22 * s)], fill=(180, 155, 130), width=lw)
        else:
            d.line([(cx - 12 * s, cy + 2 * s), (cx - 24 * s, cy + 20 * s)], fill=(180, 155, 130), width=lw)
            d.line([(cx + 12 * s, cy + 2 * s), (cx + 24 * s, cy + 20 * s)], fill=(180, 155, 130), width=lw)

    draw_worker(320, 240, 1.0, True, True)
    draw_worker(430, 248, 0.92, False, False)
    draw_worker(520, 242, 0.95, True, False)

    d.rounded_rectangle([535, 255, 565, 285], radius=3, fill=(52, 58, 68), outline=(80, 88, 98), width=1)
    d.line([(540, 262), (558, 262)], fill=(75, 82, 92), width=1)
    d.line([(540, 268), (552, 268)], fill=(75, 82, 92), width=1)

    d.rectangle([620, 200, 630, 310], fill=(200, 60, 55))
    d.rectangle([640, 200, 650, 310], fill=(200, 60, 55))
    for yy in range(205, 300, 14):
        d.line([(625, yy), (645, yy + 8)], fill=(230, 230, 235), width=3)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([w - 280, -80, w + 40, 200], fill=(120, 145, 175, 35))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    img = ImageEnhance.Color(img).enhance(0.78)
    img = ImageEnhance.Brightness(img).enhance(0.97)

    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=6)
    sys.stdout.write(base64.b64encode(buf.getvalue()).decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
