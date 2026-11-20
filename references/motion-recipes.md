> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Motion design recipe library

Recipes are reusable techniques, not fixed scenes. Values are starting points for 30fps; derive actual duration from audio. Use an editable timeline, deterministic interpolation and compositing. Use 2D/2.5D for most scenes; one or two real CGI highlights in a normal promo. For each effect state its narrative purpose.

| Technique | Implementation and purpose |
|---|---|
| Word-by-word build | Lay out final phrase first so prior text does not jitter. Reveal each token at measured start, opacity or masked upward motion 12–40 px over 4–9 frames. Setup words gray/small; payoff white/bold/large. Retain accumulated text if readability benefits. |
| Typographic layout takeover | Anchor the important word; push secondary words away using shared baseline or scale into a crop. Use actual measured glyph geometry. Do not create a random scale bounce each word. |
| Stacked headline | 2–4 lines arranged editorially, one new line or word per phrase. Mask reveals; hold final readable shape. |
| Type cursor | Render actual text + caret at measured width, reveal by characters; cursor blink only while idle. Model input focus, button hover/press/check/result. A coral rejection or accent success changes emphasis; avoid fake claims. |
| Tiled word wall | Repeated phrase in a grid/marquee; use 2–3 contrast levels with one active token. Move slowly or cascade; keep exact story-related words and fade at edges. |
| Numbers and counters | Interpolate integer values tied to actual data, use tabular numerals, group digits. Ramp acceleration then controlled settle. Do not invent data. For metallic hero value, animate genuine geometry or use a distinct cut from flat counter. |
| Graph reveal | Use SVG path length or clip mask, axis/labels in muted ink, animate endpoint/counter in sync. Bar chart stagger 1–3 frames; truthful values and scale. |
| UI macro | Capture actual interface at high resolution without private information. Crop to relevant component, animate camera pan/scale and cursor action. Keep text sharp; never just scale blurry screen recording. |
| Profile carousel montage | Use real screenshots/cards at consistent frame with 0.25–0.75s inserts where quick recognition suffices; stable subtitle/key visual anchor. Transition with shared framing; no gratuitous spins. |
| Product deck | Layer 3–5 real UI cards with staggered translation/scale and depth offsets. Shadows subtle; settle one front card. Avoid unreadable fanned perspective. |
| Editorial micro-layout | Small labels, hairline separators, numeric index, grid, negative space. Animate only important lines; low contrast decorative labels. |
| Masked match cut | Align outgoing and incoming anchor (letter/circle/search bar/card edge), animate clip or crop through shared contour. Plan exact end/start positions. |
| Directional continuity | Outgoing movement carries into incoming direction, speed eases rather than abrupt unrelated reset. Use transform-based motion blur if renderer supports it. |
| Punch cut | Cut on a confirmed impact or phrase switch; brief scale 1.0→1.06→1.0 (or use no scale), no mandatory flash. Reserve for strongest points. |
| Soft focus/macro | Animate real camera focus in CGI, or layered blur for 2D foreground/background depth. Sharpen important object before reading. |
| Highlight sweep | For 2D use masked gradient sparingly; do not call it true CGI. For real 3D move reflection card/area light while object rotates slightly; never paint random sparkles on every edge. |
| Real chrome letter / logo | Use actual vector/font outline, extrude, bevel (~1–3% glyph height initial), bevel segments 3–6, smooth normals/weighted normals; metallic material, roughness ~0.15–0.3, large soft light strips, black environment with reflection sources. Animate object or lights, camera ~40–80 mm equivalent; reflection floor with physically plausible material if desired. Test curves/edges at 100%. |
| Instanced arrays / procedural swarms | Geometry Nodes or real instancing; deterministic scatter on paths/rings, seeded rotation/scale, hero silhouette. Limit instance counts and render budget; cull offscreen. Use for scale/metaphor, not filler. |
| Logo reveal | Keep original brand proportions; use clean silhouette, motion/light reveal or simple type lockup. End with URL and optional CTA with sufficient reading time. No downloader branding. |

## Curve and pacing toolkit
- Ease-out for entering objects, ease-in for exits, ease-in-out for continuous camera travel. Example cubic-bezier(0.16,1,0.3,1) for settle; (0.4,0,0.2,1) for UI motion. Use different curves according to physical action; don't apply a single easing everywhere.
- Use tiny overshoot 1–3% only for playful emphasis. Preserve baseline and avoid jitter. For motion blur use physically sensible shutter ~90–180 degrees depending on action; sharp static type. Avoid unreadable blur.
- Directional motion can bridge scene changes, but use clean hard cuts and intentional holds too. Avoid repetitive pattern (zoom, fade, zoom, fade) or transition presets on every cut.
- Separate primary motion, secondary accompaniment and atmospheric detail. One main movement should dominate. Pauses and negative space are part of the design.

## Scene selection
Map each phrase to its semantic role. Hook = typographic or visual surprise; problem = contradiction, UI error, repeated pattern; evidence = real UI or honest chart; value = comparison, motion metaphor; payoff = one hero visual, then CTA. Use multiple different scene families, not a fixed sequence. Preserve shape, direction, color, focal anchor or narrative link between neighbors.
