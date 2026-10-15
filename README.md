# Scientific Workflow Skills

**AI skills for chemistry and life-science research**

English | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

Organize NMR files, summarize activity data, draw chemical structures and prepare scientific figures with your AI assistant.

A **skill** gives your AI assistant instructions and tools for a particular task. Install it, then ask for what you need in everyday language.

## What can I do with these skills?

| Skill | What it helps with |
| --- | --- |
| [NMR data](skills/nmr-processing/SKILL.md) | Find NMR files, export Mnova spectra and assist with processing and review. |
| [IC50 data](skills/prism-ic50-analysis/SKILL.md) | Extract Prism data, organize existing fit results and summarize reviewed IC50 values. |
| [Compound characterization](skills/characterization-curation/SKILL.md) | Organize NMR, IR, HRMS and HPLC information, with sources and missing items. |
| [Chemical structures and reactions](skills/chemdraw-ole/SKILL.md) | Draw with ChemDraw and place editable structures in Word. |
| [Figure review](skills/scientific-figure-format/SKILL.md) | Check labels, font sizes, layout and correspondence between panels. |
| [Illustrator figures](skills/illustrator-scientific-figure/SKILL.md) | Assemble, edit and export editable scientific figures. |

## How do I install them?

Use an AI assistant that can read files and run programs on your computer. Copy this message into it:

```text
Install the scientific skills from this repository:
https://github.com/ESRShbb/scientific-workflow-skills

Choose the installation location for the AI tool I am using.
Include each skill's scripts and reference files, and tell me what you installed.
```

You can also ask for just one skill, such as NMR. For manual installation, see the [installation guide](INSTALLATION.md#english).

## What do I say after installing?

Tell the AI where your files are and what you want:

- “Export the proton and carbon spectra in this Mnova file as images.”
- “Organize the IC50 results in this Prism file.”
- “Put these compounds' characterization data in a table and flag anything missing.”
- “Draw this reaction in ChemDraw and put it in Word so I can still edit it.”
- “Check this figure's labels and layout, and show me what needs fixing.”
- “Arrange these panels in Illustrator and save an editable version and a PDF.”

## What do I need?

- An AI assistant with access to your local files and programs.
- The software for your task, installed and licensed separately: Mnova, Prism, ChemDraw, Word or Illustrator. Most included software-control helpers are for Windows.

You only need the applications relevant to your task. The AI can consult the [installation guide](INSTALLATION.md#english) for Python and other setup details.

[Developer guide](DEVELOPMENT.md) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [MIT License](LICENSE)
