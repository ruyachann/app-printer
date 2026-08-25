# app-printer

GKEミニサーマルプリンター（Mini Pocket Printer, 型番: S1-A20）の通信プロトコルを解析し、
PC(Python)から直接印刷できるようにするプロジェクトです。

専用Androidアプリ「Luck Jingle」の通信をキャプチャして解析し、その結果をもとにPython実装（`printer/`）を行いました。
Android専用アプリの開発は行っていません。

## 現在のステータス: プロトコル解読・Python実装 完了（実機での動作確認待ち）

- 通信プロトコルはバイトレベルで完全に解読済み（`docs/protocol_spec.md`）
- Python実装（`printer/`）は完成し、実キャプチャデータとの比較テストに全件合格（`tests/`）
- **未実施:** 実際のBluetooth接続・印刷（このプロジェクトを作成した環境にBluetoothハードウェアがないため）

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

- **Bluetooth方式: Classic（RFCOMM/SPP）** （デバイス名に"BLE"を含むが、実データ通信はBLEではない）
- 文字・QRコードとも専用コマンドは存在せず、**共通の1bitラスタービットマッププロトコル**で送信される
- 画像仕様: 幅384px（48 bytes/row）、1bit、MSBファースト、bit=1が黒
- 送信フォーマット: `[Header 8B: 1D 47 59 04 30 00 <height/4 u16 LE>] + [Bitmap] + [Footer 10B: 1B 4A 50 1B BB BB 10 FF F1 45]`

詳細は [`docs/protocol_spec.md`](docs/protocol_spec.md) を参照してください。

## セットアップ

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合は venv\Scripts\activate
pip install -r requirements.txt
```

`pybluez`（Bluetooth Classic対応ライブラリ）はOS依存の部分があり、環境によってビルドが必要な場合があります。
インストールに失敗する場合は `docs/HANDOFF_README.md` のトラブルシューティングを参照してください。

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
