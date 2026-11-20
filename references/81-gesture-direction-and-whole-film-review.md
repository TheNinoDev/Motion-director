> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V45 operational contract: purposeful interaction and whole-film review

Read this first for new projects. Use earlier guides ONLY as feature recipes. Do not load hundreds of files. This is a local programmatic workflow, not a GUI editor or generative-video service. Preserve user choices and existing good work. Never promise aesthetic parity from a test result.

## 1. Mandatory decisions before building

1. Determine whether the request is a full ad, a revision, or a technical study. For a full ad, inspect authorized product material, verify claims, choose one central benefit, and use a real authorized voice/music mix when called for. Follow guides 20–25 for voice, rights and speech alignment. Do not copy fictional demos into advertising. For a revision, identify exactly which content, timing, palette, and layer identities are locked.
2. Write three meaningfully different concepts (e.g. interaction, physical metaphor, editorial contrast). Reject concepts that can be used unchanged for an unrelated product. Select one that proves the actual benefit. Record the rejected concepts and why.
3. For each beat write an observable before state, action, after state and reason. Example: cursor drags a real screenshot card into a real slot, the second cell exposes a verified product result. Not: cards zoom and fade because the screen feels empty. A recreated UI must be grounded in screenshots or explicitly illustrative; never fake a working feature.
4. Set a dominant subject and visual scale at each moment, one secondary motion that supports it, and a readable negative-space region. Contrast dense moments with intentional holds. Do not add motion merely to avoid a low motion score. Compare at least two actual styleframes, two relevant typefaces (verify license), and for CGI two contrasting light setups. Use graphic 2D for ordinary product interaction; reserve 3D, chrome, glass and jelly for meaningful physical metaphors. No fixed material quota is a requirement.
5. Determine timing from actual approved audio; align key visual decisions with audible phrases and selected music accents. Use gesture markers as candidate click/grab/release sound cues, not a replacement for listening. Do not use a local scratch voice as the final commercial voiceover.

## 2. Select a tool, not a random preset

| Need | Use first | Why / stop condition |
|---|---|---|
| Show actual click, drag or selection | `director_v45.py catalog`, gestures below | Cursor must meet target at contact and remain there during drag; no real network/UI action is performed. Actual state changes must be authored separately. |
| Animate sequential states | `director_v43.py catalog` | Use one program per layer; do not overwrite an occupied property. |
| Persistent object moving through several shots | `director_v40.py catalog` | Shared Hermite path; use matched endpoints and review actual velocity. |
| Coordinated group positions | `director_v41.py`, `director_v42.py` catalogs | Use components/ensembles instead of duplicating tracks. |
| Impact, material movement | `director_v44.py catalog`, `elastic_recipe.py`, guide 70 | Choose motivated contact and damping; don't animate every object with a spring. |
| Optical or solid glass, type, mesh | guides 67–71 | Inspect native close-up, bevels, sampling, real geometry and ability to render. |
| Animated material or lens properties | `director_v38.py catalog`, compositor documentation | Use actual supported properties; distinguish screen refraction from physical glass. |
| Need GPU | `gpu_doctor.py --test` | Report actual backend. Simulator is not physical GPU proof. |
| Static direct-layer change | `source_repair_v44.py` | New canonical revision; no animated lanes or hidden cascading edits. For V45 gesture specs, edit canonical source explicitly and recompile with V45, not the V44 repair tool. |
| Quality issue during render | `production_v45.py advice WORK` | Inspect matching evidence, identify canonical layer owner, change only needed parameters, then rerender in a new work folder. |

## 3. Gesture compiler (new)

`gestures` is an optional top-level array in the normal authoring spec. Each controller has `pointer` and `steps`. All times are seconds. `point` moves to the target's local center; `tap` approaches, compresses and restores pointer and target scale; `drag` approaches, grabs, moves target and pointer along the identical quintic track and releases. Drag destination is **absolute in the shared parent coordinate space**, not a delta or screen pixels when parented. A group may be a target if it has a drawable direct child; its entire subtree moves and scales with it. This compiler supports 2D positions and simple affine parent groups, not perspective hit testing or real UI automation. A hollow circular pointer with a center hotspot works well. No automatic UI state is implied by a tap. Author the actual state changes through other supported properties/layers. No shared animation lane between gesture controllers; for independently moving targets use an explicitly authored alternative.

