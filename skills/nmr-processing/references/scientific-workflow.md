# Conditional scientific and display workflow

This reference guides qualified, evidence-based work. The bundle does not automate the scientific processing steps below. Use native software capabilities actually available in the target environment, and record what was done.

## Identity and source

Match sample, acquisition, batch and nucleus with the supplied records. Structures constrain interpretation but cannot generate observations. Check salt/free form, protection state, isotopes and connectivity when relevant. Preserve unknowns; do not modify a structure merely to fit a spectrum. Export or source inventory can proceed without an assignment-grade structure if clearly labelled; structure-dependent assignments cannot.

Processed MNOVA, raw FID and raster images are different evidence types. Link processed/raw versions through acquisition metadata and source records; matching names alone are insufficient. Record whether raw data and processing history are available.

## Raw processing

1. Make a verified working copy. Identify the actual experiment, measured nucleus, pulse sequence and acquisition metadata before choosing a method. The bundled inventory helper is scoped to selected 1D nuclei.
2. Record native software/version and current processing state. Choose digital-filter handling, apodization, zero filling, Fourier transformation, phase and baseline operations according to acquisition and purpose. Do not impose automatic phase/baseline actions on every experiment or reapply them to already processed data.
3. Inspect phase and baseline at meaningful regions, including broad/weak signals. Diagnostics complement visible evidence. Processing may legitimately change point counts or intensity; record expected changes rather than enforcing a universal invariant derived from one workflow.
4. Establish chemical-shift referencing from a justified internal, external or other appropriate reference. Record reference identity, nucleus, value, source/conditions and actual applied transformation. Solvent metadata or a software `Apply` flag alone is not proof. A zero shift may be valid. Residual-peak tables provide candidates, not automatic calibration or deletion rules. Do not apply proton/carbon solvent-reference conventions to 19F without appropriate evidence.
5. Save a new native result, close and reopen it. Read back processing/reference state, acquisition identity and exported trace. Inspect spectra after reopening, not only before saving. Compare against the expected effect of each operation, with justified tolerances.

If referencing is unverified, label exact shifts unverified. Do not silently correct the user's chosen processed result; propose or perform correction only within the requested scope and in a new working copy.

## Signals, integrals and interpretation

For numeric reporting, maintain a compact evidence table with sample/batch/nucleus, input hash/page or experiment, region/observed lines, measured integral and normalization basis, proposed role, assignment confidence, evidence and unresolved conflicts. A single table is enough; five separate JSON documents are not mandatory.

- Automatic peak picking can provide candidates; individual lines or multiplet classifications are not automatically distinct chemical environments.
- Preserve observed impurities, residuals and uncertainty. Do not remove peaks simply to match expected atom counts. Explain overlap and splitting using evidence, not a desired count.
- Integral boundaries and normalization must be justified from the actual spectrum. Distinguish measured integral from assigned proton count. Exchangeable or broad signals can be unreliable; no universal low-integral threshold justifies hiding them or forcing integers.
- Report J from measured separations with the correct observed-nucleus frequency and units, not from a prior acquisition or a literature expectation. Recognize unresolved/second-order cases rather than fabricating precise couplings.
- Preserve unresolved alternatives when 1D data cannot distinguish them. 2D, quantitative, kinetic or other specialized analysis requires suitable additional methods and evidence.
- Final text and annotations must agree with the reviewed observations. Literature/SI discrepancies remain traceable and cannot override this acquisition's data.

## Display-only changes

Before editing, record spectrum trace/processing/reference, peaks, integrals, multiplets, acquisition metadata, structures and page mapping to the extent the native interface permits. Specify allowed changes such as font, color, line width, labels or layout. Peak deletion, reintegration and referencing are separate scientific changes.

Keep the user's chosen zoom unless changing it is requested. Water labels, title visibility, structure placement, fonts, full-range limits and orientation are task preferences, not universal defaults. Preserve structure aspect ratio and prevent overlays from hiding peaks, integrals, axes or text. Embedded structure object types may differ.

Save to a new native file, close/reopen, compare protected fields and inspect exported pages. Counts alone cannot prove unchanged values: compare actual peak positions, integral values/normalization and trace where accessible. Unavailable readback leaves the corresponding check unverified, not passed.

## Delivery

Deliver only requested formats, with one clear editable main result when editing was requested. Separate native-file verification, visual verification and scientific conclusions. Record affected items and continuation steps for failures. Do not require a new approval for every mechanical step already authorized by the user; ask only about unresolved choices that materially affect identity, conclusions or scope.
