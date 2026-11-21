# 150 — Two-frame polish review of the ACTUAL final film (v74)

## The user's requested finishing standard
**After claiming picture lock, examine the final exported video at every second source frame**, not just one screenshot per scene and not just a technical MP4 decode. The delivered review must be drawn from the same actual export that is delivered. This is a finishing pass, not a substitute for real-time watching or a license to infer artistic quality from pixel metrics.

## Executable procedure
1. Play the entire rough cut at **1x speed with the real voice, soundtrack and SFX**. Critique scene meaning, design maturity, transition causality, pacing, sound focus, repetitive templates and readable text before microscopic polishing. If the film remains a slideshow, return to 149; don't polish it.
2. Finalize and export. Run:
   `python scripts/two_frame_finish_v74.py OUTPUT.mp4 --out REVIEW_DIR --every 2 --plan EDIT_PLAN.json`
   `--plan` is optional but strongly recommended; use the actual edit's handoff times, not invented shot boundaries.
3. The program extracts **every second native decoded frame** as a contact-sheet thumbnail, with frame number + timestamp, in paginated sheets. It also reports near-static sampled runs, unusually strong frame-to-frame pixel differences, and optional seam neighborhoods (not every difference is a defect). It saves exact source hash. All sampled frames must appear once; any decode failure means the review is incomplete.
4. **Visually scan every generated sheet**, moving in playback order, not just the first and last sheet. Open suspicious intervals at larger size, inspect the exact neighboring frames, and inspect the transition at real speed with sound. In software with an image-reading agent, give it sheet files one by one; if unable to view all sheets, state explicitly which pages were not reviewed. Do not certify frames you never examined.
5. Look for jumps in alignment/scale, keyframe pops, rough easing, missing asset layers, unsafe margins, cut-off typography, aliasing, inconsistent radii/materials, overly sharp corners where controls should be smooth, dead motion, timing mismatches, sudden direction reversals and scene seams with no bridge. For each issue provide `time/frame → visible failure → precise edit → recheck`.
6. Fix the actual timeline. **Re-export and rerun the full every-2-frame review** after the final edit; do not present an outdated clean report for a changed MP4. Check audio separately; still sheets cannot prove the final sound mix is good.

## No fake quality thresholds
- A low difference could be an intentional readable hold; a high difference could be a purposeful impact cut. Flag for *review*, never auto-fail every hold or auto-pass constant motion.
- Two-frame sampling sees half of the frames. It is valuable for visual QA but cannot prove that unsampled single-frame defects do not exist. When a suspicious interval appears, inspect *all* intervening frames or run a native full-frame pass too.
- A 24.5s 24fps export has ~588 source frames and therefore ~294 thumbnails at `--every 2`; the pages must cover all of them, not a handpicked dozen. The number varies by actual frame count and frame rate.
- If editorial strength is low, **polish cannot rescue the concept**. Redesign the relationship among objects first, then let finishing focus on small errors.

## Honest completion evidence
Record video path, SHA-256, actual dimensions, fps, decoded source count, every-N frame count, number of pages, flagged segments, inspected pages, repaired segments and date/version of final re-export. A successful script exit is not equivalent to human/agent visual signoff. Video must actually be shown or inspectable; never report 'inspected every two frames' because a script generated sheets and they weren't opened.
