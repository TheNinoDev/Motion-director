# 132 — Whole-film creative acceptance, exact revisions and cross-agent trial (V62)

The goal is to stop weak agents from shipping a working but unappealing 24-second render. The document defines **observable inspection and repair behavior**, not a fictitious quality score or an automated theorem that a film is good. Use 129 as the grounded Claude case, 130 for art direction and 131 for reproducible rendering. Keep the task scope and actual recorded assets fixed unless the user authorizes changes.

## 1. Three different reviews: each catches a different failure

**Story view, captions hidden.** Watch a full rough cut without subtitles/giant headline overlays when possible. At the opening, turn and ending: what visually happened? Is the key event perceptible without written explanation? If the same rectangle, centered icon and gradient are present across five successive headings, that's not five visual beats. Make the main object larger, change its mechanics, or restructure the scene. Do not optimize this by making everything flash.

**Composition view, sampled full-film timeline.** Generate an overview sampling roughly every 0.5–1.0 s AND individually inspect high-risk transition boundary frames. Record each major section's main silhouette, focal scale, screen position, negative space, relationship and new information. Test at mobile size. A collection that repeatedly shows `BIG TITLE / SMALL CODE CARD / BOTTOM CAPTION` is a **global art-direction defect**, even if the microanimation is technically sophisticated. Change an entire section's dominant visual idea before polishing. Use a purposeful held result when relevant; stillness alone is not failure.

**Motion and sound view, actual playback.** Watch the motion as video, if the environment supports it. Inspect jitter, discontinuous speed/rotation/visibility, uncomfortable acceleration, awkward holds, continuity and readability. Listen if a usable tool or authorized human audition is available. Audio metadata, silence regions, waveform and loudness do not prove speech pronunciation, feelings or artistic synchronization. Preserve already supplied voice/music and do not regenerate simply to satisfy a gate.

## 2. Revision loop with clear repair target

For each issue write privately a *falsifiable defect and remedy*, e.g. “8.2–10.8 s: one static center badge under repeated title; change to a full-frame gate whose distinct branches resolve on the spoken decision”; “7.3 s: cells drift diagonally due to nonzero CSS default layout; reset absolute position and test 7.2–7.7 s”; “15.0 s: visual hero misses musical downbeat by 0.4 s; align to measured event, preserve VO.”

Then do it. Compare actual before/after at key times **and** a continuous interval. After fixing a shared renderer or an ending, re-export the whole film and inspect the modified boundaries. When the problem is creative, DO NOT respond with only a new gradient, shimmer, camera shake, blur, more SFX, 3D cube or a label. A weak concept needs a new composition/action, not more polish on the weak concept.

**Issue priority:** truth/permission/scope → comprehensible premise and meaningful event → visible full-frame hierarchy/legibility → connected motion/tempo → visual artifacts/material/lighting → optional effects. Reversing this order leads to expensive beautiful slop.

## 3. No magic thresholds or forced complexity

Pixel-change diagnostics can locate low-motion segments, but they do not measure good art. A full-black hold that lands between an emotional question and a musical reveal can be correct; a noisy layer that constantly moves can be atrocious. If every scene changes rapidly but no action is legible, **reduce** movement. Do not enforce arbitrary object counts, speed, shots-per-second, 3D-percentage, particle quotas or model-specific style. Choose contrast purposefully.

For a short ~20–30-s narrated film, a practical rough cut audit examines: first ~3 seconds, pivotal action(s), the long quiet region, the climax aligned to actual sound if verified, and endcard duration. If a low-motion section has no narrative rationale, repair it. If a hero section already makes sense, protect it. This is adaptive—not a requirement for a new visual every two seconds.

## 4. Portable agent trial with the same brief

If testing Claude vs GPT or different skill versions, give each the **same** project product facts, exact locked narration, same cleared music, target runtime, format, hardware/tool access where feasible, explicit source-visual ban, and budget. Keep the case independent of brand examples used in guides. Ask for an original 9:16 product film. Capture: actual first reply, asset inventory and no duplicate questions, proposed 3 distinct mechanisms, sampled opening/turn/end styleframes, actual 1–3s moving slice, whole rough cut, diagnosis, final video/audio and corrections.

Judge from **artifacts and observed actions**, not self-praise, line count, tool invocation count, time elapsed or a claimed numeric grade. Record concrete timestamps of bad framing/slow holds and compare honestly. A missing browser or different permissions should be noted as a capability difference, not mislabeled as inferior taste. Do not supply the expected answer to the tested agent. User can then identify whether an agent failed to choose a compelling concept, failed to implement motion, failed to inspect it or failed to repair it.

## 5. Required outgoing status

The real final must name the artifact that exists and what was actually tested: e.g. full decode, 0.5s filmstrip, specific revised transitions, measured VO/music timing, or playback inspection if actually performed. Explicitly disclose missing checks and rights uncertainty. Never say “professionally edited / flawless / cinematic” as a substitute for an actual inspection. If the artifact still fails the story/composition test and the budget permits repair, **repair before claiming completion**. If tools/time/access are genuinely exhausted, deliver an honestly labeled incomplete draft and exact observed defects instead of fictional success.
