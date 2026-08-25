# GKEミニサーマルプリンター 通信解析・Python実装 作業手順書

## 1. 目的

専用Androidアプリを解析し、GKEミニサーマルプリンターとのBluetooth通信プロトコルを特定する。

最終成果物は**PC上で動作するPythonプログラム**とする。

Android専用アプリの開発は行わない。

最終的なPython側の利用イメージ：

```python
printer.connect()

printer.print_text("Hello")
printer.print_qr("https://example.com")
printer.print_image("photo.png")

printer.disconnect()
```

---

# 2. 最終目標

Pythonから以下の3種類を印刷できる状態を目標とする。

- 文字
- QRコード
- 画像

ただし、プリンターが文字やQRコードを専用コマンドとして受け付けるとは仮定しない。

以下の可能性をすべて調査する。

```text
方式A：文字を直接送信
方式B：QRコードを専用コマンドで送信
方式C：文字を画像化して送信
方式D：QRコードを画像化して送信
方式E：画像をプリンター独自形式に変換して送信
方式F：上記の組み合わせ
```

特に、**文字とQRコードが最終的に1bit画像へ変換されて送信されている可能性**を考慮する。

---

# 3. 全体工程

```text
Phase 1
対象機器・環境確認
        ↓
Phase 2
Bluetooth方式確認
        ↓
Phase 3
Android HCI Snoop Logで通信記録
        ↓
Phase 4
HCIログをPCへ取得
        ↓
Phase 5
Wiresharkで通信解析
        ↓
Phase 6
GATT・Write先を特定
        ↓
Phase 7
文字通信を解析
        ↓
Phase 8
QRコード通信を解析
        ↓
Phase 9
画像通信を解析
        ↓
Phase 10
プリンタープロトコルを仕様化
        ↓
Phase 11
Python + Bleakで再実装
        ↓
Phase 12
文字・QR・画像をPythonから印刷
        ↓
Phase 13
安定性・互換性テスト
```

---

# 4. Phase 1：対象機器・環境確認

## 4.1 必要なもの

- GKEミニサーマルプリンター
- Androidスマートフォン
- 純正/専用Androidアプリ
- Windows/macOS/Linux PC
- USBケーブル
- Wireshark
- ADB
- Python 3
- Python `bleak`
- Python `Pillow`
- Python QRコード生成ライブラリ

## 4.2 プリンター情報を記録

```text
メーカー：
製品名：
型番：
Bluetoothデバイス名：
MACアドレス：
専用アプリ名：
Androidバージョン：
スマートフォン機種：
```

本体・箱・説明書に記載された型番も確認する。

---

# 5. Phase 2：Bluetooth方式を確認

まずBluetooth ClassicかBLEかを確認する。

```text
Bluetooth Classic
        または
BLE
```

以降のステップはBLE前提

---

# 6. Phase 3：Androidで通信を記録

## 6.1 Bluetooth HCI Snoop Logを有効化

Androidの開発者向けオプションを有効にする。

```text
設定
 ↓
端末情報
 ↓
ビルド番号を複数回タップ
 ↓
開発者向けオプション
```

その後、

```text
Bluetooth HCI snoop log
```

をONにする。

端末によって名称は異なる。

設定後、BluetoothをOFF/ONする。

---

# 7. Phase 4：通信キャプチャ用テスト

重要なのは、**1回の印刷で変更する要素をできるだけ1つにすること**。

## 7.1 文字テスト

```text
T01: A
T02: B
T03: AB
T04: ABC
T05: Hello
T06: 1234567890
T07: あ
T08: あいうえお
```

---

# 8. QRコードテスト

**同じ内容を文字とQRの両方で印刷する。**

```text
Q01
文字：ABC123

Q02
QR：ABC123

Q03
文字：https://example.com

Q04
QR：https://example.com
```

これらの通信を比較する。

---

# 9. 画像テスト

画像は通信方式を特定するために重要。

```text
I01：全白
I02：黒1ドット
I03：黒い横線
I04：黒い縦線
I05：黒い四角
I06：小さな白黒画像
```

---

# 10. Phase 5：HCIログをPCへ取得

Androidでバグレポートを取得する。

```text
設定
 ↓
開発者向けオプション
 ↓
バグレポート
```

またはADBを使用する。

```bash
adb devices
```

