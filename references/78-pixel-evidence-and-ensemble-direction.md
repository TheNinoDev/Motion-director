> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V42 — executable director's contract (read first)
This is the current operational route. Older documents are feature references, not competing primary workflows. Your job is a real finished video, not an impressive list of effects or a fake score. No historical reference media required. If user asks only for an effect test, label it a study; never confuse it with an ad. Maintain canonical source JSON, creative record and immutable previous revisions. Use the user's actual product and brand; never clone the sample layout as a new commission.

## Step zero: choose a task and load just enough context
- Full ad: product intake (01), copy (02–04), audio/rights/provider workflow (20–25), then this guide. One truthful central claim, one human hook, one visible proof, one ending. Preserve exact user-tested voice prompt in guide 24. Need real evidence, actual authorized audio, and listen before export. Do not invent a proof or falsely claim to have heard anything. If media/rights are missing, make a labeled draft and explain blocker.
- Modify existing ad: read canonical source and inspect affected preview range, keep audio, wording, aspect ratio and approved elements locked. Create new revision; never edit prior evidence. Use V41 repair only on explicit selection. Preserve source and unaffected parts.
- Technical motion: choose existing layer/renderer and run the smallest functional example. Use `python scripts/director_v42.py catalog` for ensembles. V41 components, V40 continuous paths, V39 state-aware, V38/V37 macros and workbench primitives remain available. Use appropriate catalog, not all at once. GPU/CPU guide 71; verify physical GPU before speed claims. Font guide 70: check installed face and license; no font software bundled.

## Creative decisions: use this exact sequence
1. Record target viewer, what changes for them, actual product source, visual proof, locked words, audio and destination. Choose exactly one main story. Avoid invented benefits.
2. Develop three genuinely different visible concepts (e.g. action demonstration, semantic transformation, numeric scale comparison). For each explain the opening image, what changes visibly, the payoff, why it fits this product and its weakest point. Reject any idea that could be pasted unchanged into another product's ad. Avoid a question-only hook followed by a generic hero object.
3. Commit one visual grammar: base palette, accent, type roles, light contrast, geometry and persistent motif. Test at least two native styleframes with actual text. Choose one dominant subject per moment. Give supporting motion a reason; avoid ubiquitous motion and arbitrary effects. Do not force glass, chrome, jelly or CGI; flat design often wins. Render at least two competing options if choosing a material or type treatment.
4. Map voice/music to picture beats, but not one slide per sentence. Write each beat as **visible subject + meaningful verb + resulting state**. Example: not “show UI with zoom”; instead “cursor selects a real filter, the result list contracts, the selected row becomes the next frame's anchor.” Choose one main action, one secondary cue at most; alternate active bursts and readable rests. Establish active time, screen position, parent, camera move, in/out velocity and handoff. Bind beat `layer_ids` to real visible drawables (not group-only placeholders). Actual proof must be visible and legible, not just a claimed screenshot name.
5. Use editable timeline layers and namespaced components. Use parent transforms for shared motion. The 4 ensemble recipes below produce tracks; use separate parent/child tracks for overlapping motions and never silently override a property. Check choreography, not counts. Use safe composition relative to 720×1280 design coordinates; verify native export (1080×1920). Default diagnostic safe margins are heuristic, not an official platform spec; adjust composition for actual publishing UI.
6. Execute the production sequence. Fix actual issues, not merely a checklist. Each review observation names time/layer, visible issue or successful outcome and reason. Compare before and after. No invented metrics, arbitrary quality percentages, or auto-approved gates.

