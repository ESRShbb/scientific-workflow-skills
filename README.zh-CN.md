# Scientific Workflow Skills

[English](README.md) | 简体中文 | [日本語](README.ja.md)

六个面向化学与生命科学流程的通用 Agent 技能（skill）。每个 skill 包含操作说明，以及按需使用的脚本和参考资料。它们都是普通文件，Agent 可以直接读取，不需要专用的技能调用接口。

**版本：0.2.3。** 从实际科研流程中提炼。

## 包含的技能

| Skill | 用途 |
| --- | --- |
| [nmr-processing](skills/nmr-processing/SKILL.md) | 盘点 NMR 来源，导出现有 MestReNova 页面，在工作副本上指导数据处理与解析。 |
| [prism-ic50-analysis](skills/prism-ic50-analysis/SKILL.md) | 提取支持的 PZFX XY 数据，整理 Prism 原生结果导出，汇总经过审核的 IC50 数值。 |
| [characterization-curation](skills/characterization-curation/SKILL.md) | 整理化合物身份、批次及 NMR、IR、HRMS、HPLC 证据，追溯来源并标明缺项。 |
| [chemdraw-ole](skills/chemdraw-ole/SKILL.md) | 制作原生化学结构图，检查或交付 Office 中可编辑的 ChemDraw 对象。 |
| [scientific-figure-format](skills/scientific-figure-format/SKILL.md) | 检查科研图片的标注、排版、字体和视觉完整性，不绑定特定绘图软件。 |
| [illustrator-scientific-figure](skills/illustrator-scientific-figure/SKILL.md) | 在 Illustrator 中整理和核验可编辑科研图片，包括原生文件保存、重新打开及导出检查。 |

## 如何让 Agent 使用

克隆仓库：

```sh
git clone https://github.com/ESRShbb/scientific-workflow-skills.git
```

把 `skills/` 中需要的技能文件夹复制到自己项目的 `.agents/skills/`，保留每个文件夹内的脚本和参考资料。支持该目录的 Agent 工具可以自动发现技能；其他工具可以直接读取相应的 `SKILL.md`，也可以按工具要求配置技能目录。`agents/openai.yaml` 是可选的工具界面元数据。

如果工具不支持自动发现，在项目的 `AGENTS.md` 中加一段简短入口即可，例如：

```text
处理 NMR 时，先读取 .agents/skills/nmr-processing/SKILL.md，
再按当前任务读取相关参考资料。使用原始数据的工作副本。
```

随后用自然语言提出任务，给出输入路径和希望得到的结果：

> 把这个 MNOVA 文件的第 1、2 页导出成 PNG，放到新的输出文件夹，原文件保持不变。

> 提取这个 PZFX 文件的 XY 数据，告诉我哪些样品标签或浓度单位还不明确。

> 看看这张图的标注和排版有什么问题，指出需要修改的具体位置。

Agent 需要具备读取本地文件、运行脚本的工具和权限；操作原生文件时，还需要能够控制已安装的软件。只有模型或聊天界面、没有这些工具时，不能仅靠读取说明完成实际操作。

## 环境要求

- Python 辅助脚本需要 Python 3.10 或更新版本；随附的可移植脚本测试仅使用标准库。
- 原生操作需要自行安装并获得相应软件授权：MestReNova、GraphPad Prism、ChemDraw、Microsoft Office 或 Adobe Illustrator。
- 随附的软件启动及 COM 辅助脚本主要面向 Windows。部分流程需要 PowerShell，可选依赖为 `pywin32`，具体见对应 skill 的参考资料。来源盘点、静态检查和数值汇总不一定需要原生软件。
- Figure 格式技能提供审阅方法，不包含可执行的软件驱动程序。

Windows 上如果 `python` 指向旧版解释器，可以改用 `py -3`。其他系统使用本机对应的 Python 3 命令。

## 检查技能包

```sh
python -B scripts/validate.py
```

这会检查技能入口、本地 Markdown 链接及 Python 语法，再分别运行随附的合成数据测试。它不会启动科研软件，也不能证明科学内容正确。GitHub Actions 在 Windows 和 Linux 上执行同样的检查。

仓库不提供私人实验数据或软件程序。测试材料由代码合成。技能正文和详细参考资料目前以英文维护；此文件提供中文使用说明。另见[第三方说明](THIRD_PARTY_NOTICES.md)和 [MIT 许可证](LICENSE)。
