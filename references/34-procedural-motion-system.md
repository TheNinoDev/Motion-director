# Procedural motion: production recipes (standalone)
You do not need any external reference videos. Use these recipes to communicate multiplication, scarcity, growth, overload or transformation. A glyph can be a letter, digit or symbol relevant to the actual product. Do not reuse a former brand's visual identity. A high density scene is a visual metaphor, not a substitute for genuine product proof.

## Shot grammar
- Start with an isolated silhouette or a small object against a clean field. A recognizable object should emerge by 0.5–1.5 seconds. For an ad prioritize a meaningful hook over an abstract intro.
- Establish the visual unit: one token, letter or UI element. Hold its recognizable face for 12–24 frames before making it multiply. Keep caption positions fixed during extreme motion.
- Escalate: isolated unit -> grid -> ordered rotating group -> curved surface/volume. Choose at most two or three of these for a normal ad. Cut on a new idea or stressed word. A change in count alone does not need a cut.
- Reset: reduce foreground density and camera speed at the narrative pivot. Restore the original unit or its outline so the viewer recognizes the callback.
- Resolve: redirect the units toward a product-related silhouette or cut to authentic product evidence. End with a quiet, readable brand lockup (1.5–2.5 s). Never invent a product benefit to justify an effect.

## Build instructions from zero
Run scripts/doctor.py; check Python imports numpy, numba, cv2, shapely (>=2.1 for constrained triangulation), PIL. Install from trusted package source only if allowed. Check FFmpeg and font path. Use starter/scene3d/demo.json unchanged first. Generate a 360x640 preview; inspect midshots, ensure faces visible and glyph holes remain open. Then select a scene and duplicate its fields. Change one parameter group at a time. Work in a separate project copy, never edit the installed preset in place. No GUI required. Only use headless advanced renderer if it passes a real local render.

## Exact starting recipes (seconds at 30fps; stretch to speech)
All use actual perspective geometry in the CPU renderer. A scene runs on [start,end) frames, start and end adjacent. Camera Y up, eye in units, target origin unless stated. Positive size, radius and height. Start with FOV 42 degrees. Default dark neutral background; tint is approximate metal base, not full PBR. Use clear 2D text overlay through FFmpeg or render a separate transparent title and composite after CGI; the 3D renderer has no captions.

| Recipe | Parameters | Motion/purpose |
|---|---|---|
| Single macro glyph | grid, count=1, radius=0.01,height=0.01,size=3, eye_from=[0.2,0.1,7],eye_to=[1,0.3,8],spin=0.4,light_sweep=2 | 36 frames, recognizable silhouette and sweeping light; single grid point currently offset by tiny radius, acceptable at this size |
| Dense wall | grid,count=225,radius=3,height=8,size=0.36,eye_from=[0,0,12],eye_to=[2,0.5,10],random_rotation=0.1,light_sweep=3 | 45–60 frames; straight axes, preserve whitespace for labels |
| Collection ring | torus,count=480,radius=2.5,tube=0.85,size=0.27,eye_from=[3,7,7],eye_to=[6,4,7],spin=2.3,orbit=true,random_rotation=1.1 | 45–75 frames; recognizable repeated tokens; aim camera down at ring |
| Spiral sculpture | helix,count=360,radius=1.6,height=6,turns=4,size=0.3,eye_from=[0,1,11],eye_to=[3,0,11],spin=0.9,orbit=true | 60 frames; structured not random, choose product glyphs |
| Tunnel fly-through | tunnel,count=576,per_ring=48,radius=2.4,height=18,size=0.27,eye_from=[0,0,11],eye_to=[0.2,0,1],target_from=[0,0,-10],target_to=[0,0,-12],random_rotation=2 | 45–90 frames; center anchor, keep camera away from near-plane glyphs |
| Scatter to sphere | scatter,to_layout=sphere,count=480,radius=2.65,height=6,size=0.31,eye_from=[4,1,11],eye_to=[0,0,10],seed=123 | 45–75 frames; stable IDs, deterministic position lerp; avoid sudden switch of seed |
| Custom silhouette | custom with points array of N xyz triples, count=N; use outline sampling or mesh surface samples produced by authorized asset pipeline | Design own shape; test geometry and camera. Rigged hand and realistic monster are NOT supplied. |

Use same glyphs, seed, count, layout parameters and eye at adjoining boundaries if a continuous morph is needed. Scene-local random rotations are stable for the same seed; spin and orbit restart locally, so set spin=0 across seamless joins or use an intentional cut. Renderer interpolates position/camera smoothstep. No wall-clock simulation. For nonuniform growth use separate shots with increasing counts, not a claimed continuous particle sim. For a grid-to-helix merge set to_layout=helix with identical count and seed; camera move should be subtle. A scatter-to-logo morph can be approximated by custom points sampled from a logo alpha mask (see helper); do not call it an exact match to a mesh surface.

## Advanced forms: what to do when a module is missing
For organic creature: use a permitted model from product assets or sample a user-supplied silhouette; animate shape with custom points or pre-rendered independent shots. For finger articulation: use headless skeletal glTF animation if installed and tested, otherwise substitute a visually relevant ring or morph rather than create an ugly hand. For true metal use environment lighting, physically-based material and smooth multi-segment bevels if an advanced engine actually works. CPU starter uses analytical highlights with flat face normals, one bevel strip where valid and no real environment reflections, shadowing, DOF or clipping of triangles across the near plane. Avoid near intersections; choose camera safe path. No pretend support. For better edges, render at 2x supersampling, then downsample; do not upscale low-res preview as final. At high counts preview 100–500 instances first; improve density gradually; caps are not performance promises. Render shot-by-shot to limit failure cost.

## Debug from actual frames
- Black image: move camera farther, verify target, set FOV 42, lower count to 1 and increase light/tint. Do not replace shot with random particles.
- Letters tiny: enlarge size, decrease distance, or reduce count so silhouettes are legible. Use typography overlay for essential text.
- Chrome too dark: increase tint/alter light phase and camera, then inspect still. Highlights should define edges; keep dark background distinct. If plastic-looking, do not claim photorealism.
- Near plane pop: move camera or reduce extent/size; renderer discards triangles crossing near plane. Don't fly blindly through objects.
- Render too expensive: preview 360x640, split shots, reduce instances, simplify glyphs. If CPU too slow, use tested GPU path if available, or a high-quality 2D repeat/mask treatment. Record substitute.
- Bad font contour: use a different authorized bold font; narrow bevel or zero bevel only for preview; check A/O counters and thin strokes. Support of every ASCII character is not guaranteed.
- Inconsistent joins: compare last frame and next first frame, align focal point, match scale/direction, use intentional contrast cut if cannot align.

## Completion gate
A successful engine smoke test does not prove an entire source film can be made. For each selected technique store plan path, asset provenance, first/mid/last frame previews, decode status, and human/agent visual review. Then composite 2D text, authentic UI proof and aligned audio; inspect final on a phone-sized preview. Production follows the normal release gate, not merely this CGI gate.
