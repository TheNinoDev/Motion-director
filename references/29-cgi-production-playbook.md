# CGI production, from zero (v7)

Read after case 28. Most website ads do not need 3D. Use at most one or two hero CGI sequences by default; a sequence can contain several short angles or one callback of the same asset. Rest should be genuine UI, clean typography, graphic composition. A 3D sequence must earn its extra time. Ask no user to learn Blender or build the asset for you. If quality is insufficient, use a strong 2D motif, not fake blocky 3D. No claim of 3D if the result is 2D.

## Decision tree, in order
1. Write one factual promise and one visual metaphor. Identify its audience, whether this product's branding supports premium chrome, and the actual visual role (hook/reveal/payoff).
2. Run doctor.py and check actual engine. Use installed `blender --version` for Blender; inspect available renderer and API for installed version; Three.js only if a tested GPU or software WebGL context works. Prefer offline Blender Cycles/Eevee for physical glass, DOF and PBR; choose the installed engine that succeeds. Do not install paid software, buy models or download unauthorized assets without permission. Use the included CPU ray marcher for a minimal real 3D smoke test if NumPy and Pillow are available; it isn't a full renderer replacement.
3. Decide whether to generate geometry with primitives or use an authorized existing asset (preview quality, license and shape first). Choose 1–2 material families. Save an editable scene, deterministic seed, and relative assets.
4. Render three stills: macro, medium, wide; at least one near first/last lighting state. Inspect at actual phone scale and full crop. If all materials look gray, fix reflections before animation. If geometry looks angular, fix before animation. If composition looks generic, change the object or framing.
5. Animate one axis or camera or light before combining: compare frame 0, middle, end. Then render a small low-res test (same aspect/FPS/duration) and decode it. Inspect frames and preview motion where available. Render only approved-by-review shots at target resolution. No forced long full-quality render before tests.
6. Composite with 2D UI and typography as independent layers. Do not place small factual UI text in the 3D texture. Preserve exact input text and font files. Match environment black levels, framing, color management and cadence. Use rendered RGBA when supported, otherwise render matching background; prevent alpha fringes and unintended crops.

## Geometry: concrete starting values (scene units, not original NOIZ parameters)
Use hero height or diameter H=2 scene units; scale other numbers by H/2. For font extrusion, choose a licensed sans font with solid counters (holes); use actual font curves, not individual boxes. Set extrusion depth .12–.23, bevel .015–.035, bevel segments/resolution >= 4. Recalculate normals and use smooth curved faces, flat faces on cap as appropriate. Inspect silhouettes from three-quarter and macro views. For rings/cylinders start with 96–128 radial segments; scale bevel to 1–3% of radius, 4–8 segments. Avoid spline seams and overlapping near-coplanar surfaces. Keep ring plane, pivot, cap and surface normals intentional. For lettering on ring, place glyph centers at angle theta=2*pi*i/N; position (r cos theta, r sin theta); rotate local tangent to orientation. Check actual glyph orientation; lip thickness must not swallow text. Separate symbol from face by physically sensible relief, not z-fighting.

### Simple studio construction (Blender-style coordinate system, Z up)
- Object rests at z=0 on dark floor; if 2-unit tall, center z=1.0. Set scale transforms; center camera target at (0,0,1.05). For letter face pointing toward -Y, camera starts near (3,-7,2.4), looking at target. Camera orientation via look-at with up Z; ensure no roll. Floor plane ~20x20, no visible horizon or seam.
- Material A: metallic 1.0, neutral base linear ~.65–.8, roughness .16–.25. Material B: dark substrate base .015–.05, metallic .05–.3, roughness .28–.48. Floor roughness .18–.35, dark color .015–.035. Exact reflectance depends on renderer and view transform. Avoid default gray diffuse pretending to be chrome.
- Key area: rectangle ~3x6, camera-left above/front, strong broad reflection. Rim strip: ~.6x5, behind/right, edge definition. Fill card: ~2x3 on opposite side, lower energy. Begin with key:rim:fill light energy ratio 1:.65:.2, adjust based on observed reflections and renderer exposure. Use world dim neutral, black cards/negative fill to preserve contrast. Never use a point light as sole chrome light. For a truly reflective object, reflection of environment is the design.
- Camera: 65–90 mm hero 3/4, 90–120 mm macro starting point, or orthographic for pure graphic composition. Move back for an equivalent frame when increasing focal length. Keep target and place focal depth deliberately; f/3.5–5.6 macro starting point, f/8 or disable DOF for readable hero. Actual scale/lens renderer will change effect. Do not animate zoom and focal length and orbit simultaneously without reason. 
- Output: fixed exposure/view transform; test highlights, shadows and reflective floor. Cycles/Eevee exposure varies by version; choose confirmed view transform, inspect actual output. Denoise if it preserves crisp highlights; increase samples if noise dances. Render PNG sequence and retain frames, especially if heavy. Use 30 fps (or final fps); use .3–.5 shutter factor as a starting point for motion blur; check readability.

