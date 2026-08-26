"""実キャプチャデータを使った回帰テスト（実機不要）。

captures/rfcomm_jobs/ の実キャプチャから、ヘッダー生成ロジック（protocol.build_print_command）が
実際にプリンターへ送られたバイト列を寸分違わず再現できるかを検証する。
"""

from pathlib import Path

from printer.protocol import build_print_command, STRIDE

CAPTURES_DIR = Path(__file__).resolve().parent.parent / "captures" / "rfcomm_jobs"

# (キャプチャファイル名, 印字内容) -- captures/rendered/contact_sheet.png で目視確認済みの対応
CAPTURE_SAMPLES = [
    ("job_00.bin", "A"),
    ("job_01.bin", "B"),
    ("job_02.bin", "AB"),
    ("job_11.bin", "ABC"),
    ("job_16.bin", "ABC123"),
]


def _load_capture(name: str) -> bytes:
    return (CAPTURES_DIR / name).read_bytes()


def test_build_print_command_reproduces_captured_bytes():
    for filename, _label in CAPTURE_SAMPLES:
        captured = _load_capture(filename)
        header, bitmap, footer = captured[:8], captured[8:-10], captured[-10:]

        rebuilt = build_print_command(bitmap)

        assert rebuilt[:8] == header, f"{filename}: header mismatch"
        assert rebuilt[-10:] == footer, f"{filename}: footer mismatch"
        assert rebuilt == captured, f"{filename}: full byte-for-byte mismatch"


def test_text_capture_bitmap_dimensions_are_consistent():
    # このプリンターの1行テキストキャンバスは 384x23 (192 bytes/row x 23 rows) で固定
    for filename, _label in CAPTURE_SAMPLES:
        captured = _load_capture(filename)
        bitmap = captured[8:-10]
        assert len(bitmap) % STRIDE == 0
        rows = len(bitmap) // STRIDE
        assert rows == 23
