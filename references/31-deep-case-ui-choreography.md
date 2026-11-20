> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Deep case 4: NOIZ reference 3 (1000043458.mp4)

## Evidence and limitations
Original 576x1024, 30 fps, container duration 38.6 seconds. Inspected 155 target timestamps at 250ms spacing over full file (as decoded; sampling not exact source keyframes). Download watermark and TikTok end card beginning around 34.75 are not part of style. Visible text may be quoted only as a short analytical example. Voice, score, beats, exact easing and original editor are unverified. All frame counts below are proposed reconstruction settings at 30fps, not measured source keyframes.

| Observed interval | Visible development | Proposed construction, no GUI |
|---|---|---|
| 0–2.25 | Cropped reflective O becomes complete wordmark; smaller supporting text, black background. | Render an original approved wordmark hero clip or flat image; animate same center and scale 3→1 over 25–38f, keep final lockup long enough to see. Original logo not included. |
| 2.25–4.25 | Bold question accumulates from WHAT to four stacked lines; fixed left edge. | Four text layers; measure actual glyph bounds; left edges match, start per phrase, reveal 6–9f then hold. Do not center each word independently. |
| 4.25–5.5 | Very small centered text and almost empty background. | Hard contrast cut; protect important dialogue with readable subtitle if appropriate. One microtext beat, never tiny critical CTA. |
| 5.5–7 | Feature-list progressively fills row by row, with aligned labels and data. | Fixed list grid with 5–8f stagger. Real product facts; no invented numbers. |
| 7–9 | Small centered transition phrase, black negative space. | Hold a deliberate reset before introduction of visual examples. Contrast with upcoming density. |
| 9–12.5 | Pink avatar followed by alternating small visual/profile cards, nearly constant position; background stays dark. | 3–6 authorized screenshots or source-rendered examples; same size and anchor; hard cut or 3–5f crossfade per clip. Stable caption; do not animate everything at once. |
| 12.5–14 | Brief text reset; phrase builds progressively, final word larger/contrasting. | 2–3 text layers with different weights. Reset immediately before product proof. |
| 14–16.25 | Large artwork/background becomes contextualized by a profile UI; profile resolves, then framed view. | Begin with source screenshot at scale 1.8–2.3, chosen crop center; move same image to final 0.85–1 scale over 22–35f. Use DOM captures of layers where available. |
| 16.25–19.25 | Cropped high-contrast graphic transitions into monochrome profile with icons and other content appearing. | Match a distinctive shape into second profile. Capture actual initial/final product state; if interface is static, separate authorized elements and reveal with 6–12f offset. |
| 19.25–21.75 | Pink profile, content accumulates, small list expands below. | Same frame composition with new content/palette, DOM capture successive real states. Stagger rows/icons, protect safe areas. |
| 21.75–24.25 | Blue profile; icons, larger panels and rows appear; focus shifts toward lower portion. | Capture full page in a test environment. Pan camera to lower content rather than shrinking everything to unreadability. |
| 24.25–26.75 | Macro graphic then dark interface with animated-looking background and stable small UI content. | Use separate ambient layer and actual foreground crop if available; otherwise capture original background animation as source clip. Avoid inventing user functionality. |
| 26.75–28.5 | Blue-green profile, colorful icons; mildly changing composition. | Make color and user-generated content the variation; keep screen anchor stable. |
| 28.5–30.75 | Purple profile with luminous boundary; UI content builds. | Capture authorized purple variant, animate highlights in an outer compositing layer only, stagger content from real states. |
| 30.75–33.25 | Multiple profile panels consolidate into final composition, headline above them. | 3 panels with known screenshots, move from shared center into separated positions over 18–25f; small rotations ±5–10 degrees. One readable dominant screenshot and headline. |
| 33.25–34.75 | Black reset followed by NOIZ wordmark/end statement. | Original brand lockup and CTA, 30–45f minimum if sufficient audio; no copied slogan, watermark or downloader end card. |

## Core techniques and decision rules
- Explainer is a question with a payoff, not a feature checklist. The profiles become the answer. A paid product demo must show what users can really do, not generic UI imagery.
- Identity layer = fixed layout, recurring typography, text anchoring, background; variation layer = real user content, profile palettes, crop, motion scale, reveal order. Preserve the first while changing the second.
- Treat screenshot as a scene, not a texture to move aimlessly. Each change highlights a visual fact. Save captured state A, state B, element screenshot, and asset provenance. If not enough proof, ask for minimum missing information or mark conceptual mockup.
- Never use 3D phone mockups just because the source is mobile. A clean crop or flat panel is often stronger. Use 3D for meaning only.
- Match cuts: align old and new selected visual anchor to same pixel coordinate for 2–4 frames near the cut. Preserve size, silhouette or color if the transition is intended to feel continuous. Select a true hard cut for contrasts.
- Content entrance can be entirely shot-driven: vary from a 6f hard-on graphic to 15f reveal, 24f camera reframe, 40f gentle hold. Do not apply the same easing and direction on every element.
- Final proof montage should not introduce unrelated features. Each profile supports the same benefit (personal identity/customization). Reserve discovery, messaging or monetization for other films.

## How to build this with bundled tooling
1. Verify product facts and authorization. Create script and audio per earlier guides, then derive actual word/phrase timings.
2. Run `starter/ui_engine/capture.py` with local HTML or authorized URL, viewport and optional CSS selector. Inspect output image and diagnostics JSON. Use screenshot files if browser unavailable.
3. Copy `starter/ui_engine/demo-plan.json`; replace asset paths, text, palette, sizes and shot durations. Render exact frames with `render.py --frame N` before video. Do not retain fictional demo assets in actual marketing.
4. For opening metallic hero either use `hero_token.py` for an appropriate genuine geometry asset or a clean 2D wordmark. Hero token cannot reproduce arbitrary logos or custom reflective typography; implement or acquire suitable licensed assets, otherwise choose 2D. Use `stitch.py` for mixing rendered clips and still-based scenes.
5. Attach final aligned audio (not assumed source timing), inspect cuts before/after and all focal points. Use release gate. Record actual differences from the reference, not claims of identical reproduction.
