---
name: ads-wizard
description: Direct and produce original premium video ads with cinematic editorial storytelling, purposeful continuity, expressive sound, and verified visual quality. Use the proven Motion Director v67 editor baseline.
---
# Ads Wizard v73 — Direct a film, not an animated slideshow

**V67 creative baseline restored.** The production engine is the original Motion Director 67. **Priority override.** This version keeps the v67 editor, sound, animations, references and tools as the technical baseline, plus the narrow v72 softer-UI and contextual-icon exceptions. Earlier advice to prioritize hero assets, isolated icons, adding motion to every frame, maximizing motion density, or building one page per narrated feature is NOT active. Read `references/147-film-not-slides-v73.md` and the observed comparison `references/148-real-output-diagnosis-v73.md` before storyboarding. Those two guides are short active direction; the existing v67/66/65 manuals are technique references, NOT competing mandates. Do not recreate the comparison footage.

## The one production rule

**One continuing audiovisual action, not one completed design per sentence.** Before rendering, write a visual *verb* and its state change for every major film moment. The same hero can survive 2–3 narration phrases and carry into the next idea. A text change, a color change, a page reveal, an icon swap, a morph to another centered card, or a wipe onto a new static graphic is **not itself cinematic action**. Reject the concept if removing the title text makes the entire video an incomprehensible sequence of separate panels. Text can be the real subject when the words themselves actually animate or drive meaning.

**Opening/turn/payoff are distinct camera/composition moments** in a connected film. Plan the exact physical on-screen mechanism: What is moving? What causes it? What changes? What remains after the cut? What does the viewer understand before reading? This is a film story, not a checklist of features. Choose editing techniques because the story needs them, not to show off a tool. Borrow pacing/decision discipline from the supplied Claude examples, never their pixels/design/sound.

## Implementation, never another renderer reset

- Use the bundled Motion Director v67 compositor, layers, masks, typography, editable transforms, SFX and transition utilities. Read `references/134-editor-capability-routing-v64.md` for actual tool capability, and verify an editor-native moving proof before committing to a long implementation. Do not fall back to a custom Pillow slideshow because it is quicker.
- Choreograph **foreground, subject, camera, and contextual UI as linked components**, not independently eased title cards. Distinct motion mechanisms might be a handoff, occlusion, perspective turn, mask following an object, type reflow, contact/reaction, or a motivated snap cut. Mix them only where needed; no fixed quotas.
- Make the video feel spatially and typographically authored. Soft radii on controls/cards are polish, not a required radius everywhere. Maintain meaningful sharp edges where justified. Solar/Lucide SVGs are optional small affordances on established buttons/cards; **do not make a sequence of icon scenes**. A user-owned official favicon/logo can appear subtly on the outro if supplied or explicitly authorized. Other site content is research-only.
- Keep supplied script, voice and song locked. If audio inputs are missing, follow `references/123-input-and-audio-routing-v60.md` instead of silently producing a silent full ad. Tie SFX to actual movement/contacts and carry relevant tails over seams; consult `references/142-sound-direction-and-mix-v67.md`.

## Approval requires proof, not a successful export

1. **Storyboard three decisive before/mid/after frames**, not three finished slides. If they show the same layout and a new word/panel, redirect before a full render.
2. **Render a moving middle sequence and its handoff into the next shot**, not just one isolated effect. Inspect the seam with the actual audio.
3. Produce a first full rough cut, then view it at normal speed *and* as a start/middle/end sheet. Use `python scripts/film_rehearsal_v73.py INPUT.mp4 --plan PLAN.json --out DIR` (see 147); run the existing `hold_audit_v65.py`, `seam_review_v66.py`, and `sfx_story_audit_v67.py` where applicable. Automated diagnostics do not certify style or good editing.
4. **Find the worst slideshow-like sequence and reconstruct it**: remove its headline, alter the object action/composition, author the adjoining seam, and re-render. Do not simply add particles, more SVGs, microanimations or voice-synced words. Show actual before/after evidence. If the rough cut is weak, do not falsely label it approved.
5. Verify actual soundtrack/voice integrity, permissions and honest product claims. If subagents exist, delegate a bounded *independent visual critique* while the main director retains story and the final timeline; otherwise do the same review yourself. Never invent observations or tool results.

**Source boundary.** Product websites/local projects and reference videos are informational unless the user specifically authorizes isolated owned branding. Third-party SVGs/fonts need verified licenses and provenance. No reuse of other videos' frames, stock that was not authorized, fabricated functioning product states or unsafe SVGs.

**If you are about to export another film consisting of `headline → static item → wipe → new headline → new item`, stop and redesign the film.** Technical smoothness and constant pixel motion cannot make that sequence good.