# V32 — 3D glyphs, soft bodies and font catalog

Use original timelines. The demo is merely test material.

## First-class extruded text

```json
{"id":"stat","kind":"text3d","active":[0,3],"text":"08","font":"heavy","size":440,"maxw":600,"x":360,"y":600,"material":"chrome","depth":68,"bevel3d":7,"yaw":[[0,-30],[3,18,"sine"]],"pitch":10,"roughness":0.16,"light":[[0,-0.6],[3,0.7,"linear"]],"quality":0.8,"softbody":{"preset":"rubber","events":[{"time":0.35,"mode":"squash","strength":0.35}]}}
```

Extrudes a high-resolution signed distance glyph atlas as a closed 3D shape. Preserves counters, true sidewalls and rounded bevels. The renderer traces camera rays and calculates normals and analytical studio shading; not a flat metallic texture. One-line strings up to 64 characters; prefer 1–8. `depth` 1–400 design pixels, `bevel3d` 0–40 design pixels (clamped to 45% of full depth, leaving a positive core), `roughness` 0–1, `quality` .2–1, `size` 8–1000, `maxw` optional. `pitch`, `yaw`, `light`, `depth`, `bevel3d`, `size_x`, `size_y`, `scale_z`, `bend3d`, `twist3d` support global keyframes. Materials chrome, satin, ceramic, obsidian, gold. `color` tint. Parent, opacity, affine layout transform, animated masks, reveal and shadow supported. Like volume, explicit layer order, no per-layer matte/blend or global depth sorting; use whole-composite shutter for 3D motion blur. No text-as-glass refraction yet. Font outlines are sampled, so microscopic details may alias and thick bevels may consume narrow strokes; inspect side views and reduce bevel. Lighting is procedural, not HDRI/PBR or path tracing.

## Softbody

A deterministic, frame-rate-independent underdamped oscillator driven by one or more impulses; presets jelly, rubber, silicone, heavy. `frequency` .3–12 cycles per caller time unit, `damping` .08–.98, up to 64 events. Each event has nonnegative `time`, `mode`, signed `strength` -1..1. Zero before contact, decays afterward. `squash` uses reciprocal transverse scaling to preserve the local box volume; supports elastic overshoot. `bend`, `twist` warp local coordinates. Triangle mesh adds localized `dent` and `ripple`; normals recomputed each sample. `object3d`, `glass_object`, `text3d` support squash/bend/twist; validation rejects dent/ripple on those layers. For `mesh` put the exact same config under `mesh.softbody`, where times and frequency are in normalized 0–1 shot clock, not seconds. Convert `frequency_hz * shot_seconds` and clamp to supported range. For solids/text, global timeline seconds. No collision/contact detection, mass-spring integration, topology changes, plasticity or mesh-to-mesh forces. Use masks and ordered layering independently.

## Font library

`assets/font-catalog-v32.json` contains 91 curated family candidates, organized by function, with provider links, no fonts included. Primary sources Google Fonts and Fontshare; Adobe Fonts optional with active appropriate license. Use the family-specific current license and keep a project-local provenance record. Fonts must already be legally available locally; do not bundle or download without checking their license. The catalog is a shortlist, not proof each link/license/weight is current. On Windows, install through system settings or use authorized local files. CLI uses fontconfig if present, otherwise scans common local directories. Exact family and style only, no silent fallback. For variable fonts, select an available face or use a locally authorized static instance; no axis automation yet.

```
python scripts/font_library.py list --role hero_grotesk
python scripts/font_library.py list --installed
python scripts/font_library.py resolve "Inter" --style Bold --alias display
python scripts/font_library.py board work/font-board.jpg --role clean_ui --style Bold --text "Your actual headline"
```

Merge emitted `fonts` dictionary into the plan. All aliases are supported, not just bold/regular/mono/heavy. Do not expose machine-local paths to end users unnecessarily or share the font binaries. Use visual specimens and inspect glyph coverage. Style matching is exact; “Bold” is not automatically inferred from variable family.

## Reproduce
```
python starter/composite_film/softbody_compile.py --showcase work/softbody.json
python starter/composite_film/compositor.py work/softbody.json work/show --size 540
python starter/composite_film/softbody_compile.py starter/composite_film/premium-timing.json work/film.json
python starter/composite_film/demo_compile.py work/base
python starter/composite_film/mix_picture.py work/base/mix.wav work/film.json work/mix.wav
python starter/composite_film/compositor.py work/film.json work/render --size 720 --audio work/mix.wav
python -m unittest discover -s tests -p 'test_v32.py'
```

The supplied complete-film recut uses the old FORM scratch voice and music only for continuity. Independent projects need original verified product information, authorized audio, original creative direction and a finished release check.
