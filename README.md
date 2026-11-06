# gogoga-words

把一个主题拆开，用图讲清楚，用英语说出来。

给出一个主题和孩子的英语水平，这套技能会挑出可指认的部位、可比较的特征和可复述的动作，用插画、英文标注和步骤做成主题导图、图文词卡、亲子讲读页和打印练习。

A collection of [Agent Skills](https://agentskills.io/specification) for illustrated English learning materials for children.

<p>
  <a href="examples/pear/pear.png"><img src="examples/pear/pear.png" width="310" alt="梨主题英语导图，含大小、颜色、切面标注和生长过程"></a>
  <a href="examples/bulldozer/bulldozer.png"><img src="examples/bulldozer/bulldozer.png" width="310" alt="推土机主题英语导图，含部件标注、工作场景和推土过程"></a>
</p>

| 技能 | 生成的内容 | 示例 |
| --- | --- | --- |
| [gogoga-words-mindmap](skills/gogoga-words-mindmap) | 主题导图、部位标注和动作顺序 | [梨](examples/pear/pear.png) · [推土机](examples/bulldozer/bulldozer.png) |
| [gogoga-words-cards](skills/gogoga-words-cards) | 每格一图，配英文、音标和中文 | [水果图文卡](examples/fruit/fruit.png) |
| [gogoga-words-read-along](skills/gogoga-words-read-along) | 双语看图问答和连续领读 | [梨篇问答](examples/pear/pear-qa.png) · [梨篇领读](examples/pear/pear-read.png) |
| [gogoga-words-practice](skills/gogoga-words-practice) | 无字复述页和可剪贴纸页 | [梨篇无字页](examples/pear/pear-blank.png) · [梨篇贴纸](examples/pear/pear-stickers.png) |

## 安装

在目标项目的根目录运行，按提示选择 Codex、Claude Code、Cursor 或其他客户端。需要 Node.js 22.20 或更新版本。 [Skills CLI 安装说明](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-add)

```sh
npx skills add JackWeiGogoga/gogoga-words --skill gogoga-words-mindmap
```

把 `--skill` 后的名字换成表中所需的技能，或省略它并在安装时选择。用 `--agent claude-code` 可以指定客户端，`-g` 可以安装到用户目录以供多个项目使用。如果已有本地源码，把命令里的仓库名换成本地目录路径即可。

也可以把 [skills](skills/) 下所需技能的完整文件夹复制到客户端的技能目录。 [各客户端的技能目录](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)

## 使用

```text
请用 gogoga-words-mindmap 技能给英语初学的 6 岁孩子做一张企鹅主题导图。
选容易看图复述的词，标出身体部位，画出它在陆地和水里的动作。
用手绘风格，输出一张竖版 SVG。
```

在 Codex 中也可以用 `$gogoga-words-mindmap` 点名调用。制作新主题时，提供透明插画或在支持生图的环境中让 agent 生成。可以把同一套图和词交给讲读、练习技能，按相同顺序出题或复述。

## 复现示例

示例附有成品、内容清单和插画。用 [uv](https://docs.astral.sh/uv/) 从仓库根目录渲染。首次运行会准备 Python 和 Pillow，之后可用缓存离线渲染。以下命令使用 macOS 自带的 `sips` 导出 PNG。只需 SVG 时，省略 `--png` 及其输出路径即可。

```sh
mkdir -p out
uv run --script skills/gogoga-words-mindmap/scripts/render.py \
  examples/pear/pear.json out/pear.svg --png out/pear.png
uv run --script skills/gogoga-words-mindmap/scripts/render.py \
  examples/bulldozer/bulldozer.json out/bulldozer.svg --png out/bulldozer.png
uv run --script skills/gogoga-words-cards/scripts/render.py \
  examples/fruit/fruit.json out/fruit.svg --png out/fruit.png
uv run --script skills/gogoga-words-read-along/scripts/render.py \
  examples/pear/lesson.json out/pear-qa.svg --mode qa --png out/pear-qa.png
uv run --script skills/gogoga-words-read-along/scripts/render.py \
  examples/pear/lesson.json out/pear-read.svg --mode read --png out/pear-read.png
uv run --script skills/gogoga-words-practice/scripts/render.py \
  examples/pear/lesson.json out/pear-blank.svg --mode blank --png out/pear-blank.png
uv run --script skills/gogoga-words-practice/scripts/render.py \
  examples/pear/lesson.json out/pear-stickers.svg --mode stickers --png out/pear-stickers.png
```

| 示例               | 展示的内容                                           | 源文件                                                                         |
| ------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------------ |
| Pear · 梨          | 用大小和颜色做对比，用切面学部位，用箭头读生长过程   | [清单](examples/pear/pear.json) · [素材](examples/pear/assets/)                |
| Bulldozer · 推土机 | 看侧视图学部件，用小场景读动作、材料、工地和工作流程 | [清单](examples/bulldozer/bulldozer.json) · [素材](examples/bulldozer/assets/) |
| Fruit · 水果       | 20 张配英式音标的认词卡 | [清单](examples/fruit/fruit.json) · [素材](examples/fruit/assets/) |

梨篇的 [讲读和练习清单](examples/pear/lesson.json) 通过 `assets_from` 复用脑图的图片。生成的 SVG 内嵌插画，文字可编辑。脑图和词卡为 1080 × 1440，讲读和练习为 A4 纵向比例。打印时选择适合页面。复现预览字体时可用 macOS 的 Chalkboard 系列。

## 项目结构

```text
skills/
├── gogoga-words-mindmap/
├── gogoga-words-cards/
├── gogoga-words-read-along/
└── gogoga-words-practice/
examples/
├── bulldozer/
├── fruit/
└── pear/
tools/
├── worksheet.py
└── sync_worksheet_support.py
```

每个技能目录包含独立的 `SKILL.md`、清单说明和渲染脚本。修改共用的 [worksheet.py](tools/worksheet.py) 后，运行 `python3 tools/sync_worksheet_support.py` 更新词卡、讲读和练习技能各自随包安装的副本。修改或添加主题时，可从现有 JSON 清单开始。报告渲染问题时，请附上可复现的清单和预览。 [Issues](https://github.com/JackWeiGogoga/gogoga-words/issues)

## 许可

项目采用 [MIT 许可](LICENSE)，示例插画和纸底由 AI 生成。
