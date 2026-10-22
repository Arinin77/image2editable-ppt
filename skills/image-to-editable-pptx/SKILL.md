---
name: image-to-editable-pptx
description: Rebuild images, screenshots, diagrams, paper figures, and AI-generated layouts as element-level editable PowerPoint (.pptx), preserving content and visual relationships. Use for image-to-PPT conversion, 图片可编辑化, and 论文插图转PPT.
---

# Image2EditablePPT

Reconstruct the supplied visual as a PowerPoint that can be edited meaningfully. The final artifact is `.pptx`; rendering images are working material for verification, not additional required deliverables.

Start from the user's image, not from an assumed subject area, template, palette, or presentation style. Preserve its content, logical relationships, visual hierarchy, and aspect ratio unless the user requests changes. A request to convert an image does not by itself request rewriting, translation, redesign, or extra slides.

Use supplied style references and established preferences. When a meaningful choice remains unclear (for example, faithful icon reuse versus a different visual family), ask one focused question or show a small set of representative alternatives before doing the dependent work. Continue independent work while waiting. Do not require a style questionnaire for a clear image or separate approval for every icon; carry an accepted choice through the set.

## Define what will be editable

| Source element | Preferred PowerPoint representation |
| --- | --- |
| Text, numbers, labels | Native text with editable content and formatting |
| Background regions, boxes, dividers, simple symbols | Native shapes |
| Arrows, branches, feedback loops | Native connectors or editable paths with correct endpoints |
| Icons, illustrations, logos, photographs | Independent, replaceable picture objects; native vectors when supported and appropriate |
| Charts and tables | Native charts/tables when the underlying values are available or unambiguously readable |
| Complex scientific imagery or textures | Independent image assets with editable surrounding annotations |

A picture that can be moved or replaced is not internally shape-editable. An embedded SVG is not necessarily a set of native shapes. State these distinctions accurately. Do not simulate editability by placing a full-page image behind invisible text, or by slicing an entire diagram into picture tiles containing otherwise separable text and connectors.

## Inspect and choose the reconstruction approach

View the source at adequate resolution, including transparency and fine details. Identify the actual figure boundaries; document-page margins and surrounding captions are not automatically part of a figure. Use a vector/PDF source or original asset if the user supplies one and it improves fidelity.

Extract and verify visible text, numbers, units, legends, equations, and labels. OCR is a starting point, not evidence that recognition is correct. Do not silently repair spelling, infer unreadable values, or change technical claims. Ask a focused question when uncertainty would change the meaning or required editability; continue independent work where possible.

Build a lightweight element map: semantic name, type, content, bounds, layer, and representation. For process diagrams, also record each connection's source, destination, direction, and branch label. Scale the detail to the image; simple inputs do not need elaborate planning documents.

Keep verified source text and connections as the reference for construction and review. A proposed correction must be checked against the source or the user's instruction, rather than silently rewriting that reference to match the output. For dense diagrams or scripted builds, use the compact examples in [references/reconstruction-notes.md](references/reconstruction-notes.md); otherwise a short working list is sufficient.

Default to one input visual per slide with its original proportions. For multiple inputs, follow the user's ordering and grouping. Preserve intentional overlaps, background colors, and line styles instead of enforcing a universal aesthetic. Resolve fonts from available evidence; use and disclose a close substitute when exact identification or availability is uncertain.

## Obtain suitable visual assets

Read [references/visual-assets.md](references/visual-assets.md) when selecting or replacing icons and illustrations.

Prefer suitable supplied originals or already verified local assets. When new external replacements are needed, search real asset websites and inspect actual asset pages and downloaded files. Match the concept first, then the reference's visual language and the rest of the set. Search and review related icons together; retain their files and provenance so later revisions only need searches for missing roles. Website choice and icon style are task-dependent; no provider, palette, or illustration style is mandatory.

Retain complex technical imagery where a generic icon would change its meaning. A complete crop of a self-contained image or icon can be appropriate; cropping should not absorb surrounding text, arrows, or whole modules that should be reconstructed. If no suitable asset is available, report the gap and use an authorized fallback rather than silently inventing one.

## Build native structure

Use the available PPTX authoring interface or library that can produce the required native objects. Discover installed runtimes and read the relevant tool documentation instead of assuming a machine-specific path, operating system, or fixed vendor. Follow the active environment's authoring requirements; this skill does not require one named library or another skill.

Reuse a working construction/export path when it satisfies this input. In an unfamiliar environment, verify only the capabilities the figure needs (such as native text, an independent image, an arrow, and export/render) before building the full figure. Do not repeatedly reload complete manuals, regenerate unchanged assets, or rebuild unrelated slides for a local repair.

Establish the canvas and major regions, then place native structures, independent assets, text, and connections. Use stable semantic object names. Group related objects when it makes subsequent editing easier, keeping the children editable. Source images remain references or isolated assets, not flattened substitutes for the structure.

Group at a useful editing unit, such as one labeled module or a small icon-and-caption set. Preserve layer order and avoid a single group that makes the whole slide hard to edit. Before repeating a grouping or attachment technique across a dense figure, try it on one representative module and check its export.

- Match alignment, spacing, typography, line weight, and hierarchy at the intended viewing size. Measure text with the actual rendering font. Avoid shrinking text merely to hide a poorly sized text box.
- Route connections according to their meaning. Attach arrow tips at the correct boundary or explicit endpoint, keep branches unambiguous, and avoid passing through unrelated labels and symbols. Preserve source line-style semantics; do not turn all arrows into one style by default.
- Use connectors with attachment support when available and useful. Editable freeform paths are valid alternatives, but do not claim they remain attached when modules move unless verified.
- Reconstruct charts from known data. If only an ambiguous raster chart is available, request data or clearly retain that region as a non-data-editable image. When the user explicitly requires data editability, an image fallback is a partial result, not completion of that requirement. Do not fabricate values from a visually estimated chart without explicit authorization and disclosure.
- Preserve equations and special characters. Use native equation support when reliable; disclose any equation retained as an image.

## Render and verify

Read [references/verification.md](references/verification.md) for the concrete checks and optional package inspection helper.

Render the exported PPTX using an available presentation renderer and inspect the resulting slide, not merely the authoring canvas. Prefer the intended target application when available. Verify source content, process connections, layout, and native object structure separately; success in one category does not prove the others.

Fix observed defects, re-render affected slides, and inspect the final whole-slide export. Review may be done in the current task; an independent reviewer is optional when complexity warrants it, not mandatory for every image. When exact reproduction conflicts with readable reconstruction, make the smallest justified adjustment and explain a material deviation. If rendering or an essential source check cannot be completed, identify the unverified part instead of claiming full acceptance.

For a complex diagram, spot-check a meaningful edit in a disposable copy or without saving: change a label, move a grouped module, and move or replace an independent image. If attached arrows are claimed, verify that their endpoints follow the moved module. Record the observed result briefly; a package inventory alone cannot establish this behavior.

## Deliver

Save to the user-specified location or an authorized task directory. Keep the input intact and create a distinct output unless replacement is authorized. Keep temporary assets and previews separate from the final PPTX, using portable relative paths in reusable build materials.

Deliver the PowerPoint with a brief account of what is native, what remains as independent images, and any material uncertainty. Keep asset provenance and required credits accessible, for example in speaker notes when the license permits. Retain enough construction material to support requested refinements; do not require extra export formats, upload services, or synchronization steps.
