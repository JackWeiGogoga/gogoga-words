---
name: gogoga-words-upload
description: Sign in to the gogoga platform (words.gogoga.top) and upload a material made by another gogoga-words skill — its JSON manifest, the illustrations it references and the rendered pages — to the user's own private library. Use when the user asks to upload, save, publish or sync a mind map, cards, read-along page, practice sheet, bingo, role-play pack, story or phonics book to gogoga, or to sign in or out of gogoga. 把 gogoga-words 技能做好的素材上传到 gogoga 平台（只有自己可见），或登录/退出 gogoga。
license: MIT
compatibility: Python 3.10+ (standard library only). Signing in needs a browser on any device.
---

# 上传到 gogoga

把其他 gogoga-words 技能做好的素材上传到 gogoga 平台。上传后挂在用户自己的作品墙上，只有用户本人登录后能看到。

脚本：`python3 <skill-dir>/scripts/gogoga.py <命令>`（下文写作 `gogoga.py`）。

## 1. 确认已登录

```sh
python3 <skill-dir>/scripts/gogoga.py whoami
```

没登录时运行 `gogoga.py login`。它会打印一个链接和形如 `ABCD-EFGH` 的设备码，并尝试打开浏览器：

- 把链接和设备码原样告诉用户，请用户在浏览器里登录（邮箱验证码）并点「允许」。手机上打开也可以。
- 命令会一直等到用户确认（最多 10 分钟），然后把登录保存在 `~/.config/gogoga/credentials.json`。
- 不要替用户输入验证码，也不要读取或打印凭据文件里的 token。

在无法打开浏览器的环境里加 `--no-browser`。测试服务器用 `--server <地址>` 或环境变量 `GOGOGA_SERVER`。

## 2. 上传

```sh
python3 <skill-dir>/scripts/gogoga.py upload <清单.json> --type <类型> --preview <导出的.png> [--preview …] [--collection <主题>]
```

- `<清单.json>` 是生成素材时写的 JSON 清单。清单里 `assets`、`assets_from`、`style_assets` 引用的图片会自动带上，不用单独列出。
- `--preview` 传导出的成品页 PNG，平台暂时不能自己排版的类型靠它显示，多页就重复写。导图和词卡也建议带上。
- `--collection` 是主题的英文短名，比如 `pear`，把同一主题的导图、词卡、讲读归在一起。不写时按标题生成。

| 技能 | `--type` |
| --- | --- |
| gogoga-words-mindmap | `mindmap` |
| gogoga-words-cards | `cards` |
| gogoga-words-read-along | `read-along` |
| gogoga-words-practice | `practice` |
| gogoga-words-games | `games` |
| gogoga-words-roleplay | `roleplay` |
| gogoga-words-story | `story` |
| gogoga-words-phonics | `phonics` |

成功后会打印素材的链接，把它告诉用户。上传上限 40 MB。

## 其他命令

- `gogoga.py list`：列出自己上传过的素材。
- `gogoga.py delete <id>`：删除一份。删除前先和用户确认。
- `gogoga.py logout`：在这台电脑上退出。

## 出错时

- `not signed in`：重新 `login`。
- `missing files`：清单引用的图片不在磁盘上，先确认文件路径，或重新导出。
- `素材导入失败：Crop outside …`：清单里的裁切框超出了图片，修正 `crop` 后重新上传。
