# Validation and capability boundaries

Locally executable: source inventory/independent working copies and job preparation. Native inspection and roundtrip JSX require target-installation checks.

Run `python3 -B -m unittest discover -s /path/to/skill/scripts/tests -v` from another project directory. Windows may use `py -3.12 -B`. Tests use synthetic file/metadata fixtures, not native scientific acquisitions.

## Cases

1. Two inputs share a basename: separate copies and correct hash mapping; edits to a copy cannot affect the source.
2. Output already exists or source is missing: fail without overwriting; inventory alone writes no source files.
3. Target Illustrator: open a task copy with text/clipping/placed image, inspect without a modal dialog, save/reopen/export and verify content. Test scoped edits separately when needed; a save-only probe does not certify editing.

No test on a single host proves another computer, OS, software version or license is compatible. Record the actual environment and separate static, native, visual and scientific conclusions. Local helper success must not be reported as full workflow validation.

## Revision 0.2.0 focused checks

Nonmodal inspection must return JSON. Save/reopen with explicit ICC policy and dependency strategy; same-setting render comparison and relocated-package reopen are separate checks. No source-project fallback when assets are missing.

Treat scripts added in 0.2.0 as target-installation probes; consult their actual task logs. Package tests do not certify arbitrary native inputs or other computers.
