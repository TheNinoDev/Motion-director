# 137 — Strong typography, licensed external SVG and higher-quality visuals (v65)

The user explicitly permits SVG assets sourced from the internet. **This is an exception for independently licensed generic assets, not for borrowing from the advertised website or source/reference films.** The product's HTML, images, logos, screenshots and stylesheet remain information-only unless an individual asset is explicitly authorized.

## External SVG usage

Obtain only the icons needed for a real story action, from an authoritative source with verified licensing. Example independent libraries: official Lucide (ISC: https://lucide.dev/license) and Tabler Icons (MIT: https://github.com/tabler/tabler-icons). For every included SVG, record source URL, author/project, license, version or retrieval date, any notice/attribution obligation, and its purpose in the video. Consult current license terms; don't treat every internet search result as reusable. Never extract brand logos or proprietary artwork and assume permission.

Inspect and sanitize downloads: reject `script`, `foreignObject`, event handlers, remote styles/fonts/images, external `href` references, executable `data:` resources, and untrusted embedded payloads. Store a local sanitized source and rasterize/offline-render where the actual editor cannot safely use SVG directly. Do not fetch images dynamically when the final video plays. Recolor/recompose as permitted to fit the film while retaining required notices. Ten stock glyphs are not a designed scene.

## Typographic art direction

Never default to Arial/Consolas for every title and scene. Select a **deliberate typographic pairing** motivated by the story: e.g. a strong condensed/display or distinctive grotesk for hooks, a refined serif/italic accent for human stakes, a readable code mono only when showing actual script. The goal is expressive contrast and recognition, not 'always add italic'. Plan line breaks, scale contrast, spacing, weight, optical alignment and per-word emergence before animating. Type may be the hero; avoid a tiny generic paragraph plus many microscopic technical tags. Each font must permit the intended embedding/commercial video use. Official Google Fonts (https://fonts.google.com/) is a starting point for research, but verify each chosen family's license. Do not distribute raw font files to users without the relevant rights.

## Rich visuals without clutter

Claude's comparison has paper depth, ownership stamps, meaningful perspective, distinct framing and scene shifts while keeping one hero readable. The new v64 output has flatter cards, repeated similar heading layouts, static brand slashes, and icons with very little spatial impact. Repair through focal scale, layering, meaningful lighting, shape silhouette, sharp contrast, selective 2.5D camera movement, readable material cues and connected transitions. Do **not** respond by adding random particles, fake circuit grids, extra micro-labels, or arbitrary motion.

Use the real Motion Director compositor and native layers, paths, mattes, masks, groups, camera transforms, motion blur or specialist engines when those actually serve the shot. External SVG should enter as an inspected local asset in the editable pipeline. A specialized browser SVG animation shot is permitted if demonstrably better, but integrate into one final editor/audio timeline.

Preview at phone size: first glance, midway through action, impact, resolved state and transition out. If visual interest disappears when the headline is removed, redesign the main scene. If removing the decorative half improves clarity, remove it. The creative target is **simple focal hierarchy + genuinely interesting visual action**, not simplicity as an excuse for static cheap graphics.
