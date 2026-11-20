> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# V6 — Deep case 2/9: NOIZ reference 5, technical story and data choreography

## Evidence and limitations
Input 1000043460.mp4 (fifth upload in filename order), 576x1024, 30 fps, 1,230 frames / 41 seconds. Inspected 164 sampled frames at 0.25-second spacing (including download outro). Times below are approximate observed states, not exact source keyframes; tolerance ~0.25s. Smaller or faster changes may be missed. The actual ad fades around 36.75s; TikTok downloader outro from ~37.0s to 41.0s and moving watermark are excluded from the style. Visible headings are visual evidence, not a verified transcript. No reliable acoustic transcription or voice acting classification here; audio metrics in `reference5-audio-diagnostics-v6.json` are candidate measurements of the mixed file, including outro, not BPM/real speech timings. Original tools/layers/3D geometry unknown. No original code, proprietary branding, personal data or unverified product numbers should be reproduced.

## Timeline and motion logic
| Approx. time, seconds | Observed visual states | Why it works / adaptation |
|---|---|---|
| 0–1.50 | Near-black technical frame, tiny header/footer, large two-line declaration revealed in two steps | Immediate unresolved conflict; no preceding logo bumper. Keep position stable; let one word arrive after the first. |
| 1.50–2.50 | Short headline above a compact name/status list; cursor appears over rows | Makes prior effort concrete; show a real interaction or traceable fictional prototype. |
| 2.50–4.95 | Headline grows in clauses, number readout changes, line chart extends from low baseline to jagged steep rise, then holds | Same data drives text value and endpoint; viewer experiences escalation without needing to read the small labels. |
| 5.00–7.50 | Code editor with typing caret and a magnified line; headline enters above | Evidence becomes tactile; focus selected line instead of expecting viewers to read code. Use non-executable stylized product evidence, never reproduce abusive automation. |
| 7.50–9.25 | Bars, list-like activity, large changing number, bars again | Same idea in multiple representations. Number hero and chart alternate, not compete. |
| 9.25–11.75 | Single masked domain label → related labels spread → radial connection diagram → dense columns | One object becomes a network then a field. Keep one anchor. Only real or clearly illustrative relationships. |
| 11.75–14.75 | One redacted email-like text expands into list then columns of very dense rows; last grid tilts/blur-like exit | Density is a metaphor for scale; use masked data or fictional placeholders, no personal info. |
| 14.75–17.25 | Abrupt reset to tiny center icon; four separate technical panels build around middle; central anchor remains | Breathing room after density; recap evidence categories as one visual system. |
| 17.25–20.75 | Tiny typed line on black, then large stark two-line statement held ~2s; short small-text punctuation | Quiet pause before rapid evidence. Contrast in scale and speed creates drama without constant camera shake. |
| 21.00–23.95 | Metallic 429-like numeral with reflected appearance, then bars, colored log lines, radial diagram, metallic count | Rapid proof montage uses fixed headline grid and a distinctive number treatment; semantic color only. |
| 24.00–26.95 | Mixed accent bars, reflective number, highlighted policy text, another numeral then rejected logs | Evidence alternates between quantitative and textual; policy text is selectively highlighted. |
| 27.00–29.75 | Real-form-like interface with entered field and visible error state, another reflective count, horizontal status bars and bounded list | Show what user actually experiences. Highlight resulting state, not just chrome around UI. |
| 29.75–30.25 | Centered short summary on black | Summarize why this entire technical story matters. |
| 30.25–33.75 | Metallic wordmark → product CTA with compact input → populated product card → value statement, small supporting text disappears | Product appears late as resolution; reveal a tangible result, keep CTA functional and truthful. |
| 33.75–36.90 | Two short contrasting statements, then lit metallic wordmark and domain on black, fade | Brand belief is the payoff, not a new feature dump. Allow clear reading time. |

## Design system to recreate, not clone
- Use a fixed near-black / off-white editorial canvas, one restrained accent for true status changes, consistent left margin and header baseline, small mono data labels only as secondary texture. Example at 1080x1920: x=90, headline baseline 360, chart plot x=90..940/y=650..1360. Test actual phone reduction and platform safe zones. Do not enlarge irrelevant UI chrome. All required copy must be readable; tiny decorative labels not essential to the story. Alternate hero scale and whitespace rather than adding decoration.
- Use an identity/anchor ledger: headline-left, plot-area, center token, status accent, final product card. If successive shots have no shared visual property, either create a shared object/axis or use an intentional semantic hard cut. Do not morph unrelated shapes simply to show off.
- Measured sampling does not identify software. Use SVG/canvas for exact charts and UI; Blender genuine reflected material only if needed, or clean flat/gradient numeral; avoid poorly beveled fake 3D. More than two 3D shots here is not a new default rule: a repeated hero treatment may occur as one reusable motif in a specific story. Other campaigns should use 0–2 special CGI highlights as before.
- Pacing example: opening hold ~1.5s; proof beats ~0.6–2.5s; deliberate reset ~2s; rapid montage ~0.5–0.8s per simple visual; final brand ~1.8s. These are descriptive approximations, not a universal shot length. Actual VO and reading time decide. If visual is dense, show one headline and one clear inference; extend for detail. Avoid flashing.

