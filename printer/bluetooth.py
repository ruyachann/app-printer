"""Bluetooth Classic (RFCOMM/SPP) 接続・切断・送信を担当するモジュール。

通信解析の結果、このプリンターはBLEではなくBluetooth Classic（RFCOMM/SPP）を使用することが
確定した（docs/bluetooth_gatt.md参照）。そのためbleak（BLE専用）は使用しない。

接続方式は環境により2通り対応する:

- Linux等: Python標準ライブラリの `socket.AF_BLUETOOTH`（RFCOMM）でMACアドレスへ直接接続
- Windows: Bluetoothデバイスのドライバーが認識されない場合があり、生ソケット接続が
  タイムアウトすることがある。その場合はWindowsが自動生成する仮想COMポート
  （「Bluetoothリンク経由の標準シリアル」、デバイスマネージャーの「ポート(COMとLPT)」で確認可能）
  経由で `pyserial` を使って接続する方が確実。

`address` に `COM3` のようなCOMポート名を渡すとpyserial経由、それ以外（MACアドレス）を渡すと
`socket.AF_BLUETOOTH` 経由で接続する。
"""

import re

from .protocol import RFCOMM_CHUNK_SIZE, split_packets

DEFAULT_RFCOMM_PORT = 1  # captures上のRFCOMM DLCI=2 (チャネル1相当) から確定。SDPレスポンスでも確認済み
DEFAULT_BAUDRATE = 115200  # Bluetooth SPPの仮想COMポートでは実際のシリアル速度には影響しない

_COM_PORT_RE = re.compile(r"^COM\d+$", re.IGNORECASE)


class PrinterConnection:
    def __init__(self, address: str, port: int = DEFAULT_RFCOMM_PORT):
        self.address = address
        self.port = port
        self._sock = None
        self._is_serial = bool(_COM_PORT_RE.match(address))

    def connect(self) -> None:
        if self._is_serial:
            import serial
            self._sock = serial.Serial(self.address, DEFAULT_BAUDRATE, timeout=5)
        else:
            import socket
            self._sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self._sock.connect((self.address, self.port))

    def disconnect(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    @property
    def is_connected(self) -> bool:
        return self._sock is not None

    def write(self, data: bytes, chunk_size: int = RFCOMM_CHUNK_SIZE) -> None:
        if self._sock is None:
            raise RuntimeError("not connected")
        for chunk in split_packets(data, chunk_size):
            self._sock.write(chunk) if self._is_serial else self._sock.send(chunk)

    def __enter__(self) -> "PrinterConnection":
        self.connect()
        return self

    def __exit__(self, *exc_info) -> None:
        self.disconnect()
