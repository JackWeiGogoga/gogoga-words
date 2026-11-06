---
name: gogoga-words-story
description: Create four-panel English picture stories, shuffled picture cards, and parent retelling prompts for children. Use for sequencing an original story and retelling it with first, next, then, and finally. 用于少儿英语四格故事、排序和看图复述。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Supply four pictures or use an available image generator.
---

# 四格故事与复述

1. 围绕一个角色和一个可看见的小事件写四步。让起因、经过、解决和结尾能从画面看出来，每格用一句短英文和对应中文。
2. 为四步准备无字画面。角色的外形、衣服、道具和场景保持一致。每格只强调一个能用动词说明的动作，打乱后应能凭画面还原顺序。
3. 按 [故事清单](references/manifest.md) 填四格图、双语短句和家长提问。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 导出。macOS 可加 `--png <输出.png>`。
4. 先看有字故事，再剪无字卡排序。家长可以用第三页的问题帮孩子接着讲，并用 `First`、`Next`、`Then`、`Finally` 串成一段。
