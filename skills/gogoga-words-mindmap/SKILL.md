---
name: gogoga-words-mindmap
description: Create illustrated English theme maps and printable picture-speaking worksheets for children. Use for English learning mind maps about a fruit, animal, vehicle, object, or everyday scene. 用于少儿英语启蒙主题思维导图、看图说英语和手绘词汇海报。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow. uv can provision both from the script metadata. Built-in PNG export requires macOS sips. Creating illustrations requires an image generator or supplied image assets.
---

# 少儿英语主题导图

1. **先确定孩子能说什么。** 从用户指定的主题、年龄和程度选取可指认、比较或演示的词。参考 [分支与版式](references/design.md) 挑选适合这个主题的分支。先写出每组的英文标签、对应插画和预期指图问答，再开始生图。核对词义、拼写、单复数和步骤顺序。
2. **准备无字插画。** 有生图工具时，用用户指定的样图或本技能的 [Pear 样图](assets/pear-reference.png) 作风格参考。依照 [插画说明](references/design.md#插画) 为主物和各组词生成可独立裁取的图块。用户提供的素材也可以直接排版。实际查看插画，记录裁切框，检查图块与教学标签的对应关系。
3. **按内容选择版式。** 对比和并列用 `items`，精确部位标注用 `callouts`，步骤用 `sequence`。按 [版式输入说明](references/design.md#排版输入) 写 JSON 清单，运行 [排版脚本](scripts/render.py)。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 导出内嵌插画的 SVG。已有 Python 3.10+ 和 Pillow 的环境也可以用 `python3` 运行同一脚本。macOS 可附加 `--png <输出.png>`。
4. **打开成品验收。** 对照原参考图检查纸感、主物大小、线条、疏密和阅读路径。把成品缩到约 420 px 宽检查标题和小字。放大检查每条引线、每个箭头、每个词与图的对应。将图块重叠、错标和读不清的问题修正后再交付。
