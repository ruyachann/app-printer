"""QRコードを生成し、プリンター用1bitビットマップに変換するモジュール。

docs/protocol_spec.md の判定: このプリンター・アプリにQR専用コマンドは存在せず、
QRも通常の画像プロトコル（image.to_1bit_bitmap）に乗せて送信すればよいことが確認済み。
"""

import qrcode

from .image import to_1bit_bitmap
from .protocol import WIDTH_PX


def generate_qr_bitmap(data: str, error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size: int = 8, border: int = 2) -> bytes:
    """QRコードを生成し、幅384pxのプリンター用1bitビットマップに変換する。"""
    qr = qrcode.QRCode(
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("L")

    # QRは正方形のまま384幅に合わせて拡大縮小する（アスペクト比を保つ）
    if img.width != WIDTH_PX:
        ratio = WIDTH_PX / img.width
        new_height = max(1, round(img.height * ratio))
        img = img.resize((WIDTH_PX, new_height), resample=0)  # 0=NEAREST（モジュールの境界をぼかさない）

    return to_1bit_bitmap(img, dither=False)
