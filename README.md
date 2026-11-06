# gogoga-words

把一个主题拆开，用图讲清楚，用英语说出来。

给出一个主题和孩子的英语水平，这个技能会挑出可指认的部位、可比较的特征和可复述的动作，再把插画、英文标注和步骤排成一张手绘英语主题导图。

An [Agent Skill](https://agentskills.io/specification) that breaks down topics into illustrated English words, parts, and actions for children.

<p>
  <a href="examples/pear/pear.png"><img src="examples/pear/pear.png" width="310" alt="梨主题英语导图，含大小、颜色、切面标注和生长过程"></a>
  <a href="examples/bulldozer/bulldozer.png"><img src="examples/bulldozer/bulldozer.png" width="310" alt="推土机主题英语导图，含部件标注、工作场景和推土过程"></a>
</p>

## 安装

在目标项目的根目录运行，按提示选择 Codex、Claude Code、Cursor 或其他客户端。需要 Node.js 22.20 或更新版本。 [Skills CLI 安装说明](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-add)

```sh
npx skills add JackWeiGogoga/gogoga-words --skill gogoga-words-mindmap
```

可用 `--agent claude-code` 指定客户端，或用 `-g` 安装到用户目录以供多个项目使用。如果已有本地源码，把命令里的仓库名换成本地目录路径即可。

也可以把完整的 [`skills/gogoga-words-mindmap`](skills/gogoga-words-mindmap) 文件夹复制到客户端的技能目录。 [各客户端的技能目录](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)

## 使用

```text
请用 gogoga-words-mindmap 技能给英语初学的 6 岁孩子做一张企鹅主题导图。
选容易看图复述的词，标出身体部位，画出它在陆地和水里的动作。
用手绘风格，输出一张竖版 SVG。
```

在 Codex 中也可以用 `$gogoga-words-mindmap` 点名调用。可以指定词汇难度、分支或要练习的句子。制作新主题时，提供透明插画或在支持生图的环境中让 agent 生成。技能会把插画与文字分开处理，便于修正拼写、移动引线或更换个别图块。

## 复现示例

两组示例都附有成品、内容清单和源插画。用 [uv](https://docs.astral.sh/uv/) 从仓库根目录渲染。首次运行会准备 Python 和 Pillow，之后可用缓存离线渲染。以下命令使用 macOS 自带的 `sips` 导出 PNG。只需 SVG 时，省略 `--png` 及其输出路径即可。

```sh
mkdir -p out
uv run --script skills/gogoga-words-mindmap/scripts/render.py \
  examples/pear/pear.json out/pear.svg --png out/pear.png
uv run --script skills/gogoga-words-mindmap/scripts/render.py \
  examples/bulldozer/bulldozer.json out/bulldozer.svg --png out/bulldozer.png
```

| 示例               | 展示的内容                                           | 源文件                                                                         |
| ------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------------ |
| Pear · 梨          | 用大小和颜色做对比，用切面学部位，用箭头读生长过程   | [清单](examples/pear/pear.json) · [素材](examples/pear/assets/)                |
| Bulldozer · 推土机 | 看侧视图学部件，用小场景读动作、材料、工地和工作流程 | [清单](examples/bulldozer/bulldozer.json) · [素材](examples/bulldozer/assets/) |

SVG 是 1080 × 1440 的自包含文件，插画和纸底内嵌，文字可编辑。复现预览字体时可用 macOS 的 Chalkboard 系列。

## 项目结构

```text
skills/gogoga-words-mindmap/
├── SKILL.md       技能入口与调用说明
├── agents/        可选的 Codex 界面元数据
├── assets/        细纹纸底和风格样图
├── references/    分支选题、插画与清单格式
└── scripts/       JSON 到 SVG / PNG 的排版脚本
examples/
├── pear/
└── bulldozer/
```

修改或添加主题时，可从现有 JSON 清单开始，按 [设计与排版说明](skills/gogoga-words-mindmap/references/design.md) 调整。欢迎在 [Issues](https://github.com/JackWeiGogoga/gogoga-words/issues) 提交主题建议或排版问题。报告渲染问题时，请附上可复现的清单和预览。

## 许可

项目采用 [MIT 许可](LICENSE)，示例插画和纸底由 AI 生成。
