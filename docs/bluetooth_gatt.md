# Bluetooth 通信解析結果（Phase 6-7）

`btsnoop_hci_2026-08-26.log`（Phase 4テスト印刷時のキャプチャ）を
`tools/btsnoop_parser/` の自作スクリプトで解析した結果です。手順書 Phase 6（GATT・Write先を特定）に対応。

## 接続方式（確定）

| 項目 | 内容 |
|---|---|
| Bluetooth方式 | **Bluetooth Classic（確定）**。BLE/GATTのATT PDU（CID 0x0004）は全キャプチャ中0件 |
| プロファイル | **SPP（Serial Port Profile）**。SDPレスポンスに文字列「SPP slave」を確認 |
| トランスポート | RFCOMM（L2CAP上のシリアル通信プロトコル） |
| 備考 | Android側では `PPS1_DD4C_BLE` と"BLE"を含む名前で見えていたが、実際の印刷データ通信はBLEではなくClassicのRFCOMM/SPPだった。2026-08-26、Windows側でペアリング済みデバイス名を確認したところ `PPS1_DD4C`（"_BLE"接尾辞なし）と表示されており、同一機器でもOS・discovery経路によって表示名が異なることが分かった（Classic Bluetoothとしての機器名自体には元々"BLE"は含まれていなかった可能性が高い） |

## GATT情報（BLEの場合）→ 該当なし

このプリンターはBLE/GATTを使用していないため、Service UUID・Characteristic UUID等は該当しません。

## RFCOMM接続シーケンス（確認済み）

```text
1. L2CAP接続要求（PSM=0x0001, SDP）→ SDPでサービス検索、"SPP slave"を確認
2. L2CAP接続要求（PSM=0x0003, RFCOMM）
3. RFCOMM: DLCI=0（マルチプレクサ制御チャネル）で SABM → UA
4. RFCOMM: DLCI=2（データチャネル、RFCOMMチャネル1相当）で SABM → UA
5. 以降、DLCI=2 の UIH（Unnumbered Information with Header check）フレームで印刷データを送信
```

解析に使用したCID: **0x0051**（このキャプチャセッションでは、全ての印刷ジョブがこの1本のRFCOMM接続の中で連続して送信されていた）

## 印刷データの構造（概要、詳細は protocol_spec.md 参照）

- 各印刷ジョブは同一のヘッダー `1D 47 59 04 30 00 17 00` で開始
- ペイロードの大半が `0x00`（白）で、一部のみ非ゼロ（黒） → 1bitラスタービットマップと推定
- ジョブ末尾に `1B 4A 50 ...`（ESC/POSの `ESC J n` に類似したフッター）

## 備考・気づき

- ジョブとジョブの間に、短い制御フレーム（例: `01 10 ff`, `01 10 ff f1`）が挟まる。ステータス確認/ポーリングの可能性
- 1回のキャプチャセッションで18件の印刷ジョブを検出（テスト計画は10件だったため、給紙トラブルシューティング中の再送信を含む可能性。`captures/rfcomm_jobs/README.md` 参照）
