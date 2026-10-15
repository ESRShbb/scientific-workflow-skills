---
name: nmr-processing
description: Inventory NMR sources, export existing MestReNova pages, and guide evidence-based 1D NMR processing or interpretation on working copies. Use for MNOVA, Bruker FID, NMR peak tables, reference checks, and spectrum display changes. Spectrum-atlas document layout is outside this skill.
---

# NMR processing

## Choose the requested operation

| Request | Procedure |
|---|---|
| Locate data, inventory a Bruker folder/ZIP or record selected MNOVA pages | [Source inventory](references/source-inventory.md) |
| Export an experimenter's existing MNOVA results unchanged | [Native export](references/native-export.md); no new interpretation or signal ledger required |
| Change spectrum appearance | [Scientific and display workflow](references/scientific-workflow.md), display section |
| Process FID, review referencing, integrate or report chemical shifts | [Scientific and display workflow](references/scientific-workflow.md) |

Preserve the distinction between source inventory, native file readability, processing quality, scientific interpretation, and visual acceptance. A successful script proves only its stated checks.

## Operating boundaries

- Use explicit input locations, selected versions and a new output directory. Never edit source data. Existing results selected by the user stay selected; modification time and a filename containing `final` do not establish correctness or adoption.
- Identify sample, batch, nucleus and source separately. A matching filename is a discovery clue, not proof of chemical identity. Missing identity can block interpretation without blocking an accurately labelled source inventory or unchanged export.
- Copy before native operations. Compare source and working-copy hashes before and after unchanged export. For intentional edits, preserve the source hash and verify saved changes by closing and reopening the native result.
- Installed software does not establish valid licensing or scripting support. Record executable/version and actual interface results. Never close or kill an existing user session to run a job.
- Do not turn automatic peak lists, expected structures or literature values into measured shifts, integrals, couplings or assignments. Keep observed signals, proposed roles and reviewed conclusions distinguishable.
- Changes to fonts, labels and page layout do not authorize phase, baseline, reference or integration changes. Preserve embedded structures and acquisition metadata.
- Use a few representative inputs for a new software version or new operation before expanding. A failed item need not block unrelated samples.

## Current capability boundary

This is an extraction candidate, version 0.2.3. The Python utilities use only Python 3.10+ standard library. Run them with a Python 3 interpreter available on the target computer; Windows examples may use `py -3 -B`, other systems `python3 -B`.

- Executable helpers: hash-locked source inventory, safe Bruker copy/extraction, unchanged MNOVA export job preparation, and technical export evidence checking.
- Inventory supports 1D Bruker `acqus` + `fid`, and explicit 1H, 13C, 19F mappings. MNOVA and `1r` registration verifies bytes and declarations, not native readability or scientific content. Other nuclei, 2D/`ser`, vendor formats and quantitative NMR need a separately verified method.
- The included QS export template uses native Mnova APIs inherited from an earlier working workflow. The adapted runner needs a real native test on the target installation. Only a Windows runner is included; macOS/Linux native launching is not validated or implemented here.
- Raw spectrum processing and signal interpretation are guided procedures, not a bundled automatic processing engine. Do not describe them as executed merely because the inventory helper passed.

Read [validation cases](references/validation.md) before first use on a new environment. Preserve actual environment results in the task output, not as new universal rules in this skill.


The runner also checks common automatic script startup effects and separates verified export from pending application cleanup.
