# Visual asset selection

Use this reference when a source contains icons or illustrations that need extraction, replacement, or reconstruction.

## Choose the right source

1. Inspect user-provided originals first. Exact logos, UI screenshots, photographs, microscopy, maps, and other evidence-bearing imagery usually should retain their identity.
2. Reuse suitable supplied or previously verified assets before searching. For conceptual icons needing new external assets, search by meaning plus style. Provider options include Iconfont, Flaticon, Icons8, Material Symbols, official brand resources, and specialist collections; these are examples, not a mandatory search order. Honor a user-specified source.
3. Open the actual asset page and inspect the original asset. Search thumbnails alone do not establish the author, format, quality, or permitted use. Use available browser or web retrieval tools and permitted download routes.
4. Evaluate the whole set at its intended size before committing it to the diagram. Use a small comparison sheet when a style decision materially affects the result; do not turn every icon into a separate approval step.

Gather the required semantic roles first and search related roles together. If style is ambiguous, ask about a representative pair or family, then apply the answer consistently. Keep verified files and source records in the task's working assets directory and reuse them for revisions. A download or an attractive search thumbnail alone is not a completed asset check.

## Selection criteria

- **Meaning:** represent the specific object, action, or state. Reuse a symbol consistently when it denotes the same concept; different concepts may need distinct visuals.
- **Style:** match outline/fill treatment, stroke weight, corner shape, perspective, shading, detail density, and palette. Prefer coherent collections where suitable without sacrificing meaning to enforce one author.
- **Legibility:** fine details that disappear at slide size do not help. Compare visible content, not only the image's rectangular dimensions.
- **Identity:** do not replace a technical evidence image with a generic illustration or present a representative icon as the actual observation.

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
