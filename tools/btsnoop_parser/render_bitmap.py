#!/usr/bin/env python3
"""Render a job_NN.bin raster payload as a PNG to visually verify the bitmap protocol."""
import sys
from PIL import Image

WIDTH_BYTES = 48  # 384 px
HEADER_LEN = 8

def render(path, out_path, invert=False):
    with open(path, "rb") as f:
        data = f.read()
    header = data[:HEADER_LEN]
    height_units = int.from_bytes(header[6:8], "little")
    rows = height_units * 4
    body = data[HEADER_LEN:HEADER_LEN + rows * WIDTH_BYTES]
    print(f"{path}: header={header.hex()} height_units={height_units} rows={rows} body_len={len(body)} expected={rows*WIDTH_BYTES}")

    img = Image.new("1", (WIDTH_BYTES * 8, rows), 1)  # 1=white background
    px = img.load()
    for row in range(rows):
        row_start = row * WIDTH_BYTES
        row_bytes = body[row_start:row_start + WIDTH_BYTES]
        if len(row_bytes) < WIDTH_BYTES:
            break
        for byte_idx, b in enumerate(row_bytes):
            for bit in range(8):
                pixel_on = (b >> (7 - bit)) & 1  # MSB first
                x = byte_idx * 8 + bit
                val = pixel_on
                if invert:
                    val = 1 - val
                # bit=1 -> black(0), bit=0 -> white(1) in PIL mode "1" (1=white)
                px[x, row] = 0 if val else 1
    img.save(out_path)
    print(f"saved {out_path} ({img.size})")

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], invert=("--invert" in sys.argv))