## Ensemble recipes
`choreography` is an optional root list on V41-compatible source. Catalog provides exact fields. Use 2–24 distinct siblings sharing parent coordinates. Existing tracks on written properties are rejected. All times lie within active intervals; stagger delays start but ends synchronize. Every recipe begins from authored scalar state, not hardcoded center. Smooth interpolation sampled at 4× FPS; inspect rapid motion. No physical collision.
- `fan_out` — x/y/rotate: fan items from their starting states to a spatial arc; center, spacing, rise, angle, stagger. Use where separation conveys difference. Negative rise/spacing are allowed for reversal.
- `gather` — x/y/scale: concentrate several items into a row at a chosen center, spacing and scale. Do not stack legible text on top of other text.
- `wave` — y: a phase-staggered, windowed oscillation with rest at beginning/end. Use for a meaningful signal, not endless decoration.
- `orbit_exchange` — x/y: rotate existing positions along a shared ellipse. Start on the specified ellipse; degrees determines direction. No simulated depth ordering, so manually inspect overlap.
To combine two recipes writing the same property, author one explicit continuous path, or animate separate nested groups. Don't assume sequential recipes overwrite safely.

## Run exact commands (from skill root)
```
python scripts/production_v42.py start examples/director-v42.json examples/creative-v42.json work/study42
python scripts/production_v42.py next work/study42
python scripts/production_v42.py preview work/study42 --size 720 --backend auto
python scripts/production_v42.py pixels work/study42
python scripts/production_v42.py review-template work/study42
python scripts/production_v42.py gate work/study42
```
For real product replace both example inputs with actual source and creative JSON; add `--audio path/to/authorized-mix.wav` on start. Use `next` to identify the next permitted step. Preview, then pixel comparisons, then manually inspect full playback, audio and native stills. The `pixel` directory has triptychs: left actual frame, center same frame with chosen drawable omitted, right colored measured delta. Compare with intent; a masked/occluded or low-contrast object can produce zero contribution. Text contribution outside default margin may be a deliberate oversized crop. A lens can affect areas beyond the object. This is CPU single-time RGB differencing (threshold 10/255), not OCR, alpha coverage, exact preview-frame provenance or proof of art quality. Actual review still required. Use `scripts/pixel_review_v42.py render PLAN REQUESTS OUT --size 1080` for custom frame/layer checks (JSON array of `{ "frame": 90, "layer": "headline" }`). `verify` checks fingerprints. Up to 32 targets, one main drawable plus optional text per beat. Long timelines with >32 beats must use the previous route with separate section reviews, not pretend the limit vanished.

## Repair decision table
| Symptom | Required investigation | First correction |
|---|---|---|
| Cut feels harsh | last outgoing, overlap midpoint, first incoming; direction and speed | preserve shared anchor; begin incoming movement before outgoing stops |
| Text seems missing | RGB triptych, ancestor opacity and matte, native still | correct actual covering layer, reveal or contrast; don't just increase font |
| Text clipped | sample native frame, intended crop, platform overlay | move hierarchy inside safe region, adjust max width; preserve text |
| CGI edges rough | native lossless PNG, atlas and antialias, light | increase internal quality; verify native pixels not just encode |
| Glass too busy | inspect refracted text and underlying proof | reduce strength, frost, or remove; use solid only for motivated metaphor |
| Jelly looks floaty | check cause, mass/impulse, recovery | use contact solver for a wall, tune damping; don't invent collision capabilities |
| Repetitive frames | check story event and motif | replace weak composition/idea rather than add random zooms |
| Audio jump or off-beat | listen actual track and compare onset candidate | adjust cue or mix, keep narration intact; transients are not guaranteed beats |
| Product proof unclear | inspect source & actual visible proof | show genuine action or result; never fabricate UI functionality |

## Release rules
Review template starts pending. Inspect actual PNG triptychs, full preview and audio. Mark pass only after direct evidence; a warning can be `intentional` with a concrete reason, otherwise repair canonical source, new session and rerender. Never mark intentional merely to unblock. `gate` requires pixel report hashes and every prior V40 check. Then `upload` (1080 width high profile), optional `master` (RGB lossless), then `verify-export` and inspect final output. Do not bypass by calling old export CLI for V42 job. If real validation fails deliver labeled preview and state blocker. User should receive actual MP4, source project and concise honest limitations, not just technical claims. The gate is a self-attestation and file-integrity check, not an aesthetic certification or independent reviewer.
