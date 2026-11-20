# V40 primary execution contract
Read this first. Use older guides only as feature manuals. Do not load the whole skill. Never require NOIZ references, repeat a prior demo as an ad, or report success before verifying files. User-locked brand, copy, claims, audio and unaffected edits are protected. This guide does not replace product evidence, voice, rights or release checks in SKILL.md.

## Pick one route
- New ad: inspect one adequate source; choose verified problem/proof/audience; generate three different hook/concept families; select a single story. Write and direct speech per guides 20–25. Obtain or use authorized actual VO/music as required; verify timing and mix. Build a creative record following `examples/creative-v40.json` with mode `advertisement`, verified real proofs and layer links, and a new source using `examples/director-v40.json` only as schema, NOT design. Use the commands below. For an intentionally silent ad use the earlier explicit silent workflow if requested; v40 production route conservatively requires audio for advertisements and revisions.
- Revision: inspect canonical source and existing video, note exact user-requested changes, preserve other properties and assets. Write new source and output directories. Use `scripts/agent_revision.py` for direct timeline edits; do not rebuild unrelated shots. Keep existing audio; don't invent it.
- Tool study: use mode `fictional_study`, no claims of real product; silent allowed. Do not call a study a full ad.
- Script/audio only: use guides 02–04, 20–25; no unnecessary renders.

## Exact commands in order (from skill root, replace paths only)
```
python scripts/director_v40.py catalog
python scripts/production_v40.py start examples/director-v40.json examples/creative-v40.json work/test40
python scripts/production_v40.py preview work/test40 --backend auto --size 540
python scripts/production_v40.py review-template work/test40
python scripts/production_v40.py gate work/test40
python scripts/production_v40.py upload work/test40 --backend auto
python scripts/production_v40.py master work/test40 --backend auto
python scripts/production_v40.py verify-export work/test40
```
For actual ads pass `--audio path/to/authorized-mix.wav` to start. If gate is blocked, read its errors. Review template starts pending: inspect actual video/audio, record a concrete time & observed detail per beat, resolve issues in a new source/revision. Never fill pass by default. Gate checks recorded decisions and hashes, not truth or aesthetic quality. If incapable of inspecting video or sound, say what is unverified; do not certify final. Review native typography, material edges and handoffs with compositor `--at` / `--range` (guide 71). Final upload/master render at 1080 width; actual final playback verification is still required. A completed preview is not delivery. Do not overwrite failed output: preserve logs and use a fresh work directory after fixing source. The audit is advisory; low local motion may be a deliberate hold or masked/material movement. No claims of GPU performance without real hardware tests.

## Motion grammar / choosing tools
- An object visits three or more positions without stopping: `continuous_motion` / `continuous_path`. Write knots in seconds and 720×1280 design pixels. First knot must match starting position. Tension 0–1 (higher reduces tangents), endpoint `rest` for stopping, `moving` only if boundary cut hides start/end. Cubic Hermite has shared derivatives inside the path; exported as linear samples at 4× fps, not exact C1 interpolation at every subframe. Inspect overshoot and clipping; if taking a precise corner use a separate intended stop or increase tension. Existing x/y keyframes cannot be replaced. Use on flat or solid layers, group for linked compositions.
- A marker or element trails another: `velocity_follow`. Source path before follower, shared parent, offset in parent-local pixels, delay in seconds, blend is entry duration. Follower needs unused x/y. Motion follows sampled source; not physical constraints or collision.
- Rotate in travel direction: `tangent_turn`. Source path first, angle offset degrees, max_turn relative to initial rotation, lookahead/response seconds. Uses low-pass smoothing; no mesh orientation solver. Unused rotate track required.
- Subtle breathing: `breathing_scale` with amount 0–.3 and cycles .5–12; unused scale track. Envelope returns to initial scale. Never apply across all objects by default.
- Prior 54 actions/recipes remain available. Use `director_v39`, 38, 37 catalogs and `motion_workbench.py catalog`. Advanced direct JSON remains valid; use renderer-specific guides. Never invent parameter names. New recipes run after earlier compiler tracks; author dependencies in order, don't combine multiple writers for the same channel.

## Concrete creative and repair requirements (before adding VFX)
At each beat choose: intended thought → visible event caused by product/story → focal subject → supporting motion → outgoing anchor → incoming anchor. Document deliberate cut if no shared anchor. Keep one primary idea per ad; avoid feature soup. Design type around actual words and render at least two plausible font families from library; don't send font software. Use image/UI as proof only if genuine, never a fictional UI for a real claim. Treat chrome, glass, jelly as materials when justified, not universal branding. Vary scale, layouts, and timing, not just color. Keep sufficient reading time and intentional negative space. Use 0–2 CGI heroes by default, not a quota. Avoid generic logo intro and repetitive centered headline/card/caption.

Repair cookbook (change one causal property and rerender same interval):
- Stop-start: compare speed approaching and leaving shared knot; use a continuous path or make an intentional hold, not extra fades. Inspect 3 frames before/after and at motion speed.
- Floating marker: compare source and follower at delayed timestamps; ensure same parent coordinates and offset; never patch by arbitrary screen offsets.
- Unwanted reversal: increase tension or move knot; inspect actual silhouette and path overshoot. Keep motion direction through wipe.
- Cheap graphics: remove competing accents; use actual product evidence; increase meaningful scale contrast; verify optical edges at native resolution.
- Busy composition: preserve focal subject; shorten or dim supporting motion only. Do not flatten all animation.
- Missing motion: read `motion-audit.json`; inspect listed layer and time. It samples local translation, scale, rotation, yaw/pitch, opacity at frame cadence. Not pixel visibility, occlusion, mask, mesh deformation or material motion. Treat warnings as investigation, not orders to add effects.
- Unsmooth text: check line breaks, safe area, glyphs, native antialias, motion blur and timing. 3D metal: guide 69, quality/atlas/bevel and two lighting setups; do not mask defects with blur.
- Music: measure real onsets, choose motivated picture accents, listen to entire mix; do not call transients verified beats.

## Evidence and limits
`production.json` hashes explicit plan, source, creative, audio and assets. `preview/evidence.json` hashes rendered MP4, contact sheet and backend report, checks decoded frames/duration/size. `review.json` ties decisions to that preview. Files are local records, not tamper-proof signatures; no independent proof of listening/viewing. Default system fonts, renderer code, nested dependency versions not fully fingerprinted. Never auto-mark visual or audio checks. A weak agent must stop at a blocker, explain it, and show what is actually complete. Keep original source, new plan, report and output. In final reply state resolution/FPS, actual audio, known limits, whether output is a study or ad, and link only verified files.
