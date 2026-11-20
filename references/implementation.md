> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Implementation and rendering

Choose a toolchain that actually exists in the execution environment. Do not conflate video editing with generating new image/video assets. This skill does not install or include external rendering engines, TTS models, paid APIs or third-party assets.

| Route | Appropriate use |
|---|---|
| HTML/CSS/SVG + JS and frame renderer (e.g. available HyperFrames, Playwright/Chromium or Remotion project) | Precise kinetic typesetting, live-looking UI, layout, SVG masks and graphs, reproducible 2D/2.5D. Render deterministic timeline; don't rely on realtime browser recording. |
| Blender (Python + Eevee/Cycles) | Genuine beveled 3D lettering, chrome, macro materials, instanced letters, geometry nodes, correct lighting and depth. Render image sequences separately; transparent alpha when needed. |
| Three.js/WebGL | Real 3D in web-based timeline when actual 3D geometry, PBR lighting/environment and frame-accurate stepping are supported. Avoid fake extrusion stacks. |
| FFmpeg | Audio decode/mix, compositing image sequences, muxing, encoding, inspection. Not a substitute for a coherent motion design timeline. |
| Existing professional editor (After Effects, Resolve/Fusion etc.) | Use if environment provides automation/export. Preserve native editable project. |

## Suggested project layout
```
project/
  inputs/                 # original script/music/assets; read-only
  assets/                 # approved working assets
  audio/voiceover.wav
  audio/music-bed.wav
  audio/final-mix.wav
  audio/alignment.json
  audio/cues.json
  plan/edit-plan.json
  src/                    # renderer-specific editable code/project
  renders/                # CGI RGBA sequences / previews
  output/final.mp4
  output/qa.json
  README.md
```

## Determinism / actual rendering
- Probe available binaries/versions, fonts, memory, GPU and external services. Select simplest viable engine; avoid installing huge packages blindly. Use renderer documentation when needed. Respect environment and user limits. Do not require secrets in source.
- Author time-driven components: input `t = frame/fps`; calculate interpolated values, masks and visibility from time; seed random generators; disable nondeterministic auto-playing CSS/JS animations. If using browser, wait for document.fonts.ready and all images/video frames; seek media and wait for decoded frame before capture. Use fixed viewport, local assets, exact aspect ratio. Capture frame boundaries without duplicates. Use quality native font rendering.
- Real 3D: convert user-supplied logo vector to geometry only if shape stays intact; avoid unneeded rectangular extrusions, use beveled geometry and material tests. Use area lights/reflection cards; test highlights and normals. Render passes in PNG with alpha or high-quality intermediate; composite with 2D layers in matching color space. If 3D unavailable, use great 2D and explicitly note deviation, not counterfeit CGI.
- Fonts/asset resolution: use provided fonts locally, don't redistribute restricted fonts; manage paths and license manifest. Capture web UI at a sufficient resolution and stable state. Prefer actual product over approximated UI; label conceptual mockups.
- Render a few complex shots and inspect contact sheets plus 100% images, then full frame sequence. Use FFmpeg to produce H.264/yuv420p + AAC for compatibility. Example (adjust to verified source frame count and audio duration before running):
```
ffmpeg -framerate 30 -i renders/frame_%06d.png -i audio/final-mix.wav \
  -map 0:v:0 -map 1:a:0 -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -movflags +faststart output/final.mp4
```
- Match duration prior to mux; do not mask incorrect sync with `-shortest`. Allow encoder delay tolerances, no unexpected missing words or frames. Inspect FFprobe metadata, decode full output (`ffmpeg -v error -i output/final.mp4 -f null -`), validate audio loudness and media dimensions. Verify render actually exists and plays. Source export must be runnable given documented dependencies.
