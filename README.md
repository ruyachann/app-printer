# app-printer

GKEミニサーマルプリンター（Mini Pocket Printer, 型番: S1-A20）の通信プロトコルを解析し、
PC(Python)から直接印刷できるようにするプロジェクトです。

専用Androidアプリ「Luck Jingle」の通信をキャプチャして解析し、その結果をもとにPython実装（`printer/`）を行いました。
Android専用アプリの開発は行っていません。

## 現在のステータス: プロトコル解読・Python実装・実機確認 全て完了

- 通信プロトコルはバイトレベルで完全に解読済み（`docs/protocol_spec.md`）
- Python実装（`printer/`）は完成し、実キャプチャデータとの比較テストに全件合格（`tests/`）
- **文字印刷・QRコード印刷・画像（写真）印刷の全てを実機（Windows PC）で確認済み**
- **✅ 2026-08-26: QRコード等が紙面に横4分割されて印字される不具合を解決・実機確認済み。**
  本物のアプリのAPKを逆コンパイルした結果、プロトコルが「1bit白黒」ではなく
  **「4階調グレースケール（1バイトに2画素）」**だったことが判明し、これが根本原因だった。
  修正後、実機で**きれいな大きなQRコード**・**日本語を含む文字**・**自然な階調のグレースケール
  写真**が、いずれも正しく1回だけ印字されることを確認済み。
  詳細は [`docs/protocol_spec.md`](docs/protocol_spec.md) の「根本原因の判明と修正」セクションを参照

## クイックスタート

```python
from printer.printer import Printer

with Printer("dd:4c:b9:33:22:10") as printer:  # MACアドレスは実機のものに置き換え
    printer.print_text("Hello")
    printer.print_qr("https://example.com")
    printer.print_image("photo.png")
```

## ディレクトリ構成

```text
app-printer/
├── docs/
│   ├── progress.md          # 進捗トラッカー・決定事項ログ
│   ├── device_info.md       # 対象機器・環境情報
│   ├── bluetooth_gatt.md    # Bluetooth解析結果（Classic/RFCOMM確定）
│   ├── protocol_spec.md     # プリンタープロトコル仕様書（確定版）
│   ├── test_plan.md         # 通信キャプチャ用テスト計画・実施記録
│   ├── HANDOFF_README.md    # 共有先の人向けの引き渡し資料
│   └── reference/           # 元となった作業手順書
├── captures/                 # 実通信データ（btsnoopログ、抽出済みジョブ、レンダリング画像）
│   ├── rfcomm_jobs/          # 印刷ジョブ単位の生バイナリ（テストの正解データ）
│   └── rendered/             # ビットマップを画像化した確認用PNG
├── tools/btsnoop_parser/     # btsnoopログ解析用の自作Pythonツール
├── printer/                  # Python実装（bluetooth/protocol/image/qr/printer）
└── tests/                    # テストコード（実機不要のもの全てPASS済み）
```

## 通信プロトコルの概要

- **Bluetooth方式: Classic（RFCOMM/SPP）** （Android側では"BLE"を含む名前で見えることがあるが、実データ通信はBLEではない。詳細は`docs/bluetooth_gatt.md`参照）
- 文字・QRコードとも専用コマンドは存在せず、**共通の4階調グレースケールラスタービットマッププロトコル**で送信される
- 画像仕様: 幅384px、**1バイトに2画素（4bit/画素、値0〜3、192 bytes/row）**、0=白・3=黒
- 送信フォーマット: `[Header 8B: 1D 47 59 <gray_levels=04> <width_ref u16 LE=30 00> <height u16 LE>] + [Bitmap] + [Footer 10B: 1B 4A 50 1B BB BB 10 FF F1 45]`

詳細は [`docs/protocol_spec.md`](docs/protocol_spec.md) を参照してください。

## セットアップ

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合は venv\Scripts\activate
pip install -r requirements.txt
```

Bluetooth接続はPython標準ライブラリの `socket.AF_BLUETOOTH` を使用しており、追加のBluetoothライブラリは不要です
（Linux/Windowsで動作。macOSは別途対応が必要です）。Windowsで接続する場合は、事前にWindowsの設定でプリンターを
ペアリングしておいてください。

## テストの実行

```bash
python -m pytest tests/
```

実キャプチャデータとの比較を含む10件のテストが実機不要で実行できます。

## 進め方の記録

このプロジェクトは以下の手順書に沿って進めました（一部、実際の解析結果に基づき方針変更した箇所があります。
詳細は `docs/progress.md` の決定事項ログを参照）。

- [`docs/reference/GKE_thermal_printer_python_reverse_engineering_workflow.md`](docs/reference/GKE_thermal_printer_python_reverse_engineering_workflow.md)

## 共有・引き渡しについて

このプロジェクトを別の方に引き渡す際は [`docs/HANDOFF_README.md`](docs/HANDOFF_README.md) を参照してください。
