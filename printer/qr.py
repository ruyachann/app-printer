"""QRコードを生成し、プリンター用4階調グレースケールビットマップに変換するモジュール。

docs/protocol_spec.md の判定: このプリンター・アプリにQR専用コマンドは存在せず、
QRも通常の画像プロトコル（image.to_gray4_bitmap）に乗せて送信すればよいことが確認済み。

【2026-08-26 解決済み】以前、このモジュールが生成したQR画像は実機で紙面に横4分割される
既知の不具合を抱えていたが、根本原因（プロトコルが1bit白黒ではなく4階調グレースケール
だったこと）をAPK逆コンパイルにより特定し、修正した。詳細は protocol.py・image.py 参照。
"""

from PIL import Image

import qrcode

from .image import to_gray4_bitmap
from .protocol import WIDTH_PX

QR_BOX_SIZE = 10


def generate_qr_bitmap(data: str, error_correction=qrcode.constants.ERROR_CORRECT_M) -> bytes:
    """QRコードを生成し、プリンター用ビットマップに変換する（384px幅いっぱいにリサイズ）。"""
    qr = qrcode.QRCode(error_correction=error_correction, box_size=QR_BOX_SIZE, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")

    ratio = WIDTH_PX / qr_img.width
    new_height = max(1, round(qr_img.height * ratio))
    qr_img = qr_img.resize((WIDTH_PX, new_height), Image.Resampling.LANCZOS)

    return to_gray4_bitmap(qr_img, dither=False)
