# Bluetooth / GATT 解析結果（Phase 6-7）

Wiresharkでの解析結果をもとに記入します。手順書 Phase 6（GATT・Write先を特定）に対応。

## 接続方式

| 項目 | 内容 |
|---|---|
| Bluetooth方式 | 未確認（Classic / BLE） |
| 接続手順（ペアリング要否など） | 未確認 |
| MTUサイズ | 未確認 |
| Notification/Indicationの有無 | 未確認 |

## GATT情報（BLEの場合）

| 項目 | 内容 |
|---|---|
| Service UUID | 未確認 |
| Write Characteristic UUID | 未確認 |
| Write方式（Write Request / Write Command） | 未確認 |
| Notify Characteristic UUID（あれば） | 未確認 |

## 接続シーケンス（判明した順に記載）

```text
1. （例）スキャンでデバイス発見
2. （例）接続
3. （例）Service Discovery
4. （例）Write Characteristicへ書き込み開始
```

## 備考・気づき

（Wireshark上で気づいた点、パケットのパターンなどを自由に記載）
