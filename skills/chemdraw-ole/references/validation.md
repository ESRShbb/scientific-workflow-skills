# Validation and capability boundaries

Locally executable: conservative CDXML snapshot/integrity and OOXML OLE relationship/geometry comparison. Optional Windows COM roundtrip needs a native target-installation check; static helpers do not certify CDX/Office readability or chemistry.

Run `python3 -B -m unittest discover -s /path/to/skill/scripts/tests -v` from another project directory. Windows may use `py -3.12 -B`. Tests use synthetic file/metadata fixtures, not native scientific acquisitions.

## Cases

1. Translate coordinates: snapshot stable; change isotope/charge/bond order: snapshot changes.
2. Missing bond endpoint, duplicate object ID or missing OLE payload: report failure; custom embedding names still resolved.
3. Target ChemDraw and Office: real structure with stereo/charge and Word/PPT OLE; native save/reopen, activate one mapped embedded object at a time and render. Validate each native application operation actually requested; CDX roundtrip alone does not certify Office OLE editing.

No test on a single host proves another computer, OS, software version or license is compatible. Record the actual environment and separate static, native, visual and scientific conclusions. Local helper success must not be reported as full workflow validation.

## Revision 0.2.0 focused checks

Office payload/geometry changes must be reported even when native atom/bond models agree. Activate/read/close one mapped object at a time. Native COM helper must use explicit registered ProgID and extension-selected exports.

Treat scripts added in 0.2.0 as target-installation probes; consult their actual task logs. Package tests do not certify arbitrary native inputs or other computers.
