# Illustrator operations and acceptance

## Source copies

Run `python3 -B /path/to/skill/scripts/source_copies.py source1.ai source2.ai --output new-work` to create a new copy directory and manifest. Files receive numeric prefixes to avoid basename collisions. The helper compares hashes and filesystem identity; links/reparse inputs are rejected. It never overwrites existing output. With no `--output`, it prints inventory only.

Keep panel-to-source mapping explicit, including artboard/group and linked assets. If linked images need relocation, verify source hashes and package/embedding requirements. Do not relink to a similarly named different image.

## Native environment

Determine application version, available scripting/MCP/COM interface, fonts and profile support. Do not assume one OS or versioned COM class. A connection or executable being present is not proof of supported native operations. If the requested interface is unavailable, a disclosed alternative is valid only when it satisfies the user's actual goal. A specifically required interface remains unverified if not used.

Protect existing user documents and preferences. Open task copies; close only those documents. Do not call application Quit or terminate a process to clear state. The included inspection JSX returns JSON through `DoJavaScript` and writes to the scripting console, without an `alert`. Capture its returned text to a task log. It reports unavailable properties explicitly. A manually invoked host without return capture can use its scripting console or a task-owned output wrapper; do not add modal dialogs to unattended runs.

## Inspect, edit and save

Record artboards, layer/group mapping, text, paths, placed/raster objects, clipping masks, links, substitutions and color/profile information. Object counts are context, not equivalence evidence. Match panels by visible content, labels and source relationships, not filenames alone.

Prefer native duplication/transforms/grouping. Cross-document transfer must preserve editable text, clipping and appearance; verify these after transfer. Visible bounds may differ from raw image bounds because of white margins or clipping. Keep one understandable top-level group/layer per panel where useful without forcing unrelated figures into one composite.

Preserve scientific values, curves, image pixels/crops, chemical structures, group order, axes and statistical semantics unless a scientific change is in scope. Avoid flattening transparency or outlining text merely to suppress problems; when the destination requires such derivatives, preserve an editable main file and disclose the transformation.

Save is distinct from export. Keep document color mode/profile unless conversion is requested; record actual available profile information rather than infer it from appearance. Export requested AI/PDF/SVG/PNG from the current saved master. Do not promise the same fonts or raster color appearance on another machine without checking.

## Verification and delivery

### Prepared save/reopen/export tool

Run `python3 -B /path/to/skill/scripts/prepare_roundtrip.py input.ai --output new-job --strategy preserve --scale 100` for a faithful local roundtrip without relocation. Execute the generated `run.jsx` using the actual Illustrator scripting interface. The preparation manifest records preparation only; `report.json` contains actual native execution, inspection before/save/reopen, failures and remaining review. No software installation path or versioned COM identifier is fixed in the package. The tool does not change user preferences or suppress application warnings. A blocked native dialog is a bounded failed probe; preserve evidence without terminating a user session.

Choose the dependency policy according to the deliverable:

- `preserve`: retain existing links for a local roundtrip; external links do not become portable merely because they render locally.
- `package`: provide a verified `--assets assets.json`; the tool copies and relinks all placed assets inside the job, retaining linked images.
- `embed`: use the same verified asset map, relink first and save with `embedLinkedFiles=true`. Native conversion from placed to raster objects can be expected; it must not flatten editable text/vector panels.

Asset JSON is `{"assets":[{"placed_index":0,"source":"relative/or/absolute/image.png","sha256":"actual file SHA256"}]}`. Source paths resolve against that JSON. Map each zero-based index to the exact inspected placed item and actual content; do not use basename matching. Package/embed requires one verified supplied asset per placed item. Missing assets remain a specific dependency blocker; do not fetch them from an excluded source project. Opening an original linked AI can already cause native link reads, so `file.exists` checks or copied AI bytes do not prove isolation. For a strict no-source-access test, use an environment where excluded paths are unavailable; do not claim the script itself sandboxes native file access.

The tool explicitly requests `embedICCProfile=true`, preserves document color space and uses current native save compatibility rather than a fixed historical version. Reopen and inspect actual profile information; a requested option is not proof of successful color preservation. Both source-working and reopened PNG use identical settings; compare decoded pixels and objects, not just file existence. PNG scale is configurable, not a universal publication DPI. PDF is a derivative, not the editable master.

For migration, copy only the delivery package to another directory/environment, reopen the master without access to the old asset paths, and compare links, fonts, color and rendering. A package that still resolves only through its old absolute path is incomplete; relink to the delivered assets and verify again. An embedded result still needs a genuine native reopen test. `migration: NOT_VERIFIED` stays unresolved until that evidence exists.

For a linked package, copy the master and assets together. On the destination, inspect each placed item, map it to the supplied asset by source identity/hash, and relink to that asset under the new package root (for example, `item.relink(new File(newRoot+'/assets/'+mappedName))`); then save, close/reopen and export. Ship the relative asset map and this relinking step with the master. For an isolated local test, use only task-created assets: after relinking/saving, temporarily move the old task asset folders out of their original paths, reopen the destination and compare. Restore those folders afterwards. Do not rename another project's files to simulate isolation. For embed, reopen with the task's original bitmaps unavailable and confirm text/vector editability as well as absence of external links.

Close/reopen the saved task document. Compare linked assets, fonts, text, groups/masks and protected content; inspect final exports at whole-figure, detailed and intended-use size. Check artboard clipping, hidden/duplicate objects, leaders, labels, crop boundaries, color and missing links. Match derivatives to the reopened master.

Deliver requested editable master/derivatives, source mapping and concise verification evidence. Record unsupported properties, native errors and visual limitations separately. The source copy helper cannot supply native/visual acceptance; an active-document object report alone cannot supply it either.
