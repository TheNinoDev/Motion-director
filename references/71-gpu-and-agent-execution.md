# V35 — GPU rendering and reliable small-agent execution

## Choose one route, not every manual
- Full product ad: inspect actual product, write three distinct hooks and select a truthful central story. Follow SKILL phases 1–3 for real voice, music rights and timing. Then build one editable global compositor plan using README.md in starter/composite_film. Use legacy unified engines for specialized shots, not as a second timeline schema. Never treat the included FORM film as required visual design.
- Visual revision: keep source and audio unchanged unless requested; isolate the faulty interval, render that interval, inspect the old and new versions, then produce the complete master. Edit the smallest meaningful group of layers. Avoid swapping the whole design to a demo.
- 3D solid/glass: use object3d/glass_object. Shape, material, transform and softbody behavior are independent. See README-v31.md. Do not use a lens for a solid rotating volume.
- Metal typography: use text3d, inspect both face and sides at 1080 width, atlas 960–1280, quality 1, AA 1.5–2. Prefer short strong letters and real counters; read README-v32.md. Use font_library.py pairs and resolve; no font files included.
- Real wall contact: use contact3d/render.py and named presets. For decorative wobble generate an editable recipe with scripts/elastic_recipe.py; label it stylized. The solver stays on CPU.

## Setup — verify instead of guessing
From skill root:
```
python scripts/doctor.py
python scripts/gpu_doctor.py
python scripts/gpu_doctor.py --test
```
The last command is for an actual available CUDA device. It renders small comparison cases and compares them with CPU output. It is not a speed benchmark. On a machine without a physical GPU, `python scripts/gpu_doctor.py --simulate` exercises kernel logic using Numba's CPU simulator; it is NOT a real CUDA compilation, GPU test or performance result. The normal renderer refuses simulator-only acceleration.

Optional installation, in the user's chosen virtual environment, with permission. Install/update the compatible NVIDIA display driver first. Select ONE toolkit branch based on driver, GPU support and NVIDIA's instructions:
```
python -m pip install "numba-cuda[cu12]"
```
or `python -m pip install "numba-cuda[cu13]"`. Do not install both blindly. See https://nvidia.github.io/numba-cuda/user/installation.html for the currently supported requirements. For other GPUs or failed CUDA setup continue using CPU. Do not require a GUI, buy GPU time, invent detected hardware, or silently install dependencies.

## Render and verify
```
python scripts/agent_preflight.py examples/type-v33.json work/preflight --backend auto
python starter/composite_film/compositor.py examples/type-v33.json work/style --backend auto --at 0.4 --at 1.2 --size 1080 --profile high
python starter/composite_film/compositor.py examples/type-v33.json work/excerpt --backend auto --range 0.4 1.2 --size 720
python starter/composite_film/compositor.py examples/type-v33.json work/master --backend auto --size 1080 --profile lossless
python starter/contact3d/render.py examples/jelly-v34.json work/contact --backend auto --still 2.0
```
Always use fresh output directories for each attempt, especially after errors. --range is an absolute-time, end-exclusive, picture-only excerpt. It preserves the original timebase and ignores no active layers. Do not use it for an audio master. --at writes native PNGs, not contact-sheet thumbnails. --profile high/lossless raises internal CGI quality and antialiasing; lossless uses RGB video, not raw/uncompressed video. Preflight outputs executable argv arrays and GPU discovery. `scripts/review_targets.py` proposes bounded review moments around layer starts/ends, keyframes, elastic impacts and the opening/closing. Inspect the actual PNGs; sampling does not prove continuity or artistic quality. Run full playback, inspect transition excerpts and verify sound before claiming completion.

`--backend auto`: CUDA if available, otherwise CPU with diagnostic. On kernel failure auto logs the error and falls back to CPU for that kernel family. `--backend cuda`: fail on missing device or kernel failure, no hidden fallback. `--backend cpu`: explicitly use the reference renderer. `--device 0`: choose visible CUDA index; consult discovery rather than guessing. `--gpu-tile-mib 64`: approximately bound per-transfer grids/output, 4–512 MiB. Available memory also bounds tile size. Contact uses a guarded full frame. This is not a total GPU VRAM limit. Never claim an all-GPU render: check `render-backend.json` for actual kernel call counts and fallbacks.

GPU scope: volume ray marching (9 shapes and materials), bevelled type ray marching (5 materials), 3D contact ray raster. CPU scope: glyph atlas construction, compositing, background refraction sampling, format conversion, audio/video encoding, contact dynamics and older renderers including triangle mesh. No Tensor/RT-core specific code, full path tracing, multi-GPU pooling, GPU physics or NVENC. GPU speedups depend on GPU, transfers and scene; warmup/compile time and CPU portions remain. Do not assert speed gains without comparing matched, warmed renders on actual hardware. GPU may be slower for tiny frames. Existing plans remain compatible.

## Creative correction checklist (bounded, concrete)
1. State the shot's semantic action in one line, then decide primary object, secondary motion and supporting negative space. If all elements compete, remove a decorative element rather than adding an effect.
2. At each boundary, identify a shared anchor (position, shape, direction, color, semantic action). Check before/during/after frames and track the same element through the cut. Preserve movement on both sides; do not crossfade unrelated compositions just to conceal a discontinuity.
3. On 3D shots inspect front, grazing angle and smallest visible size. Fix clipping, facet/normal artifacts, font counters, unreadable specular bands, and internal resolution before adding motion blur. Do not use blur to hide flawed geometry.
4. On elastic shots verify contact where intended, readable compression, recovery speed, volume and no implausible intersection. Choose a motion preset independently of material. No wall solver for arbitrary collisions.
5. For UI proof zoom to one verified feature; preserve readable, real product evidence, no fake claims. Change one parameter group per revision and record what changed and what the render actually showed. Keep best prior render if the new one is worse.
6. Review full playback at target FPS and native quality. Prioritize visual coherence, timing, type, audio and verified claims. No automatic score may label an ad professional. If voice, licensing, independent agent testing or hardware testing is unavailable, disclose the remaining gap.

## Minimal state contract for the agent
Write `production-state.json` with: route, verified product evidence, current plan, source audio and rights, design intent, chosen font/materials, review issues with seconds and layer IDs, render commands and outputs, actual backend report, next correction, release blockers. After every render record exit status and verify the file exists/decodes. Do not reload the historical guides unless a feature needs them. Never write a new renderer when a supported recipe solves the task. Never copy reference brands or assets.
