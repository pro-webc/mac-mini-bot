#!/usr/bin/env python3
"""One-off: emit base64 PNG for website placeholder (no text)."""
import base64
import io
import math

from PIL import Image, ImageDraw

W, H = 768, 432
img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):
    for x in range(W):
        cx, cy = (x + 0.5) / W, (y + 0.5) / H
        vignette = 0.92 + 0.08 * math.sin(cx * math.pi) * math.sin(cy * math.pi)
        base_r = 236 + int(8 * math.sin(cx * 2.1))
        base_g = 240 + int(6 * math.cos(cy * 1.7))
        base_b = 248 + int(4 * math.sin((cx + cy) * 1.3))
        r = int(max(0, min(255, base_r * vignette)))
        g = int(max(0, min(255, base_g * vignette)))
        b = int(max(0, min(255, base_b * vignette)))
        px[x, y] = (r, g, b)

draw = ImageDraw.Draw(img)
margin_x, margin_y = int(W * 0.12), int(H * 0.14)
draw.rectangle(
    [margin_x, margin_y, W - margin_x - 1, H - margin_y - 1],
    outline=(198, 208, 224),
    width=2,
)

buf = io.BytesIO()
img.save(buf, format="PNG", compress_level=6)
print(base64.b64encode(buf.getvalue()).decode("ascii"))
