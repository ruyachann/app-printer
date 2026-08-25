# 作業進捗トラッカー

このファイルは `GKE_thermal_printer_python_reverse_engineering_workflow.md` の手順書に沿った作業進捗を記録するものです。
更新の都度、日付・担当・決定事項を追記していきます。

参考: 元手順書は `docs/reference/GKE_thermal_printer_python_reverse_engineering_workflow.md` に保管しています。

---

## フェーズ進捗チェックリスト

| Phase | 内容 | 状態 | 備考 |
|---|---|---|---|
| 1 | 対象機器・環境確認 | 🟡 進行中 | `docs/device_info.md` に記入待ち |
| 2 | Bluetooth方式確認（Classic/BLE） | ⬜ 未着手 | |
| 3 | Android HCI Snoop Logで通信記録 | ⬜ 未着手 | |
| 4 | 通信キャプチャ用テスト実施（文字/QR/画像） | ⬜ 未着手 | |
| 5 | HCIログをPCへ取得 | ⬜ 未着手 | |
| 6 | Wiresharkで通信解析 | ⬜ 未着手 | |
| 7 | GATT・Write先を特定 | ⬜ 未着手 | `docs/bluetooth_gatt.md` |
| 8 | 印刷データ抽出（captures/配下） | ⬜ 未着手 | |
| 9 | 文字通信を解析 | ⬜ 未着手 | |
| 10 | 文字が画像化されているか判定 | ⬜ 未着手 | |
| 11 | QRコード通信を解析（専用コマンド or 画像） | ⬜ 未着手 | |
| 12 | 画像プロトコルを解析 | ⬜ 未着手 | |
| 13 | パケット分割方式を解析 | ⬜ 未着手 | |
| 14 | プロトコル仕様書作成 | ⬜ 未着手 | `docs/protocol_spec.md` |
| 15 | Python環境構築（venv, bleak, pillow, qrcode） | ⬜ 未着手 | |
| 16 | PythonからBLE接続確認 | ⬜ 未着手 | |
| 17 | キャプチャデータをそのまま送信して再現確認 | ⬜ 未着手 | |
| 18 | Pythonプロトコル実装（printer/配下） | ⬜ 未着手 | |
| 19 | 文字印刷実装 | ⬜ 未着手 | |
| 20 | QR印刷実装 | ⬜ 未着手 | |
| 21 | 画像印刷実装 | ⬜ 未着手 | |
| 22 | 複合印刷（文字+QR）実装 | ⬜ 未着手 | |
| 23 | テスト実施（tests/配下） | ⬜ 未着手 | |
| 24 | 引き渡し資料（README/HANDOFF）作成 | 🟡 進行中 | ドラフト作成済み、随時更新 |

凡例: ⬜ 未着手 / 🟡 進行中 / ✅ 完了 / ⚠️ ブロック中

---

## 決定事項ログ（Decisions Log）

作業を進める中で確定した事項をここに追記していきます。まだ何も確定していません。

| 日付 | 項目 | 決定内容 | 根拠 |
|---|---|---|---|
| - | - | まだ決定事項なし | - |

---

## 未確定事項（Open Questions）

- Bluetooth方式（Classic / BLE）: 未確認
- Service UUID / Write Characteristic UUID: 未確認
- 文字が画像化されているか: 未確認
- QRコードが専用コマンドか画像化か: 未確認
- 画像プロトコルの詳細（幅、bit深度、ビット順など）: 未確認

---

## 次にやるべきこと（Next Action）

現在のステップ: **Phase 1 - 対象機器・環境確認**

→ ユーザーへ質問中: `docs/device_info.md` の記入項目についてヒアリング中。
