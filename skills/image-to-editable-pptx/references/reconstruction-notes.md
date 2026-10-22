# Compact reconstruction records

Use these examples when a dense figure or scripted build benefits from persistent records. They are not a mandatory schema or extra deliverable for every image.

## Content and connection map

Keep stable names so a repair can target one element without rebuilding the slide. Separate observed content from uncertain readings.

| Name | Type | Source content / role | Bounds | Representation |
| --- | --- | --- | --- | --- |
| query | text | Query | source-relative x/y/w/h | native text |
| search | module | Search | source-relative x/y/w/h | native shape + text |
| search-icon | icon | document search | source-relative x/y/w/h | independent website asset |

| Name | From | To | Direction / style | Label |
| --- | --- | --- | --- | --- |
| query-to-search | query.right | search.left | forward, solid | — |
| review-return | review.bottom | search.bottom | return, dashed | Refine |

Confirm the map against the source before using it to check the output. Record a user-approved content change separately. Do not infer arrow direction from placement alone, and do not let a reviewer edit verified source content merely to match the constructed slide.

## Reuse the construction setup

Use an authoring backend already available in the environment. Probe required features once when the backend is unfamiliar; do not introduce a backend-specific dependency merely to follow this reference. Keep canvas dimensions, font choices, recurring line styles and semantic element names in the build material. Reuse working asset and rendering paths during local repairs.

Keep native text, modules, icons and arrows separately addressable. Attachment support varies by backend: a freeform arrow can be editable while not automatically following a moved module. Check and describe the actual behavior.

## Focused repair

Identify the observed defect, patch its named element or route, and render the affected slide. Compare the repaired area and then the final whole slide. Keep detailed inventories on disk; load object-level details only when investigating a defect. A compact report is an interface improvement, not permission to skip visual or semantic checks.
