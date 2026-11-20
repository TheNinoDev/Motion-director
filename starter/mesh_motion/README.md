> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Mesh Motion V23 — real smooth 3D without a GUI

Use `engine: mesh` inside a unified version-1 plan. Python, NumPy, Numba, Pillow, OpenCV, FFmpeg. No external reference videos, browser GPU or Blender necessary. The rasterizer uses a depth buffer and perspective-adjusted barycentric interpolation of normals, positions, and UVs; analytic environment lighting approximates studio softboxes. This is not a path tracer.

```sh
python starter/unified/production.py examples/mesh-v23.json --check
python starter/unified/production.py examples/mesh-v23.json --preview
```

## Options

- `kind`: `ribbon` (flattened twisted toroidal tube), `knot` (round linked path), `sheet` (continuous two-dimensional surface in 3D), `obj` (single triangulated local OBJ mesh). `material`: `chrome`, `satin`, `ceramic`, `ink`; `texture` only for `sheet`. OBJ importer ignores materials, UVs and rigging; uses averaged vertex normals. No topology morphing or collision simulation.
- `src`: local authorized image for textured sheet, or triangle-only OBJ. `crop`: normalized `[left,top,right,bottom]`; use actual product evidence. Never source code or a URL in this field. `phase`: 0–1 (opening/reveal state); `bend`: -2.4..2.4 radians; `twist`: -3.2..3.2; `yaw`, `pitch`, `roll` are radians; camera-style `zoom` .45–2.4; `panx`, `pany` normalized screen offsets; `light` angle; `roughness` .05–.85. Tracks use `[normalized time, value, incoming easing]` with 0 and 1 endpoints. Modes linear, smooth, in, out. Static numbers also accepted. Positive pan y moves down. OBJ only rotates/scales; phase/bend/twist do not deform it. Ribbon/knot use phase/twist, not bend. For sheet phase changes lighting, bend/twist determine geometry.
- `resolution`: 24–160 (mesh longitudinal subdivisions); `quality`: .4–1 internal raster scale; `samples`: 1–3 temporal samples and `shutter`: 0–1 frames. `bloom`: 0–.25; `grain`: 0–2. `bg`, `fg`, `accent`, `tint` hex colors. `label`, `title`, `caption` optional static overlays. Prefer no overlays on macro shots and use other typography engine for animation. Set quality 1 for sharp actual product evidence. Use an unwarped UI shot afterward for legibility. Native delivery raster from parent plan.

## How to choose

Metal ribbon: one metaphor for a tangled or unfolding idea; use a close angle first and reveal the silhouette. Sheet: transition from abstract graphic to a real product screenshot; set bend/twist/yaw/pitch/roll to 0, phase to 1 and hold the flat plane for reading. OBJ: only if supplied/licensed and already triangulated. Use one or two CGI shots, not an entire CGI film. Avoid default rings unless semantically relevant. Reuse shape/color/anchor across adjacent beats. Match connection with an actual cut on a shape or movement, not an arbitrary transition. A cut to flat UI is better than holding deformed copy.

## Troubleshooting

- Strange shimmer: increase resolution, roughness and quality; reduce twist/light speed; inspect direct intermediate frames.
- Unreadable texture: lower bend/rotation, phase=1 by end; enlarge salient crop or use separate native UI detail. Never claim the screenshot itself is interactive.
- Jagged edges: full raster and slower movement; optional temporal samples. No MSAA on stills.
- Invalid OBJ: triangulate externally with an authorized command line tool or choose a packaged shape. No untrusted material script execution. Importer caps 50k vertices / 80k faces.
- Test candidate stills at 0, .5, 1 before rendering; compare actual motion. Don't claim physical glass/reflection or professional quality from technical tests.

Quick generation and actual candidate comparison:
```
python starter/mesh_motion/preset.py sheet work/surface.json --asset path/to/screenshot.png --frames 60 --crop 0 0 1 1
python starter/unified/production.py work/surface.json --check
python starter/mesh_motion/style_board.py examples/mesh-v23.json work/board.jpg --font /path/to/authorized/font.ttf --shot ribbon
```
The generator copies the local asset into the project. The board uses three actual moments per candidate; it cannot rate beauty. Keep the selected parameters in the one unified film and set its duration to actual voice/beat timing.
