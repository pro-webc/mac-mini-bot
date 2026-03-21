#!/usr/bin/env python3
"""Generate abstract telecom/base-station illustration PNG; emit raw base64 to stdout."""
from __future__ import annotations

import base64
import math
import struct
import sys
import zlib

W, H = 768, 432


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix_rgb(
    r1: float, g1: float, b1: float, r2: float, g2: float, b2: float, t: float
) -> tuple[int, int, int]:
    t = clamp(t, 0.0, 1.0)
    return (
        int(lerp(r1, r2, t)),
        int(lerp(g1, g2, t)),
        int(lerp(b1, b2, t)),
    )


def point_in_rect(px: float, py: float, x: float, y: float, rw: float, rh: float) -> bool:
    return x <= px <= x + rw and y <= py <= y + rh


def point_in_poly(px: float, py: float, pts: list[tuple[float, float]]) -> bool:
    n = len(pts)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if ((yi > py) != (yj > py)) and (
            px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi
        ):
            inside = not inside
        j = i
    return inside


def dist(ax: float, ay: float, bx: float, by: float) -> float:
    return math.hypot(ax - bx, ay - by)


def pixel_rgba(x: int, y: int) -> tuple[int, int, int, int]:
    fx, fy = float(x), float(y)
    t_y = fy / (H - 1) if H > 1 else 0.0

    # Soft sky gradient (cool corporate)
    sky_top = (186, 198, 212)
    sky_mid = (210, 218, 228)
    sky_horizon = (232, 235, 238)
    if t_y < 0.55:
        u = t_y / 0.55
        r, g, b = mix_rgb(*sky_top, *sky_mid, u * 0.55 + 0.45 * (1 - u))
    else:
        u = (t_y - 0.55) / 0.45
        r, g, b = mix_rgb(*sky_mid, *sky_horizon, u)

    # Distant hills (abstract bands)
    hill_y = 0.52 * H
    if fy > hill_y:
        hill_t = clamp((fy - hill_y) / (0.08 * H), 0, 1)
        hr, hg, hb = 168, 178, 168
        r = int(lerp(r, hr, hill_t * 0.35))
        g = int(lerp(g, hg, hill_t * 0.35))
        b = int(lerp(b, hb, hill_t * 0.35))

    # Ground plane
    ground_y = 0.62 * H
    if fy > ground_y:
        gt = clamp((fy - ground_y) / (H - ground_y), 0, 1)
        gr, gg, gb = 118, 128, 118
        r = int(lerp(r, gr, gt * 0.92))
        g = int(lerp(g, gg, gt * 0.92))
        b = int(lerp(b, gb, gt * 0.92))

    a = 255

    # Perspective road (trapezoid)
    vanish_x, vanish_y = W * 0.5, H * 0.58
    road_w_near = W * 0.42
    road_w_far = W * 0.06
    y_near = H * 0.98
    y_far = vanish_y + 8
    x0 = vanish_x - road_w_far / 2
    x1 = vanish_x + road_w_far / 2
    x2 = vanish_x + road_w_near / 2
    x3 = vanish_x - road_w_near / 2
    road_poly = [(x0, y_far), (x1, y_far), (x2, y_near), (x3, y_near)]
    if point_in_poly(fx, fy, road_poly):
        rd_r, rd_g, rd_b = 88, 94, 92
        blend = 0.88 if fy > ground_y else 0.5
        r = int(lerp(r, rd_r, blend))
        g = int(lerp(g, rd_g, blend))
        b = int(lerp(b, rd_b, blend))
        # Lane markings (broken center — abstract dashes, no numbers)
        cx = vanish_x + (fx - vanish_x) * (1.0 - 0.35 * (fy - y_far) / max(y_near - y_far, 1))
        lane_w = max(3.0, (fy - y_far) / (y_near - y_far) * 14.0)
        if abs(fx - cx) < lane_w * 0.5:
            period = 28.0 + (fy - y_far) * 0.12
            phase = (fy + fx * 0.02) % period
            if phase < period * 0.45:
                lr, lg, lb = 210, 212, 208
                r = int(lerp(r, lr, 0.75))
                g = int(lerp(g, lg, 0.75))
                b = int(lerp(b, lb, 0.75))

    # Base station silhouette (right third, geometric)
    tx = W * 0.72
    ty = H * 0.42
    scale = 1.0

    def tower_local(px: float, py: float) -> bool:
        lx = (px - tx) / scale
        ly = (py - ty) / scale
        # Mast
        if point_in_rect(lx, ly, -6, 40, 12, 120):
            return True
        # Cross arms (3 tiers)
        for yi in (55, 85, 115):
            if point_in_rect(lx, ly, -28, yi, 56, 5):
                return True
        # Equipment cabin at base
        if point_in_rect(lx, ly, -18, 155, 36, 22):
            return True
        # Dish (circle approx — octagon)
        cx_, cy_ = 22.0, 70.0
        rad = 18.0
        if dist(lx, ly, cx_, cy_) < rad:
            return True
        # Fence hint (low posts)
        if 158 < ly < 168 and -40 < lx < 40 and int(lx // 8) % 2 == 0 and -2 < (lx % 8) < 2:
            return True
        return False

    if tower_local(fx, fy):
        tr, tg, tb = 52, 58, 62
        edge = 0.92
        r = int(lerp(r, tr, edge))
        g = int(lerp(g, tg, edge))
        b = int(lerp(b, tb, edge))

    # Left distant tower (smaller, atmospheric)
    tx2, ty2 = W * 0.22, H * 0.48
    s2 = 0.55

    def small_tower(px: float, py: float) -> bool:
        lx = (px - tx2) / s2
        ly = (py - ty2) / s2
        if point_in_rect(lx, ly, -4, 30, 8, 95):
            return True
        for yi in (45, 72, 98):
            if point_in_rect(lx, ly, -20, yi, 40, 4):
                return True
        return False

    if small_tower(fx, fy):
        tr2, tg2, tb2 = 78, 84, 88
        r = int(lerp(r, tr2, 0.55))
        g = int(lerp(g, tg2, 0.55))
        b = int(lerp(b, tb2, 0.55))

    # Subtle sun glow (no readable detail)
    sx, sy = W * 0.18, H * 0.22
    d = dist(fx, fy, sx, sy)
    if d < 55:
        glow = (1.0 - d / 55) * 0.22
        r = min(255, int(r + 25 * glow))
        g = min(255, int(g + 28 * glow))
        b = min(255, int(b + 22 * glow))

    return r, g, b, a


def write_png_rgba(path: str | None, raw: bytes, width: int, height: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    out = bytearray(sig)
    out.extend(chunk(b"IHDR", ihdr))
    stride = width * 4
    zlib_obj = zlib.compressobj(9, zlib.DEFLATED, 15)
    cdata = bytearray()
    for row in range(height):
        cdata.append(0)
        start = row * stride
        cdata.extend(raw[start : start + stride])
    compressed = zlib_obj.compress(bytes(cdata)) + zlib_obj.flush()
    out.extend(chunk(b"IDAT", compressed))
    out.extend(chunk(b"IEND", b""))
    blob = bytes(out)
    if path:
        with open(path, "wb") as f:
            f.write(blob)
    return blob


def main() -> None:
    row_stride = W * 4
    buf = bytearray(W * H * 4)
    for y in range(H):
        for x in range(W):
            r, g, b, a = pixel_rgba(x, y)
            i = y * row_stride + x * 4
            buf[i : i + 4] = bytes((r, g, b, a))
    png = write_png_rgba(None, bytes(buf), W, H)
    out = base64.b64encode(png).decode("ascii")
    if len(sys.argv) >= 2:
        with open(sys.argv[1], "w", encoding="ascii", newline="") as f:
            f.write(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
