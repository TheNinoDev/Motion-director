# 147 — A film has continuing action, not sequential finished boards (v73)

## The observed design failure

Recent agent edits repeatedly choose a new background, centered caption, one complete code card, then replace that composition with another title and card. The compositing and easing can be technically flawless, and frame differences can be large, but the viewer experiences an animated presentation. This failure persists even after changing to rounded corners, introducing downloaded SVGs, adding particles, increasing SFX, or raising motion density. The fix is editorial direction **before** asset creation.

## One visual sentence across multiple voice sentences

Start with a *verb* the audience can watch, not a product feature or static noun. Write a cause and consequence in visible space:

- **Initial state**: recognizable subject and physical or graphic relationships (where, relative to what?).
- **Intervention**: an identifiable action changes that relationship, ownership, state, scale, hierarchy or destination; the action may be implied by a hand/cursor/gate/shadow/mark instead of explicitly simulated.
- **Response**: secondary subject or environment reacts in a different time/motion layer. Don't animate independent parts with identical curves.
- **Handoff**: an edge, motion, carried subject, mask, light, surface, camera axis, sonic tail or *justified* contrast cut leads into the next beat.
- **Payoff**: viewer learns something new through the resulting image, not only through a changed sentence.

Do not limit each voice phrase to one shot. Several narration phrases can happen in one evolving scene, and one dramatic transition may span a sentence break. Tension/holds can be intentional; the command is not to shake everything or enforce a cuts-per-second target.

## Stage one actual scene, then prove it

Write one short private direction statement for each major transformation: `subject/its starting relationship → concrete change → resulting relationship → how this connects forward`. Show first/middle/last *images from the actual renderer* with enough detail to tell whether something has materially changed. A motion test that only rotates a finished square is insufficient. If every preview is a finished center-aligned board, there is no film.

Three alternate visual strategies worth comparing (never copy these as compulsory assets):

1. **Material continuity:** one physical-looking document or dimensional form survives a camera move while its markings or ownership change. A following element reacts to that cause. UI can appear as an attached control, not a separate poster.
2. **Graphic editing:** the frame itself is the active medium: negative space gets filled, title baseline bends to reveal the product, type is partially masked by a subject that crosses the camera. The next scene is uncovered by the *same movement*.
3. **Meaningful contrast:** a violent mismatch can be stronger than a smooth wipe if its opposing colors/compositions make the narrative turn obvious and the music underscores it. Do not demand an artificial morph between unrelated ideas.

Review all three on phone size. Pick whichever strengthens the actual story; don't force the film into one method for all shots. Ordinary direct cuts, quiet holds, simple fonts and hard shapes are not inherently bad.

## The editorial checkpoints

**Before full export:** The opening should begin an action, not display a brochure cover. The 7–15 s region must not turn into a feature-title montage. Establish one causal transformation through an actual A→B boundary. Use one native-editor proof that includes masks/paths/transforms only if the scene needs them.

**After first export:** Watch real-time. For every scene boundary ask: "Was there an unresolved action, and what completed it?" If the edit cuts from one fully completed composition to a totally unrelated completed composition, add the missing causal step or make the contrast cut deliberately meaningful. Reject a generic wipe that hides this discontinuity. Listen for sound that arrives with the action, not a stock whoosh on every slide.

**Elimination test:** Turn off decorative icons and small labels. Can the viewer follow the problem, transformation and payoff? If not, the symbols have been carrying an undeveloped film. Restore only useful UI affordances at the end. A small Solar/Lucide glyph can replace a verbose Run/Execute control when the meaning is unmistakable; an isolated giant glyph is rarely a plot.

**Revision contract:** Name the weakest 2-second interval and its structural defect. Fix object staging, camera relationship or transition logic first, re-render it, then reassess neighboring intervals at normal playback speed. Only then touch micro-polish, fonts, colors and radii. Do not tell the user it is "premium" without actually watching the exported film.

## Human evidence: do not optimize the wrong metric

A comparison sampling frames 0.8 s apart from the latest 24.5 s 1080×1920 v72-like render and Claude's 24.6 s comparison found *fewer* low-change intervals in the new video than Claude, yet the new video still looked more like a series of boards. The metric is frame difference (average downscaled gray pixels), NOT a film quality score or a reliable count of dead frames. Reject frame-count optimization as a creative goal. See 148 for the timestamped visual diagnosis.

## Proof tooling and honesty

Run `python scripts/film_rehearsal_v73.py film.mp4 --plan examples/film-rehearsal-v73.json --out review-v73` after replacing example timings with the actual film's beats. It produces scene before/middle/after sheets and A→B seam strips plus the cue/diagnostic notes. This is a human-review artifact, not an automatic gate claiming art can be measured. The plan must come from the actual storyboard/film, not fabricated evidence to game the checker. Keep existing v65 hold and v66 seam audit tools for additional diagnostics; preserve locked voice/music; inspect the mix.