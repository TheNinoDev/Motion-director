> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# 92 — Execution, review and recovery: never pass your own weak work by default

## 1. Before running production
For new narrated commercial/public ads use existing v50 manifest, performance, alignment, actual assets, and compatible source/creative specs. Guide 87 documents the exact workflow and guide 86 documents syntax. Values must correspond to real decisions, not strings inserted merely to satisfy checks. `preproduction_v50.py next` returns a stage, not automatically a user-visible reply. Translate the stage into the next appropriate action. Complete missing user-owned decisions in chat; complete agent-owned work yourself. `handoff` creates files, not proof the user received instructions. Send the applicable content in chat. Never populate a user decision or audition observation with imaginary confirmation. Don't force the user to use a CLI or JSON.

Existing command sequence from skill root, placeholders here mean actual project paths:
```
python scripts/preproduction_v50.py next WORK/brief.json
python scripts/preproduction_v50.py handoff WORK/brief.json WORK/handoff
python scripts/director_v49.py diagnose SOURCE.json
python scripts/production_v50.py start SOURCE.json CREATIVE.json WORK/session --manifest WORK/brief.json
python scripts/production_v50.py next WORK/session
python scripts/production_v50.py gate WORK/session
python scripts/production_v50.py verify-export WORK/session
```
Do not run `handoff` with an existing output directory; choose a new folder for revised script and update actual evidence. Start in fresh work/session. Use `next` to find exact remaining commands (preview, evidence, review, export). Only after actual evidence is inspected may the corresponding review be recorded. Do not auto-answer all reviews. `advice` helps diagnose; compatibility/catalog tools help select fields. Keep raw files unchanged, avoid overwriting source. `creative.product`, `audience`, `central_idea` must match manifest exactly; maintain one real brief, not after-the-fact changes to pass validation. Coverage checks actual linked local motion, not whether it is interesting, and expects compositions to be distinct. Do not add meaningless motion or rename layouts for a pass.

## 2. Honest limits in existing v50 tools (do not attempt to work around)
- The compiler supports only the small model/cue table in guide 90; it doesn't generate voice. Script-only and manual handoff remain useful if alternate providers are chosen. For short or immutable scripts that fail heuristic requirements (three beats/hooks, two cues), never pad or rewrite locked text without permission. Explain limitation; complete text deliverable and label any unverified export honestly.
- `production_v50.py start` invokes `preproduction.check(..., release=True)` and the actual mix. It requires cleared voice, non-scratch narration, actual alignment and separate music unless an explicit waiver is recorded. A real silent advert, platform-only insertion workflow or private-preview-only rights can be legitimate but are not supported by this gated release route. A creative draft/styleframe/explicitly requested technical test may still be created through appropriate existing tools. Do not mark a real ad as `fictional_study`, fabricate stems, use an old production route to bypass requirements, or claim a finished upload-ready deliverable. If the user asks for something the current pipeline cannot truthfully release, explain the exact limitation and offer appropriate draft or cleared route; don't demand narration against the user's wishes.
- Audio files and hashes are actual evidence of files, not proof of licenses, human listening, accurate ASR or consent. Video QA estimates do not establish creative quality. Cannot see/hear? Do not mark inspected; use labeled technical output or describe pending review, not final approval.
- Legacy/standalone engines remain available for technique work and compatible legacy revisions, not an exemption from user requirements or honest release checks. Do not rewrite tool code unless user requests development. No forced CUDA; actual device telemetry, not assumptions.

## 3. Two independent editorial passes after rendering
**Pass A — viewer first:** watch/listen to the full preview at normal speed if supported. Do not start by reading a list of metrics. Write a short concrete first impression: what actually caught my attention, what did I learn, where did I stop caring or get confused, what proof could I read, did the ending pay off the beginning? Mute and view again if possible: does the picture communicate rather than simply repeat narration? Listen without video if possible: speech clear, emotional delivery, music supports rather than buries, sound events believable. If modalities unavailable, explicitly mark them pending. A contact sheet is not playback and waveform is not listening.

