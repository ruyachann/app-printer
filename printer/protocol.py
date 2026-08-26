"""GKE Mini Pocket Printer (S1-A20) の独自ラスター画像プロトコル。

【2026-08-26 修正・根本原因判明】本物のアプリ（com.dingdang.newprint、内部SDK名
com.luckprinter.sdk_new）のAPKを逆コンパイルして判明した正しい仕様に全面的に修正した。

以前の実装は「1bit白黒、8画素/バイト、48バイト/行」という誤った前提だった。実際には
**4階調グレースケール、1バイトに2画素（4bit/画素、値0〜3）、192バイト/行**が正しい仕様
だった。48×4=192という数値の一致により、誤って「height_units×4=実際の行数」という
辻褄の合う（しかし誤った）解釈を長らく採用してしまっていた。この誤りが、自前生成した
画像データが紙面に横4分割されて印字される既知の不具合の直接の原因だった。

    [Header 8 bytes] + [Bitmap payload (height_px * STRIDE)] + [Footer 10 bytes]

Header = 1D 47 59 <gray_levels:1> <width_bytes_ref:u16 LE> <height_px:u16 LE>
    - gray_levels: 階調数。実機キャプチャでは常に4（4階調グレースケール）
    - width_bytes_ref: 幅384pxを8で割った値（48）。実際の行バイト数（STRIDE=192）では
      なく、1bit換算の参照値として格納されているだけ（逆コンパイルしたSDKコードで確認）
    - height_px: 実際の行数（4倍する必要はない）
Footer = 1B 4A 50 1B BB BB 10 FF F1 45  (固定値)

Payload: 1行 = STRIDE(=WIDTH_PX/2=192)バイト。1バイトに2画素、各画素4bit
    （上位ニブル=左側の画素、下位ニブル=右側の画素）。画素値は 0〜GRAY_LEVELS-1(=3)で、
    0=白、GRAY_LEVELS-1=黒（値が大きいほど黒に近い）。
"""

import struct

WIDTH_PX = 384
WIDTH_BYTES_REF = WIDTH_PX // 8  # 48 -- ヘッダーに格納される参照値（実際の行バイト数ではない）
STRIDE = WIDTH_PX // 2  # 192 -- 実際の1行あたりバイト数（2画素/バイト、4bit/画素）
GRAY_LEVELS = 4  # 4階調（画素値0〜3）

HEADER_PREFIX = bytes.fromhex("1d4759")  # 3 bytes
FOOTER = bytes.fromhex("1b4a501bbbbb10fff145")  # 10 bytes

RFCOMM_CHUNK_SIZE = 240  # captures上で観測されたRFCOMM UIHペイロードの単位


def build_print_command(bitmap: bytes) -> bytes:
    """4階調グレースケールのビットマップ（1行=STRIDEバイト）から送信用バイト列を組み立てる。"""
    if len(bitmap) % STRIDE != 0:
        raise ValueError(f"bitmap length must be a multiple of {STRIDE} bytes (one row)")
    height_px = len(bitmap) // STRIDE
    if not (0 <= height_px <= 0xFFFF):
        raise ValueError("bitmap too tall to encode in a 16-bit height field")

    header = (
        HEADER_PREFIX
        + bytes([GRAY_LEVELS])
        + struct.pack("<H", WIDTH_BYTES_REF)
        + struct.pack("<H", height_px)
    )
    return header + bitmap + FOOTER


def split_packets(data: bytes, chunk_size: int = RFCOMM_CHUNK_SIZE) -> list[bytes]:
    """送信データをRFCOMM送信単位（既定240バイト）に分割する。"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
