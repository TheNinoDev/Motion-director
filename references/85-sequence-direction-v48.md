# V48 production contract — reusable cue sequences

Read the short root SKILL first. This guide extends rather than replaces the actual rendering, rights and review requirements. For audio and full production phases use `84-production-phases.md`; for low-level markers and older rules use `83-named-cue-direction.md` when needed. All paths relative to skill root.

## Exact decision rules

| Visible task | Choose | Do not choose / failure check |
|---|---|---|
| Same reaction on several objects | `sequences`, bind distinct actual layer IDs | Do not duplicate dozens of raw keys. Look at active and parent intervals. |
| Click with visible response | V45 gesture + gesture marker + `contact_feedback` or `status_reveal` | Do not animate a halo if no real result occurs. Check pointer hotspot and visible outcome. |
| Two titles exchange | `title_handoff`, set actual `exit_y`, `enter_y` | Do not assume sample coordinates work for a different design; test mid-transition for overlapping letters. |
| Attention shifts | `focus_exchange` on compatible layers | Do not dim useful evidence below readability. |
| Object arrives | `arrival_accent` for a small pulse and sound | Not contact physics. For collision use softbody solver; for continuous path use Hermite. |
| Several layers respond in order | Author `sequence_library` definition with normalized phases | Do not build recursive presets or use guessed renderer keys. |
| Sound tied to an actual event | `impact_sound`, `click_sound`, or raw V47 sounds | Don't play sound on every movement. Check actual mix, rights and onset. |
| Change timings | Move marker, instance offset or duration; compare compiled revisions | Do not individually retime all sound/action tracks. |
| Non-cue features | V47 lower-level cues, V36 actions, V40 paths, V41 components, V42 ensemble, V45 gestures | Do not force every animation into a sequence. |
| 3D and premium materials | Guides 67–71, renderer READMEs, native PNGs | Check bevels, edge quality, material, light and actual backend. |

## Syntax: copy this pattern, not the demo's design

```json
{
  "markers": [{"id":"arrive","time":1.2}],
  "sequences": [{"id":"feedback","recipe":"contact_feedback","marker":"arrive","offset":0,"duration":0.5,"bind":{"halo":"actual_halo_layer"},"params":{"flash":0.65,"grow":0.08}}]
}
```
The layer must exist, with compatible static/available lanes, and be active throughout the action. In the example the halo starts with opacity 0 and scale 1. Pulse adds its offset and returns; values must remain in range. `params` may be empty to use defaults. `bind` must include every named slot exactly once, with distinct layer IDs. An audio-only sequence uses empty `bind`. All fields are required. The sequence id is unique. Offsets and duration are seconds, phases are fractions 0..1 of the duration; compiler quantizes endpoints to frames before calculating action length. Negative offsets allowed only if resulting full window is inside picture. No zero-length phases; pulses require two frames. One property lane can have sequential nonoverlapping actions; separate properties may overlap. Older V47 cue limits apply globally: 32 markers, 128 expanded cue actions, 200 expanded sounds, at most 64 phases per lane including holds. No silent clipping or conflict overrides.

Custom example (not a rendered design):
```json
{"sequence_library":{"feedback_pair":{"slots":["indicator","label"],"params":{"level":1},"actions":[{"slot":"indicator","start":0,"end":0.6,"op":"animate","values":{"opacity":"$level"},"ease":"smooth"},{"slot":"label","start":0.2,"end":1,"op":"animate","values":{"opacity":1},"ease":"smooth"}],"sounds":[]}},"sequences":[{"id":"reveal_result","recipe":"feedback_pair","marker":"arrive","offset":0,"duration":0.5,"bind":{"indicator":"real_indicator","label":"real_label"},"params":{"level":0.9}}]}
```
Definitions use `slots`, numeric default `params`, `actions`, `sounds`. Phase values may contain a numeric literal or `$parameter` (no expressions). All slots and params must be used. `animate` sets absolute, `relative` adds delta, `pulse` adds then returns. Sound phases specify start/end/kind/gain_db/pan. Get the exact complete built-in catalog with `python scripts/director_v48.py catalog`. Custom definitions cannot shadow built-ins. A sequence is a reusable *motion mechanism*, not a complete creative concept.

## Run commands in this order

1. Create original product-specific source and creative record (use V48 examples only to learn schema). Choose actual timing from voice/music/interaction, not a guessed beat. For real ads follow phase 1–3 before final.
2. `python scripts/director_v48.py inspect SOURCE` — check all resolved markers and actual action windows. `python scripts/sequence_audit_v48.py schedule SOURCE --out NEW_REPORT.json` gives instance/layer/action/sound detail. Fix source and retry if compile fails. Do not alter expanded files.
3. `python scripts/production_v48.py start SOURCE CREATIVE WORK [--audio AUTHORIZED_BED]` — new work directory, not old output. Run `next WORK`, execute its argv. For preview details use `preview WORK --size 720 --backend auto`; native controls are 1080, not upscaled preview. CUDA requires actual hardware checks; use logs, do not promise speedup.
4. Inspect actual preview from start to end, audio and cue sheets. A pending decision is not a pass. Existing V47 review stages and export gate remain. Use `advice WORK` for concrete diagnostics. If visual or audio playback cannot be inspected, keep review pending and tell user.
5. For revision: `python scripts/sequence_audit_v48.py compare OLD_SOURCE NEW_SOURCE --out NEW_DIFF.json`. Read changed layers, properties, markers, sequence windows and sounds. Reject unintended changes; compare actual renders too, including unchanged asset paths which may hold different bytes. New source/revision directory required. Do not allow old evidence to approve a new rendering.
6. Deliver only after full checks. Include actual MP4 and editable source/assets as allowed. Optional lossless master for quality diagnosis. If blocked, provide clearly labelled preview and describe blocker, not an imaginary final result.

## Repair matrix

- Phase too short: increase instance duration or change fractions; never clamp to one frame without considering timing. Pulse requires two frames.
- Unknown parameter or slot: print catalog, fix exact spelling and bind IDs. Do not guess another key.
- Overlapping or occupied lane: identify all owners in source; move only intended cue, or use another compatible property/group. Never discard accepted animation.
- Changed gesture identity: inspect actual gesture events and rebind expected operation/target. Same op and target can occur repeatedly, so check the actual moment.
- Title overlap: inspect mid-frame native PNG and playback; update exit/enter position, mask or timing while preserving literal copy.
- Weak concept: change actual action and visible result; a new preset does not fix a weak narrative. Strong clean compositions do not need an obligatory effect count.
- Unnatural bounce: pulse is not physics; choose contact solver for impact, elastic recipe for visual response; inspect speed and damping.
- Cheap 3D: render high-quality native still, correct bevel/normal/edge/lighting; lossless only diagnoses compression, not geometry.
- Bad beat: use supplied aligned audio, actual audible accent and a named marker; waveform isn't a listening test.

## Acceptance criteria for agents

A real ad has an original product-specific concept, actual proof, clear natural script and real authorized media, legible type, intentionally directed motion, no unintended black gaps/clipping, no fake product functions, and verified export. Review every beat and cue that affects the story. Preserve the user's approved decisions. Technical metrics only locate candidates for review, not aesthetic success; do not assign arbitrary NOIZ percentages or autoapprove. A technical study can be silent or SFX-only, but must be labelled as such. User-supplied duration/aspect constraints override defaults. The original reference videos are not needed at runtime.
