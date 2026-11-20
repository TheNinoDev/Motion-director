> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# 113 — Direct a whole short film, not isolated animations (V57)

Operational guide for visual direction, editing and motion repair. Root governs scope. The example is a fictional product case and conceptual production plan, not measured output or an actual render. It is designed to teach transfer of editing judgment, not to impose the same story, pacing, shots, effects or aesthetic on every ad.

## 1. Choose the film mechanism from evidence

Inspect actual product elements at readable resolution. Identify an action or change with an observable before and after. Pick a visual motif that can survive changes of scale, layout and perspective. At film level, define the opening expectation, turn and consequence; at section level, define the visible action and the anchor into the next section; at frame level, define dominant silhouette, hierarchy, typography, camera/layer geometry and contrast. Use rhythm and negative space deliberately. The opening needs immediate visual information; it need not be a logo, an explosion, or a fast montage.

Choose a design system intentionally: one core palette with meaningful contrast, one or two type families where justified, a coherent material/light vocabulary, and an editorial accent for the key change. Do not force the original NOIZ brand or imitate its assets, text or logo. Use learned devices such as macro-to-wide, match movement, scale contrast, tactile interaction, typography behaving as an object, reveal and narrative callback. Distinct compositions can share the same palette. A stable background is fine if the actual composition and action evolve. A quiet hold is useful if the payoff needs reading time. Do not confuse "much motion" with every layer constantly moving.

## 2. Worked 24-second case: a scan-to-document app (fictional)

Assume inspected actual product evidence supports importing a photograph, adjusting four crop corners, and saving a corrected document. No OCR, automatic edge detection, security, speed or quality comparison is established. Use actual input photo and three verified captures: crop editor before, adjusted crop, saved result. The user delegates visual direction, wants English, vertical public video, and approximately 24 seconds. This example does not presume cleared audio or generate claims of actual audio availability.

Three candidate mechanisms:
- "The corners": a skewed sheet becomes a clean rectangle; corners and paper geometry connect the whole film. Strong when the real crop editor and output are demonstrable.
- "Wrong frame": comic editorial framing failure creates surprise; real manual controls resolve the problem. Strong when humor fits audience.
- "Desk to document": tactile macro-to-wide journey from paper surface to digital file. Strong when original texture and captures are good. Can be done in 2D with excellent compositing rather than mediocre 3D.

Choose the first mechanism for the assumed proof. A concise spoken direction might be: "I got the whole page. And half the desk. Let's fix that. This corner, this one... there. Just the document now." This is a fictional sample, not a universal script, and it does not claim automation. Actual provider-native acting tags and user-facing audio handoff are supplied per 112. If the user requires 24 seconds, allow intentional picture-led segments but add only meaningful content; if the concept naturally ends at 15 seconds and duration is flexible, do not artificially stretch it. The timings below are a provisional arrangement, not measured voice timings.

| Range (draft) | Visible choreography, not a caption list | Connection and sound intention | Actual evidence / review |
|---|---|---|---|
| 0–2.5 | Start close on the paper corner and surrounding desk texture; frame pulls back to reveal a conspicuously crooked page, editorial corner marker travels with the page | Same corner remains visually registered during pullback; initial musical accent introduces texture | Actual uncropped photograph; clear hook without logo; phone-size silhouette |
| 2.5–6 | Actual photo occupies most of frame; desk margins push outward while an editorial outline isolates the page; slight directional shift exposes the bad crop | Exit using four-corner geometry, not a new fade-to-title; subtle sound when outline arrives | Distinguish overlay from real app UI; no claim of edge recognition |
| 6–10 | Match the outlined corner to the true crop editor; reframe around relevant portion rather than shrink whole screen; show pointer approaching first actual corner | Match location and angle; use a short anticipatory motion before drag; cue accents after actual pointer contact | Actual editor capture; legible handles, no invented buttons or control movement |
| 10–15.5 | Show successive manual adjustments using captured real before/after states or actual recorded interaction; the target corner becomes dominant; other handles serve as context | Maintain paper plane; vary short adjustment accents with one longer deliberate action; use existing gesture/cue system if reconstruction is faithful | Actual operation sequence; check cursor registration, corner coordinates and no impossible state |
| 15.5–19 | Show the actual corrected result and save result, at large scale. Hold long enough to read; secondary motion quietens. A possible single tactile 3D paper hero is an editorial metaphor, not proof | Match rectangle footprint from editor into output. Accent when actual result appears, not before | Verified final file; compare to original; no fake correction or invented save behavior |
| 19–24 | Return to the opening corner motif now aligned, briefly show input/output contrast if useful, integrate brand/CTA only after result can be understood | Callback and musical resolution; end on stable intentional composition | Actual result and brand assets; no generic feature grid; ending readable and not cut mid-phrase |

