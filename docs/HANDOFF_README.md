# 引き渡し資料（HANDOFF README）

このドキュメントは、本プロジェクト（GKEミニサーマルプリンターのPython制御化）を他の方へ共有・引き渡す際のガイドです。
作業の進行に合わせて随時更新します。（現時点ではドラフト段階です）

## このプロジェクトは何か

専用Androidアプリの通信を解析して得たプロトコル仕様をもとに、PC上のPythonから直接GKEミニサーマルプリンターを操作できるようにするものです。

- 文字印刷
- QRコード印刷
- 画像印刷

を、Androidアプリを介さずPythonから実行できます。

## 渡されたら最初に見るもの

1. `README.md` … プロジェクト概要
2. `docs/progress.md` … 現在の進捗・確定事項・未確定事項の一覧
3. `docs/protocol_spec.md` … 通信プロトコルの最終仕様（実装のリファレンス）
4. `printer/` … Python実装本体

## 動かし方（Python実装完了後に記載予定）

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # または pip install bleak pillow qrcode

python
>>> from printer.printer import Printer
>>> p = Printer("XX:XX:XX:XX:XX:XX")  # 実際のMACアドレスに置き換え
>>> p.connect()
>>> p.print_text("Hello")
>>> p.disconnect()
```

※ 上記は実装完了後の想定例です。実際のAPIは `printer/printer.py` の実装に合わせて確定します。

## 必要な環境

- Python 3.x
- Bluetooth（BLE）対応PCまたはドングル
- GKEミニサーマルプリンター本体
- ライブラリ: `bleak`, `Pillow`, `qrcode`

## 既知の制約・未確定事項

（`docs/progress.md` の「未確定事項」セクションに準拠。作業完了時点の最新状態をここにも反映します）

## 連絡先・引き継ぎ事項

（必要に応じて記載）

---

*このファイルはプロジェクト完了時に最終版として整備します。現時点では骨子のみです。*
