# Bluetooth接続・切断・Writeを担当するモジュール（Phase 15-17で実装予定）
#
# 通信解析の結果、このプリンターはBLEではなくBluetooth Classic（RFCOMM/SPP）を使用することが
# 確定した（docs/bluetooth_gatt.md参照）。そのためbleak（BLE専用）は使用せず、
# pybluez等のClassic Bluetooth RFCOMM対応ライブラリで実装する。
