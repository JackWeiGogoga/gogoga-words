# 词卡清单

```json
{
  "title": "Fruit",
  "zh_title": "水果",
  "pronunciation": "British English · IPA",
  "columns": 5,
  "rows": 4,
  "assets": {"pear": {"file": "pear.png"}},
  "items": [{"asset": "pear", "en": "pear", "ipa": "/peə/", "zh": "梨"}]
}
```

`items` 按从左到右、从上到下的阅读顺序排列。`file` 相对清单路径。如果多幅图在同一张图上，用 `crop` 指定 `[左, 上, 右, 下]` 像素坐标。可用 `assets_from` 指向含 `assets` 的 JSON，例如同一主题的脑图清单，再在 `assets` 中补充个别图块。继承的图块按原清单路径查找。

默认每页五列四行，两项都可以设为 2–5。词汇较长或孩子刚开始认词时，减少每页格数。超出一页时，脚本按 `-01`、`-02` 等后缀输出多张 1080 × 1440 图片。