端末が認識されていることを確認する。

取得したHCI Snoop LogをPCへ保存する。

---

# 11. Phase 6：Wiresharkで通信解析

Wiresharkは今回、Androidで既に記録したHCIログを解析するために使用する。

役割：

```text
Android
 ↓
Bluetooth HCI Snoop Logを記録
 ↓
PC
 ↓
Wiresharkでログを開く
 ↓
Bluetoothパケットを解析
```

Wiresharkで主に確認するもの：

```text
Bluetooth HCI
Bluetooth ACL
ATT
GATT
```

BLEの場合は、

```text
ATT Write Request
ATT Write Command
```

を重点的に確認する。

---

# 12. Phase 7：GATT通信を特定

以下を特定する。

```text
Service UUID
Characteristic UUID
Write方式
MTU
Notificationの有無
接続手順
```

作業記録例：

```text
Service UUID:
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Write Characteristic:
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Write Type:
Write Without Response
```

---

# 13. Phase 8：印刷データを抽出

Wiresharkからプリンター方向のWrite通信を抽出する。

例えば以下を個別に保存する。

```text
T01_A
T02_B
T03_AB
Q01_TEXT
Q02_QR
I02_DOT
I03_LINE
```

推奨ディレクトリ：

```text
captures/
├── text_A/
├── text_B/
├── text_AB/
├── qr_text/
├── qr_code/
├── image_dot/
├── image_line/
└── image_square/
```

---

# 14. Phase 9：文字通信を解析

文字の通信を比較する。

```text
A
B
AB
ABC
```

以下の変化を調べる。

```text
固定ヘッダー
コマンド
データ長
文字コード
画像データ
チェックサム
終端
```

---

# 15. 文字が画像化されているか確認

ここが重要。

`A` と `B` の通信データを比較し、文字コードのような値が見つからない場合は、文字が画像化されている可能性がある。

さらに、

```text
A
```

を印刷したデータと、

```text
黒い画像
```

を印刷したデータを比較する。

もし同じ画像転送形式が使われているなら、

```text
文字
 ↓
画像化
 ↓
1bit bitmap
 ↓
BLE
 ↓
プリンター
```

と判断できる。

---

# 16. Phase 10：QRコード通信を解析

最重要の比較：

```text
文字：
ABC123

QR：
ABC123
```

この2つの通信を比較する。

## パターンA：専用QRコマンド

例えば、

```text
[QR COMMAND]
[SIZE]
[ERROR CORRECTION]
[DATA LENGTH]
[ABC123]
```

のような構造が見つかった場合、QR専用プロトコルとして実装する。

## パターンB：画像として送信

QRコード通信が画像データと同じ形式だった場合、

```text
ABC123
 ↓
QR生成
 ↓
Bitmap
 ↓
1bit化
 ↓
プリンター用画像形式
 ↓
BLE送信
```

として実装する。

**どちらなのかをキャプチャ比較によって判断する。**

---

# 17. QRコードが画像化されている場合

Python側ではQRコードを生成する。

```python
import qrcode

img = qrcode.make("https://example.com")
img.save("qr.png")
```

その後、

```text
qr.png
 ↓
Pillow
 ↓
プリンター幅に合わせる
 ↓
グレースケール
 ↓
1bit化
 ↓
プリンター独自bitmap形式
 ↓
BLE送信
```

とする。

---

# 18. Phase 11：画像プロトコルを解析

画像について、

```text
白紙
1ドット
横線
縦線
四角
```

のデータを比較する。

確認項目：

```text
画像幅
画像高さ
ビット深度
1bit / 8bit
白黒反転
横方向ビット順
縦方向ビット順
パケットサイズ
画像開始コマンド
画像終了コマンド
チェックサム
```

特に、

```text
8 pixels = 1 byte
```

のような1bit bitmap構造がないか確認する。

ただし、384pxなどの幅を最初から決めつけず、実際のキャプチャから特定する。

---

# 19. Phase 12：パケット分割を解析

BLEでは画像データが複数Writeに分割される可能性がある。

例：

```text
Packet 1
Header

Packet 2
Image data 1

Packet 3
Image data 2

Packet 4
Image data 3

Packet 5
Footer
```

確認項目：

- 1パケットの最大サイズ
- 分割単位
- シーケンス番号
- パケット番号
- 終端
- チェックサム
- ACK/Notificationの有無

