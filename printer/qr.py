"""QRコードを生成し、プリンター用1bitビットマップに変換するモジュール。

docs/protocol_spec.md の判定: このプリンター・アプリにQR専用コマンドは存在せず、
QRも通常の画像プロトコル（image.to_1bit_bitmap）に乗せて送信すればよいことが確認済み。

実機テストで、384px幅いっぱいまで正方形に引き伸ばしたQR（384x384px、384行）を送ると、
横に4分割されたQRが4つ並んで印字される現象を確認した（プリンター側の1ジョブあたりの
高さ上限に起因すると推測。136行程度の文字印刷では問題が起きなかった）。
そのため、QRは幅いっぱいまで拡大せず、余白付きで小さめのサイズに収めて印字する。
"""

from PIL import Image

import qrcode

from .image import to_1bit_bitmap
from .protocol import WIDTH_PX

DEFAULT_QR_SIZE_PX = 200  # 384px幅キャンバスの中に収める正方形QRの一辺のサイズ（安全マージンを見て控えめに設定）


def generate_qr_bitmap(data: str, error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size: int = 8, border: int = 2, target_size_px: int = DEFAULT_QR_SIZE_PX) -> bytes:
    """QRコードを生成し、プリンター用1bitビットマップに変換する。

    QRは384px幅いっぱいには拡大せず、target_size_px四方に収め、384px幅キャンバスの左寄せで配置する。
    """
    qr = qrcode.QRCode(
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")

    if qr_img.width != target_size_px:
        qr_img = qr_img.resize((target_size_px, target_size_px), resample=Image.Resampling.NEAREST)

    canvas = Image.new("L", (WIDTH_PX, target_size_px), 255)
    canvas.paste(qr_img, (0, 0))

    return to_1bit_bitmap(canvas, dither=False)
