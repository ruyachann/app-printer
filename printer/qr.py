"""QRコードを生成し、プリンター用1bitビットマップに変換するモジュール。

docs/protocol_spec.md の判定: このプリンター・アプリにQR専用コマンドは存在せず、
QRも通常の画像プロトコル（image.to_1bit_bitmap）に乗せて送信すればよいことが確認済み。

【重要・未解決の既知の問題】
実機テストで、このモジュールが生成したQR画像を送ると、紙面に**横4分割**されて印字される
現象を確認している（実際のキャプチャデータ captures/rfcomm_jobs/qr_*.bin をそのまま
再送信した場合は常に正しく1つだけ印字される）。

送信経路（bluetooth.py）とヘッダー生成（protocol.py）は実データで正常動作することを
確認済みのため無関係。box_sizeを8の倍数にしない、0xFFバイトを減らす、サイズを変える、
実データと同じ行数に揃える等、複数の対策を試したが解決しなかった。最終的に、単色/市松模様/
ランダムノイズいずれの自前生成データでも同じ症状が再現される一方、実データのみ正常動作する
ことを確認しており、**本物のアプリが生成したピクセルデータと本モジュールが生成したピクセル
データの間にある、未特定の違い**が原因と考えられる。詳細な調査記録は
docs/protocol_spec.md の「既知の未解決問題」セクションを参照。

現状、QRコードの実用的な印刷は未達成。今後の調査には、プリンターメーカーの公式資料の入手や、
ロジックアナライザでの実通信比較などが有効と考えられる。
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
