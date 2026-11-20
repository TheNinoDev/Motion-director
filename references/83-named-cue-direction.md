> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V47 — named-cue production contract (primary route)

## Read this first; do not read 400 files

Your task is to make an original, specific, polished video, not to reproduce FORM or any study. The user provides product material, constraints and any required audio. You must make the routine creative decisions, write and execute source JSON, inspect actual results, repair actual defects and deliver verified files. The current user request and this guide govern; older guides are reference material only. Keep accepted copy, art direction, sound, source, FX and unaffected animation unchanged unless the user asks otherwise. Never require the old reference videos. Never use a test result as evidence of design quality.

## Mandatory order and decisions

1. **Choose mode:** script only / real advertisement / fictional technical study / revision. Script-only ends with copy and audio direction, not a video. For revision inspect real source and last accepted video. If no accepted source is accessible, say so and ask for that source; do not recreate it from memory. For marketing inspect the actual product or the user's supplied description/screenshots. Ask only for missing essentials once (product proof, authorized audio). Verify what can actually be shown; do not invent capabilities, follower counts, prices, or testimonials. Do not edit the live product to manufacture evidence.
2. **Write the creative record** (syntax in `examples/creative-v47.json`). Propose three concepts with different physical/visual mechanisms, not three colorways. Select the one specific to this product. Write one problem, one change, one visible result, and an earned CTA. Do not list every feature. Do not open with a logo by default. For real narration use `SKILL.md` phases 1–3 and guides 20–25: natural spoken copy, licensed music, actual aligned voice; preserve the exact user-supplied voice design prompt. Research current song availability only if relevant. No fake listening, no rights assumptions. Choose an appropriate length based on actual speech, not a fixed demo duration.
3. **Direct every beat:** use a real object/action/payoff. For each beat write the starting state, dominant object, actual transformation, support motion, result, and outgoing anchor. Decide where the eye should go first; never animate decoration simply because an effect is available. Vary shot size/composition and motion density. In a smooth handoff establish incoming motion before outgoing motion finishes, match direction and scale or intentionally cut for a stated reason. Avoid black/empty gaps and overlaid unreadable headlines. Hold product evidence long enough to read. Use an intentional layout and type system; render at least two suitable styleframes with the real wording, choose based on actual rendering. No mandatory glass, chrome, particles or jelly.
4. **Author source:** use `director_v47.py catalog`, the syntax study, and only the relevant feature guide from the table below. Keep named semantic markers for related events. Use named cue actions instead of independent hand-timed keyframes when multiple objects react to one moment. Pick one owner for each layer property, with different lanes allowed in parallel. Don't move an entire shot to fix a single late reaction. If you need an unsupported effect, compose existing primitives or a local procedural asset rather than faking support; inspect output. Explicitly use real screenshot/image assets for product proof. Study layouts are not templates to copy.
5. **Compile/check:** `director_v47.py inspect` prints resolved marker frames and reactions; use it before starting. Set correct layer lifetimes and group lifetimes. Resolve conflicts in canonical source, not in expanded output. `production_v47.py start` validates and creates a new work directory, never overwrites one. Use actual authorized aligned audio for an ad. The named cue stem is only SFX, not a replacement for VO or music.
6. **Execute, not describe:** from skill root repeatedly run `production_v47.py next WORK` and execute the argv returned. Watch complete preview and listen to actual audio if you have playback capability. Inspect per-beat pixels, cue sheets, boundaries, flow and cadence, native 1080px control frames for fine text/CGI, and actual decoded output. A frame sheet cannot substitute for playback. A waveform cannot prove intelligibility or sync. If playback is unavailable, state it and leave the relevant review pending. No self-approval without inspection.
7. **Repair:** use `advice WORK`; choose the earliest cause, smallest effective change; edit canonical source into a new revision, rerender and compare the changed interval AND unaffected locked work. Fix the worst 3 *actual* issues if present, not arbitrary values to meet a quota. Never delete working motion to pass a tool. Stop when the specific defects are resolved, not when the file count grows. If a failed render left a directory, preserve it and create a new revision. Do not circumvent the gate by running a lower-level export command.
8. **Release:** inspect, explicitly record the review, pass the gate, run upload/master and verify-export. Re-inspect the final exported picture and sound. Deliver final MP4 (1080×1920 default), editable source/assets where authorized, optional lossless master, actual limitations and any pending approval. Never label a study as an upload-ready ad. Technical verification does not certify premium design or rights.

## Tool routing — decision, exact action, repair

| Goal | Feature / guide | First thing to check |
|---|---|---|
| Reactions to same visual event | V47 `markers`, `cue_actions`, `cue_sounds` | Named cue frame, clip bounds, lane ownership, actual result |
| UI click / drag | V45 `gestures`; guide 81 | Target and pointer same parent, hotspot and real result visible |
| Continuous path | V40 Hermite paths; guide 76 | Tangents at shared endpoints, direction, velocity |
| Multiple instances | V41 components; V42 ensembles, guides 77–78 | Parent active, individual IDs, coordinated movements |
| Mask / reveal / transition | compositor, V43–44, guides 79–80 | Real frame before/during/after, hold outgoing anchor |
| 3D glass / text / metal | guides 67–69 and compositor READMEs 31–33 | Geometry, smooth normals, bevel, lighting, native PNG |
| Jelly / softbody | guide 70 and `elastic_recipe.py` | Impulse, weight, damping; do not call analytical deformation full physics |
| Font choice | `font_library.py pairs MOOD`, `list --installed` | Real glyphs and legal font, rendered alternatives |
| CUDA/device | guide 71; `gpu_doctor.py`, `--backend auto` | Actual backend log, CPU fallback; no guessed performance |
| Music / voice | guides 20–25, audio intake | Actual authorization, spoken timing, audible mix |
| Review/repair | `production_v47.py advice WORK` | Exact layer/attribute/time and actual evidence |

