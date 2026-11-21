**V71 placement correction:** Solar Bold/Bold Duotone icons are mainly compact polish for functional-looking UI components (buttons, tabs, cards, badges and statuses). They are NOT the default scene heroes or a cue to animate multiple floating icons. See `152-edit-first-icon-polish-v71.md`. The licensing/source/sanitization instructions below remain valid.

# V70 — Solar Bold & Bold Duotone: practical production use

**Source:** https://solar-icons.dev/ and https://solar-icons.dev/docs/v2/packages/static . Their official `@solar-icons/static` package ships individual SVG files, sprite and icon metadata. Get the catalog with `npm install @solar-icons/static` in a network-enabled project; do **not** assume the agent's sandbox has network access. Select the exact names from the installed metadata or list files; never invent icon IDs.

**License:** Solar icon artwork by 480 Design is **CC BY 4.0 with attribution**, even though the library source code is MIT. For a released ad, retain icon names, exact paths/versions, creator, license, changes and a reasonable credits/attribution method. This file is a workflow guide, not legal clearance of a particular asset. Download from an official package/CDN, validate each SVG before rendering, and do not copy from the client's website or Claude/NOIZ films.

**Use two closely related modes:**
- **Bold:** solid, immediately readable; best when scale is small or for forceful visual verbs (copy, delete, lock, send).
- **Bold Duotone:** primary solid body plus restrained secondary shape to distinguish depth or state. For film use one primary color + one controlled secondary, not five gradients and decorative outlines. Secondary opacity around 0.35–0.55 is a design starting point, not a requirement.
- Use a **cohesive family per film**, not one package per scene. Keep consistent optical size, rounded silhouette, edge softness and proportions. Balance bold icons against accessible large type. Avoid fake extrusion, noisy gradients and fine strokes that make these icons feel like clip-art.

**Actual source → render pipeline:**
1. `npm install @solar-icons/static` in a scratch folder (or reuse an installed local copy). Inspect `node_modules/@solar-icons/static/dist/icons/` and `icons.json` to confirm exact names and style folders; the v2 static docs show `dist/icons/bold/heart.svg` as an official example.
2. Run `python scripts/solar_svg_import_v70.py --source node_modules/@solar-icons/static/dist/icons --find lock` to discover actual names; use `--name NAME --style bold` or `--style bold-duotone` after confirming the matching file. No network call is made by this script.
3. The importer rejects suspicious SVG elements/events/network links, substitutes color tokens where possible, writes a sanitized SVG, a transparent PNG and a per-icon provenance JSON. Review both bold and duotone renders; some exporters need browser rendering when using CSS variables.
4. Import the PNG as an image layer in the existing compositor; keep SVG as editable source. **Do not place an icon as a static centered image under a title**. Pair it with another actor and choreograph cause/reaction/hand-off when the story warrants.
5. Document attribution, e.g. `Solar Icons by 480 Design, CC BY 4.0, modified colors/scale`, link to source and license (`https://creativecommons.org/licenses/by/4.0/`); attribution may be in campaign description/credits rather than cluttering the picture, subject to applicable requirements.

**Fallback when package is unavailable:** Use a small, internally consistent, ORIGINAL two-tone set with a manifest identifying original authorship. The bundled v70 demo provides *original* SVG and raster files that merely demonstrate silhouette/color/interaction, not copied Solar SVG paths or a license to claim they are Solar. Do not block all video work or fabricate downloaded artwork.
