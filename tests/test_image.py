"""image.py の単体テスト（実機不要）。"""

from PIL import Image

from printer.image import text_to_bitmap, to_1bit_bitmap
from printer.protocol import WIDTH_BYTES


def test_text_to_bitmap_dimensions():
    bitmap = text_to_bitmap("Hello")
    assert len(bitmap) % WIDTH_BYTES == 0
    rows = len(bitmap) // WIDTH_BYTES
    assert rows % 4 == 0
    assert rows > 0


def test_text_to_bitmap_nonempty_has_black_pixels():
    bitmap = text_to_bitmap("A")
    assert any(b != 0 for b in bitmap), "printed text should contain black pixels"


def test_to_1bit_bitmap_resizes_to_width():
    img = Image.new("L", (100, 50), 128)
    bitmap = to_1bit_bitmap(img)
    assert len(bitmap) % WIDTH_BYTES == 0


def test_to_1bit_bitmap_all_white_is_empty():
    img = Image.new("L", (384, 8), 255)
    bitmap = to_1bit_bitmap(img, dither=False)
    assert all(b == 0 for b in bitmap)


def test_to_1bit_bitmap_all_black_is_full():
    img = Image.new("L", (384, 8), 0)
    bitmap = to_1bit_bitmap(img, dither=False)
    assert all(b == 0xFF for b in bitmap)
