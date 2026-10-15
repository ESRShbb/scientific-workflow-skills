# Source inventory

Record selected input, sample/batch identity, nucleus, acquisition or processing provenance, and intended operation. Never use `NUC2=1H` to invent a proton experiment: it may be a decoupling channel. The helper selects the measured `NUC1`. Duplicate experiment numbers in different nested acquisitions are ambiguous and stop selection.

For a source directory, obtain its tree hash with `directory_manifest(Path(...))` from `scripts/raw_source_adapter.py`. File hashes use SHA-256. The directory hash covers ordered relative file paths, sizes and SHA-256, not timestamps or empty directories. It is a reproducibility check, not an instrument identity check.

Minimal request (replace placeholders with measured values):

```json
{
  "compound_id": "sample-A",
  "spectrum_sources": {
    "1H": {
      "source_kind": "bruker_folder",
      "path": "inputs/acquisition",
      "sha256": "REPLACE_WITH_DIRECTORY_TREE_SHA256",
      "nucleus": "1H",
      "experiment_id": "10",
      "pdata_procno": "1",
      "processing_profile": "process_from_raw"
    }
  }
}
```

Run from any project directory with the installed skill script's location:

```text
python3 -B /path/to/skill/scripts/raw_source_adapter.py request.json --output run/inventory.json --materialize-root run/raw-copy
```

Relative source paths resolve against the request JSON, not the shell directory. Output arguments resolve against the shell directory. Omit `--materialize-root` for read-only inventory. The report and copy destination must be new, and must not overlap sources. All source entries are checked before copying, including separate entries sharing the same ZIP. Failed operations can leave partial output; inspect it and use a fresh run directory rather than merging it into a successful result.

Source kinds:

- `bruker_folder`: tree hash required; explicit experiment ID; `process_from_raw` denotes intended later processing, not completed processing.
- `bruker_zip`: whole ZIP hash required; explicit experiment ID. Reject traversal, case-colliding members, links and filenames incompatible with Windows. Check available disk space before extracting large packages. This is a scientific data utility, not an untrusted archive sandbox.
- `mnova_container`: file hash and zero-based nonnegative `page_index` required. Page existence and nucleus require native readback later.
- `bruker_1r`: file named `1r` and hash. Keep `procs`, acquisition metadata and related files for interpretation; a standalone `1r` is insufficient evidence for a valid ppm axis.
- `independent_raw`: opaque file registration only; no parser or processing is claimed.

The convenience request holds one selected source per nucleus for a sample. Multiple acquisitions of the same nucleus use separate requests with sample/batch/acquisition identifiers; never silently discard them. The helper reports inventory only, not a chemical identity decision. For unknown or unsupported metadata, keep the original data and report the specific limitation.