## Implementable recipes (30fps, normalized)
All frame counts below are suggested implementation baselines. For an actual plan calculate `f=round(seconds*fps)`, use global frame clock, derive local progress p=clamp((f-start)/(duration-1),0,1); cubic ease-out e=1-(1-p)^3. No animation timers. Use one source of truth and deterministic seeded layout. Check samples start/middle/end.

### A. Text reveal tied to data
Keep headline container at fixed x,y. Reveal clause groups using discrete aligned word events, not per-letter typewriter for prose. For each group, clip to its measured box and move y +12px→0 over 8–10 frames, alpha 0→1. Reserve full line widths before reveal; don't re-center every word. With actual charts draw line only up to a normalized sample index over 35–60 frames; interpolate between samples for endpoint. Counter = interpolated measured value at same sample index, using fixed-width digit font. Area fill alpha .10–.18 behind line; marker radius 5–6px. Hold final chart at least 15 frames. Never generate false uptime/user counts. For a conceptual trend use label "Illustrative" and actual units only when known.

### B. Activity table to histogram to metric
Use time-stamped sample records, redact identifiers, define explicit bucket width and aggregation. Show 5–9 legible rows with highlight on event. Build columns scaled to max with base y fixed; 2–4 frame stagger with height easing 10–15 frames. Wipe table out only after last highlighted row. For the numeral hero, keep total computed from the same records, use a fixed-size bounding box and hold. Switch back to bars if needed. No random values for evidence; keep simulated visuals clearly marked and separate from claims.

### C. Macro code or UI focus
Source code screenshot must be from safe authorized view, or create a clearly illustrative non-runnable mock. Build caret movement, 2–3 line typing chunks and focus rectangle; highlight the exact safe line with a duplicated cropped crop at 1.5–2x using matching origin. Animate that crop 12 frames in, hold 15–30, return or cut to effect. Avoid tiny monospaced paragraphs, live credentials or executable abuse recipes. Code should explain visible concept, not act as technical decoration.

### D. One object to many
Start single badge at (540,960) or scene anchor. After 6–10 frames spawn 6–12 satellite nodes with stable IDs, distribute by fixed angles; animate x,y radial distance 0→r over 12–18 frames with 2-frame delays. Lines grow from anchor to node (opacity .2–.55), labels fade in at endpoints. Preserve central token. Then map satellites to first column positions by ID over 12–18 frames, introduce additional rows in waves rather than morphing text. Use seeded mock identities, never private data. The node count does not imply actual volume unless backed by evidence.

### E. Controlled density and reset
Start one row, reveal 5, then 12, then duplicate *layout* into columns. Increase density while reducing legible content to visual texture. Keep headline stable. At climax move all columns 10–30px / fade over 6–8 frames or cut to a single center token; pause 8–18 frames. Avoid flashing white transitions, unbounded loops, or unreadable important information. The contrast is the effect.

### F. Four-panel evidence recap
Build four panels in 2x2 around a persistent center token, each with one label, independent motif and shared margin. Stagger panel crops 3 frames, translate 25px and ease 12 frames. Maintain center negative space. After visual summary, hard cut to a sparse text card as a semantic beat. No view zoom on every panel. Reuse panel assets instead of recompiling unrelated animations.

### G. Reflective numerical motif (optional)
For real 3D render approved typeface numeral meshes with 1–3% bevel relative to height, smooth normals, front-facing camera, broad key, grazing strip light, roughness ~.18–.35 and dark HDRI/studio environment. Reflection via plane with controlled roughness or art-directed mirrored text beneath baseline. Motion can be only subtle lighting shift. Render transparent PNG sequence or approved alpha format; composite below headline. 2D fallback: bold normal text with restrained gradient, reflected copy flipped vertically under baseline, masked to fade. Clearly label as 2D stylization. Avoid oversaturated metal, unreadable digit shapes, or excessive extrusion. Count values need factual backing.

### H. Evidence montage + UI reaction
Use consistent slide header/plot coordinates. A montage beat should encode one claim, one graphic. Change representation (bar, line, log, UI) rather than transitions. For UI capture, use actual authorized browser action or mock that is labeled; match font and state geometry, animate cursor along eased path 12–20 frames, click compress 0.97 then return, error/status visible at actual response event. Do not stage false product reliability claims. Use restrained accent to encode status and text/icon so color isn't the only signal.

## Adaptation example, fictional product
One story: a team loses track of saved files. Show three search attempts (not invented global usage numbers), one sparse visual reset, real saved-file collection with a successful search, closing line. If user provides verified measurements, show only attributable values. Do not copy NOIZ headlines, username mechanism, brand or reflective logo. The point is technical language that visually explains one obstacle and resolution. For RobloxLarp, a specific discovery or creator friction could work if actually verified; never invent metrics or assert features from prior discussions.

## Handoff to actual production
Read guide 27 for data evidence and reusable scene design, then run the sample renderer when unfamiliar with charts. Replace example data, fonts, wording and durations with product evidence. Align to actual voice and music. Validate frames, actual readability, visual variation, data semantics, audio levels, and user-visible claims before release. This deep case completes 2 of 9 detailed reviews (8 and 5). Next candidate 7 (luxury object/CGI) only when requested. Never treat the downloaded outro as content.
