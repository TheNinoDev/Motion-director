> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Tool choice — find capabilities before coding
Run `python scripts/doctor.py`. This discovers executables/imports, not accounts or working render permissions. Verify installed version/help and do short smoke render. Do not guess commands for unfamiliar packages. Use user-approved existing tools first; any official documentation links below are starting points, actual installed command help is authoritative.

| If available | Use for | How to start |
|---|---|---|
| HyperFrames | HTML/CSS/JS motion and video composition | inspect installed skill/CLI help, use official examples matching version; verify actual render path and media assets |
| Remotion (https://www.remotion.dev/docs/) | React deterministic sequences | use useCurrentFrame / interpolate, Sequence for boundaries, staticFile for local assets as applicable; inspect installed renderer docs |
| Browser + Playwright (https://playwright.dev/docs/intro) | real website capture and frame-rendered HTML/SVG | local independent page with deterministic seek(frame), wait fonts and assets, screenshot frames at viewport; use authorized captures only |
| Blender (https://docs.blender.org/manual/en/latest/) | real 3D, lighting, rendered transparent passes | test executable; use scene script, bevel geometry, lighting, camera, export image sequence; check version/API |
| Three.js (https://threejs.org/docs/) | real 3D inside web renderer | test WebGL availability, use actual mesh material and environment; render offline by frame |
| FFmpeg (https://ffmpeg.org/documentation.html) | probe, normalize audio, encode frames, composite, validate | ffmpeg -version; ffprobe -version; inspect available filters/codecs |
| Python + Pillow | deterministic 2D fallback, QA contact sheets | use provided starter, adapt with product assets; no claim it matches flagship design automatically |
| TTS/ASR | voice, timing, transcription | discover provider/local binary and authorized model; check language, voice and timing support. No paid calls without approval. |

Never use an LLM-generated movie as the only implementation when editable source is required. Generative image/video can supply a specific asset if user agrees and capability exists; don't substitute it for accurate UI. Use local fonts and assets, no external CDN dependencies in offline render. Cache approved media in project. Render samples before full video. Use fast lower resolution preview for layout, full resolution for detailed QA. Render output files must exist and decode before reporting success.

Example image sequence encode (replace fps/paths):
```
ffmpeg -y -framerate 30 -i frames/%06d.png -i audio/mix.wav -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart output.mp4
ffprobe -v error -show_streams -show_format -of json output.mp4
ffmpeg -v error -xerror -i output.mp4 -f null -
```
Align audio length before encoding. Do not use -shortest blindly if it would cut brand hold. Set target resolution/frame rate intentionally. Prefer one well-understood renderer, not a kitchen sink of dependencies. If not available, degrade composition gracefully, not quality claims.
