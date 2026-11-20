# V28 optical compositing additions

Backwards compatible with the V27 timeline format. Run `compositor.py` as before. No new dependencies.

```json
{"kind":"gradient","id":"field","active":[0,4],"w":720,"h":1280,"x":360,"y":640,"stops":[[0,"#111321"],[0.5,"#363950"],[1,"#0c0c14"]],"angle":70}
```
Static multistop gradient with usual transforms, masks, opacity and blending. Stops ordered in [0,1], angle degrees. For color animation use two layers with animated opacity.

```json
{"kind":"lens","id":"inspection","active":[0,4],"w":240,"h":260,"x":[[0,140],[4,580,"quint"]],"y":640,"strength":0.18,"dispersion":0.012,"radius":0.30,"shine":0.65,"light":[[0,0],[4,3.14,"linear"]],"color":"#dee8ff"}
```
Optical adjustment samples the already-drawn composition in its local rectangle. Order it above affected layers and below titles that need to remain sharp. `strength` and `dispersion` are fractional displacement coefficients; `light` radians; `shine` rim intensity. Rounded corners are normalized (`radius` 0.02–0.95). Keep strength near 0–.3, dispersion near 0–.02, shine near 0–1. Lens is axis aligned, no alpha matte or external blend; its bounding size and position inherit group transform. It is approximate optical displacement, not physically based CGI.

Add `"velocity_blur":0.6` to a translating drawable layer. Five samples of its premultiplied texture are composited along measured global translation; blur extent capped at 48 output px per axis. It is inexpensive compared with full scene temporal supersampling; it does not include spinning or scaling motion. Use `--samples 2` with explicit shutter windows for those motions.

Text: `"outline":2` (inner outline in design pixels). Tracks: incoming `"back"` overshoots then settles. Never use back easing to overshoot opacity or unbounded camera positions; use it on scale/position deliberately.

## Reproduce authored full cut
From root (requires local scratch TTS as documented in story film or supplied audio):
```
python starter/composite_film/demo_compile.py work/base
python starter/composite_film/premium_compile.py work/base/timing.json work/recut/plan.json
python starter/composite_film/mix_picture.py work/base/mix.wav work/recut/plan.json work/recut/final-mix.wav
python starter/composite_film/compositor.py work/recut/plan.json work/recut/render --size 720 --audio work/recut/final-mix.wav
```
The recut is designed for the specific eight-phrase scratch timeline (`premium-timing.json`), and uses authored sub-beat offsets. For custom source audio, use the compiler as a readable example and adjust offsets or author JSON directly; do not blindly retime an unrelated script. No professional voice is bundled or claimed. Use actual authorized voice/music for release. The one CGI ribbon is generated with the existing mesh engine. No GUI or reference footage is required.
