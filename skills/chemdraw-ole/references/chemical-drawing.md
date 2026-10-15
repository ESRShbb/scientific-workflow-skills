# Chemical integrity and layout

Use recorded structures/native fragments with verifiable labels before redrawing. Record structure identity and batch separately. Do not infer a route just because the final product admits a plausible synthesis. Unknown stereochemistry remains unknown; do not replace a known multiple bond with a wavy/crossing depiction.

For generic structures, map the actual attachment atom and expand representative members to check connectivity, chain length, amide orientation, protection state and stereochemistry. A repeat index counts the explicitly defined unit, not nearby carbonyl atoms. Generic labels cannot stand in for chemically valid full structures when calculating a formula.

List actual reaction nodes, conditions and convergence before arranging them. Preserve recorded deprotection, in situ steps, crude/direct-use states and isolated intermediates. Do not invent a branch for visual symmetry or label an input as commercial merely because its preparation is missing. Shared structure identity does not make all batches equivalent.

Reuse native geometry where appropriate. Fit the layout by repositioning groups and allocating space, not stretching bonds or distorting rings to accommodate text. A translated group should retain internal coordinates, connections and stereochemistry. Check label-to-fragment mapping using row/column layout and the visible drawing; nearest point alone can select a neighboring compound.

Choose label conventions, terminal methyl visibility, bond length, condition placement and arrow style from the requested target or reference. Without a specified style, use 10 pt atom labels/captions and 0.04 cm ordinary line width (1.133858 pt in CDXML/COM). Wedge/bold widths are separate settings; retain a coherent native style rather than making every width identical. A single reaction can have conditions by the arrow; a dense multistep scheme can use a keyed legend.

For newly drawn or reformatted structures, run ChemDraw's native Clean Up Structure on the intended structure/selection, then inspect bond lengths, angles, label spacing and stereochemical marks. Reposition fragments to make room instead of lengthening a single bond. Use local cleanup when the overall orientation is intentional.

On Windows, `scripts/native_style_cleanup.py input.cdx --output new-job --progid <registered identifier> --cleanup` applies the defaults to a new copy, calls native `Objects.Clean(False)`, saves/reopens a CDX and exports CDXML/PNG with before/after geometry. Omit `--cleanup` for style changes only; `--font-pt` and `--line-cm` override defaults. It requires pywin32 and this actual COM interface; on other installations use the native menu. Inspect the exported chemistry and layout; model differences are reported, not silently accepted. This route is not used for faithful unchanged exports.

Inspect the whole route, actual placed size and close details. Chemical correctness and visual readability are separate checks. Confirm charges, small atom labels, multiple bonds, arrow endpoints, captions, brackets and uncropped conditions. Canonical SMILES/InChI may aid identity checks if appropriate tools are available, but cannot resolve ambiguous source evidence by themselves.

The CDXML helper preserves node IDs and attributes in its comparison; regenerated IDs or changed text segmentation can produce differences even for equivalent chemistry. Review differences explicitly; do not weaken comparison to force a pass. XML integrity checks do not expand aliases or prove valence, stereochemistry, molecular formula or chemical equivalence.
