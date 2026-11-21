# V68 — Asset review and the anti-morphed-PowerPoint gate

## Evidence the agent must actually create

Before committing to 20+ seconds of rendering, leave an asset-use ledger alongside the editable project. At minimum: asset ID/path; source class (`original`, `licensed-third-party`, `explicitly-authorized-product-icon`); individual right/provenance; scene role; planned movement/meaning; and whether the intended renderer can render it. Don't invent downloads or mark licenses verified when they weren't. The `scripts/asset_scout_v68.py` tool can build the first inventory/contact sheet from a passed directory; it does not fetch anything from the internet or grant rights.

## Subject test (not a rigid count quota)

- Can a silent viewer identify a concrete object/emotion/story at 3 key timecodes? If every frame is `headline + 2 boxes`, redesign.
- Is the film relying on one angular visual primitive to portray everything? If yes, investigate illustrated/vector/3D imagery and richer contours/materials.
- Are icons or emojis acting *with* the narrative, or only pinned as decorative badges? Decorative badge spam fails too.
- Are multiple shots visually different at reduced phone resolution? A color change alone is insufficient.
- If an asset comes from a website, was it singled out and authorized? A project screenshot is still prohibited by default even if it contains an icon.
- Is every source SVG free of embedded scripts/external fetches? Reject unsafe markup; do not render untrusted SVG in a live web page.
- Does the whole edit still have useful, selective audio effects, narrative transitions, readable holds and real supplied music? More artwork does not replace those prior requirements.

## Review path

1. Inspect keyframes/contact sheet for recognizable hero subjects, distinct visual language and readable composition. Use `scripts/asset_scout_v68.py` or source proofs.
2. Inspect 1.5–3 s fully animated excerpt for internal asset animation; confirm it isn't just a flat slide translation.
3. Inspect at least the opening, one story turn and the end card at 1x video speed. Verify parent/child silhouette, edge antialiasing, occlusion, mask reveal and imported image alpha; don't rely on FFmpeg metadata.
4. During whole-film review, list the 1–2 weakest spans. Repair visual subject staging if all the visuals remain geometric; don't cover up with particles or SFX.
5. An optional subagent can scout valid assets in a separate workspace while the director selects/accepts them. It may not auto-approve web rights or silently merge source-site screenshots.

## Explicit acceptable exceptions

High-end kinetic-typography-only pieces, logo-free editorial graphic films, geometric abstraction, data visualizations and pure physical-material shots can be great. If the story deserves one of them, choose it deliberately and write why. The problem observed was **unexamined, default poverty of visual vocabulary**, not a ban on rectangles, polygons or hard cuts.
