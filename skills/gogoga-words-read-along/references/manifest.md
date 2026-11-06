# 讲读清单

```json
{
  "title": "Pear",
  "zh_title": "梨",
  "assets_from": "pear.json",
  "sections": [
    {
      "title": "Inside a Pear",
      "images": [{"asset": "cutaway", "label": "pear half"}],
      "question": {"en": "What can you see inside the pear?", "zh": "你在梨里面看到了什么？"},
      "answer": {"en": "I can see the flesh and the seeds.", "zh": "我看到了果肉和种子。"},
      "read": {"en": "The seeds are in the core.", "zh": "种子在果核里。"}
    }
  ]
}
```

`qa` 读取每节的 `question` 和 `answer`，`read` 读取 `read`。每节可以放 1–6 张图。`label` 可省略。保留小节的次序，脚本会在小节之间分页。多页输出带 `-01`、`-02` 后缀。

`assets_from` 可指向脑图或含 `assets` 的其他清单。也可在本清单提供 `assets`，每个图块定义为 `{"file":"cutaway.png"}`，可选 `crop` 为 `[左, 上, 右, 下]` 像素坐标。文件路径相对声明它的清单。把同一份清单交给打印练习技能，即可复用小节顺序和图片。
