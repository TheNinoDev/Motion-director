# Procedural CGI starter — v9
Read `../../references/35-procedural-engine-playbook.md` for dependency setup, full JSON options and troubleshooting. CPU renderer tested with 180 frames, six shots, 360x640 at 30 fps, supersampled 2x. Glyph mesh test used A/O/X, with bevel accepted on all three. No font is bundled. `render_webgl.py` is optional experimental code; the current environment failed WebGL2 setup, so it is **not runtime validated**. `points-demo.json` contains generated fictional FORM word silhouette points; `demo.json` contains an inline copy for self-contained use. No final VO or soundtrack in this technical demo. Use existing audio and UI engine for real ads.

## One-command plan selection (no hand-authored scene JSON required)
```
python starter/scene3d/preset.py hero work/hero.json --glyphs X --seconds 2
python starter/scene3d/render.py work/hero.json work/hero.mp4 --font /path/to/font.ttf --preview-dir work/hero-stills
```
Available presets: hero, grid-helix, ring, tunnel, sphere, wordmark. Wordmark requires `--points` from your own authorized logo mask or generated text; it never silently uses the example logo. Customize a copy of the output plan. A plan only promises the implemented primitive, not final ad quality.
