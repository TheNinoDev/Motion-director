---
name: ads-wizard
description: Direct and produce premium original video ads through causally connected multi-element motion graphics, purposeful typography and sound, with rigorous two-frame final-film visual review. Preserve the proven Motion Director v67 editor and SFX foundation.
---
# Ads Wizard v74 — Connected motion-graphics ensembles, frame-by-frame finishing

**THIS IS THE ACTIVE EDITORIAL CONTRACT. V67 creative baseline restored.** Motion Director 67 is the retained editor baseline. V74 preserves the Motion Director **v67** editor, SFX, scene animation and reusable production tools, together with the narrow v72 softened UI and contextual icon permissions. V68–v71 'assets first / icon ensemble / icon scene' creative requirements are NOT active. V73 'film, not slideshow' was directionally right but did not force adjacent visual elements to act together and begin their next transition soon enough. This update changes the scene design and finishing loop, not the renderer.

## 1. Choreograph a connected event, NEVER a finished poster per line of narration

**Read `references/149-ensemble-motion-grammar-v74.md` FIRST.** A credible sequence contains a driving visual action, a visible reaction or consequence elsewhere in the composition, text that supports the action, and an early handoff into the next action. The elements are **causally related**, with different timing, depth and paths. A single actor may be dominant; there is no mandatory element count, but a disconnected headline and card or three independent orbiting icons fail.

Plan what happens before the shot, at the point of contact, what the rest of the space does in response, and how the consequence becomes the successor shot. Several voice phrases may share one evolving scene. Begin preparing most transitions **BEFORE the old scene ends**: carry a moving line, material, object, shape, camera vector, occlusion, musical prelap or a justified contrast; do not wait for the old board to settle and then wipe to a fresh finished board. Ordinary purposeful cuts and quiet holds remain legitimate. **Text is contextual motion graphics, not the universal main attraction.**

After writing the visual plan, run `python scripts/ensemble_story_audit_v74.py examples/ensemble-motion-v74.json` on its real project-specific equivalent. This checks whether actor, reaction, cause and handoff are specified and connected; passing a JSON schema does NOT certify the rendered result. Read `references/151-v73-to-v74-revision-notes.md` for the concrete observed failure.

## 2. Use the REAL editor and audio rather than moving presentation objects

Read `references/134-editor-capability-routing-v64.md` to understand the packaged renderer before programming anything. The v67 compositor supports layers, masks, transforms, perspective, foreground/background interaction, kinetic typography and transitions; use that capability. First render a native **3–5-second rehearsal spanning the END of one scene and START of the next**. View at 1x speed; if it reads as two completed slides connected by a wipe, redesign the visual mechanism BEFORE writing a full film. All transforms are subordinate to an understandable story. Stage camera and secondary reactions intentionally, not with uniform jitter or constant zoom.

Keep supplied voice, music, script and product facts locked. If audio choices are missing read `references/123-input-and-audio-routing-v60.md` and stop at the legitimate user input gate. Design SFX on actual contacts and events via `references/142-sound-direction-and-mix-v67.md`, keeping voice intelligible and soundtrack audible. Creative editing must not invent product behavior or misuse assets.

Optional **small**, legible Solar/Lucide SVG icons inside controls may replace obvious labels (play, copy, verification, etc.). Genuinely user-owned, permitted favicon/brand icon can appear subtly in the outro. Rounded corners on controls/cards are polish, not a ban on intentional sharp shapes. The icon is NOT the scene. No requirement to source or add external SVGs, characters, particles or decorative illustrations. Client and reference websites are information-only unless a specific owned visual exception is clearly authorized.

## 3. Finishing pass: review EVERY SECOND ACTUAL FRAME

**Read `references/150-two-frame-finish-review-v74.md`.** Once the whole rough cut has been watched with real audio, inspect the actual final exported MP4 at native cadence sampled at **every two source frames**:

`python scripts/two_frame_finish_v74.py FINAL.mp4 --out FINAL-REVIEW --every 2 --plan ACTUAL-PLAN.json`

This decodes *all* frames, captures every second frame and generates chronologically paginated sheets, source-frame/time labels, flagged near-static and jump candidates, optional seam-neighborhood pages, and a SHA-256 report. **The agent must actually inspect EVERY generated sheet**, then zoom into defects and view video/playback at 1x with sound. Generating sheets is NOT the same as inspecting them. It is forbidden to claim every frame was visually inspected if pages were not opened. The two-frame pass necessarily does not capture intervening source frames; inspect all frames around suspicious locations when needed.

If something is cheap, unconnected, unreadable, poorly eased, clipped, or unpolished: revise the real timeline, re-export, and rerun the complete two-frame pass on the *new* file. Aim to repair story structure before minor polishing. Do not use pixel-difference values as an artistic score, a dead-frame quota or a claim of premium quality. Keep traceable evidence of inspected pages and corrections; honestly disclose any unreviewed pages.

## 4. Approval and handoff

Only deliver a final ad after: (a) the story works when title/decorative icons are hidden, (b) the actor's change causes secondary visual consequences, (c) the next action is seeded by the current one or a motivated deliberate cut, (d) full film and real audio have been checked, and (e) every-second-frame sheets of the delivered export have actually been reviewed with any identified issues fixed. Good technical encode, generic smooth movement, and tool execution alone are NOT sufficient. If time or capability prevents viewing, deliver as a clearly labeled draft with exact unverified areas, not a 'perfectly polished' final.

All earlier references remain historical/tooling support, not competing mandatory creative quotas. The skill mascot under `assets/branding/` belongs to Ads Wizard, not to the customer's ad by default. Preserve sources, provenance and actual permissions. When available, use **real** bounded subagents for independent storyboard critique or visual QA (`references/135-subagent-orchestration-v64.md`), but one director owns the master timeline and release.
