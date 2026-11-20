> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

## V21 kinetic engine
Use `engine:"kinetic"` for `field`, `proof`, `type` or `lockup`. See `../kinetic/README.md`. Uses projected particles and perspective screenshot compositing, not a physical mesh simulation.

## V20 fusion engine

Use `engine: "fusion"` with `frames` and `content` validated via `starter/fusion/render.py`. Five morph families, five materials, four reveal masks, editorial type/lockup. See `../fusion/README.md`. `examples/fusion-v20.json` is a runnable fictional study. Same audio, caching and release rules apply.

## V19: Studio depth
`engine:studio` is supported; see `../studio/README.md`. Requires Numba for hero shots. Use 9:16 projects; `examples/studio-v19.json` is a fictional study.

# One Timeline Production Engine — v13

**Default runtime:** `production.py`. This is the preferred interface for a weak agent. Older `render.py` is retained for compatibility with earlier examples; do not confuse its different JSON schema with the new one.

The agent writes ONE JSON project, then the controller routes its shots through the installed, packaged renderers. It combines real UI, typography, expressive 2.5D, material studies, CPU scene3d, source clips and evidence-tagged data animations. It also performs controlled cuts/overlaps, optionally mixes real supplied narration + music, checks frame counts, caches unchanged shots, and creates a contact sheet and machine-readable report. No Blender, After Effects, GUI editor or historical reference videos.

Run from anywhere (replace `python`/paths on Windows if necessary):

```bash
python starter/unified/production.py examples/brand-story-project.json --check
python starter/unified/production.py examples/brand-story-project.json --preview
# A finalized project must have audio.voice pointing to a real, approved TTS file:
python starter/unified/production.py work/my-project.json --final
```

When audio is present, `audio.music` is optional. The controller will loop and duck it under real narration, but does **not** find, generate, license, align or validate speech semantics. Those tasks are documented elsewhere in the skill, and belong to the AI agent. Audio mixing tests use synthesized test tones ONLY; demos are SILENT and must never be called upload-ready ads. All user-supplied rights/music restrictions still apply.

For a quick editable draft after deciding verified hook, proof and CTA:

```bash
python starter/unified/quick_project.py \
  --hook 'A specific surprising question' \
  --proof 'Actual observed product benefit' \
  --brand 'YOUR BRAND' \
  --cta 'Actual URL / CTA' \
  --screenshot /path/to/authentic-screenshot.png \
  --out work/my-project.json
```

**The output is a scaffold, not a script and not a final storyboard.** Match frames to real TTS word/phrase timings, improve hook and story, add relevant changes in motion density, and use only confirmed product visuals. If no screenshot is provided, the proof scene becomes honest typography instead of an invented interface.

## Schema: production.py (NOT legacy render.py)

Root: `version: 1`, `width`, `height` (even), `fps`, optional `font` path, optional `audio:{voice,music,music_volume}`, and `shots` array.

Every shot:

```json
{
  "id":"story-01",
  "engine":"type",
  "frames":48,
  "transition_in":{"kind":"dissolve","frames":6},
  "content":{"kind":"hero","text":"THE QUESTION","subtitle":"A small supporting phrase","chrome":false}
}
```

Only the first shot may omit `transition_in`. For each following shot either `cut,frames:0`, or one of `dissolve/fadeblack/wipeleft/wiperight/smoothleft/smoothright/circleopen` with 2–24 overlapping frames less than half either shot. The effective film length is `sum(shot.frames) − sum(transition_in.frames)`. At 30fps 30+48+30+36−6−6=132 frames = 4.4 seconds. The agent must account for this before voice/musical alignment; no timeline guessing.

### Engine selector

