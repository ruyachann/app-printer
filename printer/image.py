"""画像・テキストをプリンター用1bitビットマップに変換するモジュール。

docs/protocol_spec.md の確定仕様: 幅384px（48 bytes/row）、1bit、MSBファースト、bit=1が黒。
行数（高さ）は4の倍数である必要がある（protocol.build_print_command 参照）。
"""

from PIL import Image, ImageDraw, ImageFont

from .protocol import WIDTH_BYTES, WIDTH_PX


def _pad_height_to_multiple_of_4(img: Image.Image, fill: int = 255) -> Image.Image:
    height = img.height
    remainder = height % 4
    if remainder == 0:
        return img
    pad = 4 - remainder
    padded = Image.new("L", (img.width, height + pad), fill)
    padded.paste(img, (0, 0))
    return padded


def to_1bit_bitmap(image: Image.Image, dither: bool = True) -> bytes:
    """PIL画像をプリンター用1bitビットマップに変換する（幅384pxにリサイズ）。"""
    if image.width != WIDTH_PX:
        ratio = WIDTH_PX / image.width
        new_height = max(1, round(image.height * ratio))
        image = image.resize((WIDTH_PX, new_height))

    gray = image.convert("L")
    gray = _pad_height_to_multiple_of_4(gray)

    method = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    mono = gray.convert("1", dither=method)  # PIL: 1=white, 0=black

    out = bytearray(WIDTH_BYTES * mono.height)
    px = mono.load()
    for y in range(mono.height):
        row_offset = y * WIDTH_BYTES
        for x in range(WIDTH_PX):
            if px[x, y] == 0:  # black pixel
                out[row_offset + (x // 8)] |= 0x80 >> (x % 8)
    return bytes(out)


def text_to_bitmap(text: str, font: ImageFont.FreeTypeFont | None = None,
                    line_spacing: int = 4, margin: int = 4) -> bytes:
    """文字列を描画して1bitビットマップに変換する。"""
    if font is None:
        font = ImageFont.load_default()

    lines = text.split("\n") or [""]
    dummy = Image.new("L", (WIDTH_PX, 10), 255)
    draw = ImageDraw.Draw(dummy)
    line_heights = []
    max_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
        max_width = max(max_width, bbox[2] - bbox[0])

    total_height = sum(line_heights) + line_spacing * (len(lines) - 1) + margin * 2
    canvas = Image.new("L", (WIDTH_PX, max(1, total_height)), 255)
    draw = ImageDraw.Draw(canvas)
    y = margin
    for line, h in zip(lines, line_heights):
        draw.text((margin, y), line, fill=0, font=font)
        y += h + line_spacing

    return to_1bit_bitmap(canvas, dither=False)
