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
    printer.print_qr("https://example.com")   # ※4分割不具合は解決済み・実機確認済み
    printer.print_image("photo.png")           # ※修正済み（実機での画像印刷確認は未実施）
```

## 現在の完成度（率直な状況）

| 機能 | 状態 |
|---|---|
| プロトコル解析（Bluetooth方式・通信フォーマット） | ✅ 完了。バイトレベルで解読済み（2026-08-26に4階調グレースケール形式と判明・訂正） |
| Bluetooth接続 | ✅ 実機（Windows）で動作確認済み |
| 文字印刷 (`print_text`) | ✅ 実用可能。読める大きさで印字できることを確認済み |
| QRコード印刷 (`print_qr`) | ✅ **解決済み・実機確認済み。** きれいな大きなQRコードが1個だけ印字されることを確認した |
| 画像印刷 (`print_image`) | ✅ コード上は修正済み（写真等の実機での最終確認は未実施） |

**最重要の引き継ぎ事項（2026-08-26 解決・実機確認済み）:** 自前で生成した画像データ（QRコード
など）をプリンターへ送ると、本来1枚のはずの画像が紙面に横4分割されて印字される問題が長期間
未解決だったが、**根本原因を特定・修正し、実機で解決を確認した。** 原因は「1bit白黒、
48バイト/行」という誤ったプロトコル理解で、正しくは**「4階調グレースケール、1バイトに2画素、
192バイト/行」**だった。これは本物のアプリ（`com.dingdang.newprint`）のAPKを取得・逆コンパイル
することで判明した（ブラックボックスの通信解析だけでは特定できなかった）。詳細な経緯は
[`docs/protocol_spec.md`](protocol_spec.md) の「根本原因の判明と修正」セクションを参照。

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
- ライブラリ: `Pillow`, `qrcode`, `numpy`, `pytest`（`requirements.txt`参照。`pyserial`はWindowsのCOMポート接続時のみ必要）

## 既知の制約・未確定事項

- `print_image()`（写真等の任意画像印刷）は実機で最終確認していない（QRコードは確認済み）
- プリンター本体の給紙不良（ハードウェア側の問題と推測。調査中、複数回にわたり
  実際に紙へ印字されることを確認しているため、給紙機構自体は機能している）
- フッター（`1B 4A 50 1B BB BB 10 FF F1 45`）の各バイトの正確な意味（チェックサム有無等）は未解析
- 写真等、多階調画像を送った場合の見栄え（ディザリングの要否）は未検証

その他の詳細は [`docs/progress.md`](progress.md) の「未確定事項」セクションを参照してください。

## 次の一手（おすすめ）

1. `print_image()`（写真等）を実機テストし、多階調画像の見栄えを確認する。ディザリングが
   必要そうなら`to_gray4_bitmap(image, dither=True)`を試す
2. `docs/protocol_spec.md`の未確定事項（フッターの意味等）を埋めると、より頑健な実装にできます

## 報告書

手順書作成者向けに、調査結果をまとめた報告書を作成しました。

- Webページ版（共有しやすい形式）: https://claude.ai/code/artifact/428aedc1-f2aa-4f12-b885-0b0c2b8f8545
- リポジトリ内のHTML版: [`docs/report.html`](report.html)（ブラウザで直接開けます）
- リポジトリ内のMarkdown版: [`docs/report.md`](report.md)（GitHub上でそのまま読めます）

## 連絡先・引き継ぎ事項

このプロジェクトは Claude（Anthropic の AI アシスタント）との対話を通じて、
`docs/reference/GKE_thermal_printer_python_reverse_engineering_workflow.md` の手順書に
沿って進められました。手順からの変更点・判断理由は `docs/progress.md` の決定事項ログに
全て記録されています。
