> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Sequence engine (v18)
Use the unified controller, not an editor GUI. This engine is a five-beat visual grammar for a single idea, not a universal trailer template. It turns a stack motif into a closeup, proof and endcard with shared timing and graphic anchors. It uses the existing cinematic backend.

From skill root:
```
python starter/unified/production.py examples/sequence-v18.json --check
python starter/unified/production.py examples/sequence-v18.json --build-dir work/sequence --preview
```
Copy the example to the project folder, supply real authorized assets under that folder and adapt all copy. Example assets are fictional demonstration material. No actual product claim is implied. Never invent five tabs or other claims; labels are conceptual groups, not measured statistics. Use only the appropriate grammar, and do not use this preset repetitively.

| Field | Supported values |
|---|---|
| kind | consolidate, reveal, compare (the latter requires alternate.src) |
| hook | one or two short lines separated by newline |
| turn, payoff, brand, cta | short single lines, each <=65 characters |
| labels | 2–8 short motif labels |
| src | real product screenshot, relative to project |
| alternate.src | authorized before screenshot for compare |
| crop | normalized [left,top,right,bottom] of proof detail |
| beats | five exact frame starts, first 0, at least four frames per phase |
| layout | left, center |
| motion | flow, snap, quiet |
| texture | grain, grid, none |
| samples | 1, 2, 3 temporal samples (higher cost) |
| background, foreground, accent, paper | hex colors; check contrast |

Only use the automatic 20/39/58/82% boundaries for silent concept previews. Replace them with verified audio cues for narrated ads. Hold endcard 1.3–2 seconds or longer for URL readability. Inspect the result at mobile size; the text-to-proof phase changes background deliberately, and source crops must remain meaningful. The comparisons are two provided images, not synthesized claims.

Additional optics: `focus` = `brackets`, `lens`, `none`; `transition` = `iris`, `wipe`, `cut`; `light` = 0–0.6 for the animated highlight on the stack/endcard. The masked reveal carries the next product crop into the outgoing scene. This is 2D compositing, not optical ray tracing. `examples/sfx-v18.json` is a synthetic SFX cue example and not a substitute for narration/music.
