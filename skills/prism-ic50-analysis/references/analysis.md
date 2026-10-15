# Analysis choices and evidence

## Extract without changing identity

Run `python3 -B /path/to/skill/scripts/pzfx_inventory.py input.pzfx --output new-inventory.json` (Windows may use `py -3 -B`). The report includes source SHA, table ID/title, Y column index/title, every subcolumn and row, duplicate-content candidates and unsupported tables. An extraction error is not an absent experiment. Hash-identical numbers can be independent experiments or copied records; do not silently remove either.

No compound-prefix normalization, filename-based identity, automatic RT-table exclusion or fixed four-replicate limit is applied. Resolve table/Y labels using an explicit sample map before joining an SAR table. Check omitted/excluded cells against the native project.

## Define the analysis

Record whether IC50 means an assay-relative fitted midpoint or an absolute 50% response, and whether the assay supports that interpretation. Specify concentration units, linear versus log X, direction of response, normalization/control basis, free/fixed top and bottom, Hill slope, weighting and handling of zeros and missing values. Zero cannot be log-transformed; its role as a control must be documented. Do not normalize each replicate to its own extrema unless the chosen assay method justifies that operation. Poor plateaus can make a numerical fit insufficiently identified.

Choose independent fit per experiment, pooled fit or another model based on experiment design. Retain technical replicate information and within-experiment structure. Do not replace censored values such as `>highest concentration` with the limit and average them as exact IC50s. Keep Prism's ambiguous-fit flags and units alongside numeric values.

## Native Prism execution

Determine actual analysis dependencies, not just which analysis sheets exist. For each fit record the source table/analysis, X transformation, normalization if used, model, constraints and units, with a native title/dialog or exported setting as evidence. Normalization elsewhere in the project does not mean that the fit consumes it. Top/Bottom outside 0-100 can motivate checking the chain but do not independently prove the chain. When provenance cannot be read, report it as unresolved.

Locate executable/version and license on the target machine. User-specified software paths are inputs, not constants. Test the actual command interface and export behavior for that version on a small known project. A command that exits normally but exports empty results failed.

When reusing a native analysis template, verify input slots and results-table identities, transformation/normalization/nonlinear-fit chains, column/subcolumn mapping and result labels. Fixed result row numbers or a rule such as every third results sheet are template-specific. Never reuse them across templates without verification. Command file encoding is version/environment-dependent; verify non-ASCII paths and exported text, not a universal GBK assumption.

Save a new native project. Close and reopen the task's document, inspect plotted curves/data, then export results from that exact project. Do not terminate an existing user's Prism session. Record scientific parameters, software version, template hash, input-to-output mapping and any native limitations. A numerical cross-check must be labelled as a different engine with explicitly matched model/weighting/constraints; agreement on one historical dataset is not a universal test.

## Reusable native export preparation

Prefer the native-label route when this installation supports `ExportTable`: inspect the results navigator and verify the sheet number/title, then run `prepare_native_export.py input.pzfx --sheets verified_sheets.json --output new-job --label-mode native --encoding <host encoding>`. The map only needs number, expected_title, verified and evidence; no parameter row guesses. Execute its command file using the installed Prism command interface. It writes `title_Rn.txt` with WTitle and `result_Rn.txt` with ExportTable. Read them using `read_result_labels.py result_Rn.txt --title-file title_Rn.txt --expected-title <verified title> --encoding <actual encoding> --output new-result.json`. Inspect the exported column headers and the Best-fit/CI sections. If ExportTable is unavailable, use the mapped route below after verifying its coordinates. Opening an existing project may cause native recalculation; describe actions actually issued rather than inferring engine behavior from an unchanged source hash.

`scripts/prepare_native_export.py input.pzfx --sheets verified_sheets.json --output new-job --encoding <host encoding>` copies the project and generates a Prism command file. It does not launch Prism, fit, or recalculate. `verified_sheets.json` contains `{"sheets":[{"number":1,"expected_title":"Exact native sheet title","verified":true,"evidence":"Native project locator or screenshot","columns":[1,2],"parameters":[{"row":5,"label":"Parameter label read in native UI","verified":true,"evidence":"Parameter label and row read in this native project"}]}]}`. All numbers and labels in this example are placeholders, not defaults; set verified=true only after checking their actual native locations. Sheet indices and parameter row/column coordinates are supplied only after inspection of that project. Columns form an increasing contiguous range. Do not enumerate by trying successive indices until failure; a nonexistent results sheet can leave Prism waiting for interaction.

The tool preserves a full numeric `WSheet` export and generates selected `WBlock` rows prefixed with the supplied verified parameter labels. These labels come from the operator's native-verified mapping; the command does not discover native row labels. `WTSheet` transposes numeric output and does not recover parameter labels. Never label a guessed row as IC50. Run the command file using the scripting interface actually supported by that installation; do not start another job while an earlier one is waiting, kill user sessions, or invoke `Exit` on a shared session. Verify the command encoding on that host. `read_result_labels.py export.txt --encoding <actual encoding> --expected-title <exact title> --output new-report.json` preserves labels and values and rejects empty/numeric-only evidence. It does not infer units or dependencies, and repeated labels remain separate. Select IC50 by the verified parameter label and column identity, never an inherited row number.

