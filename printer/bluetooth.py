"""Bluetooth Classic (RFCOMM/SPP) 接続・切断・送信を担当するモジュール。

通信解析の結果、このプリンターはBLEではなくBluetooth Classic（RFCOMM/SPP）を使用することが
確定した（docs/bluetooth_gatt.md参照）。そのためbleak（BLE専用）ではなく、
PyBluez（pybluezライブラリ、モジュール名は `bluetooth`）でClassic RFCOMM接続を行う。

PyBluezはLinux/Windowsで動作するが、macOSでは別対応が必要な場合がある。未検証。
"""

import bluetooth  # PyBluez

from .protocol import RFCOMM_CHUNK_SIZE, split_packets

SPP_UUID = "00001101-0000-1000-8000-00805f9b34fb"
DEFAULT_RFCOMM_PORT = 1  # SDP検索に失敗した場合のフォールバック（キャプチャ上のDLCI=2から推定）


class PrinterConnection:
    def __init__(self, address: str):
        self.address = address
        self._sock: bluetooth.BluetoothSocket | None = None

    def connect(self) -> None:
        port = self._discover_rfcomm_port() or DEFAULT_RFCOMM_PORT
        self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._sock.connect((self.address, port))

    def _discover_rfcomm_port(self) -> int | None:
        services = bluetooth.find_service(address=self.address, uuid=SPP_UUID)
        if services:
            return services[0]["port"]
        return None

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
