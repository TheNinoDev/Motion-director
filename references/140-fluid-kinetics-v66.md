# 140 — Fluid animation: path, velocity, anticipation, impact, settle (v66)

**Problem:** A technically animated object still feels stiff, sharp, linear, robotic or like disconnected keyframes. Make motion serve its subject, and check velocity behavior at boundaries.

## Separate temporal continuity from visual continuity

- **Within a movement** prioritize smooth position and sensible velocity. Arbitrary path discontinuities are actual glitches. Zero velocity at every intermediate keyframe creates robotic stop/start motion. If an object should continue traveling, maintain a compatible tangent/speed through the keyframe (C1 / velocity continuity). Direction changes may require braking, not instant reversal.
- **At an edit**, continuity can be perceptual rather than physically mathematical. A strong direct cut may intentionally reset position and velocity. Never force a morph or slow easing between unrelated scenes just to make a continuous curve.
- For camera pans/dollies and spatial transforms, check path curvature and rotational acceleration. Avoid a sudden 0→100→0 velocity jump from disconnected per-property easing segments.

## Design the complete event

For every significant motion define: `start state → anticipation (optional) → launch → travel/transform → impact/release → follow-through → readable settle`.

Three style-specific defaults, **not universal presets**:
1. **Editorial snatch:** brief setup, acceleration, strong exit, cut at maximum action. Avoid generic 1-second ease-in-out that makes theft feel leisurely.
2. **Physical panel/tab:** fast but smooth travel, restrained 3–8% overshoot when impact/elasticity fits, short damping settle, secondary labels arrive after hero. Do not overshoot typography meant to stay readable.
3. **Graphic reveal:** matte starts from the story's object, follows a designed curved or straight path, completes the frame reveal decisively, then let the next hero start. A polished matte needs no fake turbulence.

Use true Bezier path tangents (control points related to outgoing and incoming direction), velocity-aware splines, ease curves fitted to desired motion, or restrained damped spring where appropriate. `smoothstep` can provide soft endpoints but using it for *every* property at *every* segment causes all objects to start and stop together. Stagger leaders/followers by small meaningful offsets; avoid decorative perpetual drift. Secondary motion must communicate weight or relation.

## Implementation + tests

- Make timing explicit in the chosen editor timeline. Prefer its keyframes, easing, motion paths, parent transforms, vector masks and shared anchors, documented by actual CLI/schema or a working proof. Do not replace a capable editor with a simple Pillow/frame loop just because it is familiar.
- At transitions check two independent things: (1) does hero remain visually related to the next scene? (2) does its movement have a believable trajectory or intentional hard-cut logic?
- Inspect a seam loop at **1x and 0.5x**, not just a snapshot. For a claimed smooth movement, review at frames n-3, n-2, n-1, n, n+1, n+2, n+3 around any keyframe or shot edge and chart position/angle for unexpected jumps. A numeric flow detector may flag candidates, but does not decide whether a stylized impact cut is good.
- If an effect appears stuck, confirm whether the keyframe curve is animated over the intended duration, whether two layers are accidentally reparented, whether shapes leave the crop without designed reentry, and whether a mask clips the wrong coordinate system.
- Check phone readability after the motion settles. A 30-fps file can still have 3-fps-looking motion, off-by-one frame jumps or a transformation that barely registers.
- Favor strong anticipation and a quick meaningful hero action with a controlled settle over continuous mild movement. Deliberate rests are allowed when the viewer must read or feel a pause.

## Dead-frame caution

V65's low-change scanner catches holds, not bad seams, jerky physics or weak storytelling. In a **10-fps, 180x320 grayscale** comparison with per-frame mean difference below 2/255, GPT-v65 showed ~27% low-change intervals, Claude's 24.6s protection video ~67%, NOIZ's 50s sculptural spot ~19%. These values **cannot rank aesthetic quality** and differ from older 2-fps comparisons. NOIZ's last seconds intentionally rest on outro graphics; Claude has meaningful long holds. Never optimize the numerical percentage; optimize the viewer's experience. A visually static hero with an earned pause can be better than a constantly drifting dashboard.
