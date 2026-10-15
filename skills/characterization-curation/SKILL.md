---
name: characterization-curation
description: Curate chemical characterization evidence across NMR, IR, HRMS, HPLC and experiment records, preserving sample identity, batch provenance, selected sources and gaps. Use for compound characterization tables or supporting-information preparation; native processing and spectrum-atlas layout are separate operations.
---

# Characterization curation

Read [evidence workflow](references/evidence-workflow.md). Start from the user-selected compound scope and source records, not a predetermined chapter, scheme sequence or folder name.

Maintain one evidence table relating display ID, original ID/aliases, structure, sample/batch, source file/locator, modality, selected version and decision. Reuse an existing suitable table rather than creating competing ledgers.

- Inventory requests end with a source/gap report; they do not require redrawing structures, reprocessing NMR or generating documents.
- For compilation, resolve identity and provenance, transcribe/check modality-specific values, and produce requested outputs. Unresolved local items remain explicit without blocking unrelated verified items.
- Keep `missing`, `not_applicable`, `excluded`, `unusable`, `candidate` and `verified` distinct. User-selected source version is not automatically scientific verification.
- Do not infer connectivity, regio/stereochemistry, purity, batches or measured values merely from matching names or a molecular formula.
- Native editing is needed only when requested. If available, use an NMR, ChemDraw or atlas skill appropriate to that operation; those skills are not prerequisites for an ordinary evidence inventory.

`scripts/check_sources.py` checks file/locator contracts and hashes in a JSON manifest. It reports source integrity separately from scientific review and detects ambiguous selected sources. It does not read spectra or prove chemical identity. Python 3.10+ standard library is sufficient. See [validation](references/validation.md).

Version 0.2.3 is a portable candidate. No assay thresholds, source library, current paper, fixed notebook numbering or private experimental data are included.
