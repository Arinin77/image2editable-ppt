# Package changes

This revision keeps the internal skill name `image-to-editable-pptx` and presents it as **Image2EditablePPT**.

- General image-to-PPTX scope: no mandatory subject area, palette, model, OS or icon vendor.
- Focused clarification for meaningful uncertainty; accepted style references are reused without repeated approval questions.
- Native text and geometry separated from independent images; exact source artwork can be retained where a replacement would change meaning.
- Meaningful module grouping and attachment checks; no promise that all editable paths automatically follow moved modules.
- Optional inspector checks duplicate object IDs, connector references and endpoint metadata, including grouped targets. Four regression tests added, 14 total.
- Reference documentation stays separate from the short main workflow; reuse existing assets and construction paths, repair only affected slides.

No model/token benchmark is claimed. Existing conversions are presented as curated worked cases, not fresh runs of this revision. The previous installed skill is preserved; this review copy is separate.
