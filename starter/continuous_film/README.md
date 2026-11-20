# V26 / Continuous composition route

Use this when an earlier film looks choppy, repetitive or like a template. This is an alternative to the full kinetic film and unified engines, not a replacement. The example is fictional, not a real product ad. It is deliberately a single narrative motif repeated with changing context, not a universal preset.

```sh
python starter/continuous_film/render.py starter/continuous_film/demo.json work/film --size 720 --stills-only
python starter/continuous_film/render.py starter/continuous_film/demo.json work/film --size 720
python scripts/motion_cadence.py work/film/film.mp4 work/cadence.json
```
For native delivery choose `--size 1080`; test runtime first. `--fps 60` is optional, substantially more expensive, and not required for smooth motion. `--samples 2` or `3` applies approximate shutter integration only at non-cut boundaries. At 30 fps the transition lasts 6 frames; at 60 fps 12 frames. The 720px/30fps demo was completed; 60fps full render exceeded the environment time budget. Do not use partially written MP4. Use `--voice-dir work/phrases --music work/song.wav` for authorized real audio. The included local voice/music are scratch only. Real phrase timing must be checked against the supplied voice.

The JSON takes the same input asset/font locations as kinetic_film, with 4 `items`, 4 normalized `proof_crops`, and each `beats` entry containing `voice`, `min`, `kind`, `text`, optional `transition` (`cut`, `push`, `aperture`, `blend`), plus optional `paper` color. The seven scene kinds: `gesture` (original request and first attachment), `proliferate` (staggered attachment formation), `fold` (projected crop cascade), `compress` (shared-anchor collapse and full-bleed color reveal), `proof` (continuous actual UI reframing), `track` (move actual camera between two product details), `return` (narrative callback and lockup). In `gesture`, ` / ` splits headline lines. Configure brand and proof, not the original example text. The four-item assumption is explicit: for a story with another number of objects, use the unified layer/choreography routes rather than faking four.

All outgoing and incoming frames are independently evaluated through a transition. The transition begins before the next phrase boundary and incoming playback continues from its already-revealed time rather than starting over. The incoming shot is gently retimed over its allocated duration; no voice stretch. Cuts remain intentional. No frame interpolation or optical flow synthesis is required. This is not physical motion blur; it is a small multi-sample exposure approximation. Use real word times when refining timing of action; the basic demo is phrase timed.

For a revision, preserve unaffected work. Test original versus candidate at playback speed and sample frames at 0.1 s around boundaries. Mark technical flags only as flags, not proof that a creative cut is wrong. Do not export until all relevant release checks pass.
