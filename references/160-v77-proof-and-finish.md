# 160 — Title-muted whole-film review and source-level repair

Run: `python scripts/visual_story_inspection_v77.py FINAL.mp4 --out REVIEW --step 1`

The tool emits `normal-storyboard.png`, `title-muted-storyboard.png` and `report.json`. The second version obscures a common upper headline zone with a broad blur so editors can see what is happening when words stop carrying the edit. It does **not** remove all typography, cannot understand scene meaning, and is not an automated creative-quality grade. If your actual editor supports hiding typography, render a temporary text-free workprint instead: that is stronger evidence.

**Human/agent review prompts:** Do most frames have essentially the same spatial composition? Does the subject do something consequential without words? Does the eye move through scale, depth and foreground/background *for a story reason*? Does the next scene inherit a subject or an intentionally motivated contrast? Are obsolete cards, lines and text gone? Is typography/geometry aligned and readable on a phone? Are SFX attached to contacts and not a generic layer over narration?

Inspect the actual video at normal speed *with audio* as well as the contact sheets. If the answer is no, redesign the weakest **shot relationship**, not just its ease, background hue or font. Keep a short edit log with `time → actual visual defect → change in the source project → result after rerender`. Then do the existing every-two-frames pass. No claim to have watched pages that were never opened.

Latest observed repeated pattern: navy grid; large upper-left heading; mid-frame script/card/diagram; small bottom caption. In the user-supplied ad this recurs in almost every 3–4s block. The Claude comparison offers visual relationships and spatial staging as **principles**, not a shot or asset source. Respect narration/music rights and factual claim boundaries.
