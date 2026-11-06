# 练习清单

```json
{
  "title": "Pear",
  "assets_from": "pear.json",
  "sections": [
    {
      "title": "Colors",
      "images": [{"asset": "green"}, {"asset": "yellow"}, {"asset": "red"}]
    }
  ]
}
```

同一份亲子讲读清单也能直接使用。练习页按 `sections` 的顺序读图，每组可放 1–6 张，打印时按组保留顺序。无字页每页最多五组。贴纸页按首次出现顺序排，每个素材只打印一份，每页最多 16 张。多页输出带 `-01`、`-02` 后缀。

`assets_from` 用于复用其他清单中的 `assets`。也可以在本清单声明 `assets`，图块写成 `{"file":"green.png"}`，可选 `crop` 为 `[左, 上, 右, 下]` 像素坐标。文件路径相对声明它的清单。
