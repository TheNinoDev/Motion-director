> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Story Film v24 — end-to-end narrative build, GUI-free

This is a complete, editable 35-second fictional product study rather than a 6-second effect reel. It deliberately has a single story: fragmented links → presentation problem → one place → verified product detail → callback. Use the sequence as a technical starting point, never as a mandatory script or layout for another product. The actual demo uses an original local HTML fixture and its captured screenshot, not reference footage. No outside footage, fonts, music or voice model is bundled.

## Run the shipped working example
From the skill root:
```
python starter/story_film/film.py starter/story_film/demo.json work/story24 --size 720
```
Requires Python, Pillow, NumPy, SciPy, OpenCV, Numba (fold), FFmpeg with libflite for scratch voice, and a system font. Preview at 720; use `--size 1080` for a native 1080 output raster and inspect actual result; 3D is internally lower resolution by design. Full HD may be expensive on a CPU. Do not use the scratch voice as commercial final; this is a baseline demonstration, not a high-end final ad.

## Adapt to a commission
1. Complete the existing intake / hook / audio process; do not ask a user to edit or provide a script unless they wish to. Generate 3 hook candidates, verify payoff, choose internally. Use one concrete premise and narrative, not a feature list.
2. Copy the JSON, set `image` relative to the JSON's location, use a real verified product capture, set `name`, `domain`, `accent`, `background`, `foreground`. `fonts` optionally takes `{bold,regular}` relative paths to existing authorized fonts. Use `width,height,fps,bpm` for export and timing. `fictional` must be true for example assets and false ONLY for verified real product. `crops` is a list of four normalized rectangles. Adjust every crop after looking at the real capture; do not reuse example coordinates blindly.
3. Voice lines: one complete idea per beat. Keep the user's provider/voice choice and tags from guide 25. Generate a continuous voice in the provider when possible; use verified alignment to split into phrase clips (or use individual TTS clips if natural). The user need only send the audio; the agent does splitting and naming. Supply PCM/decodable WAV clips `00.wav`, `01.wav`, ... in the same order as beats, and an authorized local music excerpt long enough for the film. No need to ask the user to prepare files in that format. If no tool access for provider, use existing concierge workflow and request just the finished raw VO and song. Never label flite as professional or approved voice. The engine places each phrase by its actual decoded duration, with a short centering pause and a configurable minimum. Its music grid is only a planning grid, not beat detection. If using real music, first analyze it and set bpm accordingly; use unified timeline for complex real beat timing. Do not stretch voice to fit.
```
python starter/story_film/film.py work/film.json work/build --voice-dir work/phrases --music work/song.wav --size 1080
```
4. Before rendering, use `--stills-only` to examine all compositions; it builds scratch audio/actual inputs and fold asset as needed. Use both actual playback and a decoded contact sheet after rendering. Fix 3 weakest moments. A contact sheet alone is not playback. `film.mp4`, `timing.json`, `script.txt`, `captions.srt`, `voice.wav`, `music.wav` (including generated accent sounds), `mix.wav` and the original JSON plus local assets make the project reproducible. SRT timing is phrase-based, not word-level. For verified word times use `starter/type_motion/align.py`.
5. Use `scripts/check_render.py`, `scripts/visual_review.py`, audio intake and release gate for real delivery; run a full decode. Do not call a fictional example upload-ready. Set actual intended platform safe zones, rights, brand claims and music license. Listen to the actual mix where possible, not just peak stats.

## Recipe fields (each beat uses `voice`, `min`, `kind`)
| kind | recommended inputs | motion |
|---|---|---|
| files | lines, items (2–6), optional folio | staggered headline, stacked rows and pointer; illustrative files, not actual interactions |
| scatter | title, number, micro, crops (four) | light-sweep graphic numeral, cards radiate and reframe |
| type | lines (1–5), highlight index, invert, optional micro | line-by-line masked reveal, contrast reset |
| assemble | title, optional micro | screenshot slat reassembly |
| fold | title, optional mesh settings | real curved textured mesh unfolds, then title arrives; uses previous mesh engine |
| reframe | title, optional micro | continuous crop-to-context actual capture |
| detail | title, second, crop, layout=bottom or default, detail_mode=stack and crops | macro to wider context or enlarged evidence rows |
| split | title, second, left_crop, right_crop | asymmetrical dual colored panels for connected evidence |
| callback | title, number, result_number, crops | convergence, number callback and evidence |
| end | title, optional footer | readable steady brand lockup |

Do not put an effect on every word. Plan each sequence's visual logic (first frame, semantic development, landing). The new runtime is optional alongside the existing unified engine. Use existing engines or a source clip for techniques not represented here. The metal numerals are a stylized 2.5D highlight, not ray-traced metal. The fold is real depth-tested 3D with an internal raster, but no raytracing or physical lighting. Original music is deliberately basic and not a substitute for selected professional music. The generated example uses a local synthetic scratch voice, not the user's tested ElevenLabs preset. No automatic aesthetic score or proof of commercial quality.
