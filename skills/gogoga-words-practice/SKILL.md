---
name: gogoga-words-practice
description: Make printable wordless speaking worksheets and cut-out picture sheets for children's English practice. Use to repurpose pictures from an English theme map or reading lesson for recall, retelling, or sticker activities. 用于少儿英语无字复述页和可剪贴纸页。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Supply illustration assets or a compatible lesson manifest.
---

# 打印互动练习

1. 确定孩子要练习指认、说词还是复述顺序。沿用脑图或讲读页里清楚可辨的图块。按孩子可以指图说出来的顺序整理小节。
2. **无字复述页**按组排图片，只留下组号和书写空线。**贴纸页**把每幅图放进独立的虚线裁切框，供孩子剪、选、排、贴或说。选择适合目标的模式。
3. 按 [练习清单格式](references/manifest.md) 准备数据。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg> --mode blank` 导出无字页，或用 `--mode stickers` 导出贴纸页。已有 Python 3.10+ 和 Pillow 时可用 `python3`。macOS 可附加 `--png <输出.png>`。
4. 检查图块间距、每组次序和裁切线。打印时用 A4 纵向并适合页面。贴纸活动可以用贴纸纸，也可以用普通纸剪下后粘贴。
