> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# GUI-free procedural real 3D, v9
Use `starter/scene3d/render.py` as the primary CPU path. The agent writes JSON, not Blender scenes or shaders from scratch. It uses real triangulated extruded letter meshes including holes, small bevels where valid, repeated instances, depth-buffered rasterization, true perspective camera, frame-indexed transforms and procedural environment-like specular highlights. It does NOT simulate physical inter-object reflections, shadows, path tracing, ambient occlusion, motion blur, depth of field, skeletal animation or full 3D mesh import. No claim of cinematic photorealism. The optional WebGL file is experimental: environment could not create WebGL2 in the release test, so use CPU path. No GUI or GPU required.

## First run
From skill root, locate an installed usable font (Linux `fc-list`; Windows inspect `C:\Windows\Fonts`), verify `ffmpeg` and `ffprobe`. Use Python 3.10–3.13 where compatible wheels exist. Install dependencies in an isolated venv if allowed: `python -m pip install numpy Pillow opencv-python-headless 'shapely>=2.1' numba`. On Windows use double quotes for version spec. Do not install automatically if restricted. The CPU engine needs Numba JIT support and a writable temporary/cache location. No actual font files included.
```
python starter/scene3d/render.py starter/scene3d/demo.json work/cgi.mp4 --font /path/to/font.ttf --preview-dir work/cgi-stills --supersample 2
```
The demo is intentionally 360x640, 30fps, 180 frames, six seconds, no audio, illustrative AXO letters and FORM word. It is not a finished advertisement. Inspect stills and decoded motion. For actual final, adapt dimensions and duration to locked audio, run small previews first, then use 1080x1920 if resources permit. Supersampling 2 costs 4x pixel work. CPU rendering is much slower at high instance counts; reduce glyph complexity, count or resolution for drafts. 10,000 is validator max, not a tested throughput target; tested demo uses up to 576 instances. Choose existing 2D tools when this fails.

## Exact plan contract
Root: even width/height; positive fps; optional `depth`, `bevel`; `scenes` ordered and adjacent, `start` inclusive, `end` exclusive. Each scene needs `layout`, `count`, ASCII `glyphs` (no whitespace), `eye_from`, `eye_to` (three world coordinates). `to_layout` optional: uses same stable ID and smoothstep, positions never randomly change over frame time. `target_from`, `target_to` default [0,0,0]. `size` sets glyph height; `radius`,`height`,`turns`,`tube`,`per_ring` configure layouts. `spin` radians across shot, `orbit` rotates centers, `random_rotation` radians amplitude, `size_variation` fractional amplitude, `seed` for CPU randomness. `fov` vertical degrees default 42, `roughness` 0–1 controls highlight spread (not physical material), `tint` RGB 0–1, `light_phase`/`light_sweep` independent radians. Avoid camera straight up/down or crossing its target, collision with geometry, zero/negative dimensions, NaN. Camera near-plane intersections may drop triangles; test, change camera path, not a complete clipping renderer.

| Layout | Meaning |
|---|---|
| grid | evenly spaced planar rows |
| helix | three intertwined coils aligned top to bottom |
| torus | sampled doughnut surface |
| tunnel | repeated circular rows along Z |
| sphere | golden-angle sphere samples |
| scatter | seeded 3D random positions |
| custom | exact array of count XYZ triples in `points` |

## Shape generation
Generate text or image silhouette with `silhouette.py`; white foreground, black background, no transparent ambiguity. The optional `--depth` gives planar sample thickness, not a full model. Add returned JSON array into `points`, match `count`. Use `layout: scatter`, `to_layout: custom` or reverse. Avoid overlap: instance size ~0.10–0.18 for 560 points over width ~5.3. For wordmark hero endpoint use the user's authorized vector or actual clean text instead of leaving particle letters hard to read. For arbitrary mesh silhouettes sample a licensed model externally; no mesh importer supplied.
```
python starter/scene3d/silhouette.py --text BRAND --font /path/to/font.ttf --count 560 --width 5.3 -o work/points.json
```

## Shot integration (do not reinvent pipeline)
1. Lock audio and shot frames as existing guides describe. Mark scenes needing CGI (usually at most two sequences).
2. Write JSON for each CGI shot separately. Render a few frames or short low-res clip. Inspect all key stages; reject dark unreadable shapes, midpoint collapse, aliasing, clipped hero, collisions and indistinct metal. Move camera/light and lower density before adding effects. Do not expect full UI or logo overlays from this renderer.
3. Render clean layer and overlay exact captions via existing `starter/ui_engine/render.py` or FFmpeg. Match frame count, canvas and audio. Compose original product UI with previous browser capture tools. Stitch via `starter/ui_engine/stitch.py`; use aligned final mix, don't repeat audio or stretch frames.
4. Export production assets and JSON plus final release gate. Inspect actual MP4; valid decoding does not mean good art.

## Errors and fallbacks
- Shapely constrained triangulation missing: isolated environment with >=2.1 or skip mesh and use previous 2D text layers. Never fake success.
- `Invalid contour`: select a simpler bold font; check glyph support, change depth/bevel. Some glyphs cannot be reliably generated by contour rasterization; log if bevel dropped. ASCII chars are accepted but not all fonts/glyphs proven.
- WebGL unavailable: use tested CPU renderer. Do not spend time on driver installs or GUI. Optional `render_webgl.py`/`engine.html` only after local smoke test and with caveat that CPU/JS random positions differ.
- Complex hand, watch, character or curved text: custom silhouette primitive only if design benefits; use pre-existing authorized rendered asset, or simplify to abstract shape. Do not claim exact full clip reconstruction.
