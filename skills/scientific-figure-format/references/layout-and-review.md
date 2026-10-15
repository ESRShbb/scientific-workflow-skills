# Layout and review

## Establish the figure contract

Record panel/source mapping, independent/composite scope, intended use size, scientific values/images frozen for this edit, allowed annotation changes and requested output. Titles and panel lettering serve actual reading needs. Do not add them mechanically; remove a title only when that does not erase essential context.

Typography must remain legible at final size, including subscripts, Greek letters, gene/protein notation and statistical symbols. Verify species-appropriate gene conventions and distinguish protein names from genes. A named protein example from one project is not a universal labelling rule. Font family, boldness and sizes belong to destination requirements and content density; do not impose one historical font/minimum on every figure.

For SVG with a viewBox width V rendered at W cm, a font size f in matching user units corresponds to `f * (W / 2.54 * 72) / V` pt. Account for object transforms separately. Nominal font size and visible glyph height are different measurements. Inspect quantitative axes for readable scales/ticks or explicit numeric labels; a missing scale must be addressed before values can be read from the plot.

## Arrange with meaningful anchors

For a quantitative figure, bind each source category to its numeric value, graphical element and displayed label before suggesting an edit. Reuse the source mapping; a small comparison table is sufficient. If the user has named the authoritative data source, apply it without asking the user to choose again. Preserve uncertainty only where sources actually conflict.

Choose the smallest correction that makes the mapping agree. When bar heights already match source values and labels are misplaced, correct the labels; changing heights and labels together requires a demonstrated reason. Recheck the entire proposed mapping so two individually plausible edits do not introduce a new mismatch. One summary row per group does not establish experimental `n=1`; use design/raw-data evidence for sample size, error bars and significance.

Use shared row baselines and lane/category centers. Text alignment should consider baselines rather than only font bounding-box tops. Brackets span exactly the conditions they describe; headers center over those conditions, not the whole artboard by default. Keep values close enough to associate with the right lane/curve without merging distinct experiments.

Repeated geometry can be measured with a tolerance appropriate to the final scale. Exact coordinate reuse is useful; a universal 0.25 pt or 1 pixel threshold is not proof of readable correspondence. Optical corrections may be necessary and should not change scientific grouping.

Preserve aspect ratios, scientific crop bounds and color semantics. Align scientific images through translation and justified uniform scaling; never stretch to force equal strip widths. Preserve required scale bars. Whitespace should show grouping, not unexplained leftovers from a source artboard. Check accessibility/contrast and line weights in the actual export color space.

## Verify the actual artifact

Compare with inputs using consistent rendering settings, and separate changed regions from protected regions. Explain antialiasing differences without dismissing real scientific pixel changes. Native object/coordinate checks complement image comparisons; neither alone proves integrity.

View the whole figure, normal-size panels, dense details and final destination size. For a slide, evaluate presentation-size legibility; for a publication, check actual placed dimensions. Check every label's referent, clipped error bars/ticks, scientific crop boundaries, blank regions, reading order and panel priority.

Report findings with artifact/version and panel/position, observed issue, evidence, effect on meaning and minimal correction. Mark scientific-content acceptance and visual acceptance separately. If input data or true final-size rendering was unavailable, record that boundary instead of asserting a full pass. Once relevant checks pass, do not require ritual repeated review without new changes or unresolved issues.

Classify findings as required correction (wrong meaning, clipping or unreadability at use size), optional style improvement, or evidence insufficient. Apply publication-specific typography, resolution, color and axis-title requirements only when that destination actually requests them. Preserve synthetic/test labels when they identify the material's purpose. Do not turn every stylistic preference into a scientific blocker.
