"""利用者向けAPI。

使い方:

    printer = Printer("XX:XX:XX:XX:XX:XX")
    printer.connect()
    printer.print_text("Hello")
    printer.print_qr("https://example.com")
    printer.print_image("photo.png")
    printer.disconnect()

    # または
    with Printer("XX:XX:XX:XX:XX:XX") as printer:
        printer.print_text("Hello")
"""

from PIL import Image

from .bluetooth import PrinterConnection
from .image import text_to_bitmap, to_gray4_bitmap
from .protocol import build_print_command
from .qr import generate_qr_bitmap


class Printer:
    def __init__(self, address: str):
        self._conn = PrinterConnection(address)

    def connect(self) -> None:
        self._conn.connect()

    def disconnect(self) -> None:
        self._conn.disconnect()

    @property
    def is_connected(self) -> bool:
        return self._conn.is_connected

    def print_text(self, text: str) -> None:
        bitmap = text_to_bitmap(text)
        self._conn.write(build_print_command(bitmap))

    def print_qr(self, data: str) -> None:
        bitmap = generate_qr_bitmap(data)
        self._conn.write(build_print_command(bitmap))

    def print_image(self, path: str) -> None:
        image = Image.open(path)
        bitmap = to_gray4_bitmap(image)
        self._conn.write(build_print_command(bitmap))

    def __enter__(self) -> "Printer":
        self.connect()
        return self

    def __exit__(self, *exc_info) -> None:
        self.disconnect()
