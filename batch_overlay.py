#!/usr/bin/env python3
"""
批量叠加文字脚本：读取故事文件夹，把 raw/ 里的无文字图片叠上旁白，输出到 final/。

目录结构：
    story/stories/
    └── 鱼见泥/
        ├── raw/          ← 你放 AI 生成的无文字图 (01.png, 02.png, ...)
        ├── story.txt     ← 图编号 + 文字对应关系
        └── final/        ← 脚本自动生成，叠好文字的成品

用法：
    python3 batch_overlay.py 鱼见泥
    python3 batch_overlay.py 西换梨

story.txt 格式：
    图1
    从前有一条鱼
    图2
    在清澈的溪水里游来游去
    图7! 你知道为什么吗？      ← 加 ! 表示居中显示
    ...
"""
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).resolve().parent / "fonts" / "平方时光体.ttf"
FALLBACK_FONTS = [
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
]
BASE_DIR = Path(__file__).resolve().parent / "story" / "stories"
BASE_FONT_SIZE = 60         # 1000px 基准字号，实际按图片尺寸等比缩放
TARGET_HEIGHT_RATIO = 0.07  # 文字高度约占图高的 7%
LAST_PAGE_SCALE = 1.1


def wrap_text(text: str, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """优先按标点后的语义片段换行，再对超宽片段逐字换行。"""
    lines = []
    for paragraph in text.split("\n"):
        chunks = []
        current = ""
        for char in paragraph:
            current += char
            if char in "，。！？；：、,!?;:":
                chunks.append(current)
                current = ""
        if current:
            chunks.append(current)

        line = ""
        for chunk in chunks:
            if line and draw.textlength(line + chunk, font=font) <= max_width:
                line += chunk
                continue
            if line:
                lines.append(line)
                line = ""
            if draw.textlength(chunk, font=font) <= max_width:
                line = chunk
                continue
            for char in chunk:
                if line and draw.textlength(line + char, font=font) > max_width:
                    lines.append(line)
                    line = ""
                line += char
        if line:
            lines.append(line)
    return "\n".join(lines)


def parse_story(story_path: Path) -> dict[int, tuple[str, bool]]:
    """解析 story.txt，返回 {页码: (文字, 是否居中)}"""
    content = story_path.read_text(encoding="utf-8")
    pages: dict[int, tuple[str, bool]] = {}

    # "图N" 或 "图N!"（! 表示居中）或 "图N 文字"
    pattern = re.compile(r"^图(\d+)(!?)\s*(.*)$")
    lines = content.strip().split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("图") and not pattern.match(line):
            raise ValueError(f"story.txt 格式错误：第 {i + 1} 行不是有效图文标题")
        m = pattern.match(line)
        if m:
            num = int(m.group(1))
            if num in pages:
                raise ValueError(f"story.txt 包含重复页码：图{num}")
            centered = bool(m.group(2))  # 带 ! 就居中
            text = m.group(3)
            if not text:
                i += 1
                if i < len(lines):
                    text = lines[i].strip()
            if text:
                text = text.replace("\\n", "\n")
                pages[num] = (text, centered)
        i += 1

    return pages


def validate_page_images(raw_dir: Path, page_nums: list[int]) -> list[int]:
    """返回缺少原图的页码。"""
    return [num for num in page_nums if not (raw_dir / f"{num:02d}.png").is_file()]


def get_font_path() -> Path:
    """优先使用项目字体，缺失时尝试系统中文字体。"""
    for path in [FONT_PATH, *FALLBACK_FONTS]:
        if path.is_file():
            return path
    raise FileNotFoundError(
        f"未找到可用字体，请检查 {FONT_PATH} 或安装系统中文字体。"
    )


def overlay_page(
    image_path: Path,
    text: str,
    output_path: Path,
    is_centered: bool,
    is_last: bool,
):
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    # 字号按图片实际高度等比缩放：60pt @ 1000px → N pt @ h px
    size = int(BASE_FONT_SIZE * h / 1000)

    if is_last:
        size = int(size * LAST_PAGE_SCALE)
        if not (text.startswith("\u201c") and text.endswith("\u201d")):
            text = "\u201c" + text + "\u201d"

    font = ImageFont.truetype(get_font_path(), size)
    draw = ImageDraw.Draw(img)
    text = wrap_text(text, draw, font, int(w * 0.84))
    # 多行旁白需要明显的行间距，避免笔画相互挤压。
    spacing = max(12, int(size * 0.52))
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if is_centered or is_last:
        # 垂直居中
        x = (w - text_w) // 2 - bbox[0]
        y = (h - text_h) // 2 - bbox[1]
    else:
        # 顶部居中，距顶部约 18%
        x = (w - text_w) // 2 - bbox[0]
        y = int(h * 0.18) - bbox[1]

    draw.multiline_text((x, y), text, font=font, fill=(0, 0, 0, 255), spacing=spacing, align="center")
    img.convert("RGB").save(output_path, "PNG")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    story_name = sys.argv[1]
    story_dir = BASE_DIR / story_name

    if not story_dir.is_dir():
        print(f"错误：故事目录不存在 → {story_dir}")
        sys.exit(1)

    raw_dir = story_dir / "raw"
    story_file = story_dir / "story.txt"
    final_dir = story_dir / "final"

    if not raw_dir.is_dir():
        print(f"错误：raw/ 目录不存在 → {raw_dir}")
        sys.exit(1)
    if not story_file.is_file():
        print(f"错误：story.txt 不存在 → {story_file}")
        sys.exit(1)

    pages = parse_story(story_file)
    if not pages:
        print("错误：story.txt 中没有解析到任何图文")
        sys.exit(1)

    page_nums = sorted(pages.keys())
    last_num = page_nums[-1]
    final_dir.mkdir(parents=True, exist_ok=True)

    print(f"故事：{story_name}")
    print(f"共 {len(page_nums)} 页，最后一页为第 {last_num} 页\n")

    missing = validate_page_images(raw_dir, page_nums)
    if missing:
        print(f"错误：缺少第 {', '.join(map(str, missing))} 页原图")
        return 2

    for num in page_nums:
        img_path = raw_dir / f"{num:02d}.png"

        text, centered = pages[num]
        is_last = (num == last_num)
        output_path = final_dir / f"{num:02d}.png"

        overlay_page(img_path, text, output_path, centered, is_last)
        if is_last:
            tag = "最后一页"
        elif centered:
            tag = "居中"
        else:
            tag = "普通"
        print(f"  ✓ 第 {num} 页 → {output_path.name}  [{tag}]  {text[:20]}{'...' if len(text)>20 else ''}")

    print(f"\n完成！成品在 {final_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
