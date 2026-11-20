> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V44 — authoritative low-context production contract

The deliverable is an original, high-quality, product-specific video, not a collection of presets. Use this guide for new projects; older routes are feature references only. Read V43 guide 79 for the existing motion program schema and creative JSON examples; do not load the entire archive. Never require historical references. Keep user-locked copy, audio, proof, timing and unaffected artwork intact. Do not forward claims of real GPU use unless the GPU doctor and backend telemetry establish them. Follow the original audio/rights workflow (guides 20–25), font catalog and release checks. A silent study is not a finished ad.

## A precise operating sequence

1. **Intake**: inspect one trustworthy product source. Extract audience, problem, proof, differentiator, brand constraints and media rights. If a detail is not provable, do not put it in the script. Ask only missing essential information. If delegated, decide art direction yourself.
2. **Concept**: write three alternatives without effect names: product interaction, physical metaphor, editorial contrast. Each must contain an observable change and a reason that is specific to this product. Reject any concept that could advertise a random app unchanged. Select one central story, not all features. Do not copy FORM. For public advertising get authorized final VO/music or approved silent requirements; current gated ad route requires audio. Do not pretend that scratch audio is final.
3. **Design before effects**: compare two actually rendered font treatments and three meaningful styleframes. Keep a single dominant subject in each frame. Decide baseline colors, texture, material, light direction, hierarchy and negative space. Use screen evidence at the moment of proof. Keep real UI legible, no fabricated features. Use contrast of scale and pace, not a new decoration every second. Motion density is a choice, not a quota.
4. **Picture plan**: describe each beat as initial state → visible action → consequence. Specify primary/support motion, anchor, native frame-safe composition, and the incoming/outgoing motion direction. Bind actual IDs and times. Use exact authorized speech timing and deliberate music accents; picture and speech cuts need not coincide. Do not stretch VO just to fit a template.
5. **Tool routing**: existing layer tracks for simple motion; V43 motion_programs for sequential property changes; V40 continuous_path for a non-stopping curved trajectory; V41 components for repeated elements; V42 choreography for ensembles; V44 motion_accents for motivated anticipation and recovery on unused lanes. Glass object for volume, lens for flat screen refraction. Physics contact solver for wall impacts, analytic jelly for an art-directed impulse. Native text3d for short dimensional words only. Inspect actual catalogs before writing unfamiliar fields. Do not invent APIs or rewrite a renderer unnecessarily.
6. **Build and preview**: execute the command sequence below. The creative record is not a substitute for actual layers. If a compiler rejects a property conflict, move motion to an unused lane/parent or explicitly migrate the original track; never delete existing animation just to silence validation.
7. **Review**: watch full-speed video and listen to actual supplied audio. Then inspect native stills, pixels, joins and flow sheets. At each join compare outgoing silhouette, incoming silhouette, direction and approximate pace, screen position, and continuity of the shared anchor. Look at least three frames on each side. For a hard cut explain its purpose; for a match cut verify the matching geometry. Never use an automatic crossfade to cover a bad design. Metrics are prompts, not pass/fail for taste.
8. **Repair**: identify a defect with timecode, layer, observed symptom, concrete change, expected result and protected unaffected work. Use the direct-source safe repair when applicable. Recompile a fresh revision in a new directory, render and inspect the old vs new frames. If fixes worsen readability or motion, reject them. Do not mark pending checks pass just to get export. If a fix needs many coupled properties, change the actual owning macro or component deliberately rather than hacking generated JSON.
9. **Deliver**: high-quality 1080 upload via current route, optional lossless master, editable source and media manifest. Verify decode, duration, frame counts and audio, then watch the exported result again. Report limitations, unresolved issues, test mode and actual GPU backend honestly. Never fabricate an output or aesthetic score.

## V44 motion accents — options and guardrails

Use `python scripts/director_v44.py catalog`. Top-level `motion_accents` is an array. A profile changes one or several currently unused scalar lanes, using additive deltas in the property's native units. Minimum duration five frames, times are absolute seconds, must fit layer active interval. The curve is analytically smooth at each internal knot, sampled at 4× FPS; not exact continuous velocity between sampled linear keys. Range checks include overshoot extremes. It refuses occupied properties rather than replacing authored motion.

| Profile | Ends at | When to use | Avoid |
|---|---|---|---|
| anticipate | base + delta | brief opposite wind-up before a directional move | logo or text in every beat |
| overshoot | base + delta | slightly pass target and settle | overshoot into clipped text or another subject |
| recoil | base | contact/reaction and damped return | unexplained wobbles on rigid UI |
| double_accent | base | two distinct pulses with decreasing strength | constant sync without musical or narrative reason |