---

# 20. Phase 13：プロトコル仕様書を作成

Python実装前に通信仕様を文書化する。

```markdown
# Printer Protocol

## Connection

Service UUID:
xxxx

Write Characteristic:
xxxx

Write Type:
Write Without Response

## Packet

Header:
2 bytes

Command:
1 byte

Length:
2 bytes

Payload:
N bytes

Checksum:
1 byte

## Image

Width:
XXX pixels

Format:
1 bit monochrome

Byte order:
LSB first

Transport:
BLE
```

**不明な項目は推測で埋めず、「未確定」と記録する。**

---

# 21. Phase 14：Python環境

仮想環境を作る。

```bash
python -m venv venv
```

必要なライブラリをインストールする。

```bash
pip install bleak pillow qrcode
```

---

# 22. Phase 15：PythonからBLE接続

基本形：

```python
import asyncio
from bleak import BleakClient

ADDRESS = "XX:XX:XX:XX:XX:XX"
WRITE_UUID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

async def main():
    async with BleakClient(ADDRESS) as client:
        print("connected:", client.is_connected)

asyncio.run(main())
```

実際のUUIDは解析結果を使用する。

---

# 23. Phase 16：キャプチャデータをそのまま送る

最初からプロトコルを完全実装しない。

まず、

```text
純正アプリ
 ↓
Aを印刷
 ↓
通信をキャプチャ
 ↓
送信データを保存
 ↓
Pythonから同じデータを送信
```

を行う。

例：

```python
await client.write_gatt_char(
    WRITE_UUID,
    captured_data,
    response=False
)
```

Pythonから「A」が印刷できれば、Bluetooth通信の基本部分は再現できている。

---

# 24. Phase 17：Pythonプロトコル実装

推奨構造：

```text
gke_printer/
├── bluetooth.py
├── protocol.py
├── image.py
├── qr.py
├── printer.py
└── tests/
```

## bluetooth.py

Bluetooth接続・切断・Writeを担当。

## protocol.py

プリンター独自プロトコルを担当。

```text
create_header()
create_packet()
split_packet()
checksum()
```

## image.py

画像変換を担当。

```text
resize()
grayscale()
threshold()
to_1bit()
encode_bitmap()
```

## qr.py

QRコード生成を担当。

## printer.py

利用者向けAPIを担当。

---

# 25. 最終Python API

目標：

```python
printer.connect()

printer.print_text("Hello")

printer.print_qr("https://example.com")

printer.print_image("photo.png")

printer.disconnect()
```

---

# 26. 文字印刷の実装方針

解析結果によって2方式を実装可能にする。

## 方式1：文字コマンド

```python
printer.print_text("Hello")
```

↓

```text
プリンター文字コマンド
```

## 方式2：画像化

```python
printer.print_text("Hello")
```

↓

```text
Pillow
 ↓
文字画像
 ↓
1bit bitmap
 ↓
プリンター通信
```

**文字を画像化する方式も最初から実装可能な設計にする。**

---

# 27. QR印刷の実装方針

QRも2方式を想定する。

## 方式1：プリンターのQRコマンド

```python
printer.print_qr("https://example.com")
```

↓

```text
QR command
```

## 方式2：QRを画像化

```python
printer.print_qr("https://example.com")
```

↓

```text
QR生成
 ↓
Pillow
 ↓
1bit bitmap
 ↓
画像印刷プロトコル
```

解析結果に応じて内部実装を切り替える。

---

# 28. 画像印刷

```python
printer.print_image("photo.png")
```

内部：

```text
画像
 ↓
リサイズ
 ↓
グレースケール
 ↓
2値化
 ↓
1bit bitmap
 ↓
プリンター形式
 ↓
BLE送信
```

---

# 29. 文字＋QRの複合印刷

最終的には、

```python
printer.print_text("注文番号: ABC123")
printer.print_qr("https://example.com/order/ABC123")
```

のように連続印刷できる状態を目標とする。

また、文字とQRを1枚の画像に合成して送信する方式も考慮する。

```text
┌─────────────────────┐
│ 注文番号: ABC123     │
│                     │
│       QRコード       │
│                     │
└─────────────────────┘
```

この場合は、

