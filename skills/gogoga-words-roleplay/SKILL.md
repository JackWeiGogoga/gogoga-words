---
name: gogoga-words-roleplay
description: Create printable parent-child English role-play packs for shopping or ordering. Produces an illustrated menu, separate bilingual buyer and seller cards, and a shopping mission. 用于少儿英语情景口语、超市和点餐角色扮演。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Supply illustrations or use an available image generator.
---

# 情景任务包

1. 选一个需要开口才能完成的任务，例如在预算内买齐三样水果。用孩子熟悉的 3–9 件商品，给每件分配一个图块、价格和库存。
2. 给顾客和店员各写 1–4 句可反复用的双语短句。顾客拿购物任务单，店员拿库存。让孩子用英语点名、问数量或价格，买齐后交换角色。
3. 按 [购物任务清单](references/manifest.md) 填数据。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 导出。macOS 可加 `--png <输出.png>`。
4. 核对预算够用、库存能满足清单、图片对应商品、数量大于一时英文用复数。
