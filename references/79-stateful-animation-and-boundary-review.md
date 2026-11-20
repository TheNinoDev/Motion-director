> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V43: low-context execution contract (read this first)

## Primary route, not just another list of features
The task is to produce original, verified videos, not to maximize effect count. The user supplies minimal product/source information. A weak agent must not implement its own renderer or copy the example aesthetic. The canonical input is the authored spec + creative record + authorized media. Preserve source, timing, assets and explicitly locked text through every revision. Never require the old NOIZ clips. Use older guides only when the current tool needs a specialized feature. Commands are relative to the skill root; use `python` or the available Python 3 executable. Install dependencies via existing setup/doctor. Use `--backend auto`; if CUDA requested, run `scripts/gpu_doctor.py --test` and report actual hardware, never invent speedups.

## Decision table: turn vague feedback into a precise edit
| User says / observed defect | First action | Pass condition | Do not do |
|---|---|---|---|
| boring, generic | identify one product-specific visual event and its outcome, build three alternatives; choose one with actual evidence | can describe visible cause and effect without effect names | add random particles or copy FORM |
| choppy, weird transition | use decoded boundary sheet; compare previous and next positions, directions, speed and visibility | no unintended blank, jump, duplicate silhouette; intentional cut has reason | crossfade blindly or hold outgoing until incoming is invisible |
| motion stops repeatedly | multi-phase program for one layer; use continuous_path if passing waypoints without stopping | inspect real speed and return on playback | separate overlapping writers on x/y |
| text ugly | choose two installed faces using `scripts/font_library.py`; inspect native sample and contrast | legible exact copy at display size, intentional crop only | fake font names or stretch letters |
| glass feels cheap | select solid glass_object if volume required, lens only for optical adjustment; simplify environment, inspect refraction | distinct readable edge, meaningful optical interaction | use glass on all shots |
| jelly unnatural | set impulse/contact speed/damping based on motion cause; inspect after-contact recovery | no unexplained squash or snapping | call deformation full physics when it is analytical |
| CGI edges rough | full native PNG, increase quality/antialias/atlas, compare light; lossless master to isolate compression | smooth silhouette and readable material at output size | claim upscaling fixes geometry |
| product proof weak | capture actual UI and demonstrate an actual action/result | claim tied to verified source | fabricate screenshot or unsupported benefit |
| too busy | remove/quiet competing motion, select hero, negative space, preserve functional elements | eye reaches main message without hunting | remove locked assets or animations |
| export succeeded but looks bad | review actual frames and playback; repair canonical spec and rerender in new directory | both technical and creative review, honest limitations | mark all review flags intentional automatically |

## Concrete creative instructions before coding
1. Extract actual pain point, user, differentiator, proof, brand and desired distribution. For public ads verify music/voice rights. Use real audio and phrase-level timing; do not synthesize fake approval. Follow voice guides 21–25, font guide 68 and latest font catalog. If source inaccessible, request only the missing essential information. For silent technical studies, label as such.
2. Describe three genuinely different visual concepts: (a) visible product interaction and its result; (b) visual metaphor with physical action linked to product value; (c) typographic or editorial contradiction with evidence. Select the highest relevance and strongest visual cause-effect, not the most effects. Each concept needs a failure risk. No copying example branding, timing, palettes or arbitrary CGI.
3. Write one sentence per beat: "[subject] visibly [verb] because [cause], ending in [state]." Define primary action, secondary support, and outgoing/incoming anchor. If the same idea could advertise any random product without changes, rewrite it. Link actual layer IDs. Hook starts with meaningful action within first 1–2 seconds. Keep one message per beat; use genuine product interaction at the moment of proof, not a fake card. End with clear outcome, not a meaningless logo effect.
4. Compare alternative styleframes and fonts. Establish readable foreground, supporting contrast, consistent material role, reserved whitespace and intentional size hierarchy. Do not fill every empty region. Prefer 2D for normal UI, selective 3D for a meaningful reveal or metaphor. No mandatory glass/chrome/jelly.
5. Use one persistent timeline. If repeating structures, use components (V41). For groups use V42 choreography. If an individual property changes repeatedly, use V43 programs; if continuous travel through waypoints is needed use V40 Hermite. Use V36–V39 primitives and macro catalogs for other effects. Use direct valid timeline JSON for specialized features. Never invent unsupported options; inspect actual catalog.

## Stateful motion program: four stage types
Add `motion_programs` to the existing spec. One program per layer, one writer per property. Properties not in the program retain existing behavior. An existing track on a program property is rejected; use a group or deliberately migrate that track into the program. All times are absolute seconds; all end times monotonic and inside the layer active interval. The values start from authored scalar values (or exact defaults); the compiler carries the state from each stage. `pulse` reaches its configured additive offset at halfway, then returns to the current value. `relative` adds to the current value. `hold` carries every program property unchanged. The compiler writes global keyframes, which can be edited or rendered using the existing compositor. Smooth/quint/sine stop at stage boundaries by design, so use continuous_path for nonzero through-velocity (not solved by this compiler). `linear` may have abrupt velocity changes. The compiler deliberately rejects overshoot ease and enforces bounded values; use old advanced tools for intentional overshoot. Supported keys and ranges: `python scripts/director_v43.py catalog`.

```json
{"layer":"hero","start":0,"steps":[{"op":"animate","end":0.8,"to":{"x":360,"scale":1.15},"ease":"quint"},{"op":"hold","end":1.3},{"op":"pulse","end":1.9,"offset":{"scale":0.1},"ease":"sine"},{"op":"relative","end":2.6,"delta":{"x":80},"ease":"smooth"}]}
```

## Exact low-context commands
Use the example only as a technical smoke test. For production create your own source and creative JSON, and actual authorized audio if the mode is advertisement/revision.
```
python scripts/director_v43.py catalog
python scripts/production_v43.py start examples/director-v43.json examples/creative-v43.json work/study43
python scripts/production_v43.py next work/study43
python scripts/production_v43.py preview work/study43 --size 720 --backend auto
python scripts/production_v43.py pixels work/study43
python scripts/production_v43.py transitions work/study43
python scripts/production_v43.py advice work/study43
python scripts/production_v43.py review-template work/study43
python scripts/production_v43.py gate work/study43
python scripts/production_v43.py upload work/study43
python scripts/production_v43.py verify-export work/study43
```
The template begins pending. Watch actual preview, inspect every boundary/contact sheet and actual pixels; listen to full audio if supplied. For each boundary observation describe what is on screen and any mismatch or intentional cut reason. A large changed-frame fraction is only a prompt, not a defect verdict. A boundary summary measures decoded low-resolution RGB deltas; it cannot determine perceptual smoothness, contrast, velocity or readability. For real issues make a new revision from canonical source; do not simply mark pass. Native checks use original compositor `--at` and review targets; final upload at 1080, optional lossless master. Review final again. Never claim success from tests alone. If tools or media unavailable, clearly report blocker and provide verified partial output, not fabricated files. Do not automatically approve any review. V43 route supersedes old production routes for new projects; older projects remain supported.

The optional `advice` command links measured flags to source-layer IDs, relevant properties and evidence files. It does not guess a numeric correction, apply edits or approve a review. If there are no flags, manual review remains mandatory.
