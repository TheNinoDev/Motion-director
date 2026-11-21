# V75 — Layout mechanics, optical alignment, collisions and foreground hierarchy

## The repeated failure
The user-supplied 24.6s film shows an Account/Device fork growing into the large CUSTOM VM title zone around 13.5–15s. This is more than a tight margin: a diagram line passes where large text should remain unobstructed. Labels also compete with moving diagrams during changes. Do not assume well-chosen fonts excuse actual geometric collisions.

## Lay out on a real canvas, not as independent objects
1. Start with one intentional focal region and a simple layout hierarchy: HERO, SUPPORT, annotation, UI chrome, background. Each main object has a named parent group or viewport anchor. Make coordinates and typography responsive to chosen format, safe areas and actual fonts.
2. Set content-safe guides appropriate to destination. For an ordinary vertical 9:16 short, keep meaningful copy and controls away from system UI and screen edges; exact margins depend on platform and context, not a universal number.
3. Calculate **visible glyph bounds** or reliable measured text boxes using the rendered typeface, not estimated character count. Descenders, stroke/shadow and line height count. Non-text connectors should route around type zones, not pierce them.
4. For each keyframe and several intermediate samples, test hit boxes (AABB as rough first pass; geometry/text masks as needed). Catch **connector-versus-title**, text-versus-text, icon-versus-caption, clipped objects, UI label spills, and important button content underneath another layer.
5. A visible overlap is valid when designed: masking through a headline, a paper card passing behind a foreground object, or cinematic text revealed by occlusion. Mark the pair, intention, and when it happens. Never globally outlaw overlapping layers, which would kill depth.
6. Optical center is not always mathematical center. Align baselines, visual weight, line endpoints, button icon optical center and card padding **by eye in real frames** after automated candidates are shown.
7. Apply a contrast/legibility pass on the actual rendered composite at phone size. Avoid bright same-weight colors everywhere; use one readable focus and quieter support.

## Technical acceptance protocol
Use `scripts/scene_ownership_audit_v75.py PLAN.json` for plan-level conflicts. The script intentionally is not an image understanding system; it can flag known boxes, stale ownership and repetitive composition signatures, but it cannot judge the exact anti-aliased glyph mask, quality of easing, audience interest, or color psychology. Validate those by actual review of `scripts/two_frame_finish_v74.py` pages. On visible defects, edit keyframes/collision geometry, rerender, and repeat.

## Correct the specific class of bug
If the connector to ACCOUNT and DEVICE intersects CUSTOM VM: move the connector's branching start and route it through reserved negative space **or** replace the title placement with a nonconflicting lower third. Don't just lower opacity or add a bigger glow. Observe start, middle and end of the line animation; small bboxes at the endpoints are insufficient.
