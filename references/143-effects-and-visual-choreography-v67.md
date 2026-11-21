# 143 — More variety in motion graphics without clutter (v67)

## Observed design failure

The newly supplied 24.6-second `RobloxLARP-Script-Protection(2).mp4` is readable and uses strong black/cream/lime/red/blue color contrasts, but most frames share one repeated template: a large top headline, a small central code card/diagram, generous empty area, and a new headline. It demonstrates a source card, theft/copy, stripped key, reposting, code-to-VM, access, upload/toggle and endcard; **there are real conceptual changes**. The weakness is that many are depicted as finished card arrangements with sparse intermediate choreography. In contrast the existing Claude protection comparison uses spatially extended paper, moving perspective on the code grid, connected foreground/background layers, and more composition types, not simply greater decorative detail. This is a grounded observation about *these clips*, not a rule that Claude always wins.

## Art direction contract: FX variety comes from different visual mechanisms

A family of looks may share brand identity. Do not give every shot the same hero scale, rectangle and typographic placement. Before full render, plan **at least three different visual mechanisms when the story naturally supports them**:

1. **Physical editorial:** paper, peel, cut, stain, fold, pull, frame collision, a visual object crossing the edge, a trace of weight and follow-through.
2. **Spatial/graphic architecture:** paths, curved camera travel, depth separation, 2.5D perspective and shapes passing in front of or behind other shapes. Use actual layered objects rather than fake 3D shading on a fixed card.
3. **Type as geometry:** selected letter, rule, punctuation or selected code fragment becomes an actual mask, path, boundary or next-scene object; don't just fade a line of text up.
4. **Controlled density change:** one compact hero explodes into readable structure, resolves into one bold object; use material contrast, not repeated grids for every feature.
5. **Color as consequence:** a palette inversion coincides with the narrative reversal. Don't change hue randomly just to meet an FX diversity quota.
6. **Lens and spatial reveal:** parallax, focus hierarchy, occlusion, matte originating from a hero object; prevent claustrophobic camera shake and illegible text.
7. **Illustration and geometry:** original or separately cleared and sanitized vector icons, diagrams or 3D objects when useful. No source-website graphics, reference frames or tracing.

**Meaningful variety** is a new *relationship* (foreground/background, scale, physical behavior, framing, material, direction), not extra bloom, confetti or overlays. Prefer one dominant visual transformation per shot, supported by understated secondary details.

## A small source-card example, independent from reference visuals

The same single script can tell an animated story if the editor actually transforms it:

- **Source:** readable card occupies the foreground, lines of code enter with stagger, distant surrounding documents are out of focus. It is not motionless before the theft.
- **Theft:** the camera maintains focus on the taken corner, the card bends/shifts, an annotation slips away, a distinct short contact sound establishes the event. One coherent hero event, not a card simply changing red.
- **Protection:** a few lines transform into modular instructions as the camera follows them. Depth and perspective express an actual structure change, rather than replacing one top title with another.
- **Access:** one tile inherited from the VM transition becomes a key-shaped connection to account/device. Soft incoming movement, precise UI contact cue, short settling response.
- **Payoff:** use a connected silhouette/reveal to end on the brand sentence, with the strongest single color move and a resolved audio motif.

This is *one possible approach*, not a repeatable timeline or permission to invent a functional product demonstration. Confirm product status: planned development is not shipped capability. Keep established user script/voice/music intact.

## Tool selection and subagent routing

Read `references/134-editor-capability-routing-v64.md` **before** writing a renderer. Use native `starter/composite_film/compositor.py` group/path/parent/masks/mattes/keyframes/perspective, and `starter/unified/production.py` specialty engines if supported; test actual capabilities. If CSS/JS browser animation is genuinely better for one self-contained effect, use deterministic `render(t)` for that shot and bring the **rendered clip** into the existing film/mix pipeline. Do not handwrite 600 lines of Pillow just to animate one card when a capable editor exists. Use lawful external SVGs only as independent assets with provenance; no copying site visuals.

Optional parallel agents, when actually available: `story` defines why scene differs, `motion` prototypes high-risk effect, `sound` designs scene-specific SFX cues, `QA` checks real preview. Director selects, revises and mixes. No one should independently finalize disconnected shots and then stitch them with generic xfade; the director defines anchors and locked audio first.

## Specific visual test

Draw 6–10 time-stamped frames from the film. **If five frames have essentially the same compositional relationship, even though text and color changed, restage at least one.** Audit one long sequence on actual 1x playback: are eyes pulled toward a changing object/action or toward a static headline? Is the subject distinct within half a second? Do foreground/midground/background ever exchange roles? Can a viewer tell the visual story muted? Would 20% fewer decorations improve recognition? These are creative questions; the editor must inspect real frames, not submit checkbox claims.

The best short film has variety of **mechanisms**, consistency of **identity**, and clear continuity of **meaning**. Do not force an effect on every second or make the camera float aimlessly to keep the dead-frame scanner quiet.
