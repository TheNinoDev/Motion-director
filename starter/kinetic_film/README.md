> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Kinetic Film v25 — picture editing independent of sentences

The v24 example had one composition per phrase, leading to slide-like pacing. V25 is a runnable alternative with independently weighted picture events, derived from the actual lengths of decoded phrase audio. A 30-second film can have 18–28 distinct picture events without every beat being a cut. The packaged example is fictional FORM, not the reference brand. Reuse techniques, not its copy, colors, or layout by default.

```sh
python starter/kinetic_film/render.py starter/kinetic_film/demo.json work/film25 --size 720
python starter/kinetic_film/sound.py work/film25 --fps 30
```
Use `--stills-only` for the first test, `--voice-dir work/phrases --music work/song.wav` for real authorized audio, `--size 1080` for native delivery raster (3D insert rendered internally at up to 540px width). Requirements: Python, FFmpeg, NumPy, Pillow, SciPy, OpenCV, Numba for mesh. FFmpeg libflite for **scratch only**. Use actual TTS from the established audio concierge and verified phrase splitting. Output `finished.mp4`, caption/script, editable JSON, timelines and stems. Never ask user to adapt JSON. Do not claim exact word/beat sync: weights are visual scheduling relative to measured speech phrase lengths. Refine weights after listening to actual words; `align.py` for verified word timings. Music grid in v24 helper is not music beat detection.

## The schema
Copy demo.json into the project. Update the relative `image` to a real product capture; adjust every normalized `crop` and two `proof_crops` to the actual website. Set verified copy, brand colors, name, domain, fictional flag, optional `fonts` relative paths. One `beats` entry per spoken phrase: `voice`, `min`, `shots` array. Each shot: `kind`, positive relative `weight`, optional `text`, `sub`, `transition`. Weight is normalized within each phrase; minimum shot length 8 frames. Use actual rendered timing and avoid rapid unreadable UI. `sfx: false` disables automatic effect on a shot; or `[kind, duration_frames, gain_db]`. `sound.py` uses the computed timeline and adds a separate stem, not invented word alignment. Volume levels are conservative starting points; listen and adjust.

| kind | Inputs / behavior |
|--|--|
| macro | crop, text; oversized UI detail recedes into context |
| tabs | items, text; illustrative file rows enter on stagger |
| type | text, style=tiny/inverse/hero; masked editorial reset |
| counter | text, sub, optional end; stylized extruded metal with moving highlight; discrete count change |
| tunnel | text; projected repeated genuine product crops on a curved path |
| cascade | items, text; scrolling repeated file rows; clearly illustrative |
| field | text; orbiting spatial points converge into glyph silhouette |
| aperture | text; circular reveal of product capture |
| mesh | text, mesh overrides; real textured sheet deformation through existing mesh engine |
| reveal | text; macro to whole UI |
| detail | crop, text; camera reframe with scanning line |
| duo | text, sub; two independent product crop entrances and contrast |
| cutout | text; video-like moving image inside letters |
| lockup | text; brand hero and readable CTA/brand domain |

Transitions: cut (default), iris, shutter, match (short zoom blend, not true morph), wipe, prism (brief channel offset with blur). At most six frames in this runtime. These are available choices, not a checklist; avoid flash sequences and obscuring visual proof. The prior unified runtime remains available for advanced layer, CGI, tracking, particle, data, character and morphological sequences. This new route does not automatically compose every older effect.

## Creative recipe
Use a narrow, human problem: first establish a tangible object or gesture, turn it into an escalating motif, change the visual language at the pivot, reveal the product through a meaningful transformation, show proof, return to the hook. Never display a random chrome object merely because it looks premium. Strong art direction means withholding effects as well as adding them. A legible UI crop should be visible for the duration required to read it, and a fast graphic insert can be shorter. Plan changes in composition, scale, movement and visual subject, not a sequence of title cards. Alternate high-density and quiet moments. Maintain common anchors across cuts. Compare actual preview motion against the storyboard, correct the three weakest intervals, and do not equate a technically valid render with high-end editing.
