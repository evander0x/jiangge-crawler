---
name: story-publishing
description: Add paginated Chinese narration to generated story images and verify the finished sequence. Use when producing final story images, running overlay_text.py or batch_overlay.py, checking raw/final parity, or replacing one finished page.
---

# Story publishing and QA

输入是 `story/stories/<故事名>/raw/NN.png` 和同目录 `story.txt`。叠字前确认文案已定稿；不得覆盖 raw 原图。

## Overlay

- 单页使用 `python3 overlay_text.py <input> <text> [output] [font_size]`；最后一页加 `--last`。
- 整个故事使用 `python3 batch_overlay.py <故事名>`，脚本按 `story.txt` 的 `图N` / `图N!` 解析页面，输出到 `final/NN.png`。
- 普通页旁白顶部居中；长文案需自动换行并居中；`图N!` 或最后一页垂直居中。需要纯白背景和居中文字的最后一页，按需求保留该设计。

### 换行规则

- 优先按语义停顿换行，通常在逗号、句号、问号、感叹号等标点之后断开。
- 不得让逗号、句号、问号、感叹号等标点出现在行首；若自动换行会造成行首标点，应调整到上一行或使用手动换行。
- 普通页尽量控制为 1–2 行，保持各行长度接近，避免第一行过长、第二行过短。
- 画面空间不足时先精简旁白，再考虑增加行数；不得让文字压住主体素材。
- 需要固定语义断点时，在 `story.txt` 中使用 `\\n` 指定换行位置。
- 多行文字使用明显但不过分的行间距，确保笔画不相互挤压。
- 若自定义字体不存在，使用 `overlay_text.py` 的备用字体，并在交付中说明。

## QA checklist

1. `raw/` 与 `final/` 数量一致，且等于 `story.txt` 的预期页数。
2. 所有图片为正方形；raw 原图的像素尺寸、文件字节和画面内容不得因叠字流程改变；外围背景仍是白色或接近白色。
3. 顺序检查完整成品：无 AI 意外文字、画风漂移、主体过大、旁白遮挡或角色外观不一致。
4. 页面替换时只覆盖目标页的 raw/final，确认其他文件未发生变化。

交付时报告 `story/stories/<故事名>/raw/`、`story/stories/<故事名>/final/` 和 `story/stories/<故事名>/story.txt` 的绝对路径。
