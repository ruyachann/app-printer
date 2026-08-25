"""qr.py の単体テスト（実機不要）。"""

from printer.protocol import WIDTH_BYTES
from printer.qr import generate_qr_bitmap


def test_generate_qr_bitmap_dimensions():
    bitmap = generate_qr_bitmap("https://example.com")
    assert len(bitmap) % WIDTH_BYTES == 0
    rows = len(bitmap) // WIDTH_BYTES
    assert rows % 4 == 0


def test_generate_qr_bitmap_has_black_pixels():
    bitmap = generate_qr_bitmap("ABC123")
    assert any(b != 0 for b in bitmap)


def test_generate_qr_bitmap_longer_data_not_smaller_module_count():
    short = generate_qr_bitmap("A")
    long = generate_qr_bitmap("A" * 200)
    # 内容が長いほどQRのバージョン（モジュール数）は大きくなるはず
    assert len(long) >= len(short)
