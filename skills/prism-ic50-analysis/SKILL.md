---
name: prism-ic50-analysis
description: Extract GraphPad Prism PZFX concentration-response data and organize traceable IC50 analysis, native fitting verification, replicate QC and summaries. Use for inhibitor dose-response or SAR activity tables; do not infer a fitting model from a filename.
---

# Prism IC50 analysis

First distinguish extraction, new fitting, and summarizing existing fits. Read [analysis method](references/analysis.md) for the requested stage. Source files remain unchanged; work in a new output directory.

1. Inventory inputs, assay conditions, sample/batch identity, table and Y-column mapping, concentration units and X representation (concentration or log concentration). A file title does not resolve an empty compound label.
2. Use `scripts/pzfx_inventory.py` to extract supported numeric XY tables. It preserves all Y subcolumns, blank cells and identical records. Unsupported cells/layouts are reported rather than coerced. This is extraction, not analysis or compound assignment.
3. Before fitting, specify the model, response normalization, constraints, weighting, control treatment, replicate hierarchy and fitting engine. A supplied analysis template must be inspected and recorded with its hash; no template is bundled as a scientific default.
4. Run the selected analysis in the actual Prism version on copies. Verify the model, data linkage and exported parameter labels against the saved/reopened project. Do not call a Python result a Prism result.
5. Review convergence, uncertainty/identifiability, curve coverage, flags and residuals. Keep all replicate results and exclusions. Do not use an R-squared threshold alone as a universal acceptance rule.
6. Summarize the explicitly selected independent units with a stated method. Technical subcolumns do not establish independent biological repeats. Report n, units, dispersion and excluded/qualified results separately.

Python 3.10+ standard library suffices for the included extraction and summary helpers. `scripts/summarize_fits.py` consumes an explicitly reviewed numeric CSV; it neither fits curves nor decides QC. See [validation](references/validation.md).

For native result export, `scripts/prepare_native_export.py` prepares a copy and command file from that project's verified sheet/parameter map; `scripts/read_result_labels.py` preserves the labeled export. These do not automatically discover analysis dependencies or authorize new fitting. Details are in [analysis method](references/analysis.md).

Version 0.2.3 is a portable candidate. Local synthetic extraction/summary tests do not establish native Prism operation. Native fitting is a documented procedure, not a bundled cross-version unattended fitting engine. Binary `.prism`/`.pzf`, non-XY tables and unsupported PZFX representations require native export or an independently verified reader.


For native projects with existing results, Windows helper `scripts/discover_result_sheets.py` enumerates result titles and verifies their numbered locations before `scripts/run_native_exports.py` exports them independently. `scripts/read_native_navigator.ps1` provides a native UIAutomation route when available. Read the analysis reference before using these optional helpers.
