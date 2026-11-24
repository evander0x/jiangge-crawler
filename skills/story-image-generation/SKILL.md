---
name: story-image-generation
description: Generate or replace the text-free square illustrations for this project's paginated Chinese stories. Use when creating story page images, writing image prompts, maintaining character consistency, or regenerating a specific page.
---

# Story image generation

线条的圆润度、稳定性和粗细层级只以 `story/story_reference/line-style-reference.png` 为基准；`story/story_reference/` 中的其他参考图只用于配色、主体大小、构图和留白，不得复制其中的文字。新故事先完成并确认分页文案，再逐页生成图片。

## Image requirements

- 每页一张 1:1 插画，使用纯白 `#FFFFFF` 背景；禁止纹理、阴影、渐变、边框和噪点。
- 每页只保留一两个小而清晰的关键元素。普通页优先匹配参考图的主体比例：整体高度目标为画面 19%-29%，硬性范围为 16%-30%。不得通过放大主体模拟线条加粗。
- 普通页主体视觉中心必须与画布几何中心重合，水平和垂直偏差均不得超过画布尺寸的 2%；顶部旁白依靠小主体自然留出空间，不使用固定纵向锚点。
- 最后一页默认不生成插画：创建与前页原图像素尺寸完全一致的纯白 `#FFFFFF` 方图作为 `raw/NN.png`，再由 `story-publishing` 仅叠加垂直居中的结尾文案。只有用户明确要求“最后一页保留插画”时，才允许生成小主体并下移避让文字；不得从故事情节自行推断该例外。
- 禁止中文、英文、数字、标点、Logo 和水印。动作线、星光等画面表现元素可以按情节需要使用。
- 后续页面使用已确认的前序页面作角色参考，保持外观一致。
- 每页提示词末尾加入：`No text, no letters, no characters, no words.`
- 每张普通页生成后必须实际测量非白色主体的包围盒，不得只相信提示词中的比例。以接近白色像素为背景，计算 `主体高度 / 画布高度` 与包围盒中心；高度超出 16%-30%，或中心相对画布中心任一方向偏差超过 2%，必须重新生成，禁止通过裁切、缩放或移动成图补救。优先将高度收敛到 19%-29%。
- 每页测量合格后，再按相近主体视觉尺寸与线条基准图比较：外轮廓与内部线条保持粗细层级，并整体明显加粗约 15%–20%。成图与基准相当、更细或层级异常时重新生成。
- 将 imagegen 返回的完整 1:1 原图直接保存为 `story/stories/<故事名>/raw/NN.png`。
- 保存前后不得裁切、缩放、抠图、重新居中、拉伸或改变原始像素尺寸；不得改动 `story/story_reference/`。

## Single-page replacement

用户要求替换第 N 页时，只重新生成并覆盖 `story/stories/<故事名>/raw/NN.png`，并且本次调用仍须同时实际传入线条基准图和所需角色参考页；验收线宽合格后，再交给 `story-publishing` 只重做对应的 `final/NN.png`。其他页面不得改动。文件名过长时，可只复制参考图到临时目录并使用短文件名。

## Mandatory acceptance loop

1. 生成普通页原图，并直接保存完整 1:1 输出。
2. 测量主体包围盒高度占比和中心偏差；不合格立即重新生成该页。
3. 对照 `story/story_reference/line-style-reference.png` 检查线宽层级；不合格立即重新生成该页。
4. 检查无文字、纯白背景、关键元素数量和角色一致性；任一不合格均重新生成。
5. 所有普通页通过后，最后一页按默认纯白无插画规则创建；随后才调用 `story-publishing`。

不得因为已经生成多页、生成耗时或旁白暂时未遮挡主体而跳过上述循环。

## Handoff

生成完成后确认 `raw/` 中的页数、文件尺寸和原始字节仍正确，并报告每张普通页的主体高度占比与中心偏差，再调用 `story-publishing` 叠加旁白。最终报告 `raw/`、`final/` 和 `story.txt` 的绝对路径。
