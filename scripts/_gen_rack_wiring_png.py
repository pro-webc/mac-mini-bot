#!/usr/bin/env python3
"""Generate rack/cable-management illustration PNG; print single-line base64."""
from __future__ import annotations

import base64
import io
import math

from PIL import Image, ImageDraw

W, H = 768, 432


def main() -> None:
    img = Image.new("RGB", (W, H), (242, 243, 246))
    d = ImageDraw.Draw(img)

    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(236 + t * 14)
        g = int(238 + t * 10)
        b = int(241 + t * 8)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    d.rectangle([0, int(H * 0.74), W, H], fill=(226, 228, 232))

    rx0, rx1 = int(W * 0.20), int(W * 0.40)
    ry0, ry1 = int(H * 0.14), int(H * 0.70)
    d.rounded_rectangle([rx0, ry0, rx1, ry1], radius=6, fill=(48, 54, 60), outline=(34, 38, 44), width=2)

    nu = 9
    for i in range(1, nu):
        yy = ry0 + (ry1 - ry0) * i / nu
        d.line([(rx0 + 4, int(yy)), (rx1 - 4, int(yy))], fill=(64, 70, 76), width=1)

    for row in range(3):
        uy0 = ry0 + (ry1 - ry0) * (0.12 + row * 0.24)
        uy1 = uy0 + (ry1 - ry0) * 0.12
        d.rounded_rectangle([rx0 + 10, int(uy0), rx1 - 10, int(uy1)], radius=3, fill=(72, 78, 86), outline=(58, 64, 70))

    cx0, cx1 = int(W * 0.42), int(W * 0.48)
    cy0, cy1 = int(H * 0.16), int(H * 0.68)
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=4, fill=(208, 212, 218), outline=(188, 192, 198))

    colors = [(178, 92, 68), (92, 128, 172), (108, 148, 112), (158, 136, 82), (136, 108, 158)]
    for k in range(13):
        x = cx0 + 8 + k * ((cx1 - cx0 - 16) / 12)
        c = colors[k % len(colors)]
        for j in range(30):
            t = j / 29
            yy = cy0 + 10 + t * (cy1 - cy0 - 20)
            wobble = 2.2 * math.sin(t * math.pi * 2 + k * 0.45)
            if j > 0:
                yy0 = cy0 + 10 + (j - 1) / 29 * (cy1 - cy0 - 20)
                x0 = x + 2.2 * math.sin((j - 1) / 29 * math.pi * 2 + k * 0.45)
                x1 = x + wobble
                d.line([(x0, yy0), (x1, yy)], fill=c, width=3)

    tx0, tx1 = int(W * 0.50), int(W * 0.90)
    ty0, ty1 = int(H * 0.40), int(H * 0.48)
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=4, fill=(198, 202, 208), outline=(172, 178, 186))
    for i in range(20):
        xx = tx0 + 14 + i * ((tx1 - tx0 - 28) / 19)
        cc = colors[i % len(colors)]
        d.line([(xx, ty0 + 7), (xx + 2, ty1 - 7)], fill=cc, width=2)

    wx0, wx1 = int(W * 0.08), int(W * 0.15)
    wy0, wy1 = int(H * 0.24), int(H * 0.52)
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=3, fill=(232, 233, 236), outline=(198, 202, 208))
    for gx in range(3):
        for gy in range(5):
            jx = wx0 + 9 + gx * 16
            jy = wy0 + 11 + gy * 13
            d.rectangle([jx, jy, jx + 9, jy + 7], fill=(84, 90, 98))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse(
        [W // 2 - 100, int(H * 0.05) - 40, W // 2 + 100, int(H * 0.05) + 40],
        fill=(255, 255, 255, 35),
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=6)
    print(base64.b64encode(buf.getvalue()).decode("ascii"), end="")


if __name__ == "__main__":
    main()
