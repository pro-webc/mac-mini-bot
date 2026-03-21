#!/usr/bin/env python3
"""Generate infra illustration PNG; print single-line base64 to stdout."""
from __future__ import annotations

import base64
import math
import struct
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 1024, 576
OUT = Path("/tmp/infra_site.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def draw_gradient_sky(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    """Soft dawn: deep navy top -> warm steel/peach horizon."""
    for y in range(h):
        t = y / max(h - 1, 1)
        # top: navy-ish, bottom: warm gray-peach
        r = int(lerp(18, 168, t**0.85))
        g = int(lerp(28, 142, t**0.9))
        b = int(lerp(52, 128, t**0.88))
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def draw_sun_glow(img: Image.Image, cx: int, cy: int) -> None:
    px = img.load()
    r_max = 220
    for y in range(max(0, cy - r_max), min(H, cy + r_max)):
        for x in range(max(0, cx - r_max), min(W, cx + r_max)):
            d = math.hypot(x - cx, y - cy)
            if d > r_max:
                continue
            a = (1.0 - d / r_max) ** 2.2 * 0.42
            pr, pg, pb = px[x, y]
            nr = min(255, int(pr + 55 * a))
            ng = min(255, int(pg + 40 * a))
            nb = min(255, int(pb + 25 * a))
            px[x, y] = (nr, ng, nb)


def draw_lattice_tower(draw: ImageDraw.ImageDraw) -> None:
    """Generic triangular lattice silhouette (no brand marks)."""
    steel = (45, 58, 72)
    dark = (28, 36, 48)
    bx, by = 620, H - 8
    bw, bh = 140, 380
    # Outer frame
    draw.polygon(
        [(bx, by), (bx + bw // 2, by - bh), (bx + bw, by)],
        outline=steel,
        width=3,
    )
    # Cross-bracing (abstract lattice)
    levels = 14
    for i in range(levels):
        ty = by - int(bh * (i + 0.5) / levels)
        lx = bx + int((bw // 2) * (i + 0.5) / levels * 0.15)
        rx = bx + bw - int((bw // 2) * (i + 0.5) / levels * 0.15)
        draw.line([(lx, ty), (rx, ty)], fill=dark, width=2)
        if i % 2 == 0:
            draw.line([(bx, by - int(bh * i / levels)), (bx + bw, by - int(bh * (i + 1) / levels))], fill=steel, width=1)
        else:
            draw.line([(bx + bw, by - int(bh * i / levels)), (bx, by - int(bh * (i + 1) / levels))], fill=steel, width=1)
    # Equipment block (antenna cabinet) — abstract rectangle
    cab_y = by - bh + 40
    draw.rectangle([bx + bw // 2 - 22, cab_y - 35, bx + bw // 2 + 22, cab_y], fill=(38, 48, 62), outline=steel, width=2)


def draw_etc_gantry(draw: ImageDraw.ImageDraw) -> None:
    """Highway gantry silhouette — horizontal beam, posts, abstract sensor pods."""
    navy = (32, 42, 58)
    steel = (72, 82, 96)
    y_beam = int(H * 0.38)
    x0, x1 = 80, 420
    draw.rectangle([x0, y_beam, x1, y_beam + 14], fill=steel, outline=navy, width=2)
    # Posts
    for px in (x0 + 25, x1 - 25):
        draw.rectangle([px - 10, y_beam + 14, px + 10, H - 4], fill=navy, outline=steel, width=1)
    # Small rounded pods (no text)
    for ox in (140, 220, 300):
        draw.ellipse([ox - 12, y_beam - 18, ox + 12, y_beam - 2], fill=(55, 65, 78), outline=steel, width=1)


def draw_ground(draw: ImageDraw.ImageDraw) -> None:
    """Foreground field / shoulder."""
    top = H - 120
    for y in range(top, H):
        t = (y - top) / max(H - top - 1, 1)
        r = int(lerp(42, 22, t))
        g = int(lerp(58, 35, t))
        b = int(lerp(48, 32, t))
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def draw_workers_from_behind(draw: ImageDraw.ImageDraw) -> None:
    """Three figures from behind: helmets, high-vis vests (orange), dark pants."""
    base_y = H - 28
    positions = [(480, 1.0), (540, 0.95), (600, 1.02)]
    for cx, scale in positions:
        s = 26 * scale
        # Legs
        leg = (22, 26, 38)
        draw.rectangle([cx - s * 0.35, base_y - s * 0.9, cx - s * 0.08, base_y], fill=leg)
        draw.rectangle([cx + s * 0.08, base_y - s * 0.9, cx + s * 0.35, base_y], fill=leg)
        # Torso — high-vis orange (muted)
        vest = (196, 98, 42)
        vest_dark = (142, 68, 28)
        draw.rounded_rectangle(
            [cx - s * 0.42, base_y - s * 1.65, cx + s * 0.42, base_y - s * 0.88],
            radius=int(s * 0.12),
            fill=vest,
            outline=vest_dark,
            width=2,
        )
        # Reflective stripe (abstract band, not text)
        draw.rectangle([cx - s * 0.38, base_y - s * 1.28, cx + s * 0.38, base_y - s * 1.12], fill=(210, 200, 175))
        # Arms (slightly out — working stance)
        arm = (38, 48, 62)
        draw.ellipse([cx - s * 0.78, base_y - s * 1.55, cx - s * 0.42, base_y - s * 1.05], fill=arm)
        draw.ellipse([cx + s * 0.42, base_y - s * 1.55, cx + s * 0.78, base_y - s * 1.05], fill=arm)
        # Helmet from behind (round dome)
        helm = (48, 52, 58)
        draw.ellipse([cx - s * 0.38, base_y - s * 2.05, cx + s * 0.38, base_y - s * 1.52], fill=helm, outline=(28, 32, 40), width=2)


def draw_distant_hills(draw: ImageDraw.ImageDraw) -> None:
    hill = (30, 38, 50)
    draw.polygon(
        [(0, H - 140), (200, H - 200), (420, H - 155), (W, H - 175), (W, H - 120), (0, H - 120)],
        fill=hill,
    )


def main() -> None:
    img = Image.new("RGB", (W, H), (20, 30, 50))
    draw = ImageDraw.Draw(img)
    draw_gradient_sky(draw, W, H)
    draw_sun_glow(img, W - 180, int(H * 0.42))
    draw_distant_hills(draw)
    draw_ground(draw)
    draw_etc_gantry(draw)
    draw_lattice_tower(draw)
    draw_workers_from_behind(draw)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", compress_level=6)
    raw = OUT.read_bytes()
    if not raw.startswith(PNG_MAGIC):
        raise SystemExit("PNG magic bytes mismatch")
    # Optional: verify IHDR via struct
    if raw[12:16] != b"IHDR":
        raise SystemExit("missing IHDR")
    w, h = struct.unpack(">II", raw[16:24])
    if (w, h) != (W, H):
        raise SystemExit(f"unexpected dimensions {w}x{h}")
    print(base64.b64encode(raw).decode("ascii"), end="")


if __name__ == "__main__":
    main()
