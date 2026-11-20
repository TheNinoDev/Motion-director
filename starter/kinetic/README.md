> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Kinetic 21 — spatial glyph assembly and editorial reframing

No GUI, no reference video. Requires Python + Pillow + NumPy + OpenCV + FFmpeg, system font. Real 3D point positions and perspective projection with painter sorting; not a mesh renderer or physical particle simulation. Prefer `starter/fusion` or `studio` for reflective hero geometry and `layers` for arbitrary multi-layer compositing.

```
python starter/unified/production.py examples/kinetic-v21.json --check
python starter/unified/production.py examples/kinetic-v21.json --preview
python starter/kinetic/preset.py --hook 'Where did it go?' --glyph A --words 'LESS' 'SEARCHING' --proof 'Saved items.' --brand ACME --cta 'Find your saved work.' --screenshot /path/to/real.png --crop .1 .15 .6 .7 --frames 60 30 100 60 --out work/kinetic.json
```
The branded examples are fictional study material. Do not use their copy/assets as the user's real proof. Use actual verified speech timings to pick frame counts. The preset is an editable starting point; do not use the four-shot scaffold for every film. For custom independent shots use the same unified JSON engine `kinetic`.

| kind | controls |
|---|---|
| field | `glyph` (1–12 characters), `field` vortex/wave/burst/helix/grid, `count` 100–6000, `sprite` dot/shard/dash/mixed, `size` .35–2, `seed`, `spread` (0 = field; 1 = glyph), `yaw`, `pitch`, `zoom`, `panx`, `pany`, `glow`, `samples` 1–4, `shutter` 0–1, optional `text`, `sub`, `eyebrow` |
| proof | required real `src`, `crop` normalized left/top/right/bottom, `focus` (0 = crop; 1 = entire image), `zoom`, `yaw` (planar perspective), `panx`, `pany`, `reveal`, `mask` diagonal/iris/split/horizontal, optional text/sub/eyebrow |
| type | `words` 1–5 short phrases, `layout` stack/split/track, optional `sub`, `eyebrow` |
| lockup | `brand`, `sub`, optional `eyebrow` |
| all | `bg`, `fg`, `accent` RGB CSS hex/name, `grain` 0–2 |

Numeric motion tracks accept `[[0,value],[0.5,value,"out"],[1,value,"smooth"]]` normalized to the shot duration. Easing: linear/smooth/out/in. `spread`, `focus`, `reveal` 0..1; `yaw` −6.3..6.3 radians; `pitch` −1.5..1.5; `zoom` .4..4; pan −1..1. Frame samples are averaged in approximate linear light only for field. Proof uses a raster perspective transform; it does not fabricate UI states. Keep proof yaw roughly ±.5 for legibility. Never invent product functionality. `type` has fixed layouts; long words are fitted; test mobile readability and all lengths.  Render one still from a direct `{width,height,fps,shots}` plan with `render.py plan.json still.png --font ... --frame 15`; paths must be absolute in direct mode.

Prefer one substantial field assembly only when the story is aggregation, discovery or emergence. Choose wave for flow, burst for dispersion, helix for rotation, grid for organization. A field shape is not itself evidence. The formation can be reversed by reversing spread. Final camera at zero yaw/pitch makes glyph readable. If the image crop encompasses important small text, hold a readable crop before pulling back; avoid using zoom beyond native resolution for proof. Keep effects away from foreground text. At 1080x1920, 3600 particles and 2 samples may be CPU intensive; preview at 360x640, then rerender at native size. The tool does not provide full raytracing, depth-of-field bokeh, physics collisions or arbitrary mesh imports.
