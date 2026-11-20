> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V46 — event-driven direction, sound and low-context execution

## Read this first, then execute only the relevant branch

The goal is a distinctive, evidence-based, upload-ready short film, not a movie-like demo of the tool. The user delegates routine creative decisions. Ask once for genuinely missing product information or authorized audio; never ask the user to draw a storyboard or implement a renderer. Preserve locked copy, design, audio, timing and previous accepted work. All earlier references are feature documentation; this contract and the current user request govern new production.

### Minimal agent runbook
1. **Intake.** Read the supplied product source, identify one audience problem, one differentiator and observable proof. If actual source is unavailable, ask for the smallest usable alternative. Record which claims are verified; no invented metrics or screens. For a revision, locate actual source and establish locked vs changed fields. For a technical study label it explicitly, no false advertising claims.
2. **Concept.** Produce three genuinely different short concepts: actual interaction, product-specific physical metaphor, editorial contrast. Reject a concept if the same sequence with a renamed logo could advertise any product. Choose the one with the strongest visible payoff, not the most FX. Write natural hook, proof, payoff and CTA. See original intake/voice/music phases in SKILL.md. Do not replace supplied spoken words. Music must have appropriate rights; use actual recorded/authorized VO and align it before picture lock. A synthetic click stem is not a song or a spoken performance.
3. **Build.** Per beat write initial state → action → payoff → next anchor. Choose a dominant object and one support motion. Use real UI crops or genuine product interaction; 2D for text and UI, 3D only when the metaphor benefits. Use the routing table below. Make two type/material styleframes with actual wording, select one based on legibility and focus, not novelty. Use the existing 217-family font catalog; avoid copying example styles.
4. **Compile.** Copy a minimal example as syntax only; create original content. Run `director_v46.py events` to see actual gesture markers, bind reactions and cues to them. Start a new work directory using `production_v46.py start`. Never overwrite original project files, do not edit expanded plan by hand. If the compiler rejects a lane, move the reaction to a child or separate accent layer; never delete a working track solely to make compilation pass.
5. **Preview and inspect.** Re-run `next` for the next exact argv; execute every requested stage. Watch complete playback and listen to the actual mix; inspect per-beat pixels, boundaries, flow, cadence and audio. At each beat inspect beginning, action peak and result. Check 3D/text at native PNG resolution if needed. Do not use a quiet/moving threshold as aesthetic target. Do not invent a review, compare untouched locked sections as well as modified ones.
6. **Repair.** Use `advice` for evidence and time. Change canonical source only, preserve unrelated states; recompile in a new work directory. If no audio playback available, state the blocker; do not mark audio listened. After re-render, compare actual frames before and after. Stop revising when changes solve the stated issue instead of degrading good footage. Submit specific, honest review observations. Gate must pass before final export. Recheck the real output, audio rights, picture and sound; return verified video plus editable source and disclose limitations. A scratch preview is never a finished advertisement.

### Tool routing (examples are syntax, not design templates)
| Need | Use | Evidence / first fix |
|---|---|---|
| UI interaction | V45 `gestures` point/tap/drag | Cursor and target same local parent, visible state changes; watch release |
| Result on click/drop | V46 `event_reactions` | Bind to compiled event; avoid duplicate property writers |
| SFX follows picture | V46 `event_sounds` | Source timing + decoded waveform + actual listening |
| Continuous path | V40 `continuous_path` / Hermite | inspect endpoint tangents, shared anchor |
| Original shape choreography | V43 multi-phase / V44 accents / workbench | purposeful cause and result, not random bounces |
| Repeated parts | V41 components / V42 ensemble | shared group, independent overrides, no duplicated IDs |
| Glass/metal/3D type | V31–33 compositor volume and text3d | actual depth, appropriate material, lighting, native 1080px PNG |
| Elastic deformation | V34 presets; V33 contact solver | motivated impulse; use jelly only when justified |
| CPU/CUDA | V35 `gpu_doctor.py`; compositor `--backend auto` | read actual backend telemetry; no fabricated GPU support |
| Typography | `font_library.py pairs` and boards | verify local license, glyph coverage, render alternatives |
| Revision | inspect actual canonical source, new session | protect all unrelated copy, timing, FX, assets and audio |

### Event contract
`python scripts/director_v46.py events examples/director-v45.json` prints compiled event indices, operation, target, and exact seconds. Each optional `event_reactions` entry must have event (0-based), expect_op, expect_target, layer, delay, duration, op (animate / relative / pulse), values (property map), ease. Timing is relative to event. Animate sets absolute destination, relative adds delta, pulse adds offset and returns. One program per reaction layer in V46; use separate layers or explicit existing multi-phase program for multiple actions. Layers and ancestors must be visible when action matters; use bounded intervals; compiler enforces layer-local timing and free lanes, inspect ancestors with scene audit. Identity check prevents wrong operation/target after inserts. Duplicate same op/target event identity alone is not enough to disambiguate repeated events: after any reordering re-inspect event list.
`event_sounds`: event, expect_op, expect_target, kind, gain_db, duration, pan, offset. Six original synthetic kinds: click, impact, whoosh, chime, riser, drop. Offset from event is quantized to nearest frame; negative offset allowed for anticipation. Keep audible accents selective, usually quieter than VO. Default suggestion tap click -18 dB, grab click -24 dB, release impact -19 dB. Adjust after listening; do not apply blindly. No copyrighted audio reproduced by generator. A real ad requires actual authorized bed; source bed must align to picture within one frame when mixing SFX. Preserve source, isolated event stem and premixed result; gain is reduced globally if necessary for headroom. If speech loses clarity, lower SFX rather than moving unrelated picture. No automatic BPM or loudness claims. Waveform measures RMS/peak, not LUFS/intelligibility or proof that a sound actually syncs.

### Executable sequence (from skill root)
```
python scripts/director_v46.py catalog
python scripts/director_v46.py events examples/director-v46.json
python scripts/production_v46.py start examples/director-v46.json examples/creative-v46.json work/study46
python scripts/production_v46.py next work/study46
```
For real work pass original JSONs and `--audio work/aligned-authorized-bed.wav`. Use the returned argv repeatedly, then `advice`, inspect, revise if needed. Stages: preview → pixels → transitions → flow → cadence → audio-review if mix exists → review-template → gate → upload/master → verify-export. Do not bypass the gate using legacy commands. New sessions protect originals. Native stills/excerpts remain available via compositor CLI; picture-only excerpt never replaces audio review. Do not claim actual listening without playback capability.

### Positive/negative decisions for weak agents
- Bad: fading a label while a new logo pops up. Better: a dragged card lands in its correct slot; a short ring traces the actual state change, with one subdued release sound; the card remains the next anchor.
- Bad: click sound at every arbitrary transition. Better: one audible click at contact, distinct short confirmation at result, silence elsewhere unless music supports it.
- Bad: independent audio timestamp hardcodes after retiming gestures. Better: event index + expected identity, compile again, inspect marker and frame.
- Bad: every beat has same large headline and centered chrome object. Better: macro proof, close reading, semantic match, restrained dimensional hero at the one important moment.
- Bad: force all transitions to be smooth. Better: match position and velocity for continuation, motivated cut for contrast; inspect frames and sound around boundary.
- Bad: use bigger effects to cover unreadable UI. Better: crop to relevant action, adjust framing or font, hold just long enough to read; compare native frame.
- Bad: mark checks pass because tests pass. Better: provide real observation per cue/beat, preserve all evidence and disclose missing capability.
