# 项目地图

这是一个“中文谐音梗故事创作 + 无文字插画后期叠字”的项目。先按下面的地图定位资料和流程，再加载对应 skill；不要把所有细则重新写回本文件。

## 规则与流程入口

| 任务 | 使用 skill | 关键文件 |
| --- | --- | --- |
| 创作/改写故事、检查逐词关联与谐音因果 | `skills/story-writing/SKILL.md` | `skills/story-writing/references/story-rules.md` |
| 生成或替换分页插画 | `skills/story-image-generation/SKILL.md` | `story/story_reference/`、`story/stories/<故事名>/raw/` |
| 叠加旁白、生成成品、验收 | `skills/story-publishing/SKILL.md` | `overlay_text.py`、`batch_overlay.py`、`story/stories/<故事名>/story.txt` |

## 主流程

1. 使用 `story-writing` 创作或审核故事，并确认谐音因果、页序和分页文案。
2. 故事满意后，将确认的分页文案复制到 `story/stories/<故事名>/story.txt`，作为后续生图的唯一文案输入。
3. 使用 `story-image-generation` 读取 `story.txt`，逐页生成无文字原图并保存到 `story/stories/<故事名>/raw/`。
4. 原图验收通过后，使用 `story-publishing` 叠加旁白到 `final/`，检查页数、尺寸、顺序和文字遮挡。

## 文件地图

- `skills/story-writing/references/story-rules.md`：故事结构、逐词关联、谐音因果与正反例；创作、改写或审核故事前完整阅读。
- `prompt_list/search.md`：素材/搜索相关提示词。
- `prompt_list/ui.md`：界面相关提示词。
- `story/故事.md`：故事分类总目录与全部故事文案。
- `story/story_reference/`：画风参考图，只控制线条、配色、主体大小、构图和留白；不得复制图片中的文字，也不得移动、删除或覆盖其中文件。
- `story/stories/<故事名>/story.txt`：已确认的分页文案；`raw/` 存无文字原图；`final/` 存叠字成品。
- `overlay_text.py`：单页叠字；`batch_overlay.py`：按 `story.txt` 批量叠字。
- `story/public_story/`：公开发布整理稿与成品；`account_brand/`：账号品牌图片。

## 不可违反的总则

- 除非用户明确要求改写，不得改动用户提供的故事、页序和文案。
- 保留用户已有改动；不得用破坏性命令覆盖或删除无关内容。
- 插画中不得生成任何文字、数字、Logo 或水印；动作线、星光等画面表现元素不受此限制；旁白统一在后期添加。
- 单页替换只改目标页的 `raw/NN.png` 和 `final/NN.png`，其他页面不动。
- 完成后报告相关输出目录和 `story.txt` 的绝对路径。

## 常用命令

```bash
python3 overlay_text.py <图片> "旁白" [输出图片] [字号]
python3 overlay_text.py <图片> "最后一句" [输出图片] [字号] --last
python3 batch_overlay.py <故事名>
```
