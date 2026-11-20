> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V16 optical motion and polish

All tools are CLI driven. No GUI editor or source videos needed. Run from the skill root. `compile.py` is an editable scaffold, not a creative decision maker. It expects verified copy and an actual approved product screenshot, not a fabricated one. Example assets depict a fictional workspace. Default export is 1080x1920/30fps; the delivered example is a 720x1280 draft.

```bash
python starter/polish/compile.py examples/local-study.json --brand FORM --hook "Too many tabs?" --benefit "Your work. One place." --cta "Make it yours." --image assets/v15-workspace.png --style editorial --detail .04 .26 .52 .59 --width 720 --height 1280
python starter/unified/production.py examples/local-study.json --check
python starter/unified/production.py examples/local-study.json --preview
```

Four presets (`editorial`, `technical`, `kinetic`, `luxury`) choose different optical graphic families over the same four-beat scaffold. They are not four entirely different narrative structures. Use earlier narrative and type/data/CGI tools when a different structure is appropriate. Set `--frames` to four actual frame durations; 4-frame overlap into the final shot reduces total duration. `--accent` is a hex brand color; `--samples 2` or `3` increases render cost for genuine subframe shutter blur. Keep readable CTA on screen at least 1.25–2 seconds once fully revealed if the actual voice timing allows; extend end shot accordingly. `--detail L T R B` crops real UI pixels, normalized to screenshot dimensions. Do not use arbitrary crop coordinates; inspect product source and choose meaningful region. If absent the full product panel stays visible. Never use synthetic UI as proof.

## Eight new layer kinds
All support normal position/scale/rotation/tilt/pitch/opacity, opacity keyframes, reveal, glow, shadow, masks, composition, and the ordinary `progress` parameter. `speed` sets the animation rate (time base 30 frames/second; adjust if other fps), `count` is 3–360 (per-kind caps apply), `stroke_width` is .5–30 design pixels, `amplitude` 0–1, `seed` nonnegative integer. Use a single primary effect and one or two subtle secondary elements rather than all at once.

| Kind | Use | Tested starting parameters |
|---|---|---|
| orbit | three projected 3D orbits and depth-dependent dots | size 850x850, count 36, opacity .35–.75, speed .6 |
| ribbons | flowing multi-line fields | count 16–30, amplitude .4, opacity .25–.5 |
| network | deterministic moving points with neighbor connections | count 32–65, progress 0→1, opacity .45 |
| scanner | scanning band and ruler ticks | progress 0→1 over 18–35 frames, opacity .25–.4 |
| halftone | animated dot texture | count 100–200, scale 0.8–1.1, opacity .35 |
| waves | expanding deforming contour lines | progress 0→1, stroke_width 2, amplitude .35 |
| aperture | segmented rotating aperture motif | progress .1→.9, speed .3, opacity .4 |
| sparkfield | moving sparse twinkles | count 30–70, opacity .25–.55 |

Other new layer options: `pitch` ±70 degrees (keyframes), `feather` 0–100 (mask Gaussian sigma in design pixels), `distortion` 0–40 (local analytic displacement in design pixels, **never on product proof or readable text**), `crop` normalized on image layer. Pitch and yaw are planar perspective, not volumetric objects; orbit is a 3D point projection, not a mesh renderer. Dynamic graphics are stylized, not physical light/particle simulation. Feather is a soft approximation; reduce if edges look dark.

## Audio reactivity (optional)
```bash
python starter/polish/audio_reactive.py examples/polish-v16.json /path/to/authorized-music.mp3 examples/reactive-v16.json --shot motif --layer field --property glow --base .04 --amount .14
```
The tool uses FFmpeg decoding and smoothed RMS amplitude, not musical beat or BPM detection. It maps measured audio to one non-text/non-product layer's previously non-keyframed scale, opacity or glow and writes a separate JSON next to the original. It accounts for clip overlaps. If the actual soundtrack changes, rerun. Use only with music/FX authorized for that production. Beat placement still requires verified musical onsets and voice timing. No such input needed for preview.

## QA
Run `python -m unittest discover -s tests -p test_v16.py` and `python scripts/layout_geometry.py examples/polish-v16.json report.json`. Inspect full decoded motion and all visual holds; an automated geometry pass is advisory only. `examples/sfx-v16.json` and its generated WAV demonstrate accent timing; never treat synthetic cues as VO or music. Render actual narration and authorized music for final delivery.
