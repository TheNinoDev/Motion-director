# V68 — Make assets ACT (not icon slides)

An imported icon is not an animation. Every significant asset must change state or relation for a reason. Match the animation to the physical/graphic idea rather than applying `smoothstep` + zoom to everything.

### Five useful animation grammars

1. **Illustration acting:** part-relative motion and posing, eye/contact reaction, squash/stretch on hits, silhouette rotation; use layered SVG/PNG pieces or a short rig. Don't make a rubbery document when it should feel like crisp paper.
2. **Object continuity:** the same key, chip, stamp, eye, lock, marker or code fragment exits shot A at a believable size/direction and physically motivates shot B. Stage the next shot backwards from the incoming object.
3. **Material change:** paper tears, fragments scatter, code shards weld into a lock, foil bends, print reveals, a shadow sweeps over glass. Difference between material and color filter matters. Use live masks, roto, volume, image-layer choreography, off-axis turns, shadow or pre-rendered original layers. Avoid generic xfade.
4. **Icon/emoji punctuation:** a recognizable expressive asset appears on a meaningful emphasis, animates with follow-through and disappears after its job. Let it replace a dull sentence, not compete with readable narration. For a playful TikTok ad, colorful illustrated icons and emojis may be appropriate; for a sober B2B ad, restraint is appropriate.
5. **Real typographic character:** license-cleared display and supportive fonts, controlled line breaks, optical kerning, varying type scale/weight or serif contrast and purposeful kinetic typography. Type should share the visual story with the images, not serve as an unchanged deck heading.

### Rhythm and spacing

Build in distinct phases: anticipation, contact/energy, follow-through and clean readable payoff. A moving asset should not creep for three seconds at uniform speed. Use coordinated but nonidentical timings, consider a 2–4 frame anticipation and a 5–12 frame release for a fast 30 fps gesture as a starting hypothesis (not a mandatory number). Check at real speed and phone size. A circular button, hand, character or soft keychain should not be made from sharp squared geometry just because polygons are easy. Smooth organic shapes and textured assets are permitted.

### A native asset-based animation pass

- Create a transparent static pictogram source with sufficient resolution/edges (SVG->PNG only if editor requires; keep original SVG).
- In `starter/composite_film/compositor.py`, use an `image` layer with `src`, `w/h` and separate `x/y/scale/rotate/opacity` keyframes. Group parent/child images when pieces move differently. Use matte, mask, pitch/yaw or motion sampling only where it supports the actual scene. The sample plan `examples/asset-first-v68/scene.json` exercises this path.
- If the asset needs internal face/arm or cloth motion, split into separate transparent pieces or use the specialist engine. Do not rasterize a whole still frame and fake motion by sliding it.
- Show the scene before, at contact and after. Check visual relation at every transition. Review on a phone-sized preview and compare against one simplified alt.

### Visual diversity without clutter

Three similar line-art diagrams in a row are still the same visual language even if their labels change. Vary meaningful dimensions: recognizable subject, asset class (illustration vs physically rendered vs typography), silhouette, camera distance, depth, color/material, movement mechanism and screen hierarchy. A clean picture containing only one hero and one short label can be richer than a screen full of neon paths. Do not require every shot to mix media.
