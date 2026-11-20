> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Standalone material, light and compositing production recipes
No source videos or external designer research are required. Use a single recurring original motif selected from the product: logo fragment, interface icon, meaningful letter, bookmark, folder tab, or product-specific symbol. Do not introduce generic jewelry unless it actually communicates the benefit. Use 0–2 premium CGI inserts by default; a consistent material can recur as a callback. Never imply simulated material is an actual product feature.

## Ready sequence (adapt content, never copy branding)
1. Start with the object small and sharp, nearly black surroundings, short spoken statement. Let curiosity do the work. If first-frame readability fails, increase the object rather than adding a flashy intro.
2. On the important spoken noun or accent, use a match scale cut to a macro crop. `macro` preset: 42 frames at 30fps, large crop (1.9 canvas widths) to .78 widths. Move the camera metaphor, not the caption.
3. `metal`: 36–60 frames, one object centered with moving softbox strips, bevel .065, roughness .14–.25, reflection .20–.40, bloom .05–.12. Keep background black or deep charcoal. Do not use full-white face throughout; dark regions define shape. If a hole closes, decrease bevel and use a bold font. If edge normal aliasing remains, render larger and downsample once.
4. `focus`: 20–40 frames. Defocus only the background motif; put a crisp short question in front. Do not blur subtitles. Use narrative cue before switching to real UI.
5. Show actual product with UI capture; demonstrate the central action rather than five adjacent features. Reuse the visual anchor/position when cutting. `emissive` is only for an isolated accent. Keep glow local and use one short shot, not a permanent halo.
6. `portal`: 12–24 frames; choose a circular opening or recognizable shape, enlarge it until the crop fills the frame; next shot starts on a compatible shape at a compatible location. Hard cut at the closest geometry. If no useful shape match, use an ordinary cut. Do not add generic transitions.
7. Return briefly to original motif at the end and deliver the story payoff, then a stable, readable brand/URL hold.

## Lighting and optical decisions
Metal requires reflected environment variation: one large softbox, one smaller strip, negative fill. RGB values are not a material model; do not call a flat gradient true chrome. For significant camera orbit use real depth-tested mesh tool; for front-facing detail use the height-field tool. Use a neutral tint unless brand needs color. Distinguish motion of reflection from motion of object. On a paused frame object must still have a recognizable silhouette. The reference look relies on black/white contrast, not overdone glow or constant camera shake.

## Postprocessing router
- Moving source geometry? render shutter samples in scene, not a temporal blur on a final MP4. Never sample across hard cuts.
- Need background separation? blur only background layer; use real depth pass when available, otherwise honest layer separation.
- Need metal? use analytic material renderer or mesh, never a glow-only filter.
- Final clip is too harsh? use `finish.py` subtle preset on a copy, compare side by side, retain whichever serves readability. Do not use global bloom for white UI typography. Avoid crushed blacks, clipping, banding, color shifts, aggressive grain or edge darkening of product content.
- Mixed clip source with audio? normalize CFR and zero-based aligned audio, run finish on a copy, verify timestamps, count, playback and mix. Existing QA remains mandatory.

## Quality acceptance (internal, not user checklist)
Inspect at least first/middle/last frame of each material shot and full motion; compare to purpose, not to unavailable development footage. Check letter holes and edges, smooth light travel, coherent ground reflection, no character clipping except deliberately cropped macro, stable typography, no all-white blowout, no unintended flicker, clear mobile contrast. If any failure: adjust one parameter, rerender preview, inspect again. If heavy 3D unavailable, choose a purposeful 2D material accent or honest UI proof. Never silently claim photorealism. Avoid repeated hero shots unless meaningful callback. The release gate remains authoritative.