| engine | `content` | implementation |
|---|---|---|
| `type` | `kind: hero/list/marquee/carousel/words/counter` | `starter/type_motion/render.py` |
| `ui` | `background`, `layers` with real image/cursor/text/rect | `starter/ui_engine/render.py` |
| `material` | `kind: metal/macro/focus/emissive/portal`, `text`, reflection | `starter/material_motion/render.py` |
| `expressive` | `kind: type/hold/character/wireframe/dots`, pose keys etc | `starter/expressive_motion/render.py` |
| `scene3d` | `layout`, `count`, `glyphs`, cameras, optional nested `scenes` | `starter/scene3d/render.py` |
| `data` | `kind: line/bars/metric/logs`, evidence, values | `starter/unified/data_chart.py` |
| `brand` | `kind: palette/collapse/reset/badges/endcard`, authentic screenshots and logo | `starter/brand_motion/render.py` |
| `clip` | shot has top-level `src` to authorized video, no `content` | FFmpeg decoder/resizer |

In `data`, every content must specify `provenance: illustrative` (clearly watermarked) OR `provenance: verified` with a nonempty evidence/source citation. Never use demo numbers as actual product claims. For `scene3d`, if `scenes` is provided, specify each scene `frames` summing exactly to shot.frames. For `type/words`, only actual verified alignment is accepted, never `synthetic_demo`.

Paths for `src` or `font` must be within the project JSON's directory tree; copy images/assets there. Filenames are converted to absolute paths internally. Do not run arbitrary user-supplied commands. `--check` validates structural fields and assets before render. Installed libraries depend on chosen engine; `ffmpeg`/`ffprobe`, Pillow and a usable font are basic requirements; other engines may require NumPy, OpenCV and numba.

## Reliable production loop

1. Product intake and confirmed claims; select ONE story, 3 hook options then choose one (guides 01–04).
2. Complete clean spoken script; compile ElevenLabs/Fish Audio provider-specific tags, obtain REAL voice file; obtain selected music if desired.
3. Verify voice duration/timestamps and chosen musical section before locking scene durations. Generate/modify one project JSON, cite all data claims in brief.
4. Run `--check` then `--preview`; inspect `contact-sheet.jpg` and actual video playback. Fix content and motion, not renderer code.
5. Add `audio.voice` and optional `audio.music` to project. Run `--final` (requires voice file); listen to final video, inspect every transition, then perform release QA in existing scripts.
6. Deliver final MP4, project JSON, source assets, voice/mix/captions as allowed, completed QA/claims report. A successful CLI result only establishes technical export, NOT creative quality or music rights.

## Outputs and recovery

`build/<projectstem>/shots/*.mp4` cached shot renders; `plans/*.json` actual backend config; `assembled-XX.mp4` combined steps; `picture.mp4` silent film; `mix.wav` and `video.mp4` when voice supplied; `contact-sheet.jpg`; `report.json` with frame count/duration/status. `--build-dir` overrides build location; `--force` invalidates cached shots. If one shot fails: correct its `content` and rerun with same build directory; unmodified shots stay cached. If voice is longer than the film, do not trim the voice — adjust frame counts and rerecord/re-align. The generated report deliberately retains `visual_review_required: true`.

Run quick smoke tests on included examples:

```bash
python starter/unified/production.py examples/brand-story-project.json --preview
python starter/unified/production.py examples/engine-coverage.json --preview
python starter/unified/production.py examples/data-example.json --preview
python -m unittest discover -s tests -p 'test_unified.py'
```

The examples are technical demos only, not templates to copy literally into advertisements. Rebuild creative direction for each client.

## V15 layers and additional transitions
`engine:"layers"` supports multiple animated sprites plus `morph`, `swarm`, `samples`, `shutter` as in `starter/layer_motion/README.md`. New permitted overlap transitions: circleclose, radial, diagtl, diagbr, squeezeh, squeezev, zoomin, hblur, slideup, slidedown. These are FFmpeg xfade presets, not custom physics or automatic match cuts. Verify installed support using `ffmpeg -h filter=xfade`; fallback to cut or dissolve only if compatible with the story and recalculate duration. Each transition keeps 2–24 overlap frames and must be shorter than half either adjacent shot.
Optional `audio.sfx` is a path to a supplemental audio stem and `audio.sfx_volume` (0..1) sets gain. For SFX-only preview `--preview` is permitted; `--final` still requires actual voiceover. `starter/sound_design/render.py` creates a frame-indexed stem. Use the effective post-overlap frame count.
