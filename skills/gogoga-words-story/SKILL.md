---
name: gogoga-words-story
description: Create four-panel English picture stories with sorting cards and retelling prompts, or Chinese, English, and bilingual picture books with one scene per page. 用于少儿英语四格故事、排序和看图复述，也可制作中英文寓言、民间故事和多页绘本。
license: MIT
compatibility: Rendering uses Python 3.10+ and Pillow, provisioned by uv when available. Built-in PNG export requires macOS sips. Supply four pictures or use an available image generator.
---

# 四格故事与多页绘本

默认用 `panels` 制作双语四格故事。用户要一图一页的绘本时，用 `book`，按需选 `zh`、`en` 或 `bilingual`。先按翻页安排情节，再统一角色、道具和画法。生图时准备插画，成品的每一页都用脚本排上所选语言的正文。见 [多页绘本清单](references/manifest.md#多页绘本)。

## 双语四格故事

1. 围绕一个角色和一个可看见的小事件写四步。让起因、经过、解决和结尾能从画面看出来，每格用一句短英文和对应中文。
2. 为四步准备无字画面。角色的外形、衣服、道具和场景保持一致。每格只强调一个能用动词说明的动作，打乱后应能凭画面还原顺序。用户指定拟人动物生活（`animal-story`）或工程现场手绘（`engineering`）时，按 [画法说明](references/manifest.md#选画法) 准备插画。
3. 按 [故事清单](references/manifest.md) 填四格图、双语短句和家长提问。用 `uv run --script <skill-dir>/scripts/render.py <清单.json> <输出.svg>` 导出。macOS 可加 `--png <输出.png>`。
4. 先看有字故事，再剪无字卡排序。家长可以用第三页的问题帮孩子接着讲，并用 `First`、`Next`、`Then`、`Finally` 串成一段。
