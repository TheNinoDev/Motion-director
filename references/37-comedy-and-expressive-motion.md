> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Standalone comedy and expressive motion recipe
Do not retrieve an example video. A joke is a story beat, not a stock transition. Use these instructions directly. Default: choose a truthful non-deceptive action or exaggerated inconvenience, not a fake security confession that could damage trust. A provocative line is allowed only when the audience can immediately understand the framing and the payoff is genuine. Never fabricate customer numbers, errors, security incidents, claims or fake product UI. Label illustrative data/UI where it could be confused with evidence. Do not force humor onto serious or sensitive subjects.

## Choose a narrative
Pick one: expectation inversion (common assumption -> real outcome), visual metaphor (one small frustration grows -> product resolves), deadpan observation (small mundane action -> unexpectedly satisfying result). Write setup, escalation, reaction, pause, reveal and evidence. Hook begins within the first second. Example for a search tool, provided search is verified: "I saved it somewhere. Great. That's helpful. [pause] Or I could just search for it." Show the real search result. Do not repeat this script across products. Avoid "we lied" unless this is a clearly framed harmless joke and brand specifically approves it.

## Direct frame timing (30 fps defaults, adjust to actual narration)
| Beat | Frame guidance | What changes and why |
|---|---|---|
| Setup | 24–48 | 8–12f masked reveal, hold one readable sentence; no logo bumper |
| Reduction | 30–60 | Screenshot -> outline using measured UI boxes -> merge boxes to a shared anchor; fade actual pixels before collapse |
| Escalation | 24–60 | Large type/verified count becomes a dot field; reduce scale after formation, no random glitch |
| Reaction | 24–60 | Curiosity -> asymmetric smile -> exaggerated expression; move eyebrows and mouth nonlinearly; camera push and squash only on emotional accent |
| Reset | 15–36 | Settle to neutral in 4–8f then hold 12–30f; eyes or tiny blink only; do not add particles |
| Payoff | 15–30 | Hard contrast cut to 1–4 words; hold long enough to read, no strobe |
| Proof | length driven by VO | Demonstrate one true UI interaction; use shared anchors and crop/detail/reveal; ship actual product proof |
| End | 45–75 | Clean logo/address, no fake platform watermark |
Use audio anchors. Do not add a sound on every visual movement. One subtle tick/impact at the reveal may be useful; use licensed/authorized sources and verify mix. The quiet beat is intentional. Contrast cut uses one background inversion, not rapid flashing. Do not promise these exact times are optimal or original reference timings. If a comedic scene is inappropriate choose a normal proof sequence.

## Concrete tools
Use the packaged `starter/expressive_motion/preset.py` and `render.py` with the README commands. For a weak agent, choose a single preset by name and modify text, color, screenshot, key times only. Render stills of setup, escalation, pause and payoff. Then combine with actual UI/captions and real audio using existing stitcher. A character shot is optional and should occupy only a small portion of an otherwise UI/typography-led advert. If expressive assets look amateur, use an abstract animated shape or expressive type instead. Prefer a polished simple composition over pretending a 2.5D face is cinematic CGI.

## Repair automatically
- Text clipped: shorten wording, insert semantic line break, fit with actual font. Never shrink to unreadable microtype to save a poor script.
- Wireframe doesn't match screenshot: remeasure each bound relative to crop; remove nonessential outlines; keep one visible focal box at end. Do not use made-up rectangles as product proof.
- Boring reaction: contrast a restrained start with one pronounced change; use independent mouth/brows and a genuine neutral hold. If exaggerated distortion is ugly, reduce zoom and squash before adding more effects.
- Pause looks like an export freeze: a planned short hold is fine. Confirm intentional length in shot plan and visual QA, don't delete it blindly; distinguish from pipeline freeze.
- Punchline arrives before setup: move the change to the actual voiced keyword/end of pause. No unmotivated transition during important speech.
- Character visually inconsistent: keep palette, shading and landmarks; do not randomize shape for each frame. Do not assign unsupported lip-sync to the primitive.
- Product proof too short: shorten setup rather than racing through evidence. Reserve at least enough time to see before/action/result.
