> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V49 — current concise operator manual

## Follow exactly the appropriate branch
- Script/voice/music only: phases 1–3 in `84-production-phases.md`, no rendering requirement. Use the preserved exact voice prompt when appropriate. Research actual music and rights; never invent sources or audio availability.
- New commercial video: inspect product proof, develop three distinct concepts, choose one feature and truthful visible result, get authorized voice/music as needed. Use the sequence schema from `85-sequence-direction-v48.md`. For real exports use the gated production route below.
- Revision: obtain actual canonical source and last accepted media, capture snapshot before editing, define narrowly allowed changes, edit to a new source, compile, capture and compare, render affected and neighboring intervals; do not overwrite original approval or mutate user assets. Do not fabricate a missing source.
- Effects, 3D, collision or lettering demo: use the applicable renderer; a test is not a real advertisement. Don't use the product workflow to force a VO/music choice on a technical test.

## Make decisions from the picture, not the recipe name
For each beat write: what the audience understands, what they actually see first, what changes, why it changes, final state, and shared next-shot anchor. Define one main action, supporting action(s), and optional detail; select a clear focal point first. Plan adjacent moments together. Do not assume one sentence = one shot. Use image inspection and actual playback. Avoid fixed mandatory effect counts, repeated zoom/fade, logo intros, fake product limits, random particles, bouncing all objects, uniform chrome, template copy, excessive text. A clean quiet hold is valid when its reading or emotion is deliberate. If a detail should be prominent, reposition/crop the actual product, not a fake dashboard or invented proof. If the title handoff briefly overlaps, separate it spatially, use a matte, or stagger the exits; verify the middle frame as well as both endpoints. Avoid arbitrary simultaneous motion.

## Choose exactly supported tools
`python scripts/route_v49.py motion work --source examples/director-v49.json --creative examples/creative-v49.json --layer title2` prints current commands and relevant guides. Use exact real paths, not example copy in an advertisement. Tasks: advertisement, revision, motion, glass, type3d, jelly, collision, audio, gpu. Read only selected feature docs; earlier version entrypoints are historical. `python scripts/director_v49.py catalog` lists 16 built-in sequence definitions (8 from V48 + 8 new); all old actions and recipes are separate and remain available.

| Recipe | Required initial state and intended use |
| --- | --- |
| masked_handoff | Two flat drawable layers; incoming opacity/reveal 0, outgoing visible. Entry and exit x in same local coordinate space. Inspect overlap and correct actual geometry. |
| press_release | Existing scale within bounds; negative compression and small positive lift. For short symbolic button response, not physical contact or pressure simulation. Contains click SFX. |
| light_answer | Compatible solid or metallic 2D text with light control; label initially hidden and optionally blurred. Light alone is not a meaningful product state. |
| depth_handoff | Two compatible layers with pitch/yaw support; incoming initially rotated/hidden. Use matched visual size and purposeful camera angle. |
| proof_detail | Group or drawable product plus distinct initially hidden annotation. Set zoom and x/y in product's local coordinate system; preserve aspect ratio and inspect the real UI. |
| settle_pair | Two layers with free scale lanes. Small deltas; stagger follows visual hierarchy. |
| trace_then_label | First layer uses vertical reveal, not vector trim-path; initialize reveal=0. Label begins hidden. For actual path drawing use V37 path_draw or existing trim controls. |
| quiet_recede | Drawable with supported blur, scale and opacity; remaining focal object must stay readable. |

Example instance (real IDs and time anchors required):
```json
{"id":"press1","recipe":"press_release","marker":"click","offset":0,"duration":0.7,"bind":{"object":"button"},"params":{"compression":-0.06,"lift":0.02}}
```
V48 custom recipe names override any same-named V49 addition for backward compatibility. V48 custom-library size limits still apply to the combined used definitions. Use active intervals, local coordinates, correct units (seconds; frame-quantized) and actual valid properties. A recipe only generates keyframes, not aesthetic quality.

## Command sequence
1. `python scripts/director_v49.py diagnose SOURCE.json` — fix reported cause. `python scripts/director_v49.py capabilities SOURCE.json LAYER_ID` — supported and occupied lanes, possible slot roles. This is a compatibility hint, not a time-conflict guarantee.
2. `python scripts/director_v49.py inspect SOURCE.json` — inspect resolved markers/actions/sounds. Compile to a new filename if needed. Never edit expanded plan directly.
3. `python scripts/production_v49.py start SOURCE.json CREATIVE.json WORK [--audio BED.wav]` (omit brackets; include authorized aligned bed for real ads). Use a fresh directory. `next WORK` prints exact next argv; execute it. Review preview and native stills. `preview WORK --size 720 --backend auto` is a useful default; final width 1080. CPU when CUDA unavailable; use actual telemetry. No claims about GPU speed without hardware benchmark.
4. Review complete playback/audio; inspect pixel, transition, flow, cadence, audio and cue evidence. Run `advice WORK` for specific diagnoses. A pending item is not passed. If you cannot inspect or hear a result, disclose and leave pending. Don't set all passes programmatically.
5. Repair in new revision, repeat checks. Use `gate WORK` before upload/master. `verify-export WORK` checks actual artifacts; inspect final exported video and audio again. Deliver actual files and editable source package. Technical approval is not creative approval.

## Explicit revision contract
Capture BEFORE changing any files (including image/audio bytes):
```
python scripts/revision_guard_v49.py capture old.json before.json --creative old-creative.json --audio original.wav
python scripts/revision_guard_v49.py capture new.json after.json --creative new-creative.json --audio original.wav
python scripts/revision_guard_v49.py compare before.json after.json --allow layer:headline:size --out diff.json
```
Omit optional audio/creative flags only if absent or irrelevant; include both sides consistently. Use explicit allow tokens from the requested change, such as `layer:hero:scale`, `marker:arrival`, `sequence:arrival1`, `asset:image:product`, `layer_order`, `audio_cues`. A changed file hash at an unchanged path is a real change. Copy/relocation appears as a path change even when bytes match. Compare exit 2 = unexpected compiled/asset changes, read report and fix canonical source or confirm actual intended scope. Do not expand allowance simply to pass. Snapshot method cannot reconstruct former asset bytes if captured after edit; store backups separately when authorized. System font aliases, renderer binaries and undeclared resources are not fingerprinted. Source hash changes are reported; same compiled result with different source is not automatically blocked. Inspect actual render before/after, including neighbor frames and sound. Allowlist is not automatic approval or a security boundary.

## Failure handling with concrete actions
- Unknown prop/role: `catalog` and `capabilities`; never invent fields. A recipe using an already-occupied lane may conflict; inspect source owner and resolved windows. If one writer is needed, use parent/group or combine intended sequential motions on one lane.
- Cue too short: choose longer interval; pulse needs >=2 picture frames. Never hide invalid timing with FPS changes.
- Unnatural motion: inspect beginning, peak and settling; correct speed, easing, shared direction and time anchors. Use actual continuous path for through-motion; use contact solver for collisions, not squash preset.
- Unreadable title: compare actual fonts with same text, measure safe area and native resolution. Fix spacing and sizing, not blanket blur. Premium 3D: correct normals, bevel, edge sampling, contrast, and inspect native PNG at multiple angles.
- Cheap visual: improve concept, visual hierarchy, clean local palette and real product framing first. No forced glass/jelly/CGI. Different products need different visual stories. 
- Unclear audio: inspect actual mix, verify rights, adjust named cues and balance speech; waveform metrics do not prove listening or quality.
- Missing capabilities: use existing compatible primitives, or honestly report missing feature. Never rewrite good renderers or bypass validation to hide a failure.
