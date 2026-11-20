# 126 — V61: Premium motion grammar, even in basic code renderers

Weak agents often implement `smoothstep(a,b)` on a box and label the outcome 'kinetic'. Smoothstep is just an interpolation function. Premium direction depends on shaping the **change in position, scale, mass, direction, opacity, geometry, relationships and attention over time**. The user criticized v60 as stiff, unpleasant, too simple, and filled with inactive stretches. This guide teaches a limited, practical movement vocabulary for the existing renderer—not new tools or mandatory effects.

## Build animation with intention, not a property list

Every focal event needs four answers: why does it start NOW; what visibly changes; how does its energy travel to related objects; what readable result does it leave? Specify a **screen-space path**, motion envelope and dependent follow-through. Evaluate it at real duration, native aspect ratio, and phone-size playback. A single lovely still frame or a 3-frame strip is not motion evaluation.

**Useful progression:** attention is drawn to an object; it accelerates or deforms with purpose; something else reacts; the composition lands on an outcome. An instant cut may replace the move when contrast is stronger. A quiet dramatic hold may replace secondary movement when reading matters. Do not apply identical anticipation/recoil to every scene.

| Motion class | Concrete direction | Weak implementation to reject |
|---|---|---|
| Gesture with weight | Source card is grabbed at one edge, rotates along an arc, accelerates, releases, and transfers momentum to a different target | Entire perfectly centered card moves by 20 px with ease-in/out |
| Morph / topology | A familiar symbol splits into components, reorganizes, makes contact and visibly becomes a NEW arrangement | Same code rectangle with color/name change |
| Editorial scale shift | One small word/letter expands to full-screen and its countershape becomes the next scene's opening; maintain registration at the midpoint | Three unrelated text slides zooming independently |
| Foreground/background | Different planes react at staggered speeds with believable camera/subject logic, giving depth and a clear focal shift | All planes translate with identical scale/speed |
| Reaction | A duplicated object knocks others, producing delayed sequential reactions proportional to their proximity | All objects fade in synchronously |
| Controlled cadence | Dense short burst / readable pause / decisive reveal / release; timing tied to music/VO meaning | Same 1-second movement on every element and every transition |
| Signature material | One carefully controlled refraction/metal/softbody/light action demonstrates the story's metaphor | A permanent glow pasted over every graphic |

## No stiff 'one easing fits all'

Use time-continuous movement where objects are supposed to flow through a boundary. If one path segment ends with velocity but the next begins from rest, it snaps perceptually even when positions match. Specify tangents and at least approximate velocities at event handoff. Stagger secondary motion by role: an object responding to a hit should generally react *after* contact, not in parallel before it. Use different envelope shapes deliberately—fast ease-out, acceleration, delayed recoil, damped settle, controlled hold. Test sampling at the actual 30-fps output. Don't create discontinuities by abruptly switching between independently calculated `if t<a`/`elif t<b` poses with mismatched derivatives. A path's physical meaning matters more than an arbitrary 'motion strength' setting.

A practical motion sketch with relative times (no new API; map onto existing properties):

```
At A: a single code ribbon sits across the center; its far end is visually tethered.
A+0.00–0.12: tether tightens; 5–10% local deform, not full composition move.
A+0.12–0.42: ribbon sweeps across frame on a curved path; local glyphs lag behind.
A+0.28–0.56: glyphs peel away sequentially and occupy a NEW spatial lattice.
A+0.56–0.74: arriving fragments compress, overlap/rebound slightly, lose energy.
A+0.74–end: one readable new formation remains; cut/match to next event.
```

Do NOT copy this exact timing for a 24-second film or invoke a physics model the tool cannot perform. This is an example of a timed cascade and an actually changed arrangement. Implement with supported groups, parent transforms, piecewise paths, keyframes or a deterministic frame renderer. Validate the composition at 0%, 30%, 60%, 100% and watch the complete moving clip.

## Major composition changes are not camera shakes

A full film must alternate focal functions: an object macro; a dense pattern; a graphic rupture; a new spatial relationship; an understandable demonstration; a strong quiet resolution. Not mandatory in this order and not all every time. Frame roles should be legibly different in **silhouette, scale, negative-space distribution, number of competing objects and image depth**. A big title over a small lower panel for six sections is one composition pattern, not six. Build at least one scene with an object visibly occupying most of the frame, one with a clear spatial event, and one with a decisive visual payoff **if the story calls for them**. An original 2D edit can be excellent; forced cheap CGI is worse than an expressive flat motif.

Use visual hierarchy intelligently: if the main animation's pieces are 10 px across while the heading covers a third of the screen, that motion probably won't read on a phone. Fix scale, focus and contrast before increasing movement speed. For short text, animate the typography *as a physical participant*, not merely a timed overlay. Make new visual meaning from a moving object: a word cracks because something crosses it; a mask becomes an aperture; a line becomes a physical barrier; a token passes or fails a gate.

## Review the movement itself

Inspect actual video around action boundaries for pop/jerk, acceleration discontinuity, stutter, unreadable blurs, moving background noise and unnecessary flash intensity. Ask: does the *direction* make spatial sense? Are linked objects reacting to the same cause? Does one action lead the gaze into the next? Is the landing strong enough to be remembered? If only still frames are available, say that full motion quality is unverified. If a clip looks stiff, redesign its path/timing/causal action. Do not 'fix' stiff movement by applying more glow, random wiggle or global easing indiscriminately.

References 75–83 and 86 contain existing pathways and supported properties. The goal is precise creative choices and competent implementation with what already exists, not another animation-engine feature request.
