---
name: illustrator-scientific-figure
description: Assemble, revise and verify editable scientific figures in Adobe Illustrator, preserving source mapping, native objects, linked images, fonts and color settings. Use for AI panel extraction, composition and delivery; statistical recalculation and chemical identity decisions are separate tasks.
---

# Illustrator scientific figures

Read [native workflow](references/native-workflow.md). Establish scientific inputs, panel mapping, allowed edits, destination dimensions and requested deliverables before operating the application. For visual guidance, the companion scientific-figure-format skill is optional; this package remains usable without it.

Use true working copies with unchanged source hashes. `scripts/source_copies.py` inventories or creates verified independent copies using Python 3.10+ standard library; it does not open or validate AI internals.

Preserve native paths, editable text, groups and masks where present; preserve scientific raster content as raster. Do not substitute screenshots or Image Trace for editable scientific objects. Record actual interface use: native scripting, COM, MCP and manual operations are different routes.

Save the editable master to a new path, close and reopen that task document, then export requested previews. Structural inspection and actual viewing are both necessary. A saved file, object count or AI header does not prove complete rendering or editability.

Included `scripts/inspect_current_document.jsx` reads an already-open active Illustrator document and returns JSON without a modal dialog. It reports text/fonts, artboards, links, bounds, counts and available color information. It does not launch, save, close or edit documents. Run it only when the intended working document is active. `scripts/prepare_roundtrip.py` prepares a copy and parameterized native JSX for save/reopen/export, with explicit preserve/package/embed strategy. See [native workflow](references/native-workflow.md) and [validation](references/validation.md).

Version 0.2.3 is a portable candidate. The bundled JSX supports a bounded save/reopen/export probe, not unattended arbitrary figure editing. Native and cross-version support must be checked on the target installation.
