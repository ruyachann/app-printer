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


DEFAULT_FONT_SIZE = 56  # 実キャプチャ(captures/rfcomm_jobs/job_00.bin、文字"A")の実測グリフ高さ(約45px)を参考に設定

# 日本語を含む文字列を印刷できるよう、主要OSにプリインストールされている日本語フォントを探す。
# 見つからない場合はPILの既定フォント（英数字のみ）にフォールバックする。
_JAPANESE_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
]


def _load_default_japanese_capable_font(size: int) -> ImageFont.ImageFont:
    for path in _JAPANESE_FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _wrap_line(line: str, font: ImageFont.ImageFont, draw: ImageDraw.ImageDraw, max_width: int) -> list[str]:
    """1行分のテキストを、幅max_widthに収まるよう単語単位で折り返す。

    英数字はスペース区切りで、日本語などスペースを含まない文字列は1文字ずつ詰めて折り返す。
    """
    if not line:
        return [""]

    def fits(s: str) -> bool:
        return draw.textbbox((0, 0), s, font=font)[2] <= max_width

    words = line.split(" ") if " " in line else list(line)
    sep = " " if " " in line else ""

    wrapped = []
    current = ""
    for word in words:
        candidate = current + sep + word if current else word
        if fits(candidate):
            current = candidate
        else:
            if current:
                wrapped.append(current)
            current = word
    if current:
        wrapped.append(current)
    return wrapped or [""]


def text_to_bitmap(text: str, font: ImageFont.ImageFont | None = None, font_size: int = DEFAULT_FONT_SIZE,
                    line_spacing: int = 4, margin: int = 4) -> bytes:
    """文字列を描画して1bitビットマップに変換する（幅384pxに収まるよう自動折り返し）。"""
    if font is None:
        font = _load_default_japanese_capable_font(font_size)

    dummy = Image.new("L", (WIDTH_PX, 10), 255)
    draw = ImageDraw.Draw(dummy)
    max_text_width = WIDTH_PX - margin * 2

    lines = []
    for raw_line in text.split("\n"):
        lines.extend(_wrap_line(raw_line, font, draw, max_text_width))

    line_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in lines]

    total_height = sum(line_heights) + line_spacing * (len(lines) - 1) + margin * 2
    canvas = Image.new("L", (WIDTH_PX, max(1, total_height)), 255)
    draw = ImageDraw.Draw(canvas)
    y = margin
    for line, h in zip(lines, line_heights):
        draw.text((margin, y), line, fill=0, font=font)
        y += h + line_spacing

    return to_1bit_bitmap(canvas, dither=False)
