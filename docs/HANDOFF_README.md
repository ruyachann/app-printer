# 引き渡し資料（HANDOFF README）

このドキュメントは、本プロジェクト（GKEミニサーマルプリンターのPython制御化）を
他の方へ共有・引き渡す際のガイドです。

## このプロジェクトは何か

GKE Mini Pocket Printer（型番: S1-A20）専用Androidアプリ「Luck Jingle」の
Bluetooth通信を解析し、そのプロトコルをPythonで再実装したものです。
PC上のPythonから、Androidアプリを介さず直接プリンターへ印刷指示を送れます。

```python
from printer.printer import Printer

with Printer("dd:4c:b9:33:22:10") as printer:  # MACアドレスは実機のものに置き換え
    printer.print_text("Hello")
    printer.print_qr("https://example.com")   # ※現在4分割される既知の問題あり。下記参照
    printer.print_image("photo.png")           # ※未検証
```

## 現在の完成度（率直な状況）

| 機能 | 状態 |
|---|---|
| プロトコル解析（Bluetooth方式・通信フォーマット） | ✅ 完了。バイトレベルで解読済み |
| Bluetooth接続 | ✅ 実機（Windows）で動作確認済み |
| 文字印刷 (`print_text`) | ✅ 実用可能。読める大きさで印字できることを確認済み |
| QRコード印刷 (`print_qr`) | ⚠️ **未解決の問題あり**。紙面に4分割されて印字され、実用不可 |
| 画像印刷 (`print_image`) | ⚠️ 未検証（QRと同じ問題を抱えている可能性が高い） |

**最重要の引き継ぎ事項:** 自前で生成した画像データ（QRコードなど）をプリンターへ送ると、
本来1枚のはずの画像が紙面に横4分割されて印字されてしまう問題が未解決です。
実際にアプリが送信した本物のデータをそのまま再送すると問題なく1枚で印字されるため、
「送信の仕組み」ではなく「生成した画像データの中身」に何らかの違いがあると考えられますが、
サイズ・複雑さ・パターンの規則性など多数の要因を切り分けても原因を特定できませんでした。
詳細な調査記録は [`docs/protocol_spec.md`](protocol_spec.md) の
「既知の未解決問題」セクションに全て残していますので、続きの調査にご活用ください。

## 渡されたら最初に見るもの

1. [`README.md`](../README.md) … プロジェクト概要・セットアップ手順
2. [`docs/progress.md`](progress.md) … 作業の全記録（決定事項ログ・進捗チェックリスト）
3. [`docs/protocol_spec.md`](protocol_spec.md) … 通信プロトコルの確定仕様＋既知の問題の詳細調査記録
4. [`printer/`](../printer/) … Python実装本体（各ファイルの冒頭コメントに設計判断の背景を記載）
5. [`captures/`](../captures/) … 実通信データ、抽出済み印刷ジョブ、レンダリング画像（デバッグの参考に）

## 動かし方

```bash
git clone -b claude/gke-thermal-printer-reverse-eng-g9ouzd https://github.com/ruyachann/app-printer.git
cd app-printer
python -m venv venv
```

Windows: `.\venv\Scripts\activate` / macOS・Linux: `source venv/bin/activate`

```bash
pip install -r requirements.txt
python -m pytest tests/   # 実機不要のテスト10件が通ることを確認
```

### 実機に接続する

Bluetooth ClassicはPython標準ライブラリの`socket.AF_BLUETOOTH`を使用します（追加ライブラリ不要）。
**Windowsでは、生のソケット接続がタイムアウトすることがあります。** その場合は、
デバイスマネージャーの「ポート(COMとLPT)」で「Bluetoothリンク経由の標準シリアル」の
**出力側COMポート**（入力待ち側だと接続がハングします。2つあれば両方試してください）を確認し、
`Printer("COM4")`のようにCOMポート名を渡してください（`pyserial`経由で自動的に接続します）。

事前にWindowsの「Bluetoothとデバイス」設定でプリンターとペアリングしておく必要があります。

## 必要な環境

- Python 3.10以降（`ImageFont.load_default(size=...)`にPillow 10.1+が必要）
- Bluetooth Classic（RFCOMM/SPP）対応PC
- GKE Mini Pocket Printer S1-A20（または同系機種）
- ライブラリ: `Pillow`, `qrcode`, `pytest`（`requirements.txt`参照。`pyserial`はWindowsのCOMポート接続時のみ必要）

## 既知の制約・未確定事項

- **【最重要】QRコード等の自前生成画像が4分割されて印字される**（上記参照、詳細は`protocol_spec.md`）
- プリンター本体の給紙不良（ハードウェア側の問題と推測。ただし4分割問題の調査中、複数回にわたり
  実際に紙へ印字されることを確認しているため、給紙機構自体は機能している）
- フッター（`1B 4A 50 1B BB BB 10 FF F1 45`）の各バイトの正確な意味（チェックサム有無等）は未解析
- 写真等、多階調画像の実際の印字結果は未検証

その他の詳細は [`docs/progress.md`](progress.md) の「未確定事項」セクションを参照してください。

## 次の一手（おすすめ）

1. **4分割問題の原因調査を最優先で。** ロジックアナライザやより詳細なBluetoothスニファでの
   実通信比較、あるいはメーカー公式資料の入手が突破口になる可能性があります
2. 上記が解決すれば、QR・画像印刷も文字印刷と同様に実用化できるはずです（プロトコル自体は解明済み）
3. `docs/protocol_spec.md`の未確定事項（フッターの意味等）を埋めると、より頑健な実装にできます

## 連絡先・引き継ぎ事項

このプロジェクトは Claude（Anthropic の AI アシスタント）との対話を通じて、
`docs/reference/GKE_thermal_printer_python_reverse_engineering_workflow.md` の手順書に
沿って進められました。手順からの変更点・判断理由は `docs/progress.md` の決定事項ログに
全て記録されています。
