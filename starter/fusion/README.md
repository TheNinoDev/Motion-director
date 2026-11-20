> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Fusion 20 — form transformation, material and editorial bridging

GUI-free. Python, Pillow, NumPy, Numba, FFmpeg, OpenCV (bloom), system font. Do not install silently. First compile may take tens of seconds; afterwards Numba caches generated machine code. Cap threads to 4 if CPU-constrained, e.g. `NUMBA_NUM_THREADS=4` on POSIX, `$env:NUMBA_NUM_THREADS="4"` in PowerShell. No bundled fonts or reference clips.

From the skill root:

```sh
python starter/unified/production.py examples/fusion-v20.json --check
python starter/unified/production.py examples/fusion-v20.json --preview
```

The example is a fictional workspace study with generated scratch soundtrack, not a commercial release. For a new plan:

```sh
python starter/fusion/preset.py --style consolidate --hook "Where did it go?" --word LESS --word NOISE --proof "Your saved work." --brand FORM --cta "Open your workspace." --screenshot work/product.png --frames 48 30 84 60 --out work/fusion.json
python starter/unified/production.py work/fusion.json --check
python starter/unified/production.py work/fusion.json --preview
```

Use copy and real screenshot of the commissioned product, not the fictional example. Supply shot lengths based on actual audio/phrase cues. The controller verifies files, caches shots, supports audio and transitions. The CLI `render.py` also accepts a direct `width,height,fps,shots` plan with absolute image paths and `--font` and optional `--frame N` (first shot only).

## JSON contract (content in unified shot)

| Field | Values / behavior |
|---|---|
| kind | morph (CGI + optional text), bridge (CGI to actual screenshot), type (editorial words), lockup (brand) |
| shape | tiles (fan→merged rounded panel), ribbon (twist→flat), cube (cube→sphere), aperture (rounded frame→circle), capsules (three pieces→one) |
| material | chrome, ceramic, anodized, glass (approximate two-interface refraction), obsidian |
| phase | 0..1 morph progress, static or keyframes; reverse with 1→0 |
| twist | 0..2.5, ribbon twist, static or keyframes |
| quality | .2..1 internal render scale; native UI/type is always output resolution. For final aim .85–1 after a test |
| samples / shutter | 1..4 temporal CG samples, exposure fraction 0..1. Two samples with .5 shutter is starting point; average linear radiance before tonemap |
| roughness / ior | .03..0.65, 1.05..2.2; IOR affects glass only |
| pitch,yaw,roll,orbit,light | radians; independently animatable -6.3..6.3 |
| zoom,panx,pany,elevation | .5..9, -0.7..0.7, -0.7..0.7, -2..3. Pan is lens shift, not object position |
| exposure / bloom | .2..3 linear exposure, 0..0.6 bloom on bright CGI only |
| bg,fg,accent,tint | CSS color names or hex; use real brand colors |
| floor | boolean; approximate planar reflection and analytic contact darkening |
| guides,eyebrow | optional intentional editorial labels and progress (never imply measured product metrics) |
| src,crop | required image for bridge; normalized [left,top,right,bottom] ROI; actual product evidence only |
| mask,reveal_at | rounded / iris / split / diagonal; .08..0.72 normalized onset. Screen-space matte, not physical projection onto mesh |
| words,layout | type: 1..4 short terms, stack / mono / stripe |
| text,sub,brand | optional short headline/subtitle; brand required for lockup |

Any of the 12 named numeric motion tracks supports scalar or `[[0,value],[0.4,value,"out"],[1,value,"smooth"]]`; allowed easing: linear/smooth/out, incoming segment. Use one dominant movement. Phase is actual implicit geometry, not an image blend. At phase 1 smooth union merges intersecting components. Glass traces an entry and first exit then samples an analytic studio environment; no full internal bounces, caustics, external objects, arbitrary meshes or volumetric simulation. Reflections are analytic, not HDRI captures. Inspect every chosen geometry at 0, .5 and 1. Use small motion rather than excessive angles. Sharp UI should not be blurred by CGI shutter.

## Candidate board (no creative guessing required)

```sh
python starter/fusion/style_board.py work/board.jpg --shape ribbon --material chrome --material glass --material ceramic --font /path/to/installed-font.ttf
```

Renders a 3-phase grid of actual images for each selected material. Inspect the board, choose coherent material and geometry, then edit the project. This is a fast low-resolution diagnostic, not a final-quality still. Re-render close-ups at final scale. `study_audio.py` generates an original synthetic test bed at the example's cut times; use actual audio for commissioned video instead. It is intended for hard-cut study plans and does not account for transition overlaps.