This is one film, not six independent title cards. There are deliberate shifts in framing, scale, activity and visual density; the same geometric motif connects them. Text is minimal and used to guide attention, not duplicate every spoken word as a giant headline. Adapt any captions to platform accessibility and reading constraints; don't hide important proof behind text.

## 3. Turn the director's plan into supported implementation

Before using a recipe, identify actual source asset, its native pixels, local coordinate space or parent, start/end state, time interval, main moving property, coupled objects and visible acceptance condition. The plan should survive tool changes. Example: crop editor corner coordinate A is registered to editorial corner marker A; both share a frame transform during a reframing move; confirm the screen-space registration at start, center and end. Then look up real compatible compositor properties using guide 86 and existing CLI help. Use existing components/parents, paths, masks, cue sequences, camera-like transforms or recorded motion as appropriate. Don't fabricate a crop transform or an app behavior just because a named effect sounds correct. For a recorded actual action use the supported video handling or frame assets documented by the current toolchain; if not supported, use a faithful still-state route and disclose if it changes the portrayal. Do not build a new engine for a routine ad.

| Editorial need | Candidate implementation, subject to actual capabilities | Avoid |
|---|---|---|
| Macro-to-wide reveal | Parent-group reframe, persistent foreground anchor, distinct surface/detail layers | Scale an entire text slide repeatedly |
| Shared shape match | Same geometry/registration, mask and transformed handoff, sampled mid-transition | Dissolve two unrelated canvases and call it a match |
| Physical reaction | Supported anticipation, impact/recoil, contact physics only when appropriate | Unrelated camera shake, stiff block meshes |
| Focus shift | Composition/contrast change, readable detail crop, controlled secondary blur | Tiny screenshot plus large headline |
| Sound cue | Actual event marker and measured audio, precise transient/layer relation | Whoosh on every cut or guessed word timings |

These are routes, not guarantees that every property works for every kind. Inspect actual supported API; preserve real captures, label illustration, and keep original assets. Use 108 and 104 for reference-derived shot techniques, 111 for another full example, 86 for actual fields, and 87/92 for existing production commands. Use CUDA only when present and supported by the current renderer; a beautiful CPU preview is better than a fabricated GPU claim.

## 4. Two styleframes + one moving slice, not an infinite moodboard

When creating a new film, render actual representative frames showing different narrative states and compositions: e.g. first macro hook and proof closeup. Compare readability at phone scale and native texture/type quality. For the highest-risk motion, render a short slice with adjacent lead-in/out frames: in this example the crop editor match or corner-drag-to-result. Inspect anchor position, occlusion, acceleration and whether the real behavior remains accurate. If one slice is already good, proceed; do not waste time generating the same template repeatedly. If time/resources are limited, prioritize hook, proof and the hardest transition; plainly state if validation is incomplete.

After actual audio arrives, measure speech and cue timing where tools allow, place key visual changes to support—not blindly follow—meaning and musical emphasis. Allow intentional offset or anticipation for clarity. Check cuts and onscreen reading, music ducking around words, transient prominence, intelligibility and ending. A beat detector is a suggestion, not an instruction to cut at every beat. Recalculate dependent cues after retakes. Keep dry voice, music and SFX sources. Different providers, styles and runtimes need different pacing.

## 5. Review the film at three scales and apply repairs

- Film: mute preview where available. Is the initial question/action resolved by the visible result? If not, rework the story, not the easing. Does the video change composition meaningfully, or is it a headline/thumbnail loop? Does the opening offer a reason to keep watching and the end resolve it?
- Section: inspect transitions with outgoing, midpoint and incoming actual frames and playback when possible. Check visual anchor and direction, destination state, repeated motion, unnecessary resets, actual proof. If the section fails, identify exact interval and rewrite its core action or asset crop; protect adjacent accepted material.
- Frame: check phone readability, actual native rendering, unclipped typography, composition, material geometry, lighting, smooth edges and unwanted stretching. Inspect actual image/video artifacts rather than self-score. Do not confuse decoded frames, cadence numbers or a passed gate with creative approval.

Repair priority: truth/rights/locked scope → core premise and proof → composition and legibility → continuity, timing and acting → material/edge defects → optional polish. If the first three fail, extra FX are not the fix. If the complaint is local, patch only the affected cause, compare before/after and preserve unmodified sections. If only MP4 is available, state which edits cannot be recovered and what can be safely done without source. Deliver actual verified artifact and any remaining unverified checks. Follow guide 97 for final review and regression logic.
