> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# UI Engine: headless, reusable, code-light
Dependencies: Python 3, Pillow, FFmpeg/ffprobe on PATH; optional Playwright plus Chromium for capture. Use the included fictional UI assets only as examples. No user product or source brands included. Default font Linux path; pass `--font` with installed TTF on Windows/macOS. Run from skill root:

```
python starter/ui_engine/capture.py starter/ui_engine/demo.html starter/ui_engine/demo-profile.png --selector .profile --width 600 --height 900
python starter/ui_engine/render.py starter/ui_engine/demo-plan.json preview.png --frame 118
python starter/ui_engine/render.py starter/ui_engine/demo-plan.json demo.mp4
ffmpeg -v error -xerror -i demo.mp4 -f null -
```
Existing PNG captures allow rendering even without Playwright. Local standalone HTML uses page.set_content, not file navigation (which can be blocked by browser policy); relative dependencies need an authorized local server. For URLs use authorized read-only access. Capture is a still, not live video. Review screenshot and diagnostics. No user interaction automation in this script other than scrolling.

Plan keyframe format and effect recipes: `references/32-programmatic-production.md`. To combine separately generated shots, create JSON e.g. `{"width":540,"height":960,"fps":30,"clips":[{"src":"intro.mp4","frames":30},{"src":"proof.mp4","frames":90,"start":0.5}]}`. `python starter/ui_engine/stitch.py clips.json final.mp4 --audio final-mix.wav`. Source paths relative to plan. Stitch normalizes dimensions/fps, letterboxes rather than stretching, verifies frame counts. Audio optional for demo only; use aligned final mix in production. No automatic transitions between clips (compose transitions in individual scenes). No 3D, vector morph, word-wrap or video layering in still compositor. Use explicit alternative tested path for missing capability.

Installation if authorized: install Pillow and Playwright from trusted package index, `python -m playwright install chromium` if no working browser. Use installed FFmpeg or standard OS package installer, never random binaries. No GUI editor required. Demo is 9 seconds, 540x960, 30fps and silent by design; it illustrates primitives, not NOIZ-quality recreation.
