# V30 — reusable optical shapes and uninterrupted handoffs

Use these controls on ANY project, in any part of a timeline, only if the glass clarifies the idea. The FORM cut is an authored example, not a mandatory design. A lens samples whatever is drawn beneath it at the current time. Render UI first, lens next, foreground text last. It is an affine 2D approximation, not a 3D glass mesh. The `mesh` layer is a separate true triangle renderer (ribbon, knot, sheet, imported triangulated OBJ).

## Reusable glass layer

```json
{"id":"inspect","kind":"lens","active":[0,3],"x":[[0,180],[3,540,"sine"]],"y":640,"w":310,"h":165,"shape":"capsule","rotate":[[0,-22],[3,18,"sine"]],"strength":0.13,"dispersion":0.007,"frost":0.8,"tint_mix":0.04,"color":"#dcefff","shine":0.55,"edge_feather":1.5,"radius":0.35}
```
Shape: `roundrect`, `ellipse`, `diamond`, `squircle`, `capsule`. Use equal w/h for circles. Capsule retains semicircular ends in local coordinates. Shape and tint color static; strength, dispersion, frost, tint_mix, shine, light (radians), radius (normalized roundrect corner), edge_feather (design pixels), x, y, scale and rotation support tracks. Rotation and affine parent transforms affect sampling and outline. Width and height are static; animate scale_x/scale_y for size changes. Frost is Gaussian blur in design pixels, not physical rough glass. Lens does not support matte/3D perspective or blend modes. Older lenses without a shape keep their historical implementation exactly. Reasonable presets: clear (strength .13, frost 0, tint_mix .04); frosted (.04, 4, .15); prism (.18, .2, .04, dispersion .019). Multiple lens passes in order distort the accumulated image, so avoid excessive stacking. Glass is optional, not brand identity.

## Transition discipline
Use a single moving reveal in which incoming content arrives while outgoing content still exists. Avoid staging separate black backgrounds, mesh opacity fades and titles in consecutive nonoverlapping steps. Start incoming CGI on its actual first visible frame; expand its feathered aperture, keeping outgoing layout in motion until covered. Let typography clear the aperture. Align the next proof reveal to the still-moving hero and only then end it. Do NOT use this exact iris for every transition; choose the mask that follows the previous object or action. Use clean cuts when they express a deliberate visual accent. Inspect a 1–2s strip around each handoff at target cadence.

## Reproduce V30
```
python starter/composite_film/demo_compile.py work/base
python starter/composite_film/continuity_compile.py work/base/timing.json work/v30/plan.json
python starter/composite_film/mix_picture.py work/base/mix.wav work/v30/plan.json work/v30/mix.wav
python starter/composite_film/compositor.py work/v30/plan.json work/v30/render --size 720 --audio work/v30/mix.wav
```
Actual FORM preview retains V29 audio and revises the middle interval. Whole timeline above is editable and independently renderable. For another script write a new layer graph, don't use this fixed cue mapping. Run `python -m unittest discover -s tests -p 'test_v30.py'`.
