# btsnoop_parser

Android の HCI Snoop Log（btsnoopファイル）を解析するための自作スクリプト群です。
外部ライブラリ（scapy等）を使わず、標準ライブラリのみで btsnoop → HCI → L2CAP → RFCOMM をパースします。

Wiresharkが手元になくても、この場（Claude）でログをアップロードしてもらえれば直接解析できるようにするために作成しました。

## スクリプト

### `parse_btsnoop.py`
btsnoopファイル全体をパースし、L2CAPチャネル(CID)ごとのPDU数、HCIコマンド/イベントの一覧、
CID 0x0004（ATT/GATT、BLE用）に流れたPDUを表示します。

```bash
python3 parse_btsnoop.py <btsnoop_hci.log>
```

ATT PDUが0件で、RFCOMM関連のL2CAPチャネルにデータが流れている場合、
そのプリンターは **BLEではなくBluetooth Classic（RFCOMM/SPP）** で通信しています。

### `parse_rfcomm.py`
指定したCIDのL2CAP PDUをRFCOMMフレームとしてデコードし、DLCI・フレーム種別（SABM/UA/UIH等）・
ペイロードのhex/ASCII表示を行います。

```bash
python3 parse_rfcomm.py <btsnoop_hci.log> [cid_hex ...]
# 例: python3 parse_rfcomm.py btsnoop_hci.log 0x51
```

引数を省略すると、PDU数が多い上位6チャネルを自動選択します。

### `extract_jobs.py`
RFCOMMデータチャネル（本プロジェクトでは CID 0x0051, DLCI=2 で確認）のUIHペイロードを結合し、
印刷ジョブのヘッダーマジックバイト（`1D 47 59`）でジョブ単位に分割して保存します。

```bash
python3 extract_jobs.py <btsnoop_hci.log> <output_dir>
```

## このプロジェクトでの解析結果（2026-08-26時点）

- Bluetooth方式: **Classic（RFCOMM/SPP）確定**。ATT PDUは0件。Android側では"BLE"を含む名前で見えることがあるが、実際の印刷データ通信はBLEではない
- RFCOMMチャネル確立: CID 0x0051 上で DLCI=0（制御チャネル）→ DLCI=2（データチャネル、RFCOMMチャネル1相当）の順にSABM/UA
- 印刷ジョブは全て同一ヘッダー `1D 47 59 04 30 00 17 00` で開始（詳細な意味は未解析、`docs/protocol_spec.md` 参照）
- ペイロードの大部分は `0x00` で、一部のみ非ゼロ → 1bitラスタービットマップの特徴と一致。**文字は画像化されて送信されている可能性が高い**
- ジョブ末尾に `1B 4A 50 ...`（ESC/POSの `ESC J n` = 用紙送りコマンドに類似）を含むフッターあり
