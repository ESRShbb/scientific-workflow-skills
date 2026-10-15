# Validation and capability boundaries

Locally executable: numeric PZFX extraction and explicitly reviewed-fit aggregation. No automated native fit is claimed.

Run `python3 -B -m unittest discover -s /path/to/skill/scripts/tests -v` from another project directory. Windows may use `py -3.12 -B`. Tests use synthetic file/metadata fixtures, not native scientific acquisitions.

## Cases

1. Five Y subcolumns, blanks, excluded cells and identical tables: preserve all and expose issues.
2. Mixed units, repeated independent experiment IDs, nonfinite/censored included values: reject summary.
3. Real target Prism version: fit a known dataset with the specified template/model; save/reopen and compare labelled native exports. This native case is deferred.

No test on a single host proves another computer, OS, software version or license is compatible. Record the actual environment and separate static, native, visual and scientific conclusions. Local helper success must not be reported as full workflow validation.

## Revision 0.2.0 focused checks

Inventory counts must match actual extracted Y data cells. Native result export must include parameter labels and confirmed sheet identity; reject numeric-only exports. An existing normalization sheet does not establish fit input provenance.

Treat scripts added in 0.2.0 as target-installation probes; consult their actual task logs. Package tests do not certify arbitrary native inputs or other computers.
