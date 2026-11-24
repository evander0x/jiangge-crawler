#!/usr/bin/env python3
"""
在 AI 生成的无文字简笔画图片上叠加中文手写体文字。

用法：
    # 普通页（顶部居中，字号自动按比例适配）
    python3 overlay_text.py img.png "小耗子很喜欢射箭"

    # 最后一页（垂直居中，带双引号，字号 +10%）
    python3 overlay_text.py img.png "好想马上见到你" --last

    # 指定输出路径 / 手动覆盖字号（不填则自动计算）
    python3 overlay_text.py img.png "你好" out.png 60
    python3 overlay_text.py img.png "你好" out.png 60 --last
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = str(Path(__file__).resolve().parent / "fonts" / "平方时光体.ttf")
FALLBACK_FONTS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]
BASE_FONT_SIZE = 60          # 1000px 基准字号
LAST_PAGE_SCALE = 1.1
TEXT_MAX_WIDTH_RATIO = 0.84


def wrap_text(text: str, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """按语义标点优先、画布宽度兜底，为中文旁白自动换行。"""
    punctuation = "，。！？；：、,!?;:"
    wrapped = []
    for paragraph in text.split("\n"):
        line = ""
        for char in paragraph:
            candidate = line + char
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if line and bbox[2] - bbox[0] > max_width:
                # 优先在最近的语义停顿后换行，避免标点落在下一行行首。
                break_at = max((i for i, c in enumerate(line) if c in punctuation), default=-1)
                if break_at >= 0:
                    wrapped.append(line[:break_at + 1])
                    line = line[break_at + 1:] + char
                else:
                    wrapped.append(line)
                    line = char
            else:
                line = candidate
        wrapped.append(line)
    return "\n".join(wrapped)


def get_font_path() -> str:
    if Path(FONT_PATH).is_file():
        return FONT_PATH
    for p in FALLBACK_FONTS:
        if Path(p).is_file():
            return p
    raise FileNotFoundError(f"未找到可用字体，请安装字体后重试。尝试路径：{[FONT_PATH] + FALLBACK_FONTS}")


def calc_font_size(image_height: int) -> int:
    """按图片实际高度等比缩放字号 → 文字约占图高 7%"""
    return int(BASE_FONT_SIZE * image_height / 1000)


def overlay_text(
    image_path: str,
    text: str,
    output_path: str | None = None,
    font_size: int | None = None,
    is_last: bool = False,
):
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size

    if font_size is None:
        font_size = calc_font_size(h)

    # 最后一页：字号放大 10%，自动加中文双引号
    if is_last:
        font_size = int(font_size * LAST_PAGE_SCALE)
        if not (text.startswith("\u201c") and text.endswith("\u201d")):
            text = "\u201c" + text + "\u201d"

    font = ImageFont.truetype(get_font_path(), font_size)
    draw = ImageDraw.Draw(img)
    spacing = max(8, int(font_size * 0.45))
    text = wrap_text(text, draw, font, int(w * TEXT_MAX_WIDTH_RATIO))
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if is_last:
        # 最后一页：垂直居中
        x = (w - text_w) // 2 - bbox[0]
        y = (h - text_h) // 2 - bbox[1]
    else:
        # 普通页：顶部居中，距顶部约 18%
        x = (w - text_w) // 2 - bbox[0]
        y = int(h * 0.18) - bbox[1]

    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=(0, 0, 0, 255),
        spacing=spacing,
        align="center",
    )

    if output_path is None:
        p = Path(image_path)
        output_path = str(p.with_name(p.stem + "_text" + p.suffix))

    output = Path(output_path)
    rgb_img = img.convert("RGB")
    if output.suffix.lower() in {".jpg", ".jpeg"}:
        rgb_img.save(output, "JPEG", quality=95)
    elif output.suffix.lower() == ".webp":
        rgb_img.save(output, "WEBP")
    else:
        rgb_img.save(output, "PNG")
    print(f"已保存：{output_path}  (字号 {font_size}pt, {'最后一页·居中' if is_last else '顶部居中'})")


if __name__ == "__main__":
    args = sys.argv[1:]

    is_last = "--last" in args
    if is_last:
        args.remove("--last")

    if len(args) < 2:
        print(__doc__)
        sys.exit(1)

    image_path = args[0]
    text = args[1]
    output_path = args[2] if len(args) > 2 else None
    font_size = int(args[3]) if len(args) > 3 else None

    overlay_text(image_path, text, output_path, font_size, is_last)
