# V70 — Official Solar Bold and Bold Duotone production pipeline

**Source:** https://solar-icons.dev/docs/v2/packages/static . Obtain authentic icons from `@solar-icons/static`, not an AI-drawn approximation falsely labeled Solar. `npm install @solar-icons/static` in an allowed network-enabled project; inspect `node_modules/@solar-icons/static/dist/icons/` to determine **exact** style folders and available names. V2 documentation shows `dist/icons/bold/heart.svg`; do not guess other filenames.

**License:** Code MIT, but **icon artwork by 480 Design under CC BY 4.0, attribution required**. Record creator, source/version, original icon names, modifications, and where credit appears. Example: “Solar Icons by 480 Design, CC BY 4.0; colors modified”; link the license https://creativecommons.org/licenses/by/4.0/ . This requirement is independent of whether a personal editing program supports the images.

Bold: solid, immediate, rounded, reduced detail, best at smaller scales. Bold Duotone: one primary fill and restrained secondary fill/opacity; choose two coordinated colors and consistent proportions. Keep forms simple, striking, legible, and visually coherent across the film. Do not turn every icon into an extruded shield sticker with decorative frames and gradients.

Use `python scripts/solar_svg_import_v70.py --source node_modules/@solar-icons/static/dist/icons --find lock` to inspect actual local file names. Then `--name EXACT_NAME --style bold` or `--style bold-duotone` if that file is present; the importer validates local SVG, resolves known color variables, exports transparent PNG + sanitized editable SVG + provenance. It does not scrape the website or assume internet access.

Import the PNG into `starter/composite_film/compositor.py` as an `image` layer. Give it a path, overlap/contact with other actors and a transition anchor; never treat an isolated centered icon as a completed motion-graphics scene. No default character sticker, no decorative emoji count target.

The bundled v70 proof uses five intentionally **original** minimal SVGs/PNGs because direct network access was unavailable. They are not Solar SVGs and must not be represented as originating from Solar.