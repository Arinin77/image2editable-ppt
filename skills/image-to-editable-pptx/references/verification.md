# Verify the exported PowerPoint

Check four independent properties. A valid ZIP package or an attractive rendering is not by itself proof of an editable reconstruction.

## Content and relationships

Compare the source and exported slide for all visible text, numbers, units, symbols, legend mapping, panel order, and connector directions. Confirm that a return path points to the intended module and branch labels remain associated with the correct route. For charts, preserve axes, values, categories, and uncertainty markers when present.

## Visual rendering

Render with the intended presentation application when available; another compatible renderer is an alternative, with its limitations disclosed. Inspect every affected slide at normal viewing size and enlarged detail.

Look for text overflow, font substitution, unintentional wrapping, clipping, occlusion, line crossings, disconnected arrowheads, uneven icon size, and loss of contrast. Preserve intentional source overlaps. Quantitative bounding-box checks can flag likely defects, but false positives occur around containers and layered artwork.

Inspect bends and junctions for visible gaps, protruding caps, dark overlaps, and abrupt width changes. Check icons at their intended size and in enlarged detail for blur, pixelation, clipping, and inconsistent visual weight. Verify that vector assets remain vector in the exported file and that any raster fallback is a usable image at the intended size. Repair visible defects in the exported rendering before delivery.

An in-memory authoring preview may differ from the exported PPTX. Inspect the export. If no renderer is available, report the output as pending visual verification.

## Editability

Use the authoring application's object tree or inspect the PPTX package. Text should be native text; ordinary boxes and flow lines should be native objects. Check groups without assuming grouping flattens their children. Pictures should correspond to reasonable individual visual assets or disclosed complex-image regions.

When a package inventory or text comparison would help, use the read-only Python 3 helper from the skill directory. It is optional if the application's object tree already supplies sufficient evidence:

```bash
python scripts/inspect_pptx.py path/to/result.pptx --output path/to/work/inventory.json
```

The default stdout is a compact summary with aggregate counts and grouped review flags listing affected slides. `--output` retains per-slide counts and the full evidence on disk; read only the relevant object details when investigating a defect. Use `--full` when the full JSON is actually needed in stdout.

For verified source text in a scripted build, optionally pass `--expect-text path/to/expected-text.json`. Example:

```json
{"slides": [{"slide": 1, "texts": [{"name": "query", "text": "Query"}]}]}
```

Use 1-based slide numbers and unique semantic object names. Checks ignore whitespace only; numbers, units, punctuation and other characters must match. Missing objects, duplicate names and mismatches are reported. This is a check of the listed text, not proof that all source content was captured; extra objects are not rejected. Review the source when a check fails instead of changing the expected text to hide the mismatch.

The helper traverses slides in presentation order and text in shape-tree order, not visual reading order. It flags unresolved, missing or external current-slide image references, picture fills and unexpanded layout/master inheritance. It checks internal target existence, not image decoding. It does not assess licensing, semantic correctness, arrow direction, layout, text visibility or whether a raster icon has editable internal strokes. Object counts are evidence, not a pass score. A whole-page screenshot with one invisible textbox still fails meaningful editability.

Exit code `0` means the inventory was generated, including any review flags; `2` means input/output or package-reading failure. Inspect the summary rather than treating exit code `0` as visual acceptance.

The summary also counts connectors declaring two, one, or no attached endpoints. Full records include target IDs, target names and connection-site indices. Missing/ambiguous targets, malformed site indices and duplicate object IDs are review flags. An unattached connector is not automatically a defect, and custom paths are not included in these attachment counts. XML declarations do not prove correct routing, valid geometry sites, or that movement works in PowerPoint.

If a particular application is the target, spot-check that representative text, shapes, and an image can be selected and edited there. Do not claim automatic connector attachment unless it was built and tested.

For dense diagrams, use a compact record for the actual edit test:

| Edit | Observed result |
| --- | --- |
| Change a native label | Editable / failed / not checked |
| Move one logical module | Children move together / separate objects / not checked |
| Move or replace one icon | Independent object / failed / not checked |
| Move a module with an attached connector | Endpoint follows / fixed route / not checked |

Perform the test in a disposable copy or restore the edit without saving. Do not replace a successful rendering with the demonstration state. Report limitations that matter to the user's requested editing, without enforcing a universal minimum number of groups or bound arrows.

## Delivery integrity

Confirm that the final file is the inspected export, opens as a PPTX, and includes the expected number and ordering of slides. Keep inputs unchanged unless their modification was requested. Explain retained image regions, unavailable fonts, unverified points, or meaningful visual substitutions concisely. No fixed number of revision rounds is required; recheck the areas affected by each repair.
