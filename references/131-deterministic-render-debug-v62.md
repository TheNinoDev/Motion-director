# 131 — Scene architecture and precise debugging for coding agents (V62)

This is an implementation discipline, not a demand to adopt a new engine or alter the skill's scripts. The actual successful Claude case authored fresh `film.html` with JS `render(time)`, captured it in Playwright and rendered with FFmpeg. The weaker GPT used original Pillow/NumPy code and FFmpeg. **Either backend can be excellent.** Pick by creative need and available runtime, then preserve the same observable behavior: arbitrary-time inspection, correct layers, natural choreography and targeted revisions.

## A. Choose the simplest architecture that supports the ART

| Creative need | Good available route | Watch-outs |
|---|---|---|
| Layers, DOM type, SVG shapes, clips/masks, blur/glow and precise text layout | Authored *blank* HTML/CSS/JS scene + Playwright/Chromium screenshot or screen capture | CSS layout origins, stacking contexts, font load, transform origins, display state, excessive screenshots, browser asset restrictions |
| Full-screen vector graphics, charts, compositional masks, small moving shapes | Original SVG/Canvas or a supported composition renderer | Transform order, numerical paths, correct alpha, interpolation |
| Simple deterministic bitmap art and controlled effects | Pillow/NumPy/OpenCV with native arrays and FFmpeg | Flat pixel-art look from repeated rectangles; slow per-frame loops; fonts/hierarchy; only technical easings |
| Real spatial material, genuinely 3D silhouettes or lens movement | Supported 3D engine with real bevels, normals, lighting and camera | Fake 3D from beveled rectangles; bad perspective; expensive export before design works |
| Existing layered motion composition, recorded interaction or footage | Existing skill compositor/toolchain | State reset, unreadable wide screenshots, source-visual permission, pasted original site assets |

Render from **originally authored pixels**, not copied HTML, screenshots or images from a local project/site. Facts and truthful names can inform new artwork. If the environment lacks the ideal route, build an achievable treatment rather than a bad fake version of a complex CGI shot. Check actual tool presence first. Do not install/update many dependencies as a substitute for direction.

## B. Deterministic time model

Design `render(t)` as an idempotent pure-ish update: rendering at 7.6 s before 2.5 s must yield the same visual state as reaching 7.6 s sequentially. Reset every animated object's **visibility, display, text, opacity, transforms, absolute position, z-index, mask and derived geometry** that depends on t. Never rely on incrementally accumulated frames or previous `display:none` state unless you explicitly reset it. Use fixed RNG seed when visual elements depend on randomness; assign each procedural element stable identity and parameters. Load fonts/assets and await readiness before frame capture. For audio sync, compute state directly from actual measured seconds.

A useful **illustration, not a drop-in renderer**:

```js
const clamp = x => Math.max(0, Math.min(1, x));
const progress = (t, a, b) => clamp((t - a) / (b - a));
function render(t) {
  const p = progress(t, 5.4, 6.2);
  // Explicitly set ALL dynamic properties each call; no += or leaked state.
  sceneOne.style.display = t < 6.4 ? 'block' : 'none';
  sceneTwo.style.display = t >= 5.4 ? 'block' : 'none';
  const x = 180 + (760 - 180) * (p*p*(3 - 2*p));
  movingShape.style.position = 'absolute';
  movingShape.style.left = '0px';
  movingShape.style.top = '0px';
  movingShape.style.transform = `translate(${x}px, 690px) translate(-50%, -50%)`;
  movingShape.style.opacity = String(p);
}
```

This shows independent time state and a single resolved path, **not** a premium animation recipe. Real motion includes carefully justified anticipation, trajectory shape, overlaps, material response, focal framing and a meaningful visual result. Avoid identical ease curves for unrelated subjects. For parent/child objects inspect coordinate systems and transform origins. Do not place a child with a native CSS `left` AND a translated target without checking the resulting center in actual captured frames.

## C. Exact, cheap, falsifiable render debugging

1. Save named timestamps **before, during and after** each complex action/transition. Show them as individual native images plus a contact strip; print the intended and actual center or bounding box of the subject.
2. When elements are unexpectedly diagonal/off-center/hidden: inspect `computedStyle.position`, `left/top`, `transform`, `transformOrigin`, parent `getBoundingClientRect()`, DOM order, `display`, `opacity`, clipping and z-index. In a procedural renderer inspect equivalent parent/child matrices. Fix the **cause**.
3. Test non-monotonic time calls (e.g. 8.0 → 2.0 → 8.0) and compare target frames. This catches state retention, `display` leakage and unseeded randomness. Where rasterization causes incidental nondeterminism, compare with a tolerant pixel threshold and investigate material changes.
4. Render a short moving slice with actual continuous samples. Inspect *motion*, not just keyframes: collisions, path cusps, unnatural instant stops, anchor jumps, unexpected speed changes, transitions from one visual role to another.
5. Re-render only necessary spans while iterating. After fixing the scene or shared layout function, rebuild a **complete cut** and check neighboring transitions, because a local CSS/JS fix can change other frames.

Claude's supplied log shows this exact pattern. It first tried changing visibility and transform offsets, then corrected the default position of created elements, reviewed more frames and adjusted later transition states. The lesson is **frame evidence → hypothesis → precise code change → new frame evidence**. Don't add ten arbitrary tweaks until something looks less broken.

## D. Resource and export discipline

Choose a preview resolution that preserves key composition decisions; then render final at requested resolution/FPS only after visual direction works. When capturing via Playwright, test screenshot throughput on several frames before committing 600+ frames; use a single ready browser context, avoid restarting a browser each frame, monitor renderer logs and process errors. Catch `pageerror`, check FFmpeg exit code and final duration. When expensive rendering must be repeated, change only the minimal region or parameter as supported, then do an actual final integration check. Don't replace a complete film with a contact sheet.

If audio exists, keep original VO/music/SFX stems separate, align actual performed words and major music events before locking shots. If speech audition is unavailable, mark approximate alignment (e.g. VAD/silence based) as approximate. A statistical beat drop around 30.1 s may justify choosing an offset for one specific track; it does NOT mean all tracks have that drop or that the same offset applies to future ads.
