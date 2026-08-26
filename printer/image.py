"""画像・テキストをプリンター用4階調グレースケールビットマップに変換するモジュール。

docs/protocol_spec.md の確定仕様: 幅384px、1バイトに2画素（4bit/画素、値0〜3）、
192バイト/行。詳細は protocol.py のモジュールdocstring参照。

【2026-08-26】以前このモジュールは「1bit白黒」として実装されており、これが自前生成画像が
紙面に横4分割されて印字される既知の不具合の根本原因だった（APK逆コンパイルにより判明）。
正しい4階調グレースケール形式に全面的に修正済み。
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .protocol import GRAY_LEVELS, STRIDE, WIDTH_PX

_MAX_LEVEL = GRAY_LEVELS - 1  # 3
_STEP = 255.0 / _MAX_LEVEL


def to_gray4_bitmap(image: Image.Image, dither: bool = False) -> bytes:
    """PIL画像をプリンター用4階調グレースケールビットマップに変換する（幅384pxにリサイズ）。"""
    if image.width != WIDTH_PX:
        ratio = WIDTH_PX / image.width
        new_height = max(1, round(image.height * ratio))
        image = image.resize((WIDTH_PX, new_height))

    gray = image.convert("L")
    height = gray.height
    arr = np.asarray(gray, dtype=np.float64).copy()

    if dither:
        for y in range(height):
            for x in range(WIDTH_PX):
                old = arr[y, x]
                level = min(_MAX_LEVEL, max(0, round(old / _STEP)))
                new_val = level * _STEP
                err = old - new_val
                arr[y, x] = new_val
                if x + 1 < WIDTH_PX:
                    arr[y, x + 1] += err * 7 / 16
                if y + 1 < height:
                    if x - 1 >= 0:
                        arr[y + 1, x - 1] += err * 3 / 16
                    arr[y + 1, x] += err * 5 / 16
                    if x + 1 < WIDTH_PX:
                        arr[y + 1, x + 1] += err * 1 / 16

    levels = np.clip(np.round(arr / _STEP), 0, _MAX_LEVEL).astype(np.uint8)
    nibbles = _MAX_LEVEL - levels  # 明るい(白)=0, 暗い(黒)=_MAX_LEVEL

    hi = nibbles[:, 0::2]
    lo = nibbles[:, 1::2]
    packed = (hi << 4) | lo
    assert packed.shape[1] == STRIDE
    return packed.tobytes()


DEFAULT_FONT_SIZE = 72  # 実機テストで56pxは読めるが小さめとのフィードバックを受けて拡大

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
    """文字列を描画して4階調グレースケールビットマップに変換する（幅384pxに収まるよう自動折り返し）。"""
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

    return to_gray4_bitmap(canvas, dither=False)
