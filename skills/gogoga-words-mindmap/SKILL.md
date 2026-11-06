---
name: gogoga-words-mindmap
description: Create illustrated English theme maps for children in watercolor, flat cartoon, or science line art, with optional Chinese glosses, IPA, and a speaking prompt. 用于少儿英语主题思维导图、部位图解和看图说英语。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow. uv can provision both from the script metadata. Built-in PNG export requires macOS sips. Creating illustrations requires an image generator or supplied image assets.
---

# 少儿英语主题导图

1. **先确定孩子能说什么。** 从用户指定的主题、年龄和程度选取可指认、比较或演示的词。参考 [分支与版式](references/design.md) 挑选适合这个主题的分支。先写出每组的英文标签、对应插画和预期指图问答，再开始生图。核对词义、拼写、单复数和步骤顺序。
2. **按需加学习标注。** 默认只显示英文。用户可分别开启中文释义、中文分支标题、IPA 和页底问答。按 [学习标注与开口提示](references/design.md#学习标注与开口提示) 填数据。音标优先给主题词和重点词，并在全页统一英式或美式读音。
3. **选画法并准备无字插画。** 按用户指定的彩铅水彩（`watercolor`，默认）、平涂卡通（`flat`）、科普线描（`diagram`）或工程现场手绘（`engineering`）准备主物和图块。按 [插画说明](references/design.md#插画) 生图或使用用户素材，实际查看图块后记录裁切框。
4. **按内容选择版式。** 对比和并列用 `items`，精确部位标注用 `callouts`，步骤用 `sequence`。按 [版式输入说明](references/design.md#排版输入) 写 JSON 清单，用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 导出 SVG。可加 `--style` 选择画法。已有 Python 3.10+ 和 Pillow 时可用 `python3`。macOS 可附加 `--png <输出.png>`。
5. **打开成品验收。** 检查插画和页面配色是否符合所选风格。把成品缩到约 420 px 宽检查标题和小字。放大核对引线端点、动作箭头、音标和中英释义是否对应。
