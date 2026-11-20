> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Concrete motion recipes — 1080x1920 at 30 fps
All values below are proposed starting points; adapt scale to design and timing to actual voice. A frame span 0–12 means 12 frame intervals. Use normalized local progress p = clamp((frame-start)/(end-start),0,1). Ease out cubic = 1-(1-p)^3; ease in/out cubic = 4p^3 for p<.5 else 1-(-2p+2)^3/2. An object should have predictable final state; clamp spring overshoot for text. Prefer CSS transforms/masks or canvas/SVG operations, not layout reflow. Keep camera and content transforms separate. One primary motion, one support, optional ambient motion; ambient may be absent.

| Recipe | Exact initial → final state | Timing and trigger | Common error / correction |
|---|---|---|---|
| Word rise | Each word y+32px→0, opacity 0→1, clip in line box | 6–10f ease-out, stagger 2–4f or actual speech | Entire sentence bouncing? Pin baseline, animate words only. |
| Line build | Wrap line in overflow hidden; y+48→0, opacity .5→1 | 8–12f; next line on next phrase | Reflow jiggle? Premeasure full block. |
| Word emphasis | Regular→bold via alternate aligned layer; color gray→white | 4–8f; stressed word | Weight changes layout? Use two prealigned layers. |
| Hero zoom reveal | scale 3.2→1, center anchor remains same | 16–30f ease-in-out | Cropping unrelated content? Use one hero and controlled framing. |
| Hero to metadata | scale 1→.32, x/y hero center→final label | 10–18f; new list follows 4f later | Reset at cut? Match exact end/start transforms. |
| Camera crop | Source image big enough; scale 1.65→1, pan focus→full composition | 24–45f; deliberate reveal | Pixelation? Capture 2x or use vector, limit zoom. |
| UI interaction | Pointer x/y from outside target→center; scale 1→.92→1 on click; state swaps | Move 12–20f, press 3f, release 5f | Pointer misses? Compute target DOM bounding box. |
| Typed input | At character event show next prefix, cursor remains after text | 2–5f per char, human pause after word | Variable font text jumps? fixed alignment and measured width. |
| Feedback | Input retains position; change error accent, reveal response | 4–8f after click; hold 15–30f | Fake state? Capture real UI or mark illustrative. |
| Repeated rejection | Clone word into grid with 8–15% inactive opacity; selected bright accent | 3–5f per row, 12–22f build | Random grid? Repetition expresses quantity/conflict. |
| Collapse grid | Mask grid to strip, width 90%→4px, align final cursor | 10–16f | Disconnected effect? Use same x/y and color at boundary. |
| Mask wipe | Clip right inset 100%→0 or shape bounds shrink | 8–15f; one object leads edge | Full-screen wipes every scene? Use selectively when shape matches. |
| Chart reveal | Plot actual values; stroke dashoffset pathLength→0; marker follows curve | 20–45f; count only if supported | Invented metric? Use supplied dataset or no numeric claim. |
| Count animation | Interpolate integer from known start→end, monospace/tabular digits | 12–36f, ease-out | Fake intermediate values read as facts? label visualization. |
| Product montage | Same card 760x1000 position, swap approved capture content | 12–24f each; hold key example 45–75f | Unreadable UI? Treat fast frames as mood not proof. |
| Parallax | Background y±12px, hero ±40px, foreground ±70px; same direction/time | 30–90f | Seasick? reduce distances, no random rotations. |
| Match hard cut | Outgoing focal glyph and incoming product icon aligned | 0f transition, optional preceding 4f anticipation | Crossfade blur? Prefer hard cut at semantic connection. |
| Contrast cut | Change background and text palette once, hold clean | Instant then ≥15f hold | Strobe? Do not alternate rapidly. |
| Reflection sweep | Genuine beveled object fixed, move broad area light across | 30–100f; one highlight | Fake shiny gradient? Use real render or flat type. |
| Loop ambient | y 0→6→0 or background noise locked seed | 90–180f | Random flicker? seed per shot, don't reseed every frame. |
| Brand settle | Logo y+16→0, scale .98→1, opacity 0→1 | 10–16f then hold 45–75f | Logo too short? extend tail not narration. |

## Transition selector
Same object: shared transform with identical boundary values. Same shape: mask match (circle to icon, line to caret). Same concept different visuals: hard cut on spoken turn. New mood: deliberate palette contrast. UI navigation: move camera in direction of new panel. Time jump: editorial cut with visible context. End: brand hold. Never randomly rotate the whole composition. Limit generic fade/zoom repetition; inspect a strip of all scene transitions. Use opacity only where it supports layer hierarchy. Motion blur if engine supports correct sampling, moderate shutter, no blurred reading-critical text. Don't add blur to disguise missing frames.

## Frame-level example
At f0 title hidden except first word. f3 word1 halfway, f8 word1 settled, f10 word2 starts, f18 all settled. f24 hero icon enters from existing underline anchor. f48 icon at full scale; f54 camera begins pullback; f68 icon at upper-left of UI; f68 next scene opens with same anchor, scale and color. f72 pointer begins motion, f88 click, f92 actual UI result. This is a connected edit rather than three independent animations. Adapt times to actual VO.
