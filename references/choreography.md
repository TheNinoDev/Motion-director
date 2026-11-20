> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Motion choreography and attention design

## 1. Establish the visual system
Choose brand palette, surface/background, typography pair, type weight, alignment grid, logo treatment, rhythm and one recurring visual motif. Design first-frame, payoff, product-proof and closing frames before committing to complex code. Verify at actual phone size and keep critical content away from platform overlays; default working safe area ~8% sides, 12% top, 20% bottom, adjust after preview. Avoid placing narration captions under social controls. Use negative space as a real compositional tool. Use optical alignment, kerning and consistent spacing, not dozens of font sizes. Use user-supplied fonts with correct licensing and fallback.

## 2. Motion hierarchy
Primary = what viewer should look at now. Secondary = context and continuity. Tertiary = texture/atmosphere only if helpful. Never animate all three with equal intensity. Change visual information when narrative advances, not constantly for its own sake. A shot may evolve by revealing words, moving a light, changing scale, introducing evidence, shifting focus or changing framing. Alternate density, pace and scale. Hold legible information long enough to understand; a quick insert can be decorative but cannot carry essential claims. Do not cut just because a beat exists. Keep meaningful rest periods.

## 3. Timing and curves (starting points, adjust to actual audio)
- At 30 fps, one frame 33.3 ms. Use frame-derived evaluation; fractional time allowed internally. Quantize cut boundaries to frame indices.
- Crisp type reveal ~5–12 frames; character stagger ~1–3 frames for short words or reveal by word. Long text needs longer readable hold. Avoid jitter or shifting previous words unless intentional reflow.
- Large scale or camera drift ~0.5–2 s; fast micro interactions ~4–10 frames; transitions often ~6–15 frames. Duration is not a formula. Slow macro reveal may take several seconds. Preserve lead-in and exit velocities.
- Ease out for deceleration into focus (e.g. cubic-bezier .16,1,.3,1); ease in for departing; ease-in-out for motivated transitions. Linear for constant cursor movement or mechanical rotation where appropriate. Avoid universal elastic or overshoot. Try critically damped springs for soft responsive UI when useful, low overshoot. Use controlled motion blur on rapid movement; keep text crisp at hold. Do not blur everything.

## 4. Continuity graph
For every pair of beats, choose bridge and what survives: shape, position, color, direction, object identity, type baseline, story action, rhythm or sound. Record transition entry/exit anchors (normalized screen coordinates), expected velocity, dominant scale and previous/next motif. Rehearse as one sequence. If a hard cut cleanly shifts tension, use it; do not force a morph. Avoid repetitive slide-in/slide-out and fade-to-black between every scene. When two scenes overlap, account for it within compositor layers; master beat intervals remain gapless.

Examples (implementation suggestions):
- Big hero number shrinks and becomes the label of a real list; list scrolls while number anchors.
- Crop the actual search field, type, press, show response; response label grows into next headline at same baseline.
- Match a cursor caret to vertical divider, then chart axis; use brief hold before revealing chart.
- Hero object crosses lens; next shot begins on matching silhouette/shape; avoid stock wipe.
- One brand accent appears at the error or payoff, not on every decorative element.
- Macro photograph of an object cuts on matching curve into genuinely rendered brand mark or real UI element.
- A background word grid conveys abundance; foreground selection lifts by contrast and scale. Stop movement when viewer needs to read.
- Maintain caption location during rapid proof montage so eye doesn't hunt across changing scenes.

## 5. Advanced recipe palette
Use existing `motion-recipes.md` plus these adaptable patterns. A recipe is a technique, not a prebuilt scene. Mix at level of meaning, geometry, typography and audio, not random FX.

| Recipe | Mechanism and controls | When to use / guardrail |
|---|---|---|
| Baseline lock | Pre-layout line boxes, animate masks/transforms inside stable widths | Progressive emphasis without jumping layout |
| Word replacement | Track previous/next word metrics, cross-mask and align optical centers | Changing status/number; do not squeeze long words |
| Variable font emphasis | Interpolate weight/width axes on supported font, maintain container | Emphasize one word, not every word |
| Optical type zoom | Camera transform around anchor with compensating layout at end | Tiny clue to oversized payoff |
| Shared-element transition | Record bounding rects of same asset, interpolate position/scale/crop | UI proof to next conceptual scene |
| Layered clipped montage | Stable rounded mask, switch actual images behind it on chosen cues | Show variation; allow enough inspection time |
| Physical UI typing | Character events, caret, focus state, click state, actual result | Grounded demo; not fake mouse movement |
| Editorial data | Reveal authentic line/axis, animate counter from real values, exact units | Evidence and story, no fabricated charts |
| Contrast grid | Seeded repeat, opacity hierarchy, one selected cell | Abundance, scarcity or repetition as concept |
| Depth reveal | Real camera or 2.5D layers with physically plausible parallax | Spatial context; not every card |
| Light-driven hero | Stationary beveled form, moving area light / reflection card | Premium 3D closeup without constant spin |
| Macro rack focus | Real depth of field or masked blur by layer, focus shifts to proof | Rare; preserve readability |
| Shape-matched cut | Align silhouettes / directional lines over a few frames | Visual continuity without effect overload |
| Procedural assembly | Instanced geometry seeded positions, easing to meaningful form | Complexity motif if concept earns it |
| Semantic sound bridge | Audio cue starts before cut or tail extends into next beat | Connect story without visual gimmick |
| Intentional quiet | Remove secondary layers, hold focal text or visual, reduce SFX | Make next high-energy section feel bigger |
| Impact contrast | Fast shift from tiny/sparse to large/bright, one short hit | Payoff, avoid strobing |
| Brand lockup | Settle logo, tagline and single CTA; hold for reading | No fake platform outro |

## 6. 3D and characters
Default favor high-quality 2D/2.5D and use real 3D only where form/material/light adds semantic value. For a typical 20–45 s product film, 0–2 hero shots; a CGI-driven narrative may justify more. Real rounded bevels scaled to geometry, clean topology/smooth normals, calibrated metallic roughness, reflections from actual environment/area lights, shadows, anti-aliasing. Avoid rectangular cubes approximating complex logo or characters, arbitrary 3D floating card sequences, plastic chrome without reflections, jagged edges and excessive camera orbit. Use provided sprites/GIFs in original proportions. If character animation is low quality, choose tasteful editorial 2D instead. Do not distort assets or cut out important limbs/text.

## 7. Build and review shot-by-shot
At entry/peak/exit and transition boundary inspect actual rendered images, then playback if available. Compare with visual intent and previous shot. Avoid offscreen critical text, too small metadata being treated as vital, asset flicker, inconsistent shadows, motion blur lingering on holds, interpolation overshoot crossing safe area and excessive flashes. Measure variety over whole film; if consecutive scenes look identical, change framing, scale, pacing, mechanism or scene type. If a scene looks chaotic, simplify secondary motion first. The goal is dynamic, smooth, visually pleasing, and cohesive, not maximal raw effects.
