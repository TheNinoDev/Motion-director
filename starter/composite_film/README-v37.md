> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V37 director macros
Run from the skill root. `python scripts/director_v37.py catalog` lists required and optional fields; each recipe also needs `recipe`, `start`, `end`, and `layer` (except stagger_reveal uses `layers`). Cue names are allowed for times. Optional `ease` uses the existing workbench easing names. Coordinates are 720x1280 design units, not output resolution. Each macro expands into ordinary actions; all actions share global time and strict channel conflict validation.

```
python scripts/director_v37.py compile examples/director-v37.json work/plan.json
python scripts/director_v37.py diagnose work/plan.json
python starter/composite_film/compositor.py work/plan.json work/demo --size 720 --profile high --backend auto
python scripts/review_ledger.py create work/plan.json work/ledger.json
```
The example is a silent six-second motion study. Use the full voice/music workflow for advertisements. Keep the original source spec; expanded spec uses the original spec directory for relative assets, final plan resolves image/font paths. Review output is advisory, not a quality certification. For actual CUDA use the existing GPU doctor. No new dependencies.
