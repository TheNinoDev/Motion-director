# 117 — Zero-source-pixels firewall (V59 current)

## Why this rule exists
The user observed that the agent obtained technically accurate website screenshots but delivered a dull, derivative slideshow. For this project, website URLs, local source trees, original HTML and stylistic reference videos are **information inputs only**. The design must be invented and rendered using Motion Director's existing procedural/art/3D tools. The user explicitly reports much better results when enforcing this boundary. Earlier reference and technical docs that say “capture real UI screenshots” describe OBSOLETE workflows for new information-only films. Root V59 governs every time.

## Provenance categories, enforced before layout

| Class | Example | Allowed for research? | May appear in finished picture? |
|---|---|---|---|
| INFO_SOURCE | https://example.com, project's HTML/CSS/JS, source README, public product copy | YES, read-only | **NO**, even if cropped or transformed |
| REFERENCE_VIDEO | supplied NOIZ-style film, competitor edit, social media video | YES, analyze conceptual techniques | **NO** frames, logos, textures, exact shot recreations |
| SOURCE_SCREENSHOT | website, app screenshot, browser/Playwright capture, PNG of local UI | YES, temporary viewing for facts | **NO**, including composites, overlays or AI redrawing |
| SOURCE_VISUAL_ASSET | site logo, avatar, SVG, image, CSS animation, favicon, background, OG image, web font | YES, information about brand/product only | **NO**, not by tracing or exporting bytes |
| ORIGINAL_GENERATED | new geometry, typography, 3D, kinetic shapes, illustrations, composited original art made with skill tools | YES | **YES**, subject to truth and rights |
| USER_EXPLICIT_ASSET | a separate image/logo provided and explicitly authorized for inclusion in this film | YES | YES, ONLY within precise permitted scope |
| CLEARED_AUDIO | user-owned/licensed separate voice/music or agent-generated authorized SFX | YES | YES, if clearance and scope actually confirmed |

**Default for any .com or local project source: INFO_SOURCE, never USER_EXPLICIT_ASSET.** “Use my site” is a request about the product, not consent to lift source artwork. This also applies when the user owns the site. If they explicitly ask for an exact website screenshot as a separate image asset in this campaign, that is a changed scope; clarify the particular asset and record authorization rather than silently exploiting a general site permission. Do not infer a wholesale source-asset exemption from one authorized image. A product name or fact re-typeset as new text is informational use, not reuse of graphical pixels. A sourced brand's palette/CSS design should not be mechanically copied; choose an original art direction unless a separately supplied brand kit explicitly sets constraints.

## Information extraction versus pixels extraction

**Allowed:** Read public/local code or pages to understand product names, verified feature semantics, workflows, target users, basic facts, terminology and what must not be claimed. Observe an image of the site or video to understand it, but don't store it as a production asset. Research could reveal “users can filter scripts by game”; the eventual film can render a wholly original search motif, feature-name lettering or conceptual diagrams in a new art direction.

**Disallowed:** Save website screenshots into `assets/`, cut out a filter chip, render a browser page/HTML/CSS as a film layer, use Playwright capture for frames, use data URLs from site images, import SVG icons, use screenshot as `image_gen` image-to-image base, crop the website's actual header or branding, turn CSS cards into a layered Blender scene, trace logo silhouettes, or pull source audio. Generating an image conditioned on a source screenshot to retain its visual appearance is STILL a source derivative. “I changed the color, so now it is original” is not acceptable.

### Example: local Roblox script-platform project

**Read-only facts:** a page may describe Browse, Search, filters, publishing, or source inspection. Confirm actual availability from source as far as access allows. If site says Keyless but no results are shown, do NOT invent a populated result or security claim. If only source code is available, don't execute untrusted Roblox code as a proof exercise. Treat public legal/platform rules separately from source claims.

**Original video:** A procedural 3D search ring is pulled through a field of original abstract game glyphs; one glyph resolves into a new game title. Original small symbols orbit and peel away as conceptual search criteria; a stylized key icon dissolves to a transparent material and a newly typeset verified fact. The graphic elements are created by the agent and need not resemble the site's actual page, logo or colors. The film states supported functionality with original voice and captions; it DOES NOT show a faux “real UI” or a lifted website screenshot. Build different concepts when product story differs—this is one example, not the next template.

## No false evidence
An original diagram can accurately explain “filter by game” but cannot prove that a specific live filter UI is responsive or that results exist. Do not claim “LIVE DEMO,” “ACTUAL UI,” “VERIFIED SAFE,” or “REAL DATA” on original graphics unless each meaning is independently supported and appropriately presented. If necessary, mark a close UI-like depiction as an **illustrative visualization** in project notes and/or on screen where viewers could mistake it for actual product UI. Avoid making a counterfeit replica of the site while pretending it is real. Real source evidence can be checked for copy claims outside the film, without embedding its pixels.

## Cheap agent failure recovery
If a renderer's easiest route is screenshot -> crop -> zoom -> xfade, STOP. That route is wrong even if technically supported. Keep the extracted textual facts, discard its visual plan, and reopen 118. Choose original symbols, typography, paths, 3D shapes and causal transitions. Do not save the capture into a different extension or hide it in a texture or vector path. Do not add particles on top of the screenshot to pass the audit. If artistic tool capacity genuinely cannot create needed original visuals, say so and deliver a concept/script rather than violating the rule.
