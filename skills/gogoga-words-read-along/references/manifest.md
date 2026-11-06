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

## 绘本场景

`--mode scene` 每页用一幅完整的场景图。准备无字插画时，给每个教学目标留出能放编号的位置。优先用横向构图，把人物、物体或动作清楚地分布在画面中。可用重复句型串起三到五句领读，让孩子按编号逐个指认。

```json
{
  "title": "Farm Morning",
  "zh_title": "农场的早晨",
  "assets": {"farm": {"file": "farm.png"}},
  "scenes": [{
    "asset": "farm",
    "points": [{"en": "barn", "zh": "谷仓", "point": [0.24, 0.28]}],
    "lines": [{"en": "I can see a barn.", "zh": "我看见一座谷仓。"}]
  }]
}
```

`points` 按编号顺序放 1–8 个词。`point` 是裁切后图片内的相对坐标，左上为 `[0, 0]`，右下为 `[1, 1]`。建议把编号放在物体旁的空位。`lines` 放 1–6 组对应的英中短句。词和句子较多时拆成多页，每个 `scenes` 条目生成一页 A4 比例图片。

`style` 控制页面配色，可用 `--style` 覆盖。省略时沿用 `default`。用对应画法准备原始无字插画。

| `style` | 插画怎么画 |
| --- | --- |
| `engineering` | 工程现场手绘。用现场全景交代车、人员、工具和工作地点的关系。保留机械结构和轮廓，用水粉色块与铅笔细纹画表面，让每个教学目标在缩小后仍能指认。 |
| `pattern-search` | 几何图案找找看。用边界清楚的色块与重复图案搭场景，把少量目标藏在相似色块和轮廓中。给孩子可凭形状、颜色或方位辨认的线索，用 `Where is…?` 串起找图。 |

要让孩子独立找图，在对应的 `scenes` 条目里填 `"show_markers": false`。词表仍按原顺序显示，`point` 保留在清单里，可将该开关设回 `true` 生成有编号的对照页。默认显示编号。
