> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V39 — State-aware production: primary execution guide
Read this first. Read guide 74 only for the older catalog and guide 71 only for GPU issues. Keep the original canonical spec, actual product evidence, verified copy and audio. Old release rules still apply. Do not request historical reference clips. Do not claim tests or aesthetic quality you have not inspected.

## Small-agent decision protocol
1. Classify the task: script, new ad, revision or isolated technical study. If script only, use SKILL phases 1–3; do not render. If revision, inspect the actual preceding plan and render, identify affected IDs and intervals, preserve unrelated timing, claims, assets, design and audio. If study, explicitly identify it as a study.
2. For a real ad read only the necessary product source. Record one provable central benefit, actual product demonstration, target audience, CTA, source and rights. Write three distinct concept families, choose the one with the clearest visible payoff. Do not ask the user to decide ordinary animation choices. Use SKILL phases 1–3 for real audio, including the unchanged user-authored voice prompt and provider-specific tags. A scratch or silent render is not a final commercial film.
3. Pick one coherent art direction. Render typography with the exact words using the chosen locally available licensed face. Compare at least two actual compositions before committing. Preserve contrast, scale hierarchy and intentional space. Do not choose glass, chrome, jelly or any effect just because the catalog supports it.
4. Produce creative JSON from `examples/creative-v39.json`: replace all example claims and concepts, cover the timeline in beats, describe a concrete action, link `layer_ids` to the actual visible subjects and real proof layers. Preserve allowed proof status semantics. One dominant subject at a time. A useful beat is “cursor selects the cluttered row; the row consolidates into a real result”, not “cool 3D text”. Use a deliberate cut if a shared motif would be forced.
5. Choose primitives, authored tracks, older recipes or V39 state-aware recipes. Start motion at the actual previous endpoint; keep the main object persistent when it helps. Treat supported recipes as building blocks, not canned advertisement layouts. Every effect must clarify, focus, reveal, connect or resolve. No default hero chrome or arbitrary motion.

## Exact commands (run from the skill root)
```
python scripts/director_v39.py catalog
python scripts/director_v38.py catalog
python scripts/motion_workbench.py catalog
python scripts/production_v39.py start examples/director-v39.json examples/creative-v39.json work/study39
```
For a real film replace both example JSONs with authored files and pass `--audio /path/to/actual-authorized-mix.wav` once audio is ready. The command emits `production.json` with exact argument arrays, diagnostics, path fingerprints and creative-to-layer linkage. Execute arrays as argument lists rather than concatenating strings. Existing paths are never intentionally overwritten; new revisions get new work directories. Absolute resolved image/font/nested mesh paths keep compiled plans usable from a different working directory, but referenced assets must remain available. No font binaries are included. For a missing asset restore the actual source, never invent a substitute screenshot.

## State-aware recipes (`state_motion` array)
Times use seconds or named cues. Position units are 720×1280 design coordinates, even when output is 1080×1920. All recipe fields are required unless named optional. `ease` is optional (default quint). Earlier `actions`, `macros` and `choreography` are expanded before these blocks. New blocks process in start-time order; if same start, preserve array order. State sampling reads the already compiled properties, including prior overlapping motion on *other* channels. The compiler rejects overlapping writes to the same property. A first action on a property defines its initial value before that action, as in V38. Set explicit initial layer values and avoid conflicting authored tracks. Static props are fine. This provides value continuity, not automatic velocity continuity.

| Need | Recipe | Exact behavior / constraint |
|---|---|---|
| Continue an existing motion | glide_to | Reads position, uniform scale and roll; new endpoint only |
| Align multiple surfaces | arrange_row | Same parent coordinate space; order supplied layer IDs; stagger fraction 0–.75 |
| Cursor or marker follows moving subject | follow_offset | Reads source path, samples 8–120 linear segments, delay and blend-in, same parent; source must have been authored already and active throughout delayed interval. Recompile after source changes; do not animate source later in another state block that changes the sampled interval. |
| Separate focus from support | spotlight | Flat layers only, animates hero scale and dims/blurs other named layers; does not auto-restore |
| Refine 3D orientation | depth_turn | Volume or text3d; yaw/pitch, normalized light parameter and scale |
| Elastic arrival | elastic_settle | Solid layer only; move then authored squash impulse, not simulated collision |
| Clean removal | quiet_exit | Reads current position/scale/opacity, then moves and fades |
| Finish existing mask movement | mask_continue | Existing mask type cannot change mid-layer; explicitly initialize `mask_progress:0` to open |

## Executable review sequence
- `production.json` reports invalid layer links, missing real audio blocking final commands for advertisement mode, and plan diagnostics. Correct the smallest invalid field. If an operation is unsupported inspect catalog and use a documented alternative, not imaginary parameters.
- Run `review` and inspect native PNGs. Check the first 2 seconds, before/during/after transitions, full-frame text safe area, contour edges, 3D reflections. The baseline review hash mechanism still does not fingerprint default system fonts or nested resources; the production input snapshot also records explicit nested mesh assets. Fingerprints are not proof of viewing. Run `check_inputs` before release; changed source, plan, explicit assets or audio are rejected.
- Run `preview`. Inspect actual playback at speed and at frame steps around flagged transitions. Listen to actual audio and check intelligibility, dynamics and cue timing. If unable, disclose that. Do not substitute a contact sheet for video review. Record concrete observations/actions in `review_ledger.py`. Revise up to the three largest issues, or all if fewer, and repeat with a new revision directory.
- Run `upload` and optional `master` only after evidence, rights and real audio inspection. `check_upload`/`check_master` perform media checks including resolution, fps, decoded frame count, duration, required audio and FFmpeg full decode. They do not prove that video matches the plan creatively or that audio is licensed. The existing full release gate remains required for advertisements.

## Recovery table
| Symptom | Inspect | Fix | Recheck |
|---|---|---|---|
| Movement jumps | Tracks around exact join | Use `glide_to` or extend overlapping visible motion; match endpoints, check velocity visually | Render before/during/after |
| Tracker floats | Shared parent, source path, delay | Author source first, reduce delay, adjust offset; rebuild follower | Inspect at 3 points |
| Scene looks like slideshow | Beat action and persistent subject | Replace plain entrance with demonstration or meaningful transformation | Watch full sequence |
| Too much going on | Competing subjects and focal contrast | Dim or remove support layers, reserve quiet hold | Native frames and playback |
| 3D material looks cheap | Native detail, light direction, bevel, aliasing | Use actual geometry, adjust roughness/light, high profile, avoid overbloom | PNG at 1080 width |
| Audio absent | Mode and actual input | Acquire authorized final voice/music mix; do not use scratch as final | Listen and check stream |
| CUDA not available | `gpu_doctor.py` and backend telemetry | Auto falls back to CPU; use strict CUDA only with real device | No fabricated speedup |
| Existing project changed | Source and asset fingerprints | Recreate review in new revision; preserve unaffected work | Compare hashes and actual frames |

Do not deliver a final ad until the original SKILL release conditions are met. A successful compilation or media decode does not establish premium quality. Use the tools to reduce mistakes, not conceal them.
