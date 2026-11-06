---
name: gogoga-words-read-along
description: Create bilingual picture Q&A, read-aloud guides, and illustrated scene pages for parents and children. Turn a topic, mind map, or full scene into short, speakable English. 用于少儿英语看图问答、亲子领读和绘本式场景页。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Use supplied illustrations or an available image generator.
---

# 亲子讲读页

1. 按孩子能看见、能指认、能说出来的顺序安排小节。已有脑图时沿用合适的分支、英文词和插画，并用 `assets_from` 引用它的插画清单。新主题可以直接提供自己的插画。
2. **看图问答**（`qa`）为每组配一个能指图回答的问题和一句示范回答。**连续领读**（`read`）把同组词串成短句。**绘本场景**（`scene`）用一幅无字场景图，选出能直接指认的物体或动作，用数字和双语词表对应，再写几句可边指边读的短句。
3. 按 [讲读清单格式](references/manifest.md) 写 JSON。场景页用 [场景清单](references/manifest.md#绘本场景)。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg> --mode <模式>` 排版。已有 Python 3.10+ 和 Pillow 时可用 `python3`。macOS 可附加 `--png <输出.png>`。
4. 需要切换画风时，选工程现场手绘（`engineering`）或几何图案找找看（`pattern-search`），按 [场景画法](references/manifest.md#绘本场景) 准备无字插画。找图时可隐藏图上编号。
5. 指图试读一轮，核对图上的物体、英文和中文。启用编号时将它贴近对应物体，并给轮廓留出空间。隐藏编号时确认目标靠画面仍能找到。
