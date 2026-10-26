# Visual asset selection

Use this reference when a source contains icons or illustrations that need extraction, replacement, or reconstruction.

## Choose the right source

Choose by asset type, not by how easy it is to crop from the source:

1. **Explicit user choices:** prioritize icons the user supplies or selects for use, and honor instructions to preserve particular assets. An icon visible in the input image alone is not an explicit choice. Flag material quality or meaning problems with a chosen asset instead of silently replacing it.
2. **Conceptual and functional icons:** default to real asset websites, searching by meaning plus style, even if the source icon is clear and croppable. Prefer coherent collections where they fit the concepts. Reuse suitable, previously verified website assets with their source records; do not search again just because a new revision starts. Provider options include Iconfont, Flaticon, Icons8, Material Symbols, and specialist collections; these are examples, not a mandatory search order. Honor a user-specified source.
3. **Brand marks and logos:** prefer official high-quality assets or original files over screenshot crops. Preserve the correct identity and proportions; do not restyle a brand into a generic icon to match the set.
4. **Real or evidence-bearing imagery:** prefer clear originals for photographs, actual UI screenshots, experimental results, scientific images, and data plots. Faithful reconstruction is appropriate only when reliable data or unambiguous source information supports it. If a better source is unavailable, choose a complete crop, screenshot, or original preservation without per-asset approval; retain real content and disclose material quality limits. Do not guess hidden values, fabricate missing details, or substitute a generic illustration.

For conceptual icons, use a source crop only when necessary, when no suitable asset can be obtained (including unavailable web access), or when the user requests preservation. Keep the icon complete and legible, exclude surrounding text and connectors, and record the fallback. Prefer vector assets or sufficiently detailed raster originals; enlarging a screenshot does not restore missing detail. If the fallback cannot preserve meaning or meet required quality, state the unresolved gap and ask a focused question rather than inventing an asset.

Gather the required semantic roles first and search related roles together. Open the actual asset page and inspect the downloaded original: search thumbnails alone do not establish author, format, quality, or permitted use. Use available browser or web retrieval tools and permitted download routes. Keep verified files and source records in the task's working assets directory and reuse them for revisions.

Evaluate the set at its intended size. If style is materially ambiguous, ask about a representative pair or family or use the user's reference, then apply that choice consistently. A small comparison sheet can help; do not turn every icon into a separate approval step. A download or an attractive search thumbnail alone is not a completed asset check.

## Selection criteria

- **Meaning:** represent the specific object, action, or state. Reuse a symbol consistently when it denotes the same concept; different concepts may need distinct visuals.
- **Style:** match outline/fill treatment, stroke weight, corner shape, perspective, shading, detail density, and palette. Prefer coherent collections where suitable without sacrificing meaning to enforce one author.
- **Legibility:** fine details that disappear at slide size do not help. Compare visible content, not only the image's rectangular dimensions.
- **Identity:** do not replace a technical evidence image with a generic illustration or present a representative icon as the actual observation.

Replace a conceptual icon only when its meaning is preserved. For evidence-bearing or identity-bearing imagery, a better original, faithful reconstruction, or crop must retain the source's actual information and identity. Preserve readable source text, numbers, and labels within an asset, reconstructing them separately as native text when appropriate rather than dropping or rewriting them during replacement.

## Prepare assets without losing their identity

Use suitable original resolution and transparency. Preserve aspect ratio. Transparent padding can be controlled through native picture cropping or placement when necessary; do not crop off meaningful strokes. Prefer independent complete icon objects over fragments.

Do not add backgrounds, badges, shadows, or a new palette merely to make all assets look alike. Restyling can be useful when requested and permitted, but record it and inspect the result. If the user requested website originals, do not substitute an AI-generated image or an unlabelled reference crop.

Simple symbols may be native shapes. For complex assets, exact source reuse, website alternatives, or image generation are different choices; follow the user's authorized choice rather than automatically generating a substitute. A renderer screenshot is not proof that an asset came from its claimed website.

## Keep concise provenance

Record, as applicable:

- Semantic role and local filename.
- Origin: supplied original, reference crop, website original, native drawing, or generated asset.
- Original page URL, author/collection, and relevant license/credit requirements.
- Any modification and whether the source was visually checked.

Use relative filenames so the work can move between machines. Place required attribution where the actual license allows; do not assume speaker notes satisfy every provider's requirements. If the desired use is unavailable, choose an appropriate alternative or state the unresolved requirement. Do not buy a license or use paid generation without the corresponding authorization.

A small record is sufficient; do not create a catalog for a single icon:

```json
{"role":"document search","file":"assets/search.svg","origin":"website original","source_url":"https://example.org/icon-page","creator":"Collection or author","license":"Verified license or unresolved","modification":"none","meaning_checked":true,"style_checked":true}
```

For a public example, also identify the source figure separately from replacement icons and state which parts were reconstructed or substituted. Public availability of an image alone does not settle permission to redistribute the source or its editable adaptation.
