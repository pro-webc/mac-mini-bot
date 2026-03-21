#!/usr/bin/env python3
"""768x432 studio-style gradient + thin lightbox frame; prints PNG as one-line base64."""
from __future__ import annotations

import base64
import io
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow required: pip install Pillow", file=sys.stderr)
    sys.exit(1)

W, H = 768, 432


def main() -> None:
    # Soft cool studio: slate → blue-gray → subtle teal (top-left to bottom-right)
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        ty = y / max(H - 1, 1)
        for x in range(W):
            tx = x / max(W - 1, 1)
            t = (tx * 0.55 + ty * 0.45)
            # Cool tones
            r = int(32 + (72 - 32) * t + 8 * (1 - ty))
            g = int(42 + (88 - 42) * t + 12 * tx)
            b = int(58 + (118 - 58) * t + 18 * (1 - tx))
            px[x, y] = (min(255, r), min(255, g), min(255, b))

    draw = ImageDraw.Draw(img)
    margin = 28
    # Thin lightbox-style frame (single stroke, no corners labels)
    box = [margin, margin, W - 1 - margin, H - 1 - margin]
    # Slightly brighter border on dark-cool bg
    draw.rectangle(box, outline=(220, 228, 238), width=1)

    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=6)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    sys.stdout.write(b64)


if __name__ == "__main__":
    main()
