# Validation scope

Version 0.2.3 is an experimental extraction of practical scientific workflows. This page summarizes local observations as of 2026-10-15; it is not a guarantee of other software versions, machines or agent models.

## Portable checks

The repository includes 52 synthetic script tests: NMR 22, Prism 12, characterization 5, ChemDraw/OLE 7 and Illustrator 6. These cover the particular inventory, parsing, integrity, summary or job-preparation functions exercised by the fixtures. The figure-format skill is a method and has no script test suite.

Run `python -B scripts/validate.py` to repeat the package and script checks. CI does not install or run proprietary applications. Passing these tests does not certify spectra, chemical identities, statistical models or final figures.

## Local native and agent observations

Two agent models, Grok and DeepSeek through Pi, exercised representative tasks in a separate project on one Windows computer. Private experimental materials and their output artifacts are intentionally excluded from this repository; the following is a maintainer-reported summary rather than a publicly reproducible native benchmark.

| Skill | Observed locally | Remaining boundary |
| --- | --- | --- |
| NMR | Unchanged export of two selected, manually processed MNOVA pages in MestReNova 16; source hashes preserved and both agents produced identical PNG bytes. | Raw FID processing, integration and assignments were not scientifically validated by this export test. No macOS/Linux launcher is included. `Page.toPixmap(300)` is not a promise of 300 stored DPI. |
| Prism | Supported PZFX XY extraction, reviewed-value arithmetic/geometric summaries and existing-result reading in Prism 8 and 11. | A normalization result page was read differently between versions. Full model provenance, weighting and constraints have not all been verified in the UI. Cross-version unattended new fitting remains unvalidated. |
| Characterization | Source/locator/hash checks and representative IR/HRMS transcription review. | Models can misread handwritten identifiers and numbers. Check the original image. No OCR engine or automatic chemical-identity resolver is bundled. |
| ChemDraw/OLE | Native drawing save/reopen and a five-object Word embedding test, including geometry checks. | PowerPoint OLE has not been tested. Some COM stereochemical readings were unstable; static comparisons alone cannot establish stereochemical equivalence. Defaults are configurable: 10 pt text and 0.04 cm ordinary bond width. |
| Figure format | Agent review of deliberately introduced label and typography problems. | This depends on model judgment and actual rendered inspection, not a deterministic validator. |
| Illustrator | Illustrator 2021 save/reopen, PNG/PDF export and package/embed checks after moving the working package. | Font substitution has not been fully exercised. Discover the installed COM ProgID; an unversioned identifier was unavailable locally. |

## Testing on another installation

Choose one representative input for the operation you actually need. Record the installed application/interface, preserve the source, run on a working copy and inspect the saved/reopened native result plus its export. Record technical operation, visual quality and scientific review separately. Expand only after the representative task works.

Cross-machine testing is pending. Do not describe these skills as fully automatic NMR processing, universally portable native drivers or validated unattended curve-fitting software.
