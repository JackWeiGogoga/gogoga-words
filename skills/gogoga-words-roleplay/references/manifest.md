# 购物任务清单

输出三张 A4 纵向页，依次是图文价目表、两张可剪的角色卡、带预算和勾选框的购物任务。每张单独编号。

| 字段 | 内容 |
| --- | --- |
| `title`、`zh_title` | 主题名和中文说明，例如 `Fruit Shop` 和 `水果店`。 |
| `items` | 3–9 件商品，每项填 `asset`、英文单数 `en`、`zh`、`price` 和 `stock`。价格以整数游戏币计。任务买多件时另填 `plural`。 |
| `roles.buyer`、`roles.seller` | 各自填 `title`、`zh_title` 和 1–4 条 `lines`。每条是 `{"en":"Can I have ___, please?","zh":"请给我……好吗？"}`。 |
| `task` | 含 `budget` 和 `items`。任务项格式为 `{"asset":"apple","quantity":2}`，每种商品出现一次。 |
| `assets`、`assets_from` | 素材或含 `assets` 的 JSON。`file` 相对定义素材的清单，可用 `crop` 取拼版中的一幅图。 |

价格接受 1–99，库存接受 0–99，预算接受 1–999。任务列 1–6 件不同商品，购买数量至少为 1。渲染前会检查商品库存、数量与预算。
