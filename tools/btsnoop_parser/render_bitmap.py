#!/usr/bin/env python3
"""Render a job_NN.bin raster payload as a PNG to visually verify the bitmap protocol.

2026-08-26: updated for the corrected 4-level grayscale format (1 byte = 2 pixels,
4 bits each, values 0-3; see printer/protocol.py for the full spec), discovered by
decompiling the vendor app's APK. The previous version assumed 1-bit/8-pixels-per-byte,
which was the root cause of the "4-way duplication" bug this project spent a long time
chasing.
"""
import struct
import sys
from PIL import Image

HEADER_LEN = 8
GRAY_LEVELS = 4
MAX_LEVEL = GRAY_LEVELS - 1


def render(path, out_path, upscale=1):
    with open(path, "rb") as f:
        data = f.read()
    header = data[:HEADER_LEN]
    gray_levels = header[3]
    width_bytes_ref = struct.unpack("<H", header[4:6])[0]
    rows = struct.unpack("<H", header[6:8])[0]
    width_px = width_bytes_ref * 8
    stride = width_px // 2
    body = data[HEADER_LEN:HEADER_LEN + stride * rows]
    print(f"{path}: header={header.hex()} gray_levels={gray_levels} width_px={width_px} "
          f"rows={rows} stride={stride} body_len={len(body)} expected={stride * rows}")

    img = Image.new("L", (width_px, rows))
    px = img.load()
    for row in range(rows):
        row_bytes = body[row * stride:(row + 1) * stride]
        for byte_idx, b in enumerate(row_bytes):
            hi, lo = (b >> 4) & 0xF, b & 0xF
            x0 = byte_idx * 2
            if x0 < width_px:
                px[x0, row] = int((MAX_LEVEL - hi) * 255 / MAX_LEVEL) if hi <= MAX_LEVEL else 0
            if x0 + 1 < width_px:
                px[x0 + 1, row] = int((MAX_LEVEL - lo) * 255 / MAX_LEVEL) if lo <= MAX_LEVEL else 0
    if upscale != 1:
        img = img.resize((width_px * upscale, rows * upscale), Image.NEAREST)
    img.save(out_path)
    print(f"saved {out_path} ({img.size})")


if __name__ == "__main__":
    upscale = 1
    for arg in sys.argv[3:]:
        if arg.startswith("--upscale="):
            upscale = int(arg.split("=", 1)[1])
    render(sys.argv[1], sys.argv[2], upscale=upscale)