**Pass B — editor diagnosis:** inspect actual hook, all important transitions (before/middle/after), peak action, product proof, quiet holds, ending, native stills and phone-size frames. Use existing pixel/flow/cadence/audio/cue tools where appropriate. Compare real render to intended action, not only planned keyframes. For each weak moment record time range, observed defect, likely cause (label inference), proposed targeted change, actual new artifact, before/after result. Distinguish intended hold, deliberate hard cut and technical error. Inspect all adjacent windows when altering timing. Do not declare aesthetic approval on numerical threshold alone.

## 4. Qualitative acceptance rubric (no fake total score)
| Area | Accept when | Reject and repair when |
|---|---|---|
| Brief / claims | Central message matches approved facts and audience | Invented feature, ungrounded metrics, unclear result |
| Copy | Specific human speech, strong promise/payoff, concise | Generic marketing, feature list, unnatural or padded phrases |
| Acting | Actual take has motivated delivery and intelligible words | Tags read out, flat delivery, distortion, no reason for emotional switches |
| Hook | First meaningful visual/action and spoken premise attract curiosity quickly | Logo/title on empty background without story purpose |
| Composition | Dominant subject, legible real proof, motivated changes in framing | Tiny screenshots beneath static text, repetitive generic layout |
| Motion | Visible before/action/after, connected timing, contrast and deliberate holds | Identical fade/zoom, incidental pulsing, disconnected scenes |
| Craft | Intentional typography, fit, sharpness, proper edges/materials | Stretch, overlaps, aliasing, bad bevels, illegible text, overdone FX |
| Sound | Actual aligned words, licensed music, audible intentional accents | Guesswork, buried VO, click on wrong frame, unverified rights |
| Export | Decoded file matches requested format and source | Wrong aspect/duration, missing frames/audio, stale evidence |

All relevant areas need honest judgment; a visually weak film with technically correct metrics is a draft. A first render that truly meets every criterion may be accepted only on actual inspection; a weak first render must be revised. Don't force a cosmetic change just to claim iteration. If trying a repair, protect accepted elements and check that it genuinely improved rather than just changed the preview. One strong correction beats ten random effects. Never report “NOIZ quality guaranteed” or a made-up percentage.

## 5. Failure recovery decision tree
- Missing data/permission → resolve only dependency, deliver work already useful, no fake placeholder as final.
- Script or tags invalid → read validator + guide 90, adjust unsupported internal cue or structure without altering locked words; if incompatible, disclose and deliver text instead. Don't downgrade to plain to sneak through.
- Technical conflict → inspect property/cue ownership, actual parent coordinates, timing, and compatible fields. Fix source in new revision. Recompile/rerender affected interval and transitions. Keep earlier good work.
- Looks like a slideshow → reopen creative treatment. Redesign subject/action/result, compose new styleframes and animate verified proof. A bigger glow over same slide is not a fix.
- Poor audio → identify whether performance, source, alignment, music or mix is wrong. A rerecord requires user consent if not delegated/available. Preserve raw stem and intended words. Correct timings and regenerate affected evidence.
- User says result was bad → acknowledge specific observed issues, request source/asset only if genuinely unavailable; don't defend technical metrics. Offer concrete design changes, protect constraints and compare actual renders. Never call a synthetic example the user's new ad.
- Tool unavailable → check installed commands and existing engines; fallback compatible technique or disclosed partial work. Do not claim full output, listening or GPU without evidence; no asynchronous promise.

## 6. Final delivery format
Lead with actual file or actual text deliverable, then brief useful notes: duration, aspect, FPS, audio route and release scope only when verified; editable project files where appropriate; any unresolved limitations. Include captions/clean narration or separate stems if requested and permitted. Do not expose font binaries, private account details or licensed assets that cannot be redistributed. Do not show fake files or URLs. For an audio-handoff stage, don't call it final film delivery. For a script-only request deliver just the script and relevant performance/voice route notes. For a draft, label it draft and say what remains. Technical review JSON is supporting evidence, not a user-facing substitute for finished work.
