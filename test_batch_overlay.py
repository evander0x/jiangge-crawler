import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PIL import Image, ImageDraw, ImageFont

from batch_overlay import main, parse_story, validate_page_images, wrap_text


class WrapTextTests(unittest.TestCase):
    def test_keeps_punctuation_segment_together_when_it_fits(self):
        image = Image.new("RGB", (1254, 1254), "white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("fonts/平方时光体.ttf", 75)

        result = wrap_text("小兔抱着一大串香蕉，累得一步也走不动", draw, font, 1053)

        self.assertEqual(result, "小兔抱着一大串香蕉，\n累得一步也走不动")


class StoryValidationTests(unittest.TestCase):
    def test_duplicate_page_numbers_are_rejected(self):
        with TemporaryDirectory() as tmp:
            story_file = Path(tmp) / "story.txt"
            story_file.write_text("图1 第一页\n图1 重复页\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "重复"):
                parse_story(story_file)

    def test_malformed_page_header_is_rejected(self):
        with TemporaryDirectory() as tmp:
            story_file = Path(tmp) / "story.txt"
            story_file.write_text("图x 不是有效页码\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "格式"):
                parse_story(story_file)

    def test_missing_page_images_are_returned(self):
        with TemporaryDirectory() as tmp:
            raw_dir = Path(tmp)
            (raw_dir / "01.png").touch()

            missing = validate_page_images(raw_dir, [1, 2])

            self.assertEqual(missing, [2])

    def test_batch_main_returns_failure_when_an_image_is_missing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            story_dir = root / "示例故事"
            (story_dir / "raw").mkdir(parents=True)
            (story_dir / "raw" / "01.png").touch()
            (story_dir / "story.txt").write_text(
                "图1 第一页\n图2 第二页\n", encoding="utf-8"
            )

            with patch("batch_overlay.BASE_DIR", root):
                with patch("batch_overlay.sys.argv", ["batch_overlay.py", "示例故事"]):
                    self.assertEqual(main(), 2)


if __name__ == "__main__":
    unittest.main()
