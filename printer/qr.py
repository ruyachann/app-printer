"""QRコードを生成し、プリンター用1bitビットマップに変換するモジュール。

docs/protocol_spec.md の判定: このプリンター・アプリにQR専用コマンドは存在せず、
QRも通常の画像プロトコル（image.to_1bit_bitmap）に乗せて送信すればよいことが確認済み。

実機テストで、生成したQR画像を送ると4分割されて印字される現象が発生した。
実際のキャプチャデータ（captures/rfcomm_jobs/qr_*.bin）をそのまま送信すると問題なく
1つのQRとして印字されたため、送信経路ではなく生成したビットマップ自体に原因があると判明。
バイト値を比較したところ、実データには`0xFF`（8ピクセル全て黒のバイト）が一度も出現しない一方、
box_size=8＋NEAREST法での384/200px正方形へのリサイズを行った生成データには多数の`0xFF`が
含まれていた。box_sizeが8の倍数だとモジュールの黒領域がバイト境界に綺麗に揃って`0xFF`を
生成しやすいため、box_sizeを8の倍数にせず、かつリサイズ処理を行わない方式に変更して回避する。
"""

from PIL import Image

import qrcode

from .image import to_1bit_bitmap
from .protocol import WIDTH_PX

QR_BOX_SIZE = 5  # 8の倍数にしない（0xFFバイトの発生を避けるため）。詳細は本モジュールのdocstring参照


def generate_qr_bitmap(data: str, error_correction=qrcode.constants.ERROR_CORRECT_M) -> bytes:
    """QRコードを生成し、プリンター用1bitビットマップに変換する。

    QRは384px幅キャンバスの左寄せで配置する（幅いっぱいには拡大しない）。
    """
    qr = qrcode.QRCode(error_correction=error_correction, box_size=QR_BOX_SIZE, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")

    canvas = Image.new("L", (WIDTH_PX, qr_img.height), 255)
    canvas.paste(qr_img, (0, 0))

    return to_1bit_bitmap(canvas, dither=False)
