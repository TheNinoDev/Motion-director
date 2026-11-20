> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V33: small-model execution contract

Use this as the front door. You do not need to load the entire library. Start with a real product brief and authorized audio if required. For full advertising, follow SKILL.md phases; do not replace them with the technical showcase. Choose one verified promise. Write a natural hook, plan the story, then select effects because they communicate that promise. Every dominant object must establish a visual reason to exist. If no reason, remove it.

## Minimal tool sequences

| Goal | Run / read only |
|---|---|
| Contact-based elastic bounce | `starter/contact3d/README.md`, `examples/contact-v33.json`, run renderer. Change velocity, stiffness, color, mass, initial position. Use generated `compositor-layers.json` for side-view editing. |
| Smooth 3D type | Copy the layer from `examples/type-v33.json`. Change text, font, scale, depth and bevel; angle and light tracks can be reused as starting values. Use 2D for body copy. |
| Custom complete film | One `starter/composite_film` plan, `README.md`, guide 63, and this guide. Load only specific effect manuals as needed. |
| Glass or rigid hero | `README-v31.md`; `object3d`/`glass_object` with independent geometry and material; don't force flat glass into every design. |
| Real product UI | `starter/ui_engine/README.md`; capture from supplied product, no fake UI claims. |

## Execute, don't just describe
1. Make a project directory. Choose a semantic idea, a type family (actual available font), palette and visual proof. Write a JSON plan. Do not write a new renderer for standard operations. Keep one dominant visual per beat and one semantic handoff to the next with overlapping motion.
2. `python scripts/agent_preflight.py PATH/plan.json PATH/work` — use returned argument arrays exactly; it checks structure, font aliases, dependencies and flags likely low-res CGI. Fix errors rather than retrying unchanged. The preflight is not an aesthetic score.
3. Render styleframes first. Inspect the actual images, not the JSON. Compare alternate angle/font/light choices if weak. For type, check front, three-quarter and side views. If faces are shiny but edges look faceted, increase atlas resolution and AA; if narrow interiors close, reduce bevel or change font. If overlay text is hard to read, change position/contrast rather than piling on effects.
4. Render the complete rough picture and inspect actual timing. Fix the three worst moments. Keep all unaffected layers, preserve a revision copy. Avoid stop/start transitions. For final work use native 1080x1920 if feasible, temporal sampling selectively, high or lossless export and the audio/release gate; never upscale a low-res render and call it native. Render difficult shots independently if slow; don't silently reduce quality.
5. Deliver the compatible upload file, editable JSON/source and optional lossless master. If no narration/music was commissioned for a technical demo, silent export is fine; voiced ads require rights, speech timing, mix, and listening review. Never claim a professional voice or general model performance without testing it.

## Export profiles
`compositor.py PLAN OUT --check` validates without rendering. `--profile preview` uses H.264 CRF17/4:2:0 and per-layer quality. `--profile high` sets volumetric/text quality=1, spatial antialias ≥1.5, glyph atlas ≥960 and H.264 CRF12. `--profile lossless` uses the same render settings, RGB H.264 CRF0. Requested `--size 1080 --fps 60` is native; cost scales with the pixel count and samples. Use 30fps for most ad delivery unless 60fps really helps. Lossless is mathematically lossless codec, not no compression, and fixes no geometric or lighting defect. Audio in compositor remains AAC if supplied. Compatible upload export is still useful because RGB H.264 is not supported everywhere.

## Diagnose before release
- Aliasing/jagged silhouettes: actual native resolution, high atlas, AA 1.5/2, check full-res PNG; distinguish from chroma artifacts.
- Stair-step metal bands: use gradual normals, restrained depth/bevel, compare light orientation and stroke width; SDF still approximated, not vector CAD or full raytracing.
- Choppy transitions: check velocity, shared anchor and frame overlap; don't hide errors with blur.
- Mechanical softbody: prefer impact-derived deformation for wall collisions, choose damping and stiffness; authored impulses are for stylized motion, not contact claims.
- Heavy preview: reduce preview size, not final size; never call an interrupted file finished.

The V33 glyph distance field receives a deliberate low-pass smoothing step and normals use a larger, atlas-relative stencil. This suppresses side-wall microstripes from the sampled font outline. It is not a substitute for exact vector extrusion; narrow details can soften, so compare the actual full-resolution side view.
