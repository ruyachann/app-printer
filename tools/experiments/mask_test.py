#!/usr/bin/env python3
"""4分割バグの検証実験: バイト値ドメイン制限仮説のテスト。

docs/protocol_spec.md の「決定的な追加発見」の通り、実キャプチャデータのビットマップ本体は
1バイトあたり256通り中16通り（上位/下位ニブルとも常に0〜3）の値しか使わない。
このスクリプトは、通常どおり生成したQRビットマップの各バイトに 0x33 (0b00110011) で
AND演算をかけ、bit7・6・3・2を強制的に0にしてから送信する。これにより、送信データが
実データと同じ「16値ドメイン」に収まった状態で、4分割が解消するかどうかを確認できる。

使い方:
    python tools/experiments/mask_test.py COM4 "https://example.com"
    python tools/experiments/mask_test.py COM4 "https://example.com" --no-mask   # 比較用（従来どおり）
    python tools/experiments/mask_test.py --save-only out.bin "https://example.com"  # 送信せずファイル保存のみ
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from printer.bluetooth import PrinterConnection
from printer.protocol import build_print_command
from printer.qr import generate_qr_bitmap


def mask_bitmap(bitmap: bytes) -> bytes:
    return bytes(b & 0x33 for b in bitmap)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("address", nargs="?", help="COMポート名またはBluetoothアドレス（--save-only指定時は不要）")
    parser.add_argument("data", help="QRコードに埋め込む文字列")
    parser.add_argument("--no-mask", action="store_true", help="マスクをかけない従来どおりのデータで比較送信する")
    parser.add_argument("--save-only", metavar="PATH", help="送信せず、生成したコマンドをこのパスに保存するだけ")
    args = parser.parse_args()

    bitmap = generate_qr_bitmap(args.data)
    if not args.no_mask:
        before_nonzero = sum(1 for b in bitmap if b & ~0x33)
        bitmap = mask_bitmap(bitmap)
        print(f"[mask_test] マスク適用: 0x33の範囲外ビットを持つバイト数 {before_nonzero}/{len(bitmap)} を0にクリア")
    else:
        print("[mask_test] --no-mask 指定: マスクなし（従来どおり）で送信します")

    command = build_print_command(bitmap)
    print(f"[mask_test] 生成コマンド: {len(command)} bytes")

    if args.save_only:
        Path(args.save_only).write_bytes(command)
        print(f"[mask_test] 保存しました: {args.save_only}")
        return

    if not args.address:
        parser.error("addressを指定するか、--save-onlyを使ってください")

    conn = PrinterConnection(args.address)
    print(f"[mask_test] {args.address} に接続します...")
    conn.connect()
    try:
        print("[mask_test] 送信中...")
        conn.write(command)
        print("[mask_test] 送信完了。プリンターの印字結果を確認してください。")
    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
