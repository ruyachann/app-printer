# tests/ について

`printer/` モジュールのテストです。実行方法:

```bash
pip install -r requirements.txt
python -m pytest tests/
```

## テスト一覧

- `test_protocol_replay.py`: **最重要**。実際のキャプチャデータ（`captures/rfcomm_jobs/`）を使い、
  `protocol.build_print_command()` が実機へ送信された生バイト列を寸分違わず再現できるかを検証する回帰テスト。
- `test_image.py`: `image.py`（テキスト・画像の1bitビットマップ変換）の単体テスト
- `test_qr.py`: `qr.py`（QRコード生成・変換）の単体テスト

これらは全て**実機不要**（Bluetooth接続なし）で実行できる。

## 実機が必要なテスト（未実装・引き渡し先で実施予定）

- Bluetooth接続・切断・再接続（`printer/bluetooth.py`。追加ライブラリ不要、標準の`socket.AF_BLUETOOTH`を使用）
- 実際にプリンターへ送信して印字結果を確認するテスト

これらはBluetoothハードウェアとプリンター実機が必要なため、このセッション（クラウド環境、Bluetoothハードウェアなし）
では実行できていない。`docs/HANDOFF_README.md` に引き渡し後の実施手順を記載している。
