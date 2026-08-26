#!/usr/bin/env python3
"""4分割バグの検証実験: 「実効印字幅は384pxではなく96px」仮説のテスト。

docs/protocol_spec.md の「続報4」で記録した通り、384px幅いっぱいを使う左右非対称の
診断用画像（captures/test_assets/asymmetric_test.png）を印字した結果、紙面には円・線・三角形が
周期的に重なり合う形で複数回現れた。円と三角形の座標を96で割った余り（mod 96）を計算すると、
観測されたパターン（区画境界に線、区画内で三角形と円が重なる）とよく一致する。これは、
プリンターの実効印字幅が384pxではなく**96px**であり、96pxを超える列のデータが何らかの形で
周期的に折り返されている（あるいは384px全体を96px区画ごとに独立して処理している）ことを
示唆する。

このスクリプトは、QRコードを**96px以内に収まるサイズ**で生成し、384pxキャンバスの残り
（96px〜383px）は完全に空白（0x00）のまま送信する。この状態で1個だけ正しいQRコードが
印字されれば、「実効幅96px」仮説が強く支持される。

使い方:
    python tools/experiments/narrow_qr_test.py COM4 "https://example.com"
    python tools/experiments/narrow_qr_test.py --save-only out.bin "https://example.com"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from PIL import Image
import qrcode

from printer.bluetooth import PrinterConnection
from printer.image import to_1bit_bitmap
from printer.protocol import WIDTH_PX, build_print_command

MAX_WIDTH = 96


def generate_narrow_qr_bitmap(data: str) -> bytes:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=1, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    modules = qr.modules_count + qr.border * 2

    box_size = max(1, MAX_WIDTH // modules)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")

    if qr_img.width > MAX_WIDTH:
        raise ValueError(f"QRが{MAX_WIDTH}px以内に収まりません（{qr_img.width}px）。データを短くしてください。")

    print(f"[narrow_qr_test] QRサイズ: {qr_img.width}x{qr_img.height}px (box_size={box_size}, 96px以内={qr_img.width <= MAX_WIDTH})")

    canvas = Image.new("L", (WIDTH_PX, qr_img.height), 255)
    canvas.paste(qr_img, (0, 0))  # 左端(0px)に配置。96px〜383pxは白紙のまま
    return to_1bit_bitmap(canvas, dither=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("address", nargs="?", help="COMポート名またはBluetoothアドレス（--save-only指定時は不要）")
    parser.add_argument("data", help="QRコードに埋め込む文字列")
    parser.add_argument("--save-only", metavar="PATH", help="送信せず、生成したコマンドをこのパスに保存するだけ")
    args = parser.parse_args()

    bitmap = generate_narrow_qr_bitmap(args.data)
    command = build_print_command(bitmap)
    print(f"[narrow_qr_test] 生成コマンド: {len(command)} bytes")

    if args.save_only:
        Path(args.save_only).write_bytes(command)
        print(f"[narrow_qr_test] 保存しました: {args.save_only}")
        return

    if not args.address:
        parser.error("addressを指定するか、--save-onlyを使ってください")

    conn = PrinterConnection(args.address)
    print(f"[narrow_qr_test] {args.address} に接続します...")
    conn.connect()
    try:
        print("[narrow_qr_test] 送信中...")
        conn.write(command)
        print("[narrow_qr_test] 送信完了。プリンターの印字結果を確認してください。")
    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
