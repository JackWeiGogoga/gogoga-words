---
name: gogoga-words-cards
description: Create English vocabulary grids and picture dictionary pages for children with watercolor, flat cartoon art, or supplied photos. Each card has an English word, IPA, and Chinese gloss. 用于少儿英语分类图文词卡和实拍词卡。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. New illustrations require an image generator or supplied image assets.
---

# 分类词汇图文卡

1. 用指定词表，或按主题和孩子水平选词。每格确定一个词义，写出英文、IPA、中文和插画描述。按同一个英式或美式口径核对音标。图里有多件同类物体时，核对标签的单复数。
2. 给每个词分配可单独辨认的图块。按用户需求选择彩铅水彩、平涂卡通或实拍。平涂卡通用清楚的轮廓和实色，适合一页多格。实拍用用户提供的照片。选材和裁切细节见 [词卡清单格式](references/manifest.md#选画法与准备素材)。
3. 按 [词卡清单格式](references/manifest.md) 编写 JSON。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 排版。已有 Python 3.10+ 和 Pillow 时可直接用 `python3`。macOS 可附加 `--png <输出.png>`。
4. 查看每一页。核对每格的插画、英文、音标、中文和页码。手机上读不清时减小每页格数。保留清单与插画，方便下次改词和复现。
