# Scientific Workflow Skills

[English](README.md) | [简体中文](README.zh-CN.md) | 日本語

化学・生命科学の研究で使える AI スキル集です。NMR ファイルの整理、活性データの集計、化学構造の作図、研究用図版の作成を支援します。

**スキル（skill）**は、AI に渡す作業手順と道具のセットです。インストールしたら、普段の言葉で作業を頼めます。

## 何ができる？

| スキル | 用途 |
| --- | --- |
| [NMR データの整理](skills/nmr-processing/SKILL.md) | NMR ファイルの検索、Mnova スペクトルの書き出し、処理や確認の補助。 |
| [IC50 データの整理](skills/prism-ic50-analysis/SKILL.md) | Prism データの抽出、既存のフィッティング結果の整理、確認済み IC50 値の集計。 |
| [化合物の特性評価データの整理](skills/characterization-curation/SKILL.md) | NMR・IR・HRMS・HPLC の情報をまとめ、出典と不足項目を整理。 |
| [化学構造・反応式の作図](skills/chemdraw-ole/SKILL.md) | ChemDraw で作図し、編集可能な構造を Word に配置。 |
| [研究用図版のチェック](skills/scientific-figure-format/SKILL.md) | ラベル、文字サイズ、レイアウト、図中の対応関係を確認。 |
| [Illustrator での図版作成](skills/illustrator-scientific-figure/SKILL.md) | 編集可能な研究用図版の組み立て、修正、書き出し。 |

## インストール方法

パソコン上のファイルを読み、プログラムを実行できる AI アシスタントに、次の文章をコピーして送ってください。

```text
このリポジトリの研究用スキルをインストールして：
https://github.com/ESRShbb/scientific-workflow-skills

今使っている AI ツールに合った場所に配置して。
各スキルのスクリプトと参考ファイルも含めて、何をインストールしたか教えて。
```

「NMR のスキルだけ入れて」のように、必要なものだけ指定することもできます。手動での手順は[インストールガイド](INSTALLATION.md#日本語)をご覧ください。

## インストール後の使い方

ファイルの場所を伝えて、普段の言葉で頼みます。

- 「この Mnova ファイルのプロトンと炭素のスペクトルを画像にして。」
- 「この Prism ファイルの IC50 の結果をまとめて。」
- 「これらの化合物の特性評価データを表にして、足りない項目を教えて。」
- 「ChemDraw でこの反応式を描いて、後で編集できるように Word に入れて。」
- 「この図のラベルとレイアウトを見て、直す箇所を教えて。」
- 「Illustrator でこれらのパネルを並べて、編集用ファイルと PDF を保存して。」

## 必要なもの

- パソコン上のファイルやプログラムを扱える AI アシスタント。このようなツールを、ここではエージェントと呼びます。
- 作業に使うソフト。Mnova、Prism、ChemDraw、Word、Illustrator などは別途インストールし、有効なライセンスを用意してください。付属のソフト操作用ツールは主に Windows 向けです。

必要なソフトだけ用意すれば使えます。Python などの設定は、AI に[インストールガイド](INSTALLATION.md#日本語)を読ませて進められます。

[開発ガイド](DEVELOPMENT.md)（英語） · [第三者製品に関する注記](THIRD_PARTY_NOTICES.md)（英語） · [MIT ライセンス](LICENSE)