```json
{"gestures":[{"pointer":"cursor","steps":[
  {"op":"point","target":"tile","start":0.1,"end":0.8},
  {"op":"tap","target":"tile","start":0.9,"end":1.6,"press":0.9},
  {"op":"drag","target":"tile","start":1.7,"end":3.2,"to":[130,90]}
]}]}
```

Required: target and cursor are siblings, cursor later than target, their active intervals and ancestors cover entire action. A cursor requires free x/y/scale lanes; target drag requires free x/y, tap free scale. Use real authoring IDs. Time windows are non-overlapping; point >=6 frames; tap/drag >=12 frames. Press fraction .6–.99; destination local coordinate within +/-4000. Scale restores after tap. Drag begins moving at 53% of its interval and reaches destination at 88%; pointer and target share easing and endpoint. Multi-step gestures inherit positions from previous steps. `expanded.json` contains candidate `gesture_events` for grab/release/tap, use them for timed effects without blindly adding sound. Review contact against actual silhouette; pointer can still be hidden by later layers. A parent may move, but avoid perspective warps on pointer/target, as contact is affine center-only. If the action needs a noncentral hotspot, create a purpose-made group whose local origin is the intended hotspot or author independent tracks. For a real product use authentic UI captures.

## 4. Production route (new work)

From skill root:
```
python scripts/director_v45.py catalog
python scripts/production_v45.py start examples/director-v45.json examples/creative-v45.json work/study45
python scripts/production_v45.py next work/study45
```
Replace example paths with new product-specific sources. For an ad provide `--audio path/to/authorized_mix.wav` at start. Run the returned `argv` exactly (do not shell-join untrusted strings), then repeat `next`. Stages: preview, pixels, transitions, flow, cadence, review-template, gate, upload, verify-export. Use `master` for optional lossless; final size 1080. If a stage folder is incomplete, preserve it and start a new revision. Never edit cached plans or evidence in place. A preview can be 540/720, but inspect fine type/CGI at native 1080 using compositor `--at` or native review tooling before final delivery. No final release from silent study, unless the commission is expressly a silent study.

## 5. Evidence and correction rules

Cadence decodes **every frame** of the preview, downscales to 180×320, compares mean absolute RGB differences inside each beat (boundary differences excluded), flags near-static runs >=0.65 seconds at a threshold of 0.12 RGB levels, near-black frames, and large changes. Reports three sample frames per beat and a graph. These signals are conservative heuristics; don't confuse color change with optical velocity, smoothness, legibility, or art direction. A deliberately still endcard may be correct. An evolving microscopic detail may be missed at this resolution. Flow remains a separate boundary tool; pixels remains a visible-contribution diagnostic.

| Measured or observed issue | First diagnosis | Concrete repair | Verify |
|---|---|---|---|
| Cursor slides off card | Wrong parent or separate x/y curves | Use sibling gesture controller; group card and its content | Contact and release samples |
| Click does nothing meaningful | Only tap compression exists | Author verified post-click state separately, sync to marker | Actual visible state transformation |
| Drag reads too slowly | Long approach before contact | Shorten gesture or already-position cursor with point then shorter drag; preserve reading time | Entire beat playback, endpoint |
| Freeze in middle of sentence | Missing visible consequence, or intentional hold | If unintended, extend meaningful action or actual product detail; never decorative motion just to increase metrics | Whole-beat viewing |
| Black/blank interval | Outgoing layer ends, incoming not visible | Overlap visibility and matched anchor or intentional cut | Frames before/during/after |
| Jitter in join | Direction/velocity mismatch | Hermite path or shared tangent, match position and timing | Flow and actual playback |
| CTA not readable | Text too short, hidden, oversized | Change size/position, increase meaningful hold | Actual native still and playback |
| Metal appears rough or jagged | Normal/mesh/atlas/sampling | Review at 1080, raise atlas/antialiasing and choose better bevel/light, lossless check | PNG and export both |

Every beat needs a concrete observation of visible subject and action, not 'looks good'. Read all beat/flow/pixel/transition sheets; watch full playback and hear audio where applicable. If flagged cadence is intentional, write a specific reason (e.g., 'CTA stays still for 0.9 s to read'). Do not falsify decisions. If no playback/audio access, leave blocked and deliver verified preview with explicit limitation. New V45 gate also requires cadence report hash and one explicit resolved decision per beat. Passing gate is a structural/provenance check, not creative certification. Preserve the good scenes during repairs; create new revision from canonical source. Never claim an independent model pass unless an independent model actually performed the work.
