# Native operations and Office verification

## Environment and source protection

Identify ChemDraw version, executable/interface and license actually present. Windows COM ProgIDs such as `ChemDraw.Application.22.0` and `ChemDraw.Document.6.0` are examples from one implementation; verify registration and behavior before use. Other platforms may require native scripting/manual steps. Do not claim interface support from installed software alone.

Use a copy, preserve original hashes and identify task-opened documents. Never quit the application or close existing user documents for cleanup. If an isolated session cannot be guaranteed, use read-only inspection and defer only the affected native action. Record and restore temporary export preferences without changing unrelated global settings.

## Native drawing delivery

For a Windows COM roundtrip, `scripts/native_roundtrip.py input.cdx --output new-run --progid <registered identifier>` copies the input, opens only that copy, saves/reopens a new CDX and exports CDXML/PNG. It requires optional `pywin32`; discover the registered ProgID on the target computer. Export formats are selected by extension from the actual native type collection, not hard-coded collection positions. It never quits the application or changes preferences. Native exceptions and unavailable model properties are recorded in `report.json`; review actual outputs before accepting them. Non-Windows/unsupported COM uses an available native route instead.

Exact atom/bond snapshots can support a conservative comparison but ID reordering may make them differ without a chemical change. Counts, formula and Weisfeiler-Lehman graph hashes are not strict chemical equivalence or stereochemistry proofs. If needed, use a supported chemistry toolkit on native-exported structures and explicitly compare charge, isotope, connectivity and stereochemistry. Do not turn unavailable fields into confirmed equality.

Save a native CDX master, close/reopen that document, then export requested CDXML and previews from the reopened master. If a different layout is needed for Word/PPT, derive it from the current master and record that relationship. User-edited masters take precedence over stale generated CDXML; do not regenerate over them.

Keep source/target hashes and actual object or chemistry comparisons. `inspect_cdxml.py input.cdxml --compare baseline.cdxml` reports structural XML issues and semantic-snapshot changes. Hash identity is an implementation-level check, not proof of scientific correctness. Rendering DPI must reflect actual pixel dimensions and intended size; changing the DPI tag alone adds no detail.

## Word and PowerPoint OLE

Identify the Office object by document, part/relationship or slide/anchor, ProgID and display geometry. Activate one object at a time, obtain its model through that object's `OLEFormat.Object` when supported, and close/deactivate it before proceeding. If deactivation cannot be confirmed, stop that sequence or reopen the task document for the next object. Do not infer correspondence by the order of ChemDraw's document collection when several documents are open. A supported fallback must carry explicit object-to-document evidence.

Even activation without an intended chemical edit can cause Office to rewrite a payload or change displayed dimensions on save. Record before/after payload hashes, relationships, width/height and anchor/crop; close/reopen and render the saved document. Chemical-model equality does not prove layout preservation. Do not restore an old payload blindly to suppress a difference.

For an Office task, keep one row per required object: page/slide and anchor, native object read, editable after reopening, chemical changes, and displayed width/height. Activate the mapped object, read it through its own OLEFormat.Object, then deactivate it. If the host does not confirm deactivation, close/reopen only the task's Office copy before the next object. After the final save, reread the required objects and inspect the rendered page. Objects not reached remain incomplete; a successful first object does not stand for all objects.

For Word, native `InlineShapes.AddOLEObject` can embed the selected CDX with `LinkToFile=false` and `DisplayAsIcon=false` when supported. Record anchor/paragraph, displayed geometry, ProgID and source hash. One complete visual unit per object often aids editing, but object granularity is a delivery choice.

For PowerPoint, native `Shapes.AddOLEObject` support for CDX varies. A previously demonstrated alternative is to create a temporary ChemDraw OLE in a task-owned Word document and paste through Office clipboard using `ppPasteOLEObject`, or copy an existing verified PPT OLE. Probe the actual version. Do not treat clipboard success as proof of payload correctness. Preserve user sessions/clipboard-related workflow constraints; close only task-created documents.

Save a new Office file, close/reopen the task's file, inspect embedding relationships and activate representative required OLE objects in ChemDraw to verify editability and correct chemistry. Render pages/slides at use size. Object count, a ProgID string and CDX signature `VjCD0100` are only supporting evidence. Generic Office roundtrip libraries can strip native objects: compare embeddings/relationships before and after any such use.

`inspect_office_ole.py document.docx` emits an inventory without saving. It resolves internal OLE relationships instead of assuming names like `oleObject1.bin`; external OLE links are reported separately. It does not assert native validity from a binary signature. An unreadable/unsupported file must remain unresolved.

Use `inspect_office_ole.py after.docx --compare before.docx` to report available changes. Word can regenerate relationship IDs, shape IDs and embedding filenames; the same ID does not ensure the same object. By default only unique unchanged payload hashes are bound, with unmatched objects reported explicitly. For changed payloads supply `--mapping map.json` after native object/anchor verification: `{"objects":[{"before":["word/document.xml","rId1"],"after":["word/document.xml","rId2"],"evidence":"Native object and anchor locator"}]}`. IDs in this example are placeholders. Static geometry coverage can be incomplete, so also read native Office width/height and anchor and inspect the rendered page. `same_relationship_snapshot` is not a chemical or visual pass.

Replacement operates on the specified file/object within the user's authorized scope, after a working-copy result and rollback are available. No automatic replacement or installation is performed by these helpers.


## Executable Word object roundtrip

On Windows with `pywin32`, run `python3 -B scripts/office_roundtrip.py <source.docx> --output <new folder> --export-pdf`. It makes one `master.docx`, discovers all ChemDraw inline and floating objects by their native ProgID, then activates each before reading `OLEFormat.Object`. Each object is read, saved, closed and read again after reopening the task container. `report.json` records object locators, available atom/bond properties and native display dimensions; unavailable properties do not establish chemical equivalence. Review the static embedding inventory before/after and the reopened PDF as well.

Closing the task container is the deactivation route between objects. Each read/save or reopen/read phase uses a fresh Word instance created with `DispatchEx`, then normally quits only that instance. It does not quit ChemDraw or a pre-existing user Word session. This helper is for Word; PowerPoint still follows the native procedure above. A model difference or geometry change is an audit finding to resolve, not permission to repair chemistry or resize automatically.
