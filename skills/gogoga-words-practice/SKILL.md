---
name: gogoga-words-practice
description: Make printable wordless speaking sheets, cut-out pictures, and matching mats for children's English practice. Reuse lesson pictures or their black-and-white line art for retelling, sorting, and cut-and-paste activities. 用于少儿英语无字复述、贴纸和剪贴配对练习。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Supply illustration assets or a compatible lesson manifest.
---

# 打印互动练习

1. 确定孩子要练习指认、说词还是复述顺序。沿用脑图或讲读页里清楚可辨的图块。按孩子可以指图说出来的顺序整理小节。
2. **无字复述**（`blank`）保留分组、组号和空线。**贴纸**（`stickers`）提供虚线裁切框。**剪贴配对**（`match`）为每组制作带标题和等大空格的底板，另页提供打散顺序的图卡。配对用每幅图只有一个明确归属的分组。
3. 按 [练习清单格式](references/manifest.md) 准备数据。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg> --mode <模式>` 排版。省墨或涂色时准备对应的 [黑白线稿](references/manifest.md#黑白线稿)，加 `--line-art`。已有 Python 3.10+ 和 Pillow 时可用 `python3`。macOS 可附加 `--png <输出.png>`。
4. 检查图块间距、次序和裁切线。配对页核对剪下的图卡和底板空格尺寸一致。用 A4 纵向打印，底板与图卡使用相同的缩放设置。
