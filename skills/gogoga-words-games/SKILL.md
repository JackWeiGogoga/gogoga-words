---
name: gogoga-words-games
description: Create printable English picture Bingo sets for children from a themed vocabulary list. Generates different picture boards and matching caller cards for listening and word review. 用于少儿英语听词找图和可打印宾果游戏。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Supply illustrated vocabulary or use an available image generator.
---

# 图词宾果

1. 按主题和孩子的水平选一组容易区分的英文词。已有图文词卡时直接用原清单。每词用一幅可单独辨认的无字插画。
2. 根据词数和人数选棋盘大小与张数。新手可用 2×2，常用 3×3。玩家看图，叫词的人拿带英文的卡。每张棋盘图片各不相同，整套棋盘覆盖所有叫词卡。
3. 按 [宾果清单](references/manifest.md) 准备数据，用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 导出。macOS 可加 `--png <输出.png>`。
4. 核对棋盘图与叫词卡一一对应。剪开叫词卡并洗牌，每轮只念英文。玩家盖住对应图片，横、竖或斜线连满一排就喊 Bingo。