The PZFX inventory now reports XY-table, Y-column, subcolumn and data-cell counts directly. These are extraction counts, not the number of independent experiments or fitted curves; excluded, blank and unsupported cell status remains available. Use those counts in reports rather than mental multiplication.

### Navigate and finish an export

Find results-sheet numbers in this project's native navigator, then confirm each title before using its table. For an installation supporting these commands, the minimal pattern is:

```text
GoTo R <verified results-sheet number>
OpenOutput "<new title output path>"
WTitle
CloseOutput
ExportTable "<new table output path>"
```

Replace the placeholders with inspected sheet numbers and actual paths; compare the exported title with the expected title and inspect the nonempty labeled table. The preparation helper generates this pattern. If a navigation loop stalls, use the inspected sheet map instead of continuing blind enumeration; loop syntax and behavior can vary with Prism versions.

`Close` closes the task document and `CloseScriptDialog` dismisses its script dialog; neither promises application-process exit. Judge an export by the expected title/table files, readable labels/values and task-document cleanup. A process still running is not by itself an export failure. For a borrowed application session, leave the application running. For a separately launched task session, close only that session through its supported native interface after export verification; do not wait for application exit as the only completion signal or force-terminate it.

The XML inventory helper reads supported numeric data tables. It does not decode the complete compressed analysis template or establish native model/result settings; read those in Prism.

## QC and aggregation

Interpret slope direction from the actual equation, not the parameter name. For `Y=Bottom+(Top-Bottom)/(1+10^((LogIC50-X)*HillSlope))`, with Top>Bottom and X=log concentration, negative HillSlope gives a descending response. Evaluate X on both sides of LogIC50 to check direction. Preserve an incomplete confidence interval in its original order: `??? to b` means the lower bound is undetermined; `a to ???` means the upper bound is undetermined.

Inspect convergence/ambiguity, confidence intervals, plateau coverage, experimental concentration range, residual patterns, fitted slope and relevant controls. IC50 outside the range may be an extrapolated/qualified estimate, not automatically a valid measured result. Exclusion criteria belong to the documented assay plan; keep reasons and original values. Do not tune criteria to preserve a preferred ranking.

`summarize_fits.py fits.csv --output new-summary.json --method arithmetic --min-n 3` requires CSV columns `sample_id,experiment_id,unit,ic50,decision,reason`. Each row is one already-reviewed independent experiment, with `decision` equal to `include` or `exclude`. Excluded rows may contain censored/text results but require a reason; included rows must be finite positive exact numbers. Duplicate sample/experiment keys are rejected. Mixed units for a sample are rejected rather than converted silently.

Arithmetic mode reports mean and sample SD; log mode reports geometric mean, SD in log10 units and multiplicative geometric SD. These are not interchangeable with a confidence interval or arithmetic SD. For n=1, dispersion is unavailable. `--min-n` is explicitly supplied; below it, summary values are left empty while observations remain in the report. This helper cannot confirm that experiment IDs represent independent experiments.


## Windows helpers for navigation and isolated exports

Prefer `python3 -B scripts/discover_result_sheets.py <source.pzfx> --output <new discovery folder> --software <Prism executable> --encoding <command encoding> --text-encoding <native output encoding>` for a project containing existing results. It selects the first results sheet, uses native `ForEachSheet` to enumerate that sheet family, then verifies each title with numbered `GoTo R`/`WTitle` calls bounded by that actual enumeration. `sheet_map.json` is usable only when discovery and both normal process exits succeeded. This avoids guessing an upper index and does not depend on the navigator's UI language. No-result projects or unsupported command interfaces are reported as blocked probes.

Check actual command/output encoding and software version. If one installed version cannot expose the needed interface, another installed version compatible with the source may be tested, recording which engine read/exported the results. Do not silently treat results from different software versions as one scientific validation. The UI route below remains useful for direct navigator evidence or an unavailable command enumeration.

1. Run `read_native_navigator.ps1 -InputProject <source.pzfx> -Software <Prism executable> -OutputDirectory <new navigator folder> -ResultsSection <actual results-section title>`. It opens a copy in a new session and reads direct result children in native navigation order. The default section is `Results`; use the actual UI language (for example `结果`). `-PlaceholderPattern` selects the non-result new-analysis item. Check `navigator.json` and its raw children before exporting; an unavailable tree or ambiguous section remains unresolved. It closes only the separately started session.
2. Run `python3 -B scripts/run_native_exports.py <source.pzfx> --sheets <navigator.json> --output <new export folder> --software <Prism executable> --encoding <command encoding>`. Windows needs optional `pywin32`. Each verified result uses its own copied project and command file, so an empty/error table cannot cancel later exports. An inspected empty sheet can be explicitly marked `skip: true` with evidence in a copied sheet map; missing output alone is not proof of emptiness.
3. Review each `title_Rn.txt` and labeled `result_Rn.txt` using `read_result_labels.py`. Navigator and WTitle may localize titles differently; keep both and verify their correspondence, rather than silently equating translations. `EXPORTED_REVIEW_REQUIRED` means files exist, not that their content/model/units are accepted. Record native model and input dependencies separately.

These helpers reject an existing Prism session. `Exit` is used only in their independently launched job. They request normal closing of their own process if an export stalls; if it remains open they stop the batch with `CLEANUP_PENDING`, preserving logs. No user process is force-terminated. Use the existing preparation helper or manual native workflow when UIAutomation/command support is unavailable.
