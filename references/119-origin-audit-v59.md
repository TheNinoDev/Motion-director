> **V68 explicit user exception (RobloxLARP campaign only):** This user has specifically asked the editor to use individual original RobloxLARP site icons. These isolated icons may be used **only when product ownership or permission for the specific asset is grounded and recorded**; all other product-site HTML/CSS, screenshots, page captures, page images, logos and reference-video pixels remain forbidden. See `references/145-asset-first-regie-v68.md`. An icon source is not automatically a license.

# 119 — Mandatory asset-origin audit (V59, manual instruction)

This guide is a production checklist to be performed by the agent using tools it already has; it is NOT a new programmatic validator. A passing file-existence, codec, or previous pipeline gate is not evidence of asset originality. Treat asset lineage as a release-critical issue. The user explicitly requires websites, local projects, HTML and reference clips to be information-only.

## Source-to-output boundary

**Allowed source operations (research sandbox only):** open/read website or source, inspect features, run safe text search, check factual UI states, take temporary screenshots strictly for private understanding if needed, analyze reference-video motion qualitatively. Do not copy the screenshot/file into the film's `assets`, `cache`, `shots`, `preview`, `stills`, project timeline or master. Temporary research images must never be used for image-to-image, vector tracing, compositing, texture mapping, masks or video transition matching. Source HTML/CSS must not become rendered markup. Factual names and verified functional terms may be newly typeset.

**Allowed output ingredients:** tool-generated original geometry/vectors/type/particles/materials/motion; original generative illustrations from semantic text only (not source image transformation); separate user-provided/authorized specific asset; cleared separate audio and original SFX. Source-derived data are facts, not assets. Record externally purchased/stock items as licensed, not automatically original; prefer generating from scratch under this user's standard mode.

## Audit every new ad twice

Before first full render, inventory every visual input, regardless of where it appears:
- scene image/video layers and their resolved file paths, meshes, textures and fonts;
- imported external SVGs, downloaded photos/icons, OG images/favicons and HTML/CSS templates;
- any source-screen capture, temporary frame extraction, data URL, site-url reference or cached browser render;
- generated images that used source screenshot frames as references, retexture, ControlNet-like guidance, or tracing;
- composited clips that may include original reference footage or website elements.

For each candidate visual write provenance **ORIGINAL_TOOL_GENERATED / EXPLICIT_USER_AUTHORIZED_ASSET / SOURCE_INFO_ONLY / UNKNOWN**. Only the first two are permissible as visible output (and audio is handled separately). SOURCE_INFO_ONLY and UNKNOWN must be REMOVED or researched until proven. Changing filename, crop, compression, blur, 3D plane, recolor or using AI redraw does not change source lineage. If an image is the actual page contents but was recreated by tracing its exact layout, it is still a source-derived visual. Validate claims separately: original schematics are not factual screenshots.

After final render, examine output samples at first, middle, last and boundary frames, then full moving picture when possible. If source imagery, HTML UI or original reference footage is visible, fail even when picture looks premium. If any project input still points at the source tree, website domain, browser shot cache or original UI media for a visual role, fail and rebuild. Textual source URL in private research notes is fine. Tools may store source captures in their own temporary caches; exclude them from package and rendering path, never repurpose them in final output. Check audio origins and actual license as separate concerns. Record a short honest note about which original asset generators produced film elements. Do NOT claim “audited and 100% original” if you cannot inspect assets/frames or lineage.

## Concrete fail cases

| Bad plan | Reason it fails | Replace with |
|---|---|---|
| Playwright website capture → `film.mp4` with push zoom | Exact website pixels included | Original procedural shapes/metaphors and newly typed truthful words |
| Crop screenshot to show filters, add glowing border | Cropping doesn't change provenance | Custom original filter metaphor with distinct geometry |
| Open source HTML through headless browser to render polished ad shot | Source HTML/CSS is being used as film artwork | Build independent procedural scene from blank geometry |
| Download site logo/favicon/SVG and 3D extrude it | Original site asset is copied | Newly designed typographic product name or permitted separate asset |
| AI image redraw based on supplied reference screenshot | Image-conditioned source derivative | New render generated from textual PRODUCT FACTS only |
| Copy site's precise colors, typography and structure to “feel branded” | Design system copied rather than original | Independent art direction; honor a separately authorized brand guide only if supplied |
| Use exact NOIZ video frames as backgrounds/textures | Reference is information only | Reuse general visual grammar but create original motifs |
| Show a fabricated perfect “live UI” state to replace forbidden screenshot | Misrepresents feature/product behavior | Clear conceptual visualization with honest supported wording |

## Fast failure recovery
If a visual input is SOURCE_INFO_ONLY, remove it from timeline and cache; do not try to make it “more original” with effects. Rebuild from the semantic concept using existing original generators. If the tool's easiest production path relies on screenshots, choose another supported path. If no original route is available, stop and state the limitation rather than quietly violate user instructions. Record only actual verified review, not invented proof. This audit supersedes older screenshot-centric review manuals. See 117, 118 and 120.
