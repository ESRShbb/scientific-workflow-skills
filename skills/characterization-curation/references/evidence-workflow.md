# Evidence workflow

## Match before reporting

Keep original label, display label, batch/acquisition, structure locator and evidence for their relationship. Match complete identifiers, not prefixes: sample `2-4` must not silently match `2-47`. Same formula or similar spectrum is insufficient identity evidence. Compare protection state, acid/ester/salt, connectivity, isotope and stereochemical information as relevant.

For structures reconstructed from a drawing or record, distinguish explicit evidence from inference. Missing stereochemistry stays unspecified. A downstream final product does not by itself determine the exact intermediate or experimental procedure. Native fragments selected by nearby labels need actual visual/row-column checking; nearest coordinates alone can select a neighbor.

Select source versions from explicit adoption or a traceable revision chain. Newest date, best-looking spectrum or highest purity is not a scientific selection rule. Same compound and same batch are different claims. A spectrum from another confirmed batch may support compound characterization while not proving purity or identity of the specific weighed/biologically tested batch. Preserve that limitation.

## Modality-specific review

| Modality | Check |
|---|---|
| NMR | Actual nucleus/page or experiment, appropriate reference, sample mapping, processing state and measured signal evidence. Keep raw FID and processed containers distinct. Do not fill missing peaks from expected structure. |
| IR | Actual source identity, reported measurement mode where available, wavenumber/units and observed bands. Do not invent intensities or force a fixed band count. |
| HRMS | Neutral molecule versus ion formula, adduct/loss, charge, monomer/dimer, calculated versus measured m/z, reported precision and instrument/source record. Recalculated theoretical values are never measured values. |
| HPLC | Same method/channel, peak row, retention time and area fraction; integration and sample mapping. Area percent alone is not mass purity or universal purity across wavelengths/methods. |
| Experiment record | Correct physical page, original page number, stage, materials and batch. Preserve full pages when necessary to avoid severing context. |

Transcription and scientific verification are separate statuses. If raw content is unreadable or conflicting, identify the exact file/page/line and continue the unaffected modalities. Do not silently omit a failed modality to make a complete-looking record.

Keep three evidence levels distinct in the existing table: literal transcription with page/region; a calculation with formula, inputs and units; and an interpretation with its evidence and confidence. An ion formula containing sodium and a positive charge can be consistent with a sodium adduct but is not a literal `[M+Na]+` label unless the report or an independently supported mapping establishes it. Formula/mass agreement does not establish connectivity or sample identity. Record theoretical and measured m/z separately; for a ppm check state `(measured - calculated) / calculated * 1e6` and which ion/charge the calculation uses.

Keep ambiguous dates as printed until locale or another record resolves day/month order. Different acquisition dates alone do not invalidate compound identity; a batch claim needs supporting records. Verify uncertain digits and signs using the original-resolution scan region, and retain unresolved alternatives rather than assigning a precise value from a thumbnail.

For scan transcription, associate each value or short group of values with a page/region and inspect that region at source resolution. A value counted as a separate band must have a visible source label or separately recorded peak measurement. For overlapping/unreadable digits, keep the alternatives or leave the final-value cell empty. Upscaling does not add source information. Keep instrument-reported error and a ppm calculation from displayed m/z in separate columns: rounded display values do not establish the instrument's precision or sign convention.

## Complete a scan transcription

1. Put clearly readable values in the evidence table first, with their source page/region.
2. Inspect an uncertain region at source resolution and, if useful, compare an available original or independent record. When the source still cannot resolve it, record alternatives or leave the value pending and continue. Repeated upscaling is not a way to recover missing detail.
3. Perform the requested calculations from confirmed inputs, keeping instrument values and recalculations separate, then deliver the table and its remaining unresolved items. A few unreadable digits do not prevent delivery of the confirmed material.

## Source integrity helper

Run `python3 -B /path/to/skill/scripts/check_sources.py sources.json --output new-report.json`.

```json
{"entries":[{"entry_id":"A-H1","sample_id":"sample-A","batch_id":"batch-1","modality":"1H NMR","source":"data/sample.mnova","sha256":"REPLACE_WITH_FILE_SHA256","locator":"native page 1","selection":"selected","status":"candidate","reason":"Selected acquisition; scientific review pending"}]}
```

Paths resolve relative to the manifest. `entry_id` is unique. `selection` is `selected` or `candidate`. `status` is `candidate`, `verified`, `missing`, `not_applicable`, `excluded` or `unusable`. Selected entries must be candidate or verified, with a file/hash/locator. All entries carry a reason. Absent-source statuses need no fake path/hash. A `verified` status is a supplied review declaration, not a conclusion of this script.

Multiple selected sources for the same sample/batch/modality require an explicit shared `selection_group` and individual reasons (e.g. complementary pages/replicates). The helper otherwise reports ambiguity. This authorization does not prove complementarity; inspect the content. Shared file hashes are flagged for review, not deleted. A scan may legitimately contain several samples, so locators still matter.

## Compile and deliver

Keep requested ordering explicit. A first appearance/cross-reference rule is a document choice, not a reason to discard independent acquisitions or batches. Preserve local page, original record page and final atlas page as separate fields; fill actual final pages only after rendering the exact final document. Shared characterization and separately acquired repeats must not be conflated.

Use requested editable formats and one clear master per purpose. In the report distinguish verified content, extracted-only values, limitations and missing material. Do not modify original instrument files to repair a transcription or presentation discrepancy.
