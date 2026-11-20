> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Studio renderer v19 — headless actual 3D + editorial 2D
No GUI, Blender or reference video is required. Python, NumPy, Pillow, Numba, FFmpeg and a system TrueType/OpenType font are needed. Install missing dependencies only with permission; if Numba cannot import, use `material` or `cinematic` as a clearly identified 2.5D alternative. Numba first render compiles kernels and can take longer. Limit CPU e.g. `NUMBA_NUM_THREADS=4` on Linux or set environment variable on Windows. No font files bundled.

From skill root:
```bash
python scripts/doctor.py
python starter/unified/production.py examples/studio-v19.json --check
python starter/unified/production.py examples/studio-v19.json --preview
```
Use `--final` only with actual authorized voice file, final soundtrack and actual audio alignment. The included demo is fictional, with original synthesized tonal bed and SFX, no narration. The timeline is a starting test, never generic advertising proof.

## One shot in the unified timeline
```json
{"id":"hero","engine":"studio","frames":48,"content":{"kind":"hero","shape":"links","material":"chrome","roughness":0.06,"quality":1.0,"zoom":[[0,4.5],[1,2.2]],"pitch":[[0,0.15],[1,0.45]],"yaw":[[0,-0.3],[1,0.3]],"light":[[0,-0.4],[1,0.4]],"floor":false,"bloom":0.08}}
```
The project must be portrait 9:16. `quality` is internal CGI resolution ratio (.25–1); output UI and text remain full resolution. For final choose 1.0 where performance permits; avoid promoting an upscaled low-resolution CGI test as native. The internal rendered geometry is actual 3D signed distance geometry, not a flat texture. Lighting uses analytic environment strips and normal-derived reflected directions; floor uses a second ray. This is not global illumination/path tracing, dielectrics/glass, or mesh import.

| kind | parameters |
|---|---|
| hero | shape ring/links/wave/rounded; material chrome/ceramic/tinted; accent tints tinted material; roughness .03–.8; twist 0–.2 (wave); bloom 0–.4; quality .25–1; floor bool; optional text/sub; headline_position top/bottom; contrast_scrim 0–1 |
| kinetic | words array 1–5 strings max 30 characters; layout stack/carousel/cascade; optional sub |
| proof | src actual image path; crop [left,top,right,bottom] normalized 0–1; optional text/sub; brackets bool |
| lockup | brand required, sub optional |
All: bg/fg/accent CSS hex colors, grain 0–4. Hero camera tracks zoom (.4–10), panx/pany (lens-plane units), pitch/yaw/roll (object radians), orbit (camera radians), light (environment rotation radians). At least two strictly increasing normalized keyframes, beginning 0 ending 1. Each segment uses smoothstep. No arbitrary code evaluation. Motion does not imply genuine measured product capabilities.

For single-frame inspection create a standalone subplan `{width,height,fps,shots:[{kind,frames,...}]}` with an absolute screenshot path if any, then run `python starter/studio/render.py subplan.json still.png --font /your/local/font.ttf --frame 24`. For an actual user project copy the product screenshot into its folder and use relative `src` paths. Keep camera/floor geometry away from clipping, inspect frame 0, middle, last. Zoom above 4 is intentionally macro; no text overlay on unreadable product regions.

Rendering notes: reduce motion or crop if the hero is unreadable. For chrome use roughness .045–.12, preserve deep dark patches; ceramic .15–.35. Floor adds a reflective plane and a soft approximated contact shadow. Do not apply gratuitous bloom on UI. Use only one or two meaningful hero shots, offset their role (problem motif vs payoff). Most explanatory content uses real UI and type, not 3D. Avoid repeated rails, fixed header/footer metrics, generic center cards.

## Three creative starting structures
Use the scaffold only after you know the story, not instead of real copywriting. Styles: `fragmentation` (entangled-to-simple), `discovery` (strange detail-to-context), `precision` (careful editorial comparison). Choose for semantic fit, not randomness. Provide actual copy and screenshot. The command copies the screenshot into the working project and creates a draft; it never overwrites a project or inserts claims. Example:
```
python starter/studio/preset.py --style fragmentation --hook 'Too many tabs?' --word 'NOTES.' --word 'LINKS.' --word 'WORK.' --proof 'One workspace.' --brand FORM --cta 'Make room for your work.' --screenshot examples/assets/v15-workspace.png --out work/studio-draft.json --preview-resolution
python starter/unified/production.py work/studio-draft.json --check
```
Replace the illustrative story with the verified user product and align frames to the actual audio. The draft is intentionally silent until the agent adds approved sources. Three structures do not substitute for the existing other engines; use mixed shots when appropriate.
