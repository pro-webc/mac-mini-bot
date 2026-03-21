#!/usr/bin/env python3
"""One-off: night telecom mast + worker silhouette PNG -> stdout base64 only."""
import base64
import io
import random
import struct
import zlib

W, H = 768, 432
random.seed(42)

rows = []
for y in range(H):
    t = y / (H - 1)
    r = int(8 + t * 12)
    g = int(18 + t * 22)
    b = int(42 + t * 38)
    rows.append(bytes([0, r, g, b] * W))

buf = bytearray(b"".join(rows))


def set_px(x: int, y: int, rr: int, gg: int, bb: int, aa: int = 255) -> None:
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        buf[i : i + 4] = bytes([rr, gg, bb, aa])


for _ in range(120):
    sx = random.randint(0, W - 1)
    sy = random.randint(0, int(H * 0.55))
    br = random.randint(40, 90)
    set_px(sx, sy, br, br + 20, min(255, br + 40), random.randint(80, 200))

for y in range(int(H * 0.72), H):
    for x in range(W):
        glow = int(15 * (1 - (y - H * 0.72) / (H * 0.28)))
        i = (y * W + x) * 4
        buf[i] = min(255, buf[i] + glow // 3)
        buf[i + 1] = min(255, buf[i + 1] + glow // 2)
        buf[i + 2] = min(255, buf[i + 2] + glow)

cx = W // 2 + 40
base_y = H - 8
mast_top = int(H * 0.08)

for y in range(mast_top, base_y):
    w_at = int(8 + (base_y - y) * 0.12)
    for dx in range(-w_at, w_at + 1):
        set_px(cx + dx, y, 5, 8, 14, 255)

for k in range(0, base_y - mast_top, 14):
    yy = mast_top + k
    span = int(6 + k * 0.11)
    for t in range(span):
        set_px(cx - span + t, yy + t // 2, 6, 10, 18, 255)
        set_px(cx + span - t, yy + t // 2, 6, 10, 18, 255)

py = int(H * 0.38)
for dx in range(-55, 56):
    set_px(cx + dx, py, 8, 12, 20, 255)
for dy in range(0, 8):
    set_px(cx - 55, py + dy, 8, 12, 20, 255)
    set_px(cx + 55, py + dy, 8, 12, 20, 255)

for yy in range(mast_top, mast_top + 35):
    set_px(cx, yy, 4, 6, 12, 255)
for a in range(-3, 4):
    set_px(cx + a * 6, mast_top + 8, 5, 8, 14, 255)

wx, wy = cx + 18, py - 2
for y in range(wy, wy + 42):
    for x in range(wx - 7, wx + 7):
        if abs(x - wx) + (y - wy) // 3 < 10:
            set_px(x, y, 3, 5, 10, 255)
for dy in range(-14, 0):
    for dx in range(-9, 10):
        if dx * dx + dy * dy < 82:
            set_px(wx + dx, wy + dy, 4, 6, 11, 255)
for t in range(28):
    set_px(wx - t // 3, wy + 12 + t, 6, 9, 15, 255)
    set_px(cx + 40 - t // 4, py + t // 2, 5, 8, 13, 255)

for y in range(py, H):
    half = int((y - py) * 0.35)
    for x in range(cx - half, cx + half + 1):
        if random.random() < 0.03:
            i = (y * W + x) * 4
            buf[i + 2] = min(255, buf[i + 2] + 8)
            buf[i + 1] = min(255, buf[i + 1] + 4)


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


raw = bytes(buf)
sig = b"\x89PNG\r\n\x1a\n"
ihdr = struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0)
out = bytearray(sig)
out += png_chunk(b"IHDR", ihdr)
stride = W * 4
scanlines = b"".join(b"\x00" + raw[y * stride : (y + 1) * stride] for y in range(H))
out += png_chunk(b"IDAT", zlib.compress(scanlines, 9))
out += png_chunk(b"IEND", b"")

b64 = base64.b64encode(bytes(out)).decode("ascii")
# JSON line for piping
import json

print(json.dumps({"png_base64": b64}))
