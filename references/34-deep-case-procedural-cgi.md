# Case 2 — procedural CGI as narrative (1000043457.mp4)
Source: user reference, 576x1024, 30 fps, duration 50.233 s. Inspected stills every 0.25 s, including TikTok outro from ~46.25 s. Time ranges are visual estimates, not original keyframes. Ignore download watermark, original logo and outro. Audible words, speaker performance and exact beat alignment not verified. Captions below are brief observed visual text fragments, not a speech transcript.

## Shot map and reconstruction exercise
| Time (s) | Visible observation | Rebuild strategy (recommendation, not original software) |
|---|---|---|
| 0–1 | Dark skeletal, elongated organic object on illuminated field; caption begins | Sample a curved spine plus rib locations and lateral tendrils; instance a glyph/token at stable locations; camera sees tall silhouette; place readable text separately |
| 1–4 | Isolated shiny @ in a dark rectilinear environment; changing highlights; caption assembles | Single extruded glyph, bevel, slow camera orbit, independent light sweep, 2D grid background and progressive phrase overlay |
| 4–7 | Grid seems to multiply/recede; a few objects enter | Repeated panel/glyph array and camera dolly back; keep repeated units consistent; move foreground separately |
| 7–11 | Floating text handles, metallic swirl; caption compares collection to stones | Ring/torus layout plus a few larger rotating identifiers; focus on one hero at a time; use camera parallax rather than random shake |
| 11–12 | Large metal A, horizontally divided into slices | Extrude glyph; real slicing requires mesh intersections or separate cut meshes; fallback masked strips in 2D with perspective. Keep negative spaces open |
| 12–13.25 | X/V forms become rows of smaller letters | Hard match cut from big front-facing glyph to grid, preserving motif and central framing |
| 13.25–15.25 | Dense upright column/loop shapes composed of many little glyphs | Sample tubular or custom silhouette positions, use low-poly mesh instances, establish shape before moving camera |
| 15.25–19.5 | Original monster silhouette returns; large text announces creation of a monster, then positive twist | Reuse initial asset and angle; change lighting and caption timing to change emotional meaning; do not invent new geometry here |
| 19.5–24 | Dense curved field, vortex-like move into smaller characters, close-up of rings | Torus plus camera dolly; change near/far distance and focal subject; use motion blur only after checking legibility |
| 24–27.75 | Rhythmic layered rings, labels on bands, bright near-camera objects | Several independent rings, stable IDs, phased turns; avoid camera intersecting meshes; label overlay in compositing |
| 27.75–30 | Symmetric arched corridor with bright central vanishing point | Ring tunnel, camera aimed along axis, 2D or modeled light at far end; for exact arch use custom coordinates; maintain symmetry |
| 30–34 | Twisted dense sculpture fills frame, pulls back to a narrow upright form | Morph point layouts or custom mesh surface samples; macro-to-context cut; bright accent only on silhouette edge |
| 34–40 | Hand-like branching shape opens, fragments break away and move | Articulate finger curves or use authorized silhouette targets; true animated hand needs rig or explicit sampled poses and correspondence. Starter provides planar silhouette fallback, not skinning |
| 40–46 | Particles form brand letters, then solid metallic wordmark, long hold | Sample original user-owned wordmark mask, preserve stable point IDs, morph from scatter; match-cut to original vector or extruded wordmark; hold CTA/URL |

## Narrative architecture
The concrete apparent mistake -> collection escalation -> monster metaphor -> positive reversal -> extended visual spectacle -> brand resolution is much stronger than a feature list. Motif continuity is the central editing lesson: one family of letters appears at several scales and levels of organization. Reuse assets. In ordinary marketing videos do not copy the long 20+ second spectacle if it weakens comprehension. Reserve complex CGI for one or two sequences unless explicitly asked for a CGI-led film. A sequence can contain multiple angles of one asset. Use verified product proof elsewhere.

## Motion choreography: precise starting recipes
- Single hero: show the asset immediately, move camera 8–20 degrees over 25–60 frames; light sweep 1–3 radians independent from camera. Start with a readable silhouette, not pure black.
- Multiplication: choose 16, 64, 256, 512 instances for separate escalating beats; retain same mesh source. Increase density only when the story escalates. Avoid resampling positions each frame.
- Grid-to-helix: map stable IDs row-first top to bottom; helix y must follow same direction or the midpoint collapses. Look at 0/25/50/75/100%; the silhouette should remain intentional. Ease with smoothstep or custom timing; never call random every frame.
- Ring scene: count 300–600, start radius 2–3, tube .6–1, glyph height .2–.3 units, 20–40 frame orbit; test camera fit at final vertical aspect.
- Tunnel: ring count = ceil(count / per_ring); radius 2–3, 32–48 glyphs per ring, axial gap around 1–1.6 units. Camera on axis looking down tunnel, forward travel 4–10 world units, near clipping check. A center void is desirable, but add a clear distant focus in compositing.
- Logo morph: generate points once from authorized wordmark. Use same instance count and ordering at both endpoints; preserve the contour, not just an arbitrary density. Render a still at the final qualified state; allow 15–30 frames to recognize formation, then resolve to clean logo 45–75 frames.
- Hand/skeletal shapes: use a legal SVG/silhouette with simple recognizable outline, custom points or properly rigged geometry. Do not pretend a sampled flat image is a sculpted/rigged mesh. A 2D fallback may be better than an ugly 3D result.

## Audio
Decoded mono 16 kHz diagnostic: ~50.225 s; RMS -15.22 dBFS, 15.21% 20 ms windows below -40 dBFS, peak sample +3.06 dBFS after decoding/downmix. This is not integrated LUFS, true peak, evidence of clipping in the source, or verified music beats. Downmix/resampling may affect peak. Use actual dry VO, approved song, ASR/alignment and audition for any new film. The reference has visible progressive captions early, then extended visual-only section. Match actual new voice timing, not these visual times. Preserve the approved user voice preset and provider tags from earlier guides.
