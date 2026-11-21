# 139 — Scene handoffs, match logic and continuity (v66)

**Trigger:** An edit looks like disconnected slide cards; motion is present but there is no reason why shot B follows shot A. Fix the *relationship* between shots before polishing either one. No transition quota: strong motivated direct cuts are often preferable to generic wipe clutter.

## The seam is a designed unit

Storyboard each important **A → B** seam *before* building scene B. The unit is not "fade A, show B": it has a beginning, a visual handoff, and a consequence. For each seam, write privately:

```
A: last readable state / what viewer is looking at
Bridge: exactly what visual/audio event motivates leaving A
B: first readable state / what inherited element, geometry, action, contrast, rhythm or meaning lands
Continuity: what is continuous (shape, position, object, direction, color, camera move, sound, narrative question)
Motion: outgoing velocity and incoming movement/settle; whether a deliberately hard cut is used
Test: inspect A -0.35s, A -0.08s, B +0.08s, B +0.35s at phone size, AND watch the real seam
```

If no one can name a link beyond "both use the same color/font" and the cut has no editorial contrast, the seam is unfinished. A scene change need not carry the exact same pixel/object. A *semantic match* can be stronger: snapped code fragment becomes the first tile in the access matrix; a selected key casts a circular mask into the next shot; a typed word on the outgoing side completes on the incoming side.

## Useful handoff families (choose only one per seam where it helps)

- **Persistent-object carry:** same document, line, device, symbol, particle or contour moves, transforms or exits and enters the next scene. Preserve perceptual identity, not the entire scene.
- **Shape / silhouette match:** the outgoing outline or crop matches a new component on the other side; direction and scale align at the join.
- **Directional handoff:** outgoing translation, diagonal edge, rotation or zoom establishes motion that the next shot completes. An unrelated wipe moving a different way is not continuity.
- **Reveal matte:** physical plate, color wedge, circular iris, type glyph or masked surface originates at an existing focus point. The new visual is genuinely revealed behind it. The matte is the transition, not decorative overlay pasted on top.
- **Impact / contrast cut:** at a strong audio/visual hit, switch decisively to a deliberately different scale or visual value. This can be perfect with no wipe, if the contrast answers the preceding visual question. Avoid dissolving a strong contrast into mush.
- **Audio or semantic bridge:** the next visual starts before the current sentence ends, or one motion/SFX anticipates the next state. It should enhance the cut, not compensate for missing subject continuity.

Do not use every family. Two or three coherent transition mechanisms across a short ad are enough; repeat one family when repetition reinforces a motif, vary only where story justifies it. **No arbitrary "all shots must dissolve" rule.**

## Observed real-film cases (reference material is for principles only)

- **GPT v65 RobloxLARP at ~13.5 s:** blue Custom VM tiles → orange key-access diagram. Color changes abruptly with no perceptual anchor. Suggested independent redesign: select one VM tile; animate it as the *same* carried token crossing the seam and expanding into the key, while blue geometry recedes. This is a design proposal, not a feature claim.
- **GPT v65 at ~15.6 s:** key diagram → cream onboarding card. Link the outgoing key arc or click to the incoming document aperture, or choose a decisive cut motivated by "Now it's simple" and change camera scale. Do not simply insert a generic wipe.
- **GPT v65 at ~19.7 s:** enable-switch scene → black final statement. Make the switch's circular knob become the punctuation or circular crop into the brand statement; alternatively cut on the *audible* payoff as a strong, intentionally designed contrast and avoid adding unnecessary transition motion.
- **Claude protection video ~2.9 and ~7.9 s:** big red/indigo diagonal shape crosses the scene and reveals the next context, keeping the graphic event legible. **~15.6–15.8 s:** circular mask grows from focus into the cream scene. Do not trace or reproduce its design; notice the handoff.
- **NOIZ reference 1000043457 ~11.5 s:** a metallic letter/image is overtaken by a flowing reflective structure which becomes the next letter-space. The relation uses motion, material and scale. Independent product videos should develop their own identity; NOIZ assets, letterforms, branding and frames are not licensed inputs.

## Review loop

1. Render a 0.8–1.5 s seam clip **including both sides**, with original music/voice timing when available. An isolated in-scene animation cannot establish a good transition.
2. Watch at 1x to test comprehension, then at 0.5x to find discontinuities, wrong directional carry or camera jerk. At native phone size, ensure the hero stays identifiable.
3. Create A-before, A-edge, B-edge, B-after frames, preferably using `python scripts/seam_review_v66.py VIDEO --cuts ... --report ... --sheet ...` for prompts. Contact sheets are diagnostics, not substitutes for playback.
4. Repair by changing entering/exiting staging or the seam logic. **Do not append a random transition effect to two completed shots.** Retest the seam and adjacent seconds.
5. Check the full cut: removing an unnecessary wipe can make it cleaner. Use the minimum mechanism that communicates change.
