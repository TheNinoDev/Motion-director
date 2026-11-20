# V29 — projective shutter and selective finishing

Use the persistent V27/V28 compositor. No new dependencies. These features are optional and previous projects remain unchanged without them. Keep artwork and proof sharp at rest; do not enable blur/shadows on every layer.

## New layer options

- `projected_blur`: 0–2 frame shutter width. When a projected corner moves more than 0.7 output pixels across the exposure, the renderer averages five premultiplied homographies. Includes inherited translation, rotation, scale, yaw and pitch. Does not sample changing texture content or opacity, and is not physical camera exposure. Supersedes `velocity_blur` for that layer. Whole-composition temporal sampling is still available for animated mattes and CGI.
- `shadow`: true on a drawable. `shadow_opacity` (0–1), `shadow_blur` (design px Gaussian sigma), `shadow_x`, `shadow_y` (px) may be keyframed. `shadow_color` is static. Gaussian shadow uses the actual masked alpha, never a fixed rectangular plate. Avoid extreme values; recommended 8–30 px blur and .12–.35 opacity. Not a physically cast 3D shadow.
- `mask_feather`: normalized transition width between 0 and 1, default .025. Applies to iris, wipe, diagonal and shutter masks. Values .03–.10 are usually sufficient. Final progress 1 is fully revealed.
- incoming ease `spring`: damped overshoot, suitable for position/rotation/scale. Do not use on opacity or on proof that needs precise seating with no overshoot. Keep small movements understated.
- Thin rectangle rasterization no longer fails at small render sizes.

Example:
```json
{"id":"card","kind":"rect","active":[0,2],"x":360,"y":640,"w":550,"h":320,"color":"#e1f6a4","radius":20,"rotate":[[0,-24],[0.65,0,"spring"]],"scale":[[0,0.6],[0.65,1,"spring"]],"projected_blur":0.7,"shadow":true,"shadow_opacity":0.25,"shadow_blur":20,"shadow_y":15}
```

## Synchronize independent accents to measured soundtrack transients

```
python starter/composite_film/music_cues.py work/music.wav work/cues.json
python starter/composite_film/cue_align.py work/plan.json work/cues.json work/bindings.json work/aligned.json --window 0.09
```
`bindings.json` is an array such as `[{"layers":["group-id","child-id"],"anchor":5.4,"sound_indices":[2]}]`. Include all parent/child/matte dependencies in the same binding. Choose only optional independent accents, never proof reading holds, speech or locked semantic timing. The tool moves selected layer lifetimes and keyframe times together by a bounded whole-frame offset, keeps all other layers unchanged, optionally moves designated SFX events, and writes an alignment report beside the candidate. It refuses incomplete dependency groups and leaves content outside the picture range unmoved. The measured onsets are not necessarily the beat grid; listen and review before accepting. Audio is not time-stretched.

## Reproduce the 24.1-second full fictional study
```
python starter/composite_film/demo_compile.py work/base
python starter/composite_film/refined_compile.py work/base/timing.json work/refined/plan.json
python starter/composite_film/mix_picture.py work/base/mix.wav work/refined/plan.json work/refined/final-mix.wav
python starter/composite_film/compositor.py work/refined/plan.json work/refined/stills --stills --size 540
python starter/composite_film/compositor.py work/refined/plan.json work/refined/render --size 720 --audio work/refined/final-mix.wav
```
The compiler is a hand-authored edit of the specific eight-phrase FORM scratch script only. For a different story, use the graph syntax and selected ideas instead of substituting a brand name. The preview is deliberately a refinement of V28, not a professional voice demo. Use authorized actual voice and soundtrack for release. Style references are not required.
