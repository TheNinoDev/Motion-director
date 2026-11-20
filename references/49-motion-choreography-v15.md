> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V15 — choreographed motion, not an effects checklist

Standalone execution instructions. Original comparison clips are not needed. The developer compared the decoded V14 sample and earlier sampled reference frames; the main gap was a nearly fixed layout with separate reveals around it. This version changes the visual grammar and supplies actual code, not another requirement to invent effects.

## 1. Choose a visual mechanism before a tool

Every beat has one primary action and one visual consequence. For example, a fragmented workflow becomes a single organized space: scattered objects contract into an anchor; the anchor becomes the frame of a product shot; the product resolves into the wordmark. Do not use that mechanism for unrelated claims. Alternatives: accumulation (one object becomes a field), search (magnify a real target), contrast (two authentic states in the same layout), transformation (before becomes after), zoom out (detail becomes full interface). Only show an authentic state as proof. No numbers merely because a counter is available.

Give each sequence a density curve: low → buildup → one decisive visual peak → readable proof → clean hold. Keep at least one visual property across a major cut (central anchor, outline, scale, direction, rhythm, or color). Change composition, not merely translate the same card. Use the phone crop, not a letterboxed landscape layout. A visually quiet moment may be intentional. Do not add shake, glitch, particle overlays or flash simply to improve motion metrics.

## 2. Concrete execution decision tree

1. Write and lock the short real narration first, then verify actual timing and establish the visual meaning of each phrase. Obtain selected music/VO as described in the main skill. For a silent test explicit silent instructions suffice.
2. Collect at least one authentic product visual for the centerpiece. If showing a live workflow use true captured before/after states. Do not replace unavailable UI with concept assets.
3. For a simplification or consolidation story, run the ready-made choreography compiler. It outputs three editable scenes with a shared ring motif, tonal inversion, real product screenshot, formation of typographic brand text, and a CTA. For any different story, choose corresponding parts of these layer recipes; do not force this scaffold into every video.
4. Use `kind:morph` to change a meaningful silhouette; use `kind:swarm` to preserve and move separate particles. Choose at most one as the main effect in a beat. The identity of a particle is stable throughout its transition. Both tools are CPU 2D, not 3D particle dynamics.
5. Keep proof readable: tilt/scale settle before critical words, no chromatic shift on proof, no unnecessary bloom. At transitions use `circleclose` or another shape-related wipe only when it matches the current motif. Cuts remain an excellent default.
6. For 30fps: primary text reveal 7–14fr, secondary entries 8–16fr, major shape morph 18–30fr, swarm 20–36fr, short transition 4–12fr. Let readable holds last according to actual phrase time. Keep CTA readable for at least 45 frames if possible. At other fps preserve elapsed time. These are design defaults, not measurements of an original video.
7. Add sound at specific visible impacts/clicks or movement peaks. Use a sparse stem, never fill every gap. For actual videos real VO and user-selected music set the rhythm; procedural SFX are supplemental. Do not label synthetic effects as narration or music.
8. Run `--check`, then a 540x960 preview. Run `scripts/layout_geometry.py`, `scripts/audit_layers.py` and `scripts/visual_review.py`. Inspect opening frame and peak, transition, proof, endcard at phone size. Repair collisions or clipped text; do not blame metrics or ask user to fix assets unless truly missing. Compare at least two style variants internally when the first looks generic. Render full resolution from original sources instead of upscaling the preview.

## 3. Preset compiler and API

See `starter/choreography/README.md`. It generates an editable 3-shot unified project. The plan uses a fictional study as its bundled example. If adapting, supply your own screenshot and original copy and explicit three beat frames. The compiler is not a scriptwriter: follow main skill's writing process, then feed the selected story. A six-frame overlap at the third shot is accounted for in effective duration. If you change FPS or overlap, recalculate voice and SFX timeline. It uses a typographic rendering of brand text, not a replacement for a supplied authorized logo; if a precise logo exists, use it for the final hold. Use the real brand palette. Use a fitting real authorized font (not bundled) for your brand.

## 4. Repair map (practical)

| Symptom | Correction |
|---|---|
| Composition feels like a slideshow | Combine objects in a continuous sequence, keep one anchor, change shot scale and spatial density. Implement a meaningful morph or reframe. |
| Too much going on | Remove all but primary motion and one secondary cue. Hold proof. |
| Ring morph briefly pinches or disappears | Signed-distance interpolation may change topology. Inspect midpoint, choose a more compatible pair (circle→square), switch to swarm or a designed hard cut. |
| Particles clump at target | Change count, dot size, seed, layout or arc. Use a solid shape layer arriving after the particles, not a particle swarm as final readable text. |
| Mechanical starts/stops | Use easing `inout` on travels, `out` on arrivals; account for the end of shutter exposure. |
| Text overlaps proof | Run glyph-aware layout report. Move readable text upward or proof downward, shrink only when legibility survives. Do not hide the conflict with blur. |
| Text cropped at first frame | Inspect frame 0. A hook may start fully visible, especially if the mask would read as nonsense. |
| Motion blur smears text | Stop fast text travel before readable hold; lower shutter to .35 or reduce samples to 1 on intentional static typography. |
| Radius wipe appears gratuitous | Remove and use hard cut retaining visual anchor or one restrained overlap. |
| Sound effects dominate or sound synthetic | Reduce individual gain, shorten event, remove extra hits, prioritize VO. |
| Narrow layout/long copy | Rewrite the on-screen excerpt without changing the spoken script; wrap intentionally, check the actual glyph bounding boxes. |

## 5. Release honesty

Geometric checks and decoding are evidence of technical health only. They do not recognize visual elegance, emotional tone, source truth, or rights. Use actual review; intentional overlaps can be marked `allow_overlap:true` only when checked. A preview without voice remains a preview, even with SFX. Do not use the demo assets as customer proof. No external reference videos are required. No professional editor GUI required.
