#!/usr/bin/env python3
"""現在の接続経路（PrinterConnection、Windowsではpyserial経由のCOMポート）を使って、
captures/rfcomm_jobs/ 配下の実キャプチャデータをそのまま再送信するテスト。

これまで「実データをそのまま再送信すれば常に正しく1つだけ印字される」という結論を
プロトコル解析の初期段階で確認していたが、その後Windowsの生ソケット接続が使えないと
判明し、PrinterConnectionをpyserial経由のCOMポート接続に切り替えた。この切り替え後の
現在の送信経路で、実データの再送信が今も正しく1つだけ印字されるかどうかは、
実は再検証されていない可能性がある。もし現在の経路で実データすら4分割されるようなら、
原因はビットマップの中身ではなく送信経路（チャンク分割・チャンク間ディレイ等）にあると
判明する。

使い方:
    python tools/experiments/replay_test.py COM4 captures/rfcomm_jobs/job_00.bin
    python tools/experiments/replay_test.py COM4 captures/rfcomm_jobs/qr_ABC123.bin
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from printer.bluetooth import PrinterConnection


def main() -> None:
    if len(sys.argv) != 3:
        print("使い方: python tools/experiments/replay_test.py <COMポート> <captureファイル>")
        sys.exit(1)

    address, path = sys.argv[1], sys.argv[2]
    data = Path(path).read_bytes()
    print(f"[replay_test] {path} を読み込みました（{len(data)} bytes）")

    conn = PrinterConnection(address)
    print(f"[replay_test] {address} に接続します...")
    conn.connect()
    try:
        print("[replay_test] 送信中（現在のPrinterConnection.write()をそのまま使用）...")
        conn.write(data)
        print("[replay_test] 送信完了。プリンターの印字結果を確認してください。")
    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