## Named cue schema and usage

Add three optional arrays to existing V46 source JSON. `markers` may specify absolute seconds, a verified gesture index or another marker plus a signed offset. References may appear before the marker they depend on. Names are unique, and cycles, out-of-picture intervals, malformed values and unknown markers fail. The compiler rounds each time/offset to the nearest picture frame independently, so subframe offsets may not sum exactly as expected. Inspect actual resolved frames. Max 32 markers, 128 cue actions, 200 cue sounds; each generated property program has at most 64 phases including holds. Split a large project into meaningful separate local motion tracks where needed. Do not create needless markers for every frame.

```json
{
  "markers": [
    {"id":"drop","gesture":{"event":2,"expect_op":"release","expect_target":"card1"}},
    {"id":"feedback","after":"drop","offset":0.12},
    {"id":"hook","time":0.2}
  ],
  "cue_actions": [
    {"marker":"drop","layer":"halo1","offset":0,"duration":0.4,"op":"pulse","values":{"opacity":0.8},"ease":"smooth"},
    {"marker":"feedback","layer":"status1","offset":0,"duration":0.3,"op":"animate","values":{"opacity":1},"ease":"smooth"}
  ],
  "cue_sounds": [
    {"marker":"drop","offset":0,"duration":0.2,"kind":"impact","gain_db":-20,"pan":0}
  ]
}
```

`animate` sets an absolute value; `relative` adds a delta and retains result; `pulse` adds offset at midpoint then returns. Zero-duration actions fail; pulse needs two frames. Independent lanes on same object may overlap, but actions on same property may not overlap (touching endpoints allowed). The compiler creates holds between actions so initial values and prior absolute results persist. The complete property lane must be free of older writers; existing raw keys, gestures, macros or V46 reactions on other properties are preserved. Do not remove old tracks blindly. V43 ranges/easing apply; use `director_v43.py catalog`. Check parent lifetime and masking in rendered view; frame-local compilation checks cannot guarantee visibility. After reordering gestures, inspect exact indices; same op/target repeated can still be ambiguous. Use `director_v46.py events` on a compatible source, or `director_v47.py inspect` on V47. Move a cue marker or ancestor instead of editing all dependent times; recompile and inspect because changed timing may cause intervals to overlap or exceed the film. Non-gesture markers can drive an edit accent, a title move, a product reveal, a light cue or a sound.

## Low-context CLI sequence

```bash
python scripts/director_v47.py catalog
python scripts/director_v47.py inspect examples/director-v47.json
python scripts/production_v47.py start examples/director-v47.json examples/creative-v47.json work/study47
python scripts/production_v47.py next work/study47
```

Actual project: replace both example paths and include `--audio path/to/aligned-authorized-bed.wav` for a real ad. Use `--size 720` on `preview` for detailed CPU-friendly playback, use native stills for critical text/CGI. Stage order: preview → pixels → transitions → flow → cadence → audio-review if audio → cue-review → review-template → gate → upload/master → verify-export. `cue-review` creates before/during/after sheets for each *used* marker, with planned action/sound fields and SHA-256 bindings to decoded video and evidence. These are samples; verify actual movement and sound independently. No assertion of automatic aesthetic approval. The `expanded.json` fingerprint prevents silent alteration of cue review targets. For a legacy source with no named cues the sheet report is empty; prior gates remain. A new revision needs new evidence.

## Quality choices: good versus bad

- Bad: every motion independently timed to a guessed beat. Better: establish the visible event (contact, result, word, documented musical accent), name it, derive a reaction and sound with justified offsets; use actual recorded audio timing for an ad.
- Bad: play a pulse on a group every second. Better: give a one-time visual response to meaningful contact and a persistent state change, not perpetual decoration. One strong action plus one support motion is a good default, not a ban on complex scenes.
- Bad: two type layers both vanish halfway through a smooth transition. Better: establish an incoming positional/mask transition while the outgoing is still visible, use complementary movement and avoid glyph collisions. For an intentional hard cut don't add a fake overlap.
- Bad: increase blur, bloom or compression to hide jagged 3D sides. Better: inspect native PNG, increase geometry/atlas sampling, set suitable bevel and key/fill lighting, then choose export quality.
- Bad: render 3D text for every sentence. Better: use dimensional text for short hero words, clean flat type for readable proof, create original mesh/volume only when it adds meaning. Preserve free space and clear contrast.
- Bad: mark every test pass without playback. Better: record a specific actual visible observation (time, subject, action, result), note an actual issue as repair, keep review blocked until inspected and resolved. No fixed threshold proves creative quality.
