> **V68 explicit user exception (RobloxLARP campaign only):** This user has specifically asked the editor to use individual original RobloxLARP site icons. These isolated icons may be used **only when product ownership or permission for the specific asset is grounded and recorded**; all other product-site HTML/CSS, screenshots, page captures, page images, logos and reference-video pixels remain forbidden. See `references/145-asset-first-regie-v68.md`. An icon source is not automatically a license.

# 137 — SVG, non-generic typography and striking but legible visual direction (V65)

## What changed from V64

The user explicitly allows SVGs from the internet and wants stronger design and type. **This is a narrow third-party asset allowance, not permission to capture the product website's assets.** Product sites and local product projects remain facts-only unless the user separately names an asset to reuse. Public SVGs from independent authorized libraries may be used when their individual rights are compatible with the intended video. Never scrape arbitrary web logos, rebrand trademarks, or claim downloaded icons were hand drawn.

## Source and inspect third-party SVGs

1. First think about the scene's action and symbol. Prefer creating meaningful original artwork with shapes/paths. If a small general-purpose icon helps, use a known open library instead of drawing a poor counterfeit.
2. Valid researched options include official **Lucide** (ISC) `https://lucide.dev/license` and official **Tabler Icons** (MIT) `https://github.com/tabler/tabler-icons`. Confirm the actual file's license, keep the accompanying copyright/license notices where required, and record URL, project, version or date, author and role in a small `assets-provenance.json` or equivalent. Verify current terms when obtaining assets, rather than trusting an old cached guess. Links in this guide are starting points, not auto-authorization for every SVG on the internet.
3. Download only the particular required SVG(s), ideally pinned from the official source. No blind third-party SVG execution. Inspect/sanitize to remove `<script>`, event handlers, `foreignObject`, external images/fonts, remote imports, linked scripts, `data:` execution, animation with untrusted references and external network requests. Render in a sandbox/offline context where possible; make a local raster/vector export when the chosen Motion Director editor cannot ingest raw SVG safely. Validate output and crop/transparency. Keep the sanitized source and attribution document in project; *do not* embed remote runtime loads in the delivered video.
4. Adapt geometry, stroke, perspective, animation and color to the film's original visual language, within license and attribution rules. Using ten stock icons does not make a good scene. A thumbnail-size icon should never become the film's only hero by default.

## Typography must be directed, not defaulted

The default is **not Arial/Consolas for every beat**. Select a deliberate two-voice system appropriate to the brand and story. For example, a forceful condensed/display or weighty grotesk for action; a refined italic serif or expressive contrasting accent at the emotional turn; a tightly controlled mono only for code or measurements. This is an *example of functional roles*, not a prescription to copy Claude's italic style. Fonts must be lawful to embed in a commercial video, and their source/license documented. Open-source font directories such as `https://fonts.google.com/` are possible research sources; verify each family and license before downloading. Never ship font files to end users unless redistribution is explicitly permitted and necessary.

Type mechanics: design with visible optical sizing and contrast, purposeful weight, true or checked italic, custom per-word timing, strategic line breaks, strong negative space, deliberate tracking and anchored motion. One headline can interact with the scene, but avoid a subtitle-sized headline plus three tiny metadata labels by habit. Different scenes may use different hierarchical compositions; maintain family consistency with restrained repeated elements. Script code should be rendered with a legible code face, never as a wall of microscopic pseudo-code.

## Material and transitions — depth with clarity

High-impact scenes may use crisp vector edges, layered shadows, paper folds, perspective planes, motion blur on fast gestures, masks, camera depth, real path deformation and lighting/material contrast where the bundled editor supports them. A scene should feel directed and constructed, not like someone selected 'neon glow template'. **One major spatial or typographic event per beat is usually enough.** Remove decorative grid dots, meaningless technical labels, and duplicate UI boxes that do not help the viewer.

Use the bundled compositor for grouped geometry, path/trim, masks, mattes, animated transforms, and compositing. When native SVG vectors cannot be used directly, convert or draw them as compatible original local layers, then animate those layers with the *existing* editor. Choose browser SVG/CSS animation as a specialist shot only when that is the better tool and integrate it into one master timeline. Do not quietly rebuild an inferior entire video pipeline.

## Real preview acceptance

At phone scale, test three frames: **first glance** (what is the hero?), **mid-move** (is the action intelligible, not just moving?), and **result** (has the visual meaning changed?). Then check motion through transitions, type hierarchy and SVG attribution. Require actual color and form variation where the story calls for a new state, not arbitrary palettes on every word. **Simpler can be better — but never use simplicity as permission to leave most of the film static or cheaply drawn.**
