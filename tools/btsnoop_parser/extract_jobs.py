#!/usr/bin/env python3
"""Extract per-print-job raw byte streams from the RFCOMM data channel (CID 0x51, DLCI=2)."""
import struct
import sys
from parse_rfcomm import read_records, l2cap_pdus, decode_rfcomm

def main(path):
    records = read_records(path)
    stream = bytearray()
    events = []  # (idx, direction, nbytes)
    for idx, direction, cid, payload in l2cap_pdus(records):
        if cid != 0x0051:
            continue
        decoded = decode_rfcomm(payload)
        if decoded is None:
            continue
        dlci, ftype, info = decoded
        if dlci == 2 and ftype == "UIH" and info:
            events.append((idx, direction, len(info)))
            stream.extend(info)

    print(f"total stream bytes on CID 0x51 DLCI=2: {len(stream)}")

    MAGIC = bytes.fromhex("1d4759")
    positions = []
    start = 0
    while True:
        p = stream.find(MAGIC, start)
        if p == -1:
            break
        positions.append(p)
        start = p + 1
    print(f"job header occurrences: {len(positions)} at offsets {positions}")

    # dump header bytes around each occurrence
    for i, p in enumerate(positions):
        chunk = stream[p:p+16]
        print(f"job {i}: offset={p} header={chunk.hex()}")

    # split into blocks
    blocks = []
    for i, p in enumerate(positions):
        end = positions[i+1] if i+1 < len(positions) else len(stream)
        blocks.append(bytes(stream[p:end]))

    for i, b in enumerate(blocks):
        print(f"\nblock {i}: length={len(b)} bytes")
        print(f"  header(20B): {b[:20].hex()}")
        print(f"  tail(20B):   {b[-20:].hex()}")

    return blocks

if __name__ == "__main__":
    blocks = main(sys.argv[1])
    if len(sys.argv) > 2:
        outdir = sys.argv[2]
        import os
        os.makedirs(outdir, exist_ok=True)
        for i, b in enumerate(blocks):
            with open(os.path.join(outdir, f"job_{i:02d}.bin"), "wb") as f:
                f.write(b)
        print(f"\nwrote {len(blocks)} block files to {outdir}")
