> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V27: persistent layer compositor

This runtime is a freely authored graphic timeline, not another fixed shot preset. Use it for bespoke edits with persistent object IDs, groups, independently animated masks, pictures, type, real mesh inserts and sound cues. It does not require NOIZ or GUI tools. Existing unified engines remain available for specialized shots. Run from the skill root with Python, NumPy, SciPy, OpenCV, Pillow, FFmpeg and optional Numba for mesh. Locate system fonts or use licensed product fonts; no fonts shipped.

## Start here (working 24.1-second fictional film)
```
python starter/composite_film/demo_compile.py work/composite
python starter/composite_film/compositor.py work/composite/plan.json work/composite/render --size 540 --audio work/composite/final-mix.wav
python scripts/motion_cadence.py work/composite/render/film.mp4 work/composite/cadence.json
```
The compiler generates scratch audio and an editable **example**, not a universal script generator. `--voice-dir` takes one verified phrase file per line, `00.wav` etc.; `--music` takes an authorized file at least as long as the edit. Preserve original VO and track. For a real continuous voice take, use provider timestamps or forced alignment, and build the JSON directly from the resulting cue sheet; don't demand manual splitting from the user. The example uses measured audio durations, not word timestamps. It measures soundtrack onset candidates. Neither these nor the synthetic audio prove professional voice performance or musical quality. Use actual audio and release gates for publication.

## Author a new film without new rendering code
Timeline root: `version:1`, `width`, `height` (even 9:16), `fps` (24/25/30/60), `duration` in seconds, `background`, `layers` array in back-to-front order. All positions are design units on 720x1280 regardless of export resolution. Times are **global seconds**, `active:[start,end]` half-open. Unique IDs. Keep persistent layers alive across beats rather than restarting identical clips. A layer's center is its pivot; coordinates in a child group are relative to its parent's origin. Group must precede children. A parent transforms position, rotation and scale and multiplies opacity. 3D mesh is a rectangular render pass, not an alpha-isolated cross-layer depth buffer.

Layer types:
- `group` — nested parenting. Set `x`, `y`, `scale`, `rotate`, `opacity`.
- `text` — `text`, `size`, `font` (bold, heavy, regular, mono), `maxw`, `color`; set root `fonts` to file paths for brand fonts. `material:metal`, `light` and `bevel` create stylized moving bevel shading (not physical metal). Use `recipes.staggered_line` for Latin-character stagger with reserved positions. Whole-line masks for scripts requiring shaping.
- `rect`, `ellipse`, `line` — w/h, radius (rect), stroke, color. `line` is a narrow rectangle; for diagonal and curves use `path`.
- `image` — src relative to plan or absolute, w and optional h (aspect ratio inferred), optional normalized crop. Use real product screenshots; preserve original capture.
- `path` — w/h, points in local units, stroke; `trim` 0–1, `points_keyframes:[[sec,points],...]` with equal point count. `recipes.bezier`, `resample`, `morph_path` are supplied; matching orientation/start point is necessary to prevent folding. This is a 2D path morph, not arbitrary topology morphing.
- `mesh` — w/h and `mesh` config with validated normalized tracks from mesh_motion README, optional source. Existing depth-tested triangle renderer; background is opaque. For an actual 3D rendering alpha pass use an external authorized source and extend runtime or precompose.

Properties can be static numbers or `[ [seconds,value], [seconds,value,"easing"] ]`, with strictly increasing times. Easing is incoming (`linear`, `in`, `out`, `smooth`, `sine`, `quint`, `hold`); values outside endpoints hold. Supported channels: x,y,scale,scale_x,scale_y,rotate (degrees), opacity,reveal (vertical wipe), pitch/yaw (degrees planar perspective), blur, light, trim, glow, mask_progress. Match velocity at boundaries; for persistent movement linear tracks across cut, quint for deliberate start/stop. No repeated automatic easing on every sentence.

Masks: `mask:iris|wipe|diagonal|shutter` with `mask_progress`, or `matte:<earlier layer id>`, `matte_mode:alpha|alpha_invert|luma|luma_invert`. A matte can be hidden from normal compositing with `matte_only:true`. Use a matte to fill lettering with live imagery or reveal a moving window. Mattes do not chain recursively; do not use a matte source that itself depends on a matte. `blend:normal|screen|add|multiply`; `glow`, `glow_color`, `blur` are per layer. RGB premultiplied before warp; screen composite is in display space. Shutter exposure uses approximate gamma-to-linear integration. Enable `shutter_windows:[[start,end],...]`, `shutter:.4`, `--samples 2` or `3` to evaluate multiple full frames near fast animation (not duplicate/interpolated frames). Texture quality scales with export. Use sharp proof and subtle FX: no global blur on readable text.

```
python starter/composite_film/compositor.py starter/composite_film/technique-demo.json work/mattes --stills --size 540
python starter/composite_film/music_cues.py work/song.wav work/music-cues.json
python starter/composite_film/mix_picture.py work/mix.wav work/plan.json work/final-mix.wav
```
The SFX tool uses `sound_events:[{"time":3.2,"kind":"whoosh","gain_db":-23,"duration":.32,"pan":0}]` (six types from sound_design). Actual onset candidates are positive spectral flux peaks; snap only small nearby visual accents, preserve spoken intent. Onsets are not a verified beat grid; estimate tempo/downbeats separately and audition. Do not quantize narration to guessed beats.

## Render and quality
At commissioning time use 1080x1920 and test 30 or 60 fps. Start with stills (`--stills`) and inexpensive draft. For expensive CGI use short tests and existing unified/cached shot engine for long clips. Full 720 with double sampling exceeded this environment's time budget; the optimized 540/30 single-sample preview completed. Never distribute `.partial.mp4`. Render native when resources permit; do not upscale and claim native. Check actual video using FFmpeg decode and frame counts, measure audio and do human/agent visual and listening review. No independent weak-model quality benchmark yet. See guide 63.
