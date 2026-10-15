# Scientific Workflow Skills

English | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

Six reusable agent skills for chemistry and life-science workflows. Each skill combines focused instructions with optional scripts and references. They are plain files: an agent can read and use them without a proprietary skill invocation API.

**Version 0.2.3.** Developed from practical research workflows.

## Skills

| Skill | Purpose |
| --- | --- |
| [nmr-processing](skills/nmr-processing/SKILL.md) | Inventory NMR sources, export existing MestReNova pages, guide processing and interpretation on copies. |
| [prism-ic50-analysis](skills/prism-ic50-analysis/SKILL.md) | Extract supported PZFX XY data, organize native Prism result exports and summarize reviewed IC50 values. |
| [characterization-curation](skills/characterization-curation/SKILL.md) | Relate compound identities, batches and NMR/IR/HRMS/HPLC evidence with source and gap tracking. |
| [chemdraw-ole](skills/chemdraw-ole/SKILL.md) | Prepare native chemical drawings and inspect or deliver editable ChemDraw objects in Office. |
| [scientific-figure-format](skills/scientific-figure-format/SKILL.md) | Review scientific labels, layout, typography and visual integrity independently of drawing software. |
| [illustrator-scientific-figure](skills/illustrator-scientific-figure/SKILL.md) | Assemble and verify editable Illustrator figures, including native save/reopen/export checks. |

## Use with an agent

Clone this repository:

```sh
git clone https://github.com/ESRShbb/scientific-workflow-skills.git
```

Copy the skill folders you need from `skills/` into your project's `.agents/skills/`. Keep each folder intact, including its scripts and references. Hosts that support this location can discover the skills automatically. For other hosts, point the agent directly at the corresponding `SKILL.md`; configure its native skill directory if desired. `agents/openai.yaml` is optional host metadata.

For a project without automatic discovery, a short project `AGENTS.md` entry is sufficient:

```text
For NMR work, read .agents/skills/nmr-processing/SKILL.md and the references
needed for the requested operation. Use working copies of source data.
```

Then ask naturally, supplying input paths and the desired output:

> Export pages 1 and 2 of this MNOVA file as PNGs into a new output folder. Keep the original unchanged.

> Extract the XY data from this PZFX file and tell me which sample labels or concentration units need clarification.

> Review this figure for label and layout problems. Show me the specific areas that need fixing.

An agent needs permission and tools to read local files, run the relevant scripts and, for native operations, control the installed application. A model or chat interface without those capabilities cannot execute the workflow merely by reading the instructions.

## Requirements

- Python 3.10+ for the included Python helpers. Their portable tests use the standard library only.
- Native operations require the relevant application, installed and licensed separately: MestReNova, GraphPad Prism, ChemDraw, Microsoft Office or Adobe Illustrator.
- The bundled native launch/COM helpers primarily target Windows. Some require PowerShell and optionally `pywin32`; the skill references identify the route. Inventory, static checks and numerical summaries do not all require native applications.
- The figure-format skill is a review method and has no executable driver.

On Windows, use `py -3` if `python` points to an older interpreter. On other systems, use the appropriate Python 3 command.

## Check the package

```sh
python -B scripts/validate.py
```

This checks package entrypoints, local Markdown links and Python syntax, then runs the bundled synthetic tests in separate processes. It does not launch scientific applications or establish scientific correctness. GitHub Actions runs the same checks on Windows and Linux.

No private experimental inputs or application binaries are distributed. Tests generate synthetic fixtures. See [third-party notices](THIRD_PARTY_NOTICES.md) and the [MIT license](LICENSE).
