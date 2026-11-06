---
name: gogoga-words-cards
description: Create illustrated English vocabulary grids and picture dictionary pages for children. Use for themed word lists with one picture, English label, IPA, and Chinese gloss per card. 用于少儿英语分类词汇图文卡、图画词典和认词海报。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. New illustrations require an image generator or supplied image assets.
---

# 分类词汇图文卡

1. 用指定词表，或按主题和孩子水平选词。每格确定一个词义，写出英文、IPA、中文和插画描述。按同一个英式或美式口径核对音标。图里有多件同类物体时，核对标签的单复数。
2. 给每个词分配可单独辨认的图块。优先复用用户提供的插画。生图时用细描线和柔和的彩铅水彩色块，为每格画独立、无字、透明底的图，保留裁切留白。确认图片与中文释义表达同一个意思。
3. 按 [词卡清单格式](references/manifest.md) 编写 JSON。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 排版。已有 Python 3.10+ 和 Pillow 时可直接用 `python3`。macOS 可附加 `--png <输出.png>`。
4. 查看每一页。核对每格的插画、英文、音标、中文和页码。手机上读不清时减小每页格数。保留清单与插画，方便下次改词和复现。
