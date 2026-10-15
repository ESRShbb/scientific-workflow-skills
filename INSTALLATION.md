# Installation / 安装说明 / インストールガイド

[English README](README.md) · [中文首页](README.zh-CN.md) · [日本語 README](README.ja.md)

## English

Start with the installation message in the README. The details below are for manual setup or for the AI doing the installation.

1. Download the repository using GitHub's **Code → Download ZIP** and extract it, or run:

   ```sh
   git clone https://github.com/ESRShbb/scientific-workflow-skills.git
   ```

2. Copy the complete folders you need from `skills/` into the skill location supported by your AI tool. For tools that support project-local `.agents/skills/`, place them there. Keep `SKILL.md`, scripts, references and other supporting files together.
3. If your tool does not discover skills automatically, ask the AI to read the relevant `SKILL.md` at its actual path. For repeated use, you can add that path to your project's instructions. A tool without local file or program access will need those capabilities before it can run the workflow.
4. Ask the AI which dependencies your task needs. Python helpers require Python 3.10+. Most inventory and summary helpers use only the standard library. Some Windows application-control helpers also require PowerShell or `pywin32`. The relevant skill explains the details.

On Windows, use `py -3` when `python` points to an older interpreter. Install only the scientific applications needed for your task and use a valid license.

Example project layout:

```text
my-project/
  .agents/
    skills/
      nmr-processing/
        SKILL.md
        agents/
        scripts/
        references/
```

The `agents/openai.yaml` file is optional metadata for tools that use it. The skill instructions and resources can also be read directly by other agents. Skill instructions and detailed references are currently maintained in English.

## 简体中文

优先使用首页的安装提示词。以下步骤供手动安装，或让 AI 安装时参考。

1. 在 GitHub 点击 **Code → Download ZIP**，下载后解压。也可以使用上方的 `git clone` 命令。
2. 从 `skills/` 中选取需要的完整技能文件夹，复制到当前 AI 工具支持的技能目录。支持项目内 `.agents/skills/` 的工具可以使用该位置。保留 `SKILL.md`、脚本、参考资料等所有配套文件。
3. 如果工具不会自动发现技能，直接告诉 AI 对应 `SKILL.md` 的实际路径，让它先读取。经常使用时，可以把该路径写进项目说明。如果工具还不能访问本地文件或运行程序，需要先具备这些功能。
4. 让 AI 根据任务检查依赖。Python 脚本需要 Python 3.10 或更新版本；多数盘点和汇总脚本只用标准库。部分 Windows 软件操作工具还需要 PowerShell 或 `pywin32`，具体见相应技能。

Windows 上如果 `python` 指向旧解释器，改用 `py -3`。科研软件只安装当前任务需要的，并使用有效授权。目录结构可参考上方示例。

`agents/openai.yaml` 是供部分工具使用的可选元数据，其他 Agent 可以直接读取技能说明和配套文件。技能正文及详细参考资料目前以英文维护。

## 日本語

まずは README のインストール用メッセージを使ってください。以下は手動で設定する場合や、インストールを行う AI 向けの手順です。

1. GitHub の **Code → Download ZIP** からダウンロードして展開します。上記の `git clone` コマンドも使えます。
2. `skills/` から必要なスキルのフォルダー全体を、利用する AI ツールのスキル配置先にコピーします。プロジェクト内の `.agents/skills/` に対応するツールでは、その場所を使えます。`SKILL.md`、スクリプト、参考資料などをまとめて保持してください。
3. 自動検出されない場合は、該当する `SKILL.md` の実際のパスを AI に伝えて読ませます。繰り返し使う場合は、プロジェクトの案内にそのパスを記載できます。ファイルの読み取りやプログラム実行ができないツールでは、先にその機能が必要です。
4. 作業に必要な依存関係を AI に確認させます。Python スクリプトには Python 3.10 以降が必要です。多くの一覧作成・集計スクリプトは標準ライブラリだけで動作します。Windows のソフト操作用ツールの一部は PowerShell や `pywin32` も必要とします。詳細は各スキルに記載されています。

Windows で `python` が古いインタープリターを指す場合は `py -3` を使ってください。研究用ソフトは必要なものだけをインストールし、有効なライセンスを用意します。フォルダー構成は上の例を参照してください。

`agents/openai.yaml` は一部のツール向けの任意メタデータです。他のエージェントもスキルの手順と関連ファイルを直接読み込めます。スキル本体と詳細な参考資料は現在、英語で管理しています。