```text
文字
 ↓
QR生成
 ↓
1枚の画像へ合成
 ↓
1bit bitmap化
 ↓
画像印刷プロトコル
 ↓
BLE送信
```

となる。

---

# 30. どの方式を採用するか

優先順位：

1. 純正アプリと同じプロトコルを再現
2. 安定して印刷できる方式を採用
3. 文字・QR・画像で共通プロトコルが使えるなら共通化
4. QR専用コマンドがある場合は必要に応じて利用
5. 画像転送方式しかない場合はすべて画像化して送信

特に、**文字とQRを画像化して同じ画像プロトコルで送れるなら、Python側の実装が大幅に単純になる**。

---

# 31. テスト項目

## Bluetooth

- [ ] プリンターを検出できる
- [ ] 接続できる
- [ ] 再接続できる
- [ ] 切断を検知できる
- [ ] 接続失敗を処理できる

## 文字

- [ ] ASCII 1文字
- [ ] ASCII文章
- [ ] 数字
- [ ] 日本語1文字
- [ ] 日本語文章
- [ ] 改行
- [ ] 長文

## QR

- [ ] 短い文字列
- [ ] URL
- [ ] 長い文字列
- [ ] QRサイズ変更
- [ ] 誤り訂正レベル
- [ ] QRの印刷品質確認

## 画像

- [ ] 1ドット
- [ ] 横線
- [ ] 縦線
- [ ] 白黒画像
- [ ] 写真
- [ ] 大きな画像
- [ ] プリンター幅を超える画像

## 複合

- [ ] 文字 → QR
- [ ] QR → 文字
- [ ] 文字＋QRを1枚の画像として印刷
- [ ] 文字＋QR＋画像を1枚の画像として印刷

---

# 32. 成果物

最終的に以下を残す。

```text
gke_printer/
│
├── docs/
│   ├── device_info.md
│   ├── bluetooth_gatt.md
│   └── protocol_spec.md
│
├── captures/
│   ├── text_A/
│   ├── text_B/
│   ├── text_AB/
│   ├── qr_text/
│   ├── qr_code/
│   ├── image_dot/
│   ├── image_line/
│   └── image_square/
│
├── printer/
│   ├── bluetooth.py
│   ├── protocol.py
│   ├── image.py
│   ├── qr.py
│   └── printer.py
│
├── tests/
│   ├── test_text.py
│   ├── test_qr.py
│   └── test_image.py
│
└── README.md
```

---

# 33. 完了条件

## 通信解析

- [ ] Bluetooth方式を特定
- [ ] Service UUIDを特定
- [ ] Write Characteristicを特定
- [ ] 接続手順を特定
- [ ] 印刷開始コマンドを特定
- [ ] データ形式を特定
- [ ] パケット分割方式を特定
- [ ] チェックサムを特定（存在する場合）
- [ ] 画像形式を特定
- [ ] 文字が画像化されているか判定
- [ ] QRが専用コマンドか画像か判定

## Python

- [ ] Pythonから接続できる
- [ ] Pythonから切断できる
- [ ] Pythonから文字を印刷できる
- [ ] PythonからQRを印刷できる
- [ ] Pythonから画像を印刷できる
- [ ] 文字＋QRを印刷できる
- [ ] 再接続できる
- [ ] 通信エラーを処理できる

---

# 34. 最初に作業者がやること

最初は以下だけ実施する。

```text
1. Androidで開発者向けオプションを有効化
2. Bluetooth HCI snoop logをON
3. 専用アプリを起動
4. プリンターへ接続
5. 「A」を印刷
6. 「B」を印刷
7. 「AB」を印刷
8. 「ABC123」を通常の文字として印刷
9. 「ABC123」をQRコードとして印刷
10. 単純な黒1ドット画像を印刷
11. 黒い横線画像を印刷
12. HCIログ/バグレポートを取得
13. PCへ保存
14. Wiresharkでログを開く
15. ATT Write通信を探す
16. プリンターへ送られたデータを抽出
```

**この段階ではPython実装を始めない。**

まず、

```text
文字
QR
画像
```

の3種類の通信を比較する。

その結果から、

```text
「文字・QRも画像として送られている」
```

のか、

```text
「文字・QR・画像で別々のコマンドがある」
```

のかを確定させる。

それからPythonプロトコルを実装するのが最短かつ確実な進め方である。
