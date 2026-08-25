# app-printer

GKEミニサーマルプリンターの通信プロトコルを解析し、PC(Python)から直接印刷できるようにするプロジェクトです。

専用Androidアプリの通信をキャプチャして解析し、その結果をもとにPython実装（`printer/`）を行います。
Android専用アプリの開発は行いません。

## 最終ゴール

```python
printer.connect()
printer.print_text("Hello")
printer.print_qr("https://example.com")
printer.print_image("photo.png")
printer.disconnect()
```

## 現在の進捗

進捗状況・決定事項は [`docs/progress.md`](docs/progress.md) を参照してください。

## ディレクトリ構成

```text
app-printer/
├── docs/
│   ├── progress.md          # 進捗トラッカー・決定事項ログ
│   ├── device_info.md       # 対象機器・環境情報
│   ├── bluetooth_gatt.md    # Bluetooth/GATT解析結果
│   ├── protocol_spec.md     # プリンタープロトコル仕様書
│   ├── HANDOFF_README.md    # 共有先の人向けの引き渡し資料
│   └── reference/           # 元となった作業手順書
├── captures/                 # Wiresharkから抽出した通信データ
├── printer/                  # Python実装（bluetooth/protocol/image/qr/printer）
└── tests/                    # テストコード
```

## 進め方

このプロジェクトは以下の手順書に沿って進めています。

- [`docs/reference/GKE_thermal_printer_python_reverse_engineering_workflow.md`](docs/reference/GKE_thermal_printer_python_reverse_engineering_workflow.md)

大まかな流れ：

1. 対象機器・環境確認
2. Android側でBluetooth通信をキャプチャ（HCI Snoop Log）
3. Wiresharkで解析し、GATT構成・プロトコルを特定
4. 特定した仕様に基づきPython（bleak）で再実装
5. 文字・QR・画像の印刷をテスト

## セットアップ（Python実装フェーズ以降）

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合は venv\Scripts\activate
pip install bleak pillow qrcode
```

## 共有・引き渡しについて

このプロジェクトを別の方に引き渡す際は [`docs/HANDOFF_README.md`](docs/HANDOFF_README.md) を参照してください。
