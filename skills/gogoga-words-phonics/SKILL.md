---
name: gogoga-words-phonics
description: Create illustrated short-vowel CVC blending cards and an eight-page foldable reader for children. Checks each reading word against taught letters or explicitly approved helper words. 用于少儿英语短元音自然拼读、拼读卡和可打印折页小书。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Supply illustrations or use an available image generator.
---

# 短元音拼读小书

1. 确定孩子已学的字母音，选一个短元音和 3–12 个 CVC 词。优先选易画、易区分的词，例如 `cat`、`hat`、`mat`。从 [拼读词表](references/cvc-words.txt) 选词。
2. 用选好的词写一本八页小书。每页一个短语或一句短句，搭配无字插画。把孩子已会整体认读的辅助词明确写入 `helper_words`，例如 `a`。
3. 按 [拼读清单与折页说明](references/manifest.md) 填数据。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 导出。macOS 可加 `--png <输出.png>`。如果拼读检查报出超范围词，改用孩子已学的词。
4. 先让孩子指着拼读卡逐音合成，再读书页。检查故事能看懂，文字能按已学声音读出。小书横向单面打印，按折页说明装订。
