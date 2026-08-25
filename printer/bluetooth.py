"""Bluetooth Classic (RFCOMM/SPP) 接続・切断・送信を担当するモジュール。

通信解析の結果、このプリンターはBLEではなくBluetooth Classic（RFCOMM/SPP）を使用することが
確定した（docs/bluetooth_gatt.md参照）。そのためbleak（BLE専用）ではなく、
**Python標準ライブラリの `socket.AF_BLUETOOTH`（RFCOMM）を直接使用する。**
外部ライブラリ（pybluez等）は不要。LinuxとWindows（公式Pythonビルド）の両方で動作する。
macOSは標準のsocketモジュールがBluetoothに未対応のため、別途対応が必要。

Windowsで接続する場合、事前にWindowsの「Bluetoothとその他のデバイス」設定でプリンターを
ペア設定（PIN不要な機種が多いが、ペアリング自体は必要）しておく必要がある。
"""

import socket

from .protocol import RFCOMM_CHUNK_SIZE, split_packets

DEFAULT_RFCOMM_PORT = 1  # captures上のRFCOMM DLCI=2 (チャネル1相当) から確定


class PrinterConnection:
    def __init__(self, address: str, port: int = DEFAULT_RFCOMM_PORT):
        self.address = address
        self.port = port
        self._sock: socket.socket | None = None

    def connect(self) -> None:
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
            self._sock.send(chunk)

    def __enter__(self) -> "PrinterConnection":
        self.connect()
        return self

    def __exit__(self, *exc_info) -> None:
        self.disconnect()
