---
name: chemdraw-ole
description: Create or revise native ChemDraw structures and reaction schemes, and audit or deliver editable ChemDraw OLE in Word or PowerPoint. Use for CDX/CDXML, reaction drawings and Office chemical-object workflows; preserve chemical identity independently of layout.
---

# ChemDraw and Office OLE

Select structure, reaction/scheme, Office audit or Office embedding mode. Read [native workflow](references/native-workflow.md); drawing operations also use [chemical drawing](references/chemical-drawing.md).

Establish structure/source/label mapping, allowed chemical changes and target layout. Keep salts, charge, isotopes, stereochemistry, protecting groups, connectivity and substituent attachment positions. Do not substitute a chemically plausible inferred structure for a recorded one. Existing authorization remains valid; ask only about unresolved identity or scope decisions.

Preserve source files. Use new working copies and native software for native CDX/OLE delivery. A raster rendering or a CDXML string is not proof of an editable ChemDraw/Office result. Record actual installed version/interface and output requirements rather than assuming a versioned COM identifier exists everywhere.

Helpers (Python 3.10+ standard library):

- `scripts/inspect_cdxml.py`: XML-object integrity and a full-attribute semantic snapshot excluding listed layout attributes. It checks page/node/bond references and can compare snapshots. It is not a chemistry toolkit or stereochemical equivalence proof.
- `scripts/inspect_office_ole.py`: read-only OOXML embedded-object inventory with relationship/ProgID evidence. It does not activate native objects or certify editability.
- `scripts/native_roundtrip.py`: optional Windows COM CDX copy/save/reopen/CDXML/PNG probe, requiring `pywin32` and a target-verified ProgID. This is distinct from the standard-library static helpers.

For new drawings or requested formatting, default to 10 pt lettering and 0.04 cm ordinary bond line width. User-supplied styles or publication templates override these defaults. Apply them to existing objects as well as document defaults. Use native structure cleanup for uneven geometry, then inspect the result. Unchanged-export/audit mode preserves the supplied drawing. See the drawing reference for the executable style/cleanup route.

Version 0.2.3 is a portable candidate. Native drawing, save/reopen and Office embedding are documented operations, not bundled unattended cross-platform drivers. See [validation](references/validation.md) for portable and deferred native tests.


Optional Windows/pywin32 helper `scripts/office_roundtrip.py` audits all ChemDraw inline/floating objects in a Word copy with activate/save/reopen and geometry evidence; see the native workflow.