Example (base rotation must be scalar or absent):
```json
{"motion_accents":[{"profile":"anticipate","layer":"hero","start":0.2,"end":1.3,"delta":{"rotate":18}},{"profile":"recoil","layer":"hero","start":1.4,"end":2.3,"delta":{"scale_x":0.15,"scale_y":-0.12}}]}
```
This is art-directed deformation, not contact physics. To chain accents on the same occupied property use a V43 program or dedicated parent. The compiler deliberately rejects two writers on the same lane. Keep primary motion dominant and use only supporting accents that are perceptible at normal speed. Small secondary motion can be adequate; if motion obscures the product, reduce it.

## Failure-to-action rules

| Visible problem | First targeted fix | Acceptance condition |
|---|---|---|
| Abrupt directional change at matched join | compare flow arrows AND actual frames; adjust shared anchor path, incoming direction or overlap at canonical source | correct silhouette match, intentional pause or cut acknowledged; no unexplained jump |
| Rigid UI motion | use tiny anticipation/overshoot on an unused property only when motivated | readable result at actual playback, no needless bounce |
| Competing elements | mute secondary movement, do not scale main text indiscriminately | clear focal point with meaningful support |
| No visible change in a beat | introduce product-specific operation/result; revise concept before decorating | viewer can describe what changed |
| Text too wide | render native text, change width or size conservatively; verify exact copy and glyphs | safe necessary text and no loss of information |
| Metal/3D roughness | native PNG, bevel/geometry, normals, samples and lighting check; separate compression test | silhouette and reflective edges are clean at output size |
| Flow confidence low | watch actual sequence; distinguish pause, occlusion, textureless field, fast cut | honestly state limitation; no invented direction |
| Motion too busy | reduce independent trajectories; hold main shape or arrange groups | no need to hunt for content |
| User asks one correction | local canonical revision or narrowly edit owning recipe; compare unaffected layers | unrelated source and generated fields remain unchanged where promised |

## Current commands

Run from the skill root, using a fresh work directory. The supplied example is a recut of the V43 fictional study and exercises all four accent profiles. Use distinct authored inputs for real work.
```
python scripts/director_v44.py catalog
python scripts/production_v44.py start examples/director-v44.json examples/creative-v44.json work/study44
python scripts/production_v44.py next work/study44
python scripts/production_v44.py preview work/study44 --size 720 --backend auto
python scripts/production_v44.py pixels work/study44
python scripts/production_v44.py transitions work/study44
python scripts/production_v44.py flow work/study44
python scripts/production_v44.py advice work/study44
python scripts/production_v44.py review-template work/study44
python scripts/production_v44.py gate work/study44
python scripts/production_v44.py upload work/study44
python scripts/production_v44.py verify-export work/study44
```
For an ad pass `--audio PATH` on start. Use existing native PNG review tools separately (1080 width); the preview evidence is reduced resolution and does not substitute for them. All three evidence sets bind to current inputs/video. The flow report samples adjacent decoded frames at opening, closing, all narrative boundaries, at 240×426 using Farneback plus forward/backward consistency and gradient support. Arrows are magnified 3×. It estimates motion only where texture and consistency support it. Low support/coherence is not a defect verdict; speed and direction are in review-pixel coordinates, not physical object velocities. Compare actual motion paths; not a tracker or automated optical-flow interpolation. A report flag needs a concrete observation and explanation of intentional behavior or a new revision. Never auto-approve.

## Non-destructive direct-source corrections

Use only for simple authored static fields on non-group, direct layers. Animated fields, component internals, masks, parent changes, text, assets, timing and changes that affect other generated fields are rejected. The tool compares compiled plans before and after; no unexpected numeric property changes are allowed. It cannot guarantee pixels stay unchanged (a resized element can cover another). It does not certify visual quality. Save an explicit request as JSON (replace SHA256 with the exact source hash):
```json
{"source_sha256":"<actual SHA256>","reason":"Footer text is too wide at 6.5s; actual native sample confirms.","changes":[{"layer":"foot","field":"size","before":19,"after":17}]}
```
```
python scripts/source_repair_v44.py examples/director-v44.json repair.json examples/director-v44-revision.json
```
Output must be beside the source to preserve relative asset paths, and must not exist. A request does not affect the original. Start a fresh session using new source; keep creative record and audio unchanged unless user intends otherwise, then re-review. No old approval or evidence is reused. For complex edits use the appropriate owner route and compare actual changes.
