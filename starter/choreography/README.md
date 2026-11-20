> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Choreography compiler (V15)

Run from skill root. Generates one existing unified project, not new code. Use a real product image in the project directory. `--hook`, `--benefit`, `--brand`, `--cta` are copied exactly into on-screen elements; write them beforehand using the human copywriting/hook guides. Choose this scaffold only when the narrative is about reducing clutter or transforming a state. Default frames are a seven-second motion study, not universal ad length. The `--frames A B C` argument must follow actual verified cue timing: effective length A+B+C−6 frames. Three beats each 48..900 frames are supported; a shorter or more complex beat requires direct timeline editing. Use 30fps by default (six-frame overlap = .2s); at other fps adjust overlap/timing manually.

```bash
python starter/choreography/compile.py work/film.json --brand FORM --hook 'Too many tabs.' --benefit 'One place for your work.' --cta 'Make it yours.' --image assets/real-screenshot.png --frames 62 76 78 --width 540 --height 960 --samples 2
python starter/unified/production.py work/film.json --check
python scripts/layout_geometry.py work/film.json work/layout.json
python starter/unified/production.py work/film.json --preview
```

The input image path is relative to the output plan. If demo mode, use bundled `examples/choreography-v15-preview.json`, whose fictional website comes from the local `examples/assets/v15-workspace.html`. The bundled screenshot is captured without external resources. Do not copy demo proof into a customer ad. Use verified speech alignment before final. Change width/height to 1080/1920 and `samples` in `content` for high-quality final; use 4–8 only where render budget permits. CPU render duration scales strongly with resolution and samples. `samples:1` is quick and fully backward compatible with V14. Set additional text or UI artwork layers using the existing Layer Motion schema. Typographic brand text is not a precise logo asset; add authorized real logo for the final if available. Keep endcard readable.

```
python starter/unified/production.py examples/choreography-v15-preview.json --preview --build-dir work/choreo-demo
python scripts/visual_review.py work/choreo-demo/video.mp4 work/visual-review
```

Run `layout_geometry.py` on the original; optional `--repair work/film-fixed.json` writes a separate file in same directory and repairs simple static text fits only. Review before adopting any automatic changes.
