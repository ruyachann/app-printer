"""GKE Mini Pocket Printer (S1-A20) の独自ラスター画像プロトコル。

docs/protocol_spec.md の確定仕様に基づく実装。実キャプチャ（captures/rfcomm_jobs/）から
バイトレベルで解読済み:

    [Header 8 bytes] + [Bitmap payload (height_px * WIDTH_BYTES)] + [Footer 10 bytes]

Header = 1D 47 59 04 30 00 <height_units u16 LE>  (height_units*4 = 実際の行数)
Footer = 1B 4A 50 1B BB BB 10 FF F1 45  (固定値)
"""

import struct

WIDTH_PX = 384
WIDTH_BYTES = WIDTH_PX // 8  # 48

HEADER_PREFIX = bytes.fromhex("1d47590430" "00")  # 6 bytes
FOOTER = bytes.fromhex("1b4a501bbbbb10fff145")  # 10 bytes

RFCOMM_CHUNK_SIZE = 240  # captures上で観測されたRFCOMM UIHペイロードの単位


def build_print_command(bitmap: bytes) -> bytes:
    """1bitビットマップ（MSBファースト、bit=1が黒）から送信用バイト列を組み立てる。

    bitmap の長さは WIDTH_BYTES の倍数、かつ行数（len(bitmap)//WIDTH_BYTES）は
    4の倍数である必要がある（ヘッダーの高さフィールドが4行単位のため）。
    """
    if len(bitmap) % WIDTH_BYTES != 0:
        raise ValueError(f"bitmap length must be a multiple of {WIDTH_BYTES} bytes (one row)")
    height_px = len(bitmap) // WIDTH_BYTES
    if height_px % 4 != 0:
        raise ValueError("bitmap height (rows) must be a multiple of 4")
    height_units = height_px // 4
    if not (0 <= height_units <= 0xFFFF):
        raise ValueError("bitmap too tall to encode in a 16-bit height field")

    header = HEADER_PREFIX + struct.pack("<H", height_units)
    return header + bitmap + FOOTER


def split_packets(data: bytes, chunk_size: int = RFCOMM_CHUNK_SIZE) -> list[bytes]:
    """送信データをRFCOMM送信単位（既定240バイト）に分割する。"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
