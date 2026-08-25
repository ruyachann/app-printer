# rfcomm_jobs/ について

`btsnoop_hci_2026-08-26.log`（文字テスト）と `btsnoop_hci_2026-08-26_qr.log`（QRテスト）から、
`tools/btsnoop_parser/extract_jobs.py` の考え方（ヘッダー `1D 47 59` から次のフッター
`1B 4A 50 1B BB BB 10 FF F1 45` の終端まで）で**正確に**切り出した、印刷ジョブ単位の生バイナリです。
各ファイルは `[Header 8B] + [Bitmap] + [Footer 10B]` のみを含み、ジョブ間の制御フレームなどの
余分なバイトは含みません（`tests/test_protocol_replay.py` で `printer/protocol.py` の
再現性を検証する際の正解データとして使用）。

## テスト項目との対応（確定・目視確認済み）

`captures/rendered/contact_sheet.png` で全ジョブをビットマップとしてレンダリングし、目視で内容を確認済み。

| ファイル | 印字内容 | 対応するテスト項目 |
|---|---|---|
| job_00.bin | A | T01 |
| job_01.bin | B | T02 |
| job_02.bin | AB | T03 |
| job_03.bin | Hello | T05（先に印字された） |
| job_04.bin | 1234567890 | T06 |
| job_05.bin | あ | T07 |
| job_06.bin | あいうえお | T08 |
| job_07.bin | 1234567890 | 再送信（給紙トラブルシューティング中） |
| job_08.bin | A | 再送信 |
| job_09.bin | B | 再送信 |
| job_10.bin | AB | 再送信 |
| job_11.bin | ABC | T04 |
| job_12.bin | Hello | 再送信 |
| job_13.bin | 1234567890 | 再送信 |
| job_14.bin | あ | 再送信 |
| job_15.bin | あいうえお | 再送信 |
| job_16.bin | ABC123 | Q01 |
| job_17.bin | https://example.com（の文字表示） | Q03 |
| qr_ABC123.bin | QRコード「ABC123」 | Q02 |
| qr_url.bin | QRコード「https://example.com」 | Q04 |

いずれも文字数・種類（英数字/日本語/QR）を問わず全て同一のヘッダー・フッター形式（`docs/protocol_spec.md` 参照）。

## ファイルサイズ

文字ジョブは全て **4434 bytes固定**（384×92pxの固定キャンバス）。QRジョブは内容に応じて可変
（qr_ABC123.bin=56658 bytes、qr_url.bin=45714 bytes）。
