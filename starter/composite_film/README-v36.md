# V36 composable motion workbench

Optional authoring layer over compositor.py. No new dependencies. Use `scripts/motion_workbench.py catalog` for supported fields and `compile SPEC OUTPUT` to get an editable plan. Existing direct JSON, unified renderer and all old examples stay supported. Absolute image/font paths emitted for portability between local build folders; on another machine rebind assets. No files downloaded. A named asset is referenced as `"src":"@workspace"`. `cues` map names directly to seconds. Root fields: version 1, duration, fps, width, background, grain, fonts, assets, layers, cues, actions, sound_events, shutter_windows, shutter. `layers` follow normal compositor schema, active defaults to whole duration. Supported actions:

| Operation | Fields in addition to op/layer/start/end/ease | Effect |
|---|---|---|
| fade | from, to | opacity 0–1 |
| slide | from:[x,y], to:[x,y] | translation |
| zoom | from, to | uniform scale |
| turn | from, to | planar rotation degrees |
| tilt | from:[yaw,pitch], to:[yaw,pitch] | 2.5D or solid orientation |
| reveal | from, to | vertical reveal |
| wipe | from, to, mask | iris, wipe, diagonal, shutter |
| trace | from, to | path trim |
| morph | from, to | volume phase, shape-specific response |
| light_sweep | from, to | supported light parameter |
| pulse | from (base), amount (ratio) | rise and return scale |
| orbit | center:[x,y], radius:[rx,ry], degrees:[start,end], samples | sampled elliptical path with linear interpolation, not 3D camera orbit |
| curve | points:four [x,y] control points, samples | cubic Bezier path with chosen time easing, sampled into keys |
| stretch | from:[sx,sy], to:[sx,sy] | independent planar scales |
| bend | from, to | 3D bend (-.8–.8) |
| twist | from, to | 3D twist (-2–2) |
| refraction | from, to | volume IOR (1.01–2.3) |
| roughness | from, to | 3D roughness (0–1) |
| elastic | start, preset, mode, strength | modal deformation on solids; not contact physics; no end required |
| handoff | target | matched-anchor opacity crossfade; not geometric morph |

Operations can overlap on independent channels. Do not define conflicting tracks. Values hold before first and after last action; no silent extrapolated travel. For handoff, source precedes target, both must be active through overlap, same parent and centers within 12 design units at midpoint; manually check actual silhouette/velocity. For variable content and 3D, native temporal sampling remains available. Strict new-spec checks catch typo fields but do not guarantee every nested config or design decision. `audit` accepts existing valid plans and emits advisories rather than rewriting them. `agent_revision.py` accepts JSON `{ "source_sha256":"...", "reason":"...", "changes":[{"layer":"hero","set":{"roughness":0.16}}] }` with optional `remove` arrays; source fingerprint from sha256sum or Python hashlib, edits constrained to existing layer fields, not structural or audio changes. Both tools refuse overwrite. All source audio remains outside these operations. The included 6-second fictional example is a technical integration study, not a finished advertisement.