## Keyframe examples (30 fps, adapt after real VO)
| Recipe | Keyframes | Review |
|---|---|---|
| 24-frame macro reveal | 0 framing 1.9x tight, key light dim; 10 focus detail, light sweep; 23 framing 1.0 or cut to full object | Detail must be identifiable or create deliberate curiosity; no smear |
| 36-frame orbit | yaw 25° at f0, 14° at f18, 8° at f35; target locked; smooth ease-in-out | Keep silhouette, floor contact and highlights consistent |
| 42-frame light sweep | strip reflection from left to center to right; fixed camera, fixed material | Dark enough for contrast but edges legible; avoid flash |
| 30-frame showcase pullback | object height 80% at f0, 55% at f29; reveal plinth or context; smooth ease-out | Meaningful context appears, no abrupt clipping |
| 12–20-frame callback | cut from UI on shared central glyph to earlier asset crop, then back to genuine result | Only when resolves a thought; no unrelated CGI filler |
| 45–75-frame end card | hero object static/slow, clean logo, factual benefit, one CTA | At phone size readable, no watermark/overlay conflict |

These are intervals `[start,end)`, last rendered frame end-1. Avoid two adjacent shots rendering the same frame accidentally. For each actual shot record frame count, cue ID, object ID, starting/ending camera, focus and light state. Use normalized coordinates where compositing 2D. Do not place text or icon near platform overlays; use actual safe-region template.

## Failures and mandatory correction
- Everything grey: switch dark substrate to appropriate roughness, add large white strip reflections with contrasting dark environment, then adjust camera. Raising exposure globally washes out blacks.
- Hard rectangular edges: apply more radial segments/bevel before rendering. If bevel damages letter counters, reduce radius; test small glyphs.
- Plastic look: ensure actual metallic material, not just specularity; compare chrome with dark nonmetal floor. Avoid reflection that resembles a duplicate logo with no perspective.
- Noise/flicker: stabilize lighting/sampling, render a short sequence, inspect sequential frames. Increase sample count or use temporal-consistent approach; don't add random per-frame grain to hide errors.
- Bad DOF: focus on visually important object; disable for functional UI. Prefer 2D overlay for factual labels.
- Camera too close: check silhouette and crop through whole orbit; use intentional macro cut, not half-visible accidental crop.
- Weak metaphor: cut CGI if audience needs a long explanation. Replace with an actual UI action. Style is not proof.
- No Blender or functioning WebGL: run CPU demo or build a carefully composed 2D scene; disclose fallback. Never tell user a rendering engine was used when it wasn't.

## Included starter
`python starter/hero_token.py --out preview.png --still --width 360 --height 640` (NumPy/Pillow); `python starter/hero_token.py --out preview.mp4 --width 144 --height 256 --fps 30 --seconds 1.2` (also FFmpeg). This is genuine analytic 3D geometry using a signed-distance ray marcher, simple materials, directional reflection environment, one reflected ray for floor and camera orbit. It is intentionally limited: no physically complete lighting, no full PBR path tracing, no arbitrary font meshes, no DOF, no shadows beyond basic geometry, no audio, low-res smoke test. Never ship its stock symbol as a final ad. Adapt geometry to product or use a stronger full engine. Use test output to learn camera, metal contrast, bevel and floor continuity. Set OPENBLAS_NUM_THREADS=1 if NumPy threading slows down small renders; preview small before raising resolution.
