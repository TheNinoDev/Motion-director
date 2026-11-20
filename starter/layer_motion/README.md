> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Layer Motion v14 — one continuous, configurable scene

Prefer this backend when product panels, text, graphics, masks and camera movement must coexist. No UI editor, no references, no engine coding. It is a CPU 2D / perspective-plane compositor, not true 3D. True extruded geometry remains in scene3d; use that for brief CGI hero shots.

## First run (skill root)
```
python starter/unified/production.py examples/layer-showcase-v14.json --check
python starter/unified/production.py examples/layer-showcase-v14.json --preview --build-dir work/layer-demo
python scripts/visual_review.py work/layer-demo/picture.mp4 work/review
```
Use output path printed by production controller if it differs. The supplied concept is fictional, silent and not evidence of a real product. Set width/height to 540/960 for draft; 1080/1920 for final. Font is system default or user-supplied, not bundled. Requirements Python, Pillow, numpy, opencv-python(-headless), FFmpeg, ffprobe.

## Schema
Use v13 `version:1` unified timeline, `engine:"layers"`, `frames`, `content:{background,ambient,camera,layers}`. Each shot is independent; keep a continuous sequence within one layer shot to preserve identities. Units: 1080x1920 canvas coordinates regardless of actual raster. `x,y` refer to layer center. `size:[w,h]` is unscaled sprite dimensions. Array order is back-to-front (explicit z-order). Time is local frames. `start` inclusive, `end` exclusive. Each numeric animated property can be a scalar or an ordered array `[[0,v],[18,v,"out"]]`. Keyframe easing belongs to destination: linear, out, in, inout, back, hold. Duplicate keyframe frames invalid. `scale` uniform, `sx/sy` anisotropic, `rotation` degrees, `tilt` perspective yaw degrees. `depth` sets camera response (0=HUD, .25 background, 1=hero). Camera x/y offset and zoom may use same keys. `opacity`, `reveal` 0..1; mask axis x, y, radial, diagonal, dissolve. `blur` sigma in design pixels, `glow` strength 0..2, `glow_color` hex, `shadow` 0..1, `trail` 0..1 uses previous anchor position, `metal` stylized light sweep mix 0..1. Use `#RRGGBB` or `#RRGGBBAA`. `ambient:{color,strength,x,y}` is optional static radial light. `kind:text` needs text, font_size, optional spacing, align left/center/right; auto-fit inside size, use intentional line breaks. Kinds rect (radius/stroke/stroke_width), line, ring (stroke_width), image (src relative to project, radius), grid (step/dot), gradient (radial emissive fill), particles (seed,count). Particles are deterministic flat sprites; animate the field through transforms. No physics simulation. Perspective layer is a plane, not solid volume. Mask is a visibility wipe, not real morph. Trail is a directional echo, not physically integrated shutter.

## Recipes ready to paste
- **Macro reveal:** screenshot center same anchor, `scale:[[0,2.4],[25,1,"inout"]]`, `tilt:[[0,-22],[25,0,"out"]]`, shadow .65. Add copy layer with `start:15`, `reveal:[[15,0],[29,1,"out"]]`; check crop and actual UI.
- **Layered contrast:** one persistent panel, dark grid at depth .15, ring at .55, panel at 1, HUD at 0. Camera pan 60 px over 40 frames. Never move all at identical speed.
- **Click echo:** ring center on verified control, `scale:[[0,.25],[14,1.5,"out"]]`, `opacity:[[0,.9],[14,0,"out"]]`, `glow:.3`; keep the cursor separately and swap to actual result screenshot immediately after click.
- **Light sweep without rotation:** metal .65 on single hero text, rest static. Animate blur only in background when foreground proof enters; don't blur all.
- **Diagonal match:** old panel contracts into persistent square or ring, next panel grows from same anchor with diagonal mask, 12–18 frames. Use simultaneous exit entry only for 4–8 frames if legibility survives.
- **Type track:** split sentence into 2–5 text layers, each with fixed preplanned box and actual verified word/phrase reveal key. Do not auto-center a new sentence every word. Use `type_motion/align.py` for verified timing.
- **Controlled dissolve:** decorative grid/particles with `reveal_axis:"dissolve"`, reverse reveal from 1 to 0 over 14 frames. Never dissolve detailed proof while viewer needs to read it.
- **End reset:** all nonessential layers off; wordmark and CTA clean, lock position for >=1.5s in final. Shipped six-second smoke demo has a shorter end for capability demonstration only.

## Debug without user labor
Run --check then render low-res. For specific frames call the backend directly with generated `build/plans/<id>.json`, `--font` existing local font and `--frame 42`; output PNG. If an effect hides the focal point, isolate that layer in a copy. If text too small, use fewer words and bigger box. If card movement makes UI illegible, lock tilt at 0 during proof. If screenshot missing, use documented product evidence, not fictional proof. Validate and re-render only changed shot via controller cache. Check source image resolution >= its largest on-screen presentation. Never claim that selective lights, echoes or analytical masks are physically correct CGI.

## V15: actual shape morphs, persistent particle animation and subframe exposure

No old plan needs changes. New `content.samples:1..8` and `content.shutter:0..1` integrate full scene samples at fractional frame instants in linear light. Defaults 1 and .5 preserve V14 rendering. 2–4 exposure samples are useful for fast transitions; no need to supersample static scenes. The shot bounds are clamped; exposure does not cross a hard cut.

```json
{"id":"anchor","kind":"morph","size":[820,820],"x":540,"y":960,"color":"#ffffff","from":"circle","to":"square","progress":[[0,0],[24,1,"inout"]],"outline":8,"edge":1.3}
```

`morph`: circle, square, diamond, star, ring, cross, text; `text` for target text and optional `from_text` for source text. Signed-distance fields are interpolated continuously and their zero level is rendered as the boundary. `outline` is thickness in design pixels; zero gives filled shape. `edge` is antialias width. Some topology-changing pairs can pinch or vanish mid-morph, so review midpoint. This is genuine continuous 2D mask geometry, not a vertex/mesh morph or 3D.

```json
{"id":"field","kind":"swarm","size":[900,900],"x":540,"y":960,"from":"grid","to":"text","text":"FORM","count":450,"dot":4,"arc":0.25,"scatter":0.06,"drag":0.4,"seed":16,"color":"#c5ef78","progress":[[0,0],[26,1,"inout"]]}
```

`swarm`: grid, ring, scatter, text, spiral. 8–1500 deterministic persistent particles; `arc` and `scatter` control curved paths; `drag` attenuates arc. This is analytic choreography, not collision, fluids or rigid-body physics. Use same `seed` for reproducibility. Form wordmarks with solid text afterwards; particles alone may be illegible. Apply existing layer transforms, glow, shadows, parallax and masks as appropriate. See `starter/choreography/README.md` for a complete project. For real 3D use `scene3d` or other documented verified engines. Do not claim photorealism.
