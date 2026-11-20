> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Editorial v22 — typographic choreography and product proof

No GUI, custom renderer already included. Python, Pillow, NumPy, OpenCV, FFmpeg. OpenCV is also used for the fold projection. The original reference videos are not required. Use an installed font or the project's own authorized font. On systems with Inter Display installed the unified controller prefers its bold face for editorial shots; otherwise it uses the previous fallback. No fonts are packaged.

```sh
python starter/unified/production.py examples/editorial-v22.json --check
python starter/unified/production.py examples/editorial-v22.json --preview
python starter/editorial/preset.py --hook 'Good work' --tension 'gets buried.' --reveal 'Bring it forward.' --proof 'Your selected work.' --brand 'FORM' --cta 'Make room for your work.' --screenshot work/product.png --crop .05 .28 .50 .55 --crop2 .54 .28 .95 .55 --frames 45 39 57 66 42 --out work/editorial.json
```

The example is fictional; its screenshot was rendered from the included fictional HTML in prior development. Its audio is generated SFX only. It is a technique study, not evidence of product functionality, a finished ad, or professional creative quality. Match the actual user’s script, verified timed speech and real UI assets. Do not copy the sample text or color palette by default.

## Unified JSON (`engine: editorial`)
All shots require `frames` from 4 to 3600, and a `content.kind`. Color keys `bg`, `fg`, `accent`, `accent2` (RGB), text keys `text`, `sub`, `label`, `brand`, `repeat`; lines array up to four short, nonempty lines. `src` is a project-relative authorized screenshot; `crop` and `crop2` are [left,top,right,bottom] normalized rectangles. `progress`, `zoom`, `drift` may use normalized keyframes `[[0,0],[.6,1,"out"],[1,1]]` using strictly increasing times and linear/smooth/in/out easing. `tracking` -0.08..0.15 em, `grain` 0..3 (subtle), `samples` 1..3, `shutter` 0..1. Temporal samples use approximate linear-light averages across actual instants. Not all controls apply to every kind; see table. `accent2` is the secondary color used by `macro`. All generic fields must be valid even when unused.

| Kind | Motion | Consumed controls |
|---|---|---|
| wall | Alternating scrolling typographic field, central negative-space clearing, staggered title | lines, repeat, density 3..12, progress, drift, layout left/center/right, reveal, sub, label |
| shutter | Alternating slices of one real image consolidate into full aspect-ratio-preserved product detail | src, crop, density, progress, text, label |
| macro | Continuous actual UI crop movement with aspect preservation | src,crop,crop2,progress,zoom,text,sub,label,reveal |
| fold | Curved textured 3D plane projected in strips, flattening to the actual source image | src,crop,bend,yaw,pitch,shine,zoom,progress,density,text,sub,label,reveal |
| folio | Two product-detail rails settle alongside a large intact shot of the actual UI | src,crop,crop2,progress,text,label,reveal |
| aperture | True alpha-mask image-filled type, animated source window | src,crop,lines,progress,zoom,sub,label |
| poster | High contrast full-frame title, staggered typography and synchronized rules | lines,layout,reveal,label,sub |
| signature | Short brand lockup, animated rules, wipe and text | brand,sub,label,progress |

Reveal choices on applicable types: `slice` vertical mask (default), `glyph` approximate character-width stagger (not a full shaping engine), `wipe` horizontal, `none` opacity. Preserve legibility with short lines, especially for non-Latin scripts; test text shaping and actual font coverage. No text intentionally extends beyond safe bounds except the background texture of `wall`. Actual product details must be inspected for readable labels; a final crop must not imply a functionality/state that does not exist. `macro` and `shutter` preserve crop aspect. `fold` uses actual curved planar geometry and painter-order perspective warps, not arbitrary 3D mesh rendering. Bend/yaw/pitch tracks have ranges −1.6..1.6, −1.2..1.2 and −0.8..0.8 radians; shine 0..0.6. At the landing use bend, yaw and pitch zero to preserve source legibility. The rail previews in folio use cover crops. Avoid source crop text unless entirely visible. Use realistic UI proof, not artwork alone. Avoid extreme ratios or zoom on fold; maximum aspect height:width 2:1 for fold, and inspect projected corners. `folio` shows detail rails as illustrative cropped previews. Do not use it to imply a particular interaction occurred.

## Direct render
`python starter/editorial/render.py direct.json still.png --font /path/to/installed-font.ttf --frame 15` uses a `{width,height,fps,shots}` plan with absolute image paths and per-shot `frames`. Prefer the unified production controller for actual work; the direct tool is for tests. Do not submit a direct plan to the unified controller.

## Quality loop
Render 3–5 frames per shot plus boundaries, inspect type size, contrast, crop semantics and mobile margins. Open the actual contact sheet, compare with prior candidate, fix the weakest visual beats. Prefer the new sharper crop renderer to tiny tilted screenshots. Use intentional brief negative space, no long dead holds. Avoid making every title top-left or every shot a poster. Recombine these modules with existing physical CGI, masks, scene3d, data and character engines if the story merits them. The agent may not claim a professional aesthetic score from validation or from increasing an effect count.

## Actual alternative boards
`python starter/editorial/style_board.py examples/editorial-v22.json fold work/candidates.jpg` renders four alternatives at three times from an actual editorial shot, and produces a companion JSON with candidate patches. The agent chooses based on rendered evidence, not a numeric beauty score. For final review: `python starter/editorial/review.py PROJECT VIDEO work/boundaries.jpg` verifies timeline frame count and renders exact phase samples. Inspect the board and watch/listen if supported. The board is not the media itself.
