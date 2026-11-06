---
name: gogoga-words-read-along
description: Create bilingual picture-question sheets and short English read-aloud guides for parents and children. Use to turn a topic or illustrated English mind map into speakable questions, answers, and a guided reading page. 用于少儿英语双语看图问答和亲子领读稿。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Use supplied illustrations or an available image generator.
---

# 亲子讲读页

1. 按孩子能看见、能指认、能说出来的顺序安排小节。已有脑图时沿用合适的分支、英文词和插画，并用 `assets_from` 引用它的插画清单。新主题可以直接提供自己的插画。
2. **看图问答**让大人问一句、孩子答一句。问题要能指着图回答，示范回答用孩子够得着的短句。**连续领读**把同组词串成几句自然的短文，按小节顺序读下来。两种模式都配对应的中文。逐项核对图、英文和翻译。
3. 按 [讲读清单格式](references/manifest.md) 写 JSON。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg> --mode qa` 导出问答页，或用 `--mode read` 导出领读页。已有 Python 3.10+ 和 Pillow 时可用 `python3`。macOS 可附加 `--png <输出.png>`。
4. 打开结果，试着指图读完一轮。英文和中文应能按同一顺序对应，最后一行文字和最后一张图都应在版面内。
