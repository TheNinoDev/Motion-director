# 134 — Use Motion Director's editing potential (V64)

**Active capability-routing instruction.** The GPT runs used hundreds of lines of bespoke Pillow drawing, reimplementing elementary cards and interpolation while existing Motion Director editors offered transformable groups, timed layer properties, real path morphs, mattes, masks, perspective, shutter sampling, cached shots and integrated audio. The Claude runs used purpose-built HTML/CSS/JS and visual debugging, with stronger staging. The inference is NOT “Pillow is bad” or “every scene needs 3D”. It is: **weak agents need to inspect the available editor before building a less capable one**, while preserving Claude-like creative freedom and ruthless simplicity.

## Three-minute capability check, before creating a renderer

1. Read `starter/composite_film/README.md` and `starter/unified/README.md` (both contain historical screenshot examples; the source INFORMATION-ONLY firewall in `SKILL.md` overrides those). Check the installed `starter/composite_film/compositor.py --help` and `starter/unified/production.py --help` rather than assuming flags exist. Confirm the selected script and its dependencies are actually present.
2. Write a private 3-line film routing note: `Hero and visual action: … / Existing feature and path: … / Why this feature makes the result better: …`. If the answer to the last part is weak, simplify the shot; never add advanced effects to impress yourself.
3. Execute the **actual packaged editor**, not a lookalike implementation. For a continuous 2D/2.5D film prefer a compositor plan with persistent layer IDs. For distinct specialist shots use the unified controller and its existing shot engines. A custom scene renderer is allowed for a provably missing visual technique, unusual interaction, or performance reason; integrate its output as an authorized original asset/clip instead of rebuilding the entire editing/mixing/export stack.

## Real editor capability map: use only what the story earns

| Story need | Proven tool | Valid capability |
|---|---|---|
| A single card turns into a new arrangement while type stays attached | `starter/composite_film/compositor.py` | `group` + `parent`, timeline keyframes on `x/y/scale/rotate/opacity`, persistent object IDs |
| A line transforms into a boundary, path or moving gesture | same | `path` + `points_keyframes`, matching point counts, `trim` |
| A scene revealed by a physical-looking window | same | `mask` with `mask_progress`, `matte` and `blend` where appropriate |
| A fast purposeful 2.5D turn | same | `pitch/yaw`, grouped motion, optional `shutter_windows` and `--samples` |
| A specialized title/character/3D/data or textured shape | `starter/unified/production.py` | Actual shot engines `type`, `expressive`, `scene3d`, `mesh`, `material`, `data` etc. Read the relevant starter README/schema before authoring |
| Multiple specialist shots with cuts/caching | same | Frame-counted shots, cache, precise transitions, original voice/music inputs |
| Speech, music and end-to-end gate | `scripts/production_v50.py` and existing audio tools | `start/next/preview/gate/verify-export`; use appropriate inputs and do not fabricate review |

**Compatibility:** The compositing JSON uses `version, width, height, fps, duration, background, layers`, global seconds, and layer-local coordinates relative to a parent. `--check` checks plan validation; `--at 1.5` writes a still; `--range 1 3` renders a picture-only excerpt. These CLI flags were checked against the actual packaged code. A `matte` source must be an earlier layer ID, not a web image. `mesh` and `scene3d` are different renderers with different limits. Do not hallucinate After Effects features or promise that every kind of path can morph automatically.

## A reproducible two-second proof (real package, not an invented API)

`examples/editor-potential-v64.json` is a tiny **original** illustration. It contains grouped text and geometry, an independent animated path, and a clear movement/settle. Use it only to confirm editor controls, not as a scene to copy into a real ad.

```sh
python starter/composite_film/compositor.py examples/editor-potential-v64.json work/engine-test --check
python starter/composite_film/compositor.py examples/editor-potential-v64.json work/engine-test --size 360 --at 0.3 --at 1.3 --at 2.6
python starter/composite_film/compositor.py examples/editor-potential-v64.json work/engine-test --range 0 3 --size 360 --profile preview
```

If any step fails on the target machine, read the error, compare the schema to the installed README and fix that problem before inventing an alternate pipeline. Do not report a capability as tested without a successful command/result.

## Keep the editor in the loop, not just in the ZIP

- **Pre-production:** choose one human problem, a hero, a meaningful action and contrast. Choose 1–2 *relevant* native capabilities, not all of them. Edit the real project JSON; do not just mention a tool in the final response.
- **Proof:** render a still before the event, a midpoint, a settled result and a short actual-motion excerpt from the same editor. Reject unappealing framing even if every feature works. Diagnose parent transforms and easing before adding new renderer code.
- **Full cut:** keep coherent persistent objects within the compositor or combine cached native engine shots. Drive timing by supplied VO/music; do not force people to regenerate provided assets. Keep native editable projects and separate source audio.
- **Review:** inspect the whole film and its actual frame-to-frame timing, text readability and audio. A screenshot is not proof of smooth animation; file metadata is not proof of creative quality. When the weak shot is cluttered, subtract before using more editor capabilities.
- **Release statement:** give a factual line such as `Editor used: compositor (groups, animated path, keyframes); specialized scenes: none; custom renderer: no; review: actual timed excerpts + final decode.` If using custom code, name the genuinely missing capability and the bundled component used for integration. No false claims about actual usage.

## Anti-patterns and corrective behavior

**Bad:** Immediately create a 500-line script with `draw.rectangle()`, uniform `smoothstep()` for every object, one headline across all scenes and an FFmpeg export. The packed editors are untouched, no editable layer plan exists, and the model later wonders why the edit feels stiff.

**Better:** Keep the film idea equally simple, choose actual semantic objects and model their interaction in an editable compositor timeline. Use precise per-object easing and parenting where needed. Let the first object carry motion into the next scene. Check the actual playback, and change the staging when the shot is boring. The editor unlocks the technique; the director still makes the taste decisions.

**Also bad:** Demand three masks, a mesh, particles and 3D in every commercial simply because those features exist. The most effective Claude shots are sometimes only one large shape and one dramatic change. A hard cut at the correct lyric can be better than a complicated shader transition. **Use the editor's possibilities to express an idea, never to decorate a lack of one.**
