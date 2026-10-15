# Scientific Workflow Skills

**化学与生命科学 AI 技能集**

[English](README.md) | 简体中文 | [日本語](README.ja.md)

让 AI 帮你整理核磁、汇总活性数据、绘制化学结构和制作科研图片。

**技能（skill）**可以理解为给 AI 准备好的操作方法和工具。安装后，直接告诉 AI 你想做什么。

## 能帮我做什么？

| 技能 | 用途 |
| --- | --- |
| [核磁数据整理](skills/nmr-processing/SKILL.md) | 查找核磁文件，导出 Mnova 谱图，辅助处理与核对。 |
| [IC50 数据整理](skills/prism-ic50-analysis/SKILL.md) | 提取 Prism 数据，整理已有拟合结果，汇总经过核对的 IC50 数值。 |
| [化合物表征整理](skills/characterization-curation/SKILL.md) | 汇总 NMR、IR、HRMS、HPLC 信息，标明来源和缺项。 |
| [化学结构与反应式](skills/chemdraw-ole/SKILL.md) | 使用 ChemDraw 绘图，并将可编辑结构放入 Word。 |
| [科研图片检查](skills/scientific-figure-format/SKILL.md) | 检查标注、字号、排版和图中内容的对应关系。 |
| [Illustrator 科研作图](skills/illustrator-scientific-figure/SKILL.md) | 拼接、修改和导出可编辑的科研图片。 |

## 怎么安装？

在能读取本地文件、运行程序的 AI 助手中，复制发送下面这段话：

```text
帮我安装这个仓库里的科研技能：
https://github.com/ESRShbb/scientific-workflow-skills

按我当前使用的 AI 工具选择安装位置。
请包含每个技能的脚本和参考文件，并告诉我安装了哪些技能。
```

也可以只安装需要的技能，例如“只安装核磁相关的技能”。手动安装方法见[安装说明](INSTALLATION.md#简体中文)。

## 装好后怎么用？

把文件的位置告诉 AI，再像平时一样提出要求：

- “把这个 Mnova 文件里的氢谱和碳谱导出成图片。”
- “帮我整理这个 Prism 文件里的 IC50 结果。”
- “把这些化合物的表征数据整理成一张表，标出缺什么。”
- “用 ChemDraw 帮我画这个反应式，放进 Word，保持可以编辑。”
- “看看这张图的标注和排版有什么问题，指出需要改的地方。”
- “用 Illustrator 把这些小图拼好，保存可编辑文件和 PDF。”

## 需要准备什么？

- 一个能读取电脑文件、运行程序的 AI 助手，也就是这里说的 Agent。
- 当前任务需要的软件，例如 Mnova、Prism、ChemDraw、Word 或 Illustrator，需要自行安装并获得授权。随附的软件操作工具主要面向 Windows。

只需准备当前任务用到的软件，不必全部安装。Python 等具体配置可以让 AI 按[安装说明](INSTALLATION.md#简体中文)处理。

[开发说明](DEVELOPMENT.md)（英文） · [第三方说明](THIRD_PARTY_NOTICES.md)（英文） · [MIT 许可证](LICENSE)
