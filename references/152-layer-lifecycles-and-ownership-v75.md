# V75 — Timeline ownership: every layer must arrive, act, hand off, and leave

## Case evidence, not a reusable storyboard
The user's new 24.6-second RobloxLARP export is no longer mainly static: objects animate. But at 3–7.5 seconds the original code window, copy/theft graphic, and stolen message stay active together without clean hierarchy. At 8.5–12 seconds the shield and later obfuscation matrix appear on top of a faint code window. Around 15.5–16 seconds new copy begins while the old VM/account-device diagram remains in the same area. Near 19.5–20 seconds the upload card persists into the beginning of the brand ending. These are visual observations; this source video did not ship an editable layer manifest, so exact object owners/opacity cannot be verified. Do NOT copy its visuals.

## Every rendered layer needs a finite lifecycle
Each important layer/group gets a stable identifier, scene owner, a semantic role, start/end in seconds, entrance, useful action, and exit/disposal. Exit is **not** optional by default: remove from render tree, mask away, dissolve with motivated depth, transform into a successor, or hand over with explicit ownership. Merely setting a long lifetime and hiding it behind the next opaque card is not disposal. The old object should not silently return after a cut, nor fade through unrelated text.

- Prepare a **scene ownership sheet** before encoding. Record active `start/end` times, layer IDs and proposed `handoff` from scene A to B.
- A persistent visual anchor (e.g., one code page transforming into a protective envelope) may cross the seam, but name the persistent layer and state what it becomes. Keep the persistent portion meaningful and subordinate; don't keep an entire old layout behind it.
- After the causal beat, foreground, labels, remnants and particles have a clear exit. A shape still visible 2 seconds after it served its purpose must have an explicit reason.
- At the transition, decide what remains, what leaves, and what enters. Every time-coded overlap is either an **intentional compositor interaction** or a defect. Unplanned overlap is not a scene bridge.
- Don't blindly hide all elements at each cut. That produces abrupt PowerPoint slides. The desired solution is object continuity with *clean ownership*, not sweeping the screen to black.

## Implementation in bundled editors
Use native clip/layer offsets, keyframes, transforms and masks. For HTML/CSS renderers, update opacity/visibility/pointer states and remove expired items; use independent `render(t)` visual verification. For Python/compositor renderers, stop drawing expired layers and bring transition shapes to the appropriate z index. A bounding box may change during animation; plan and validate its **swept region** rather than checking only the final coordinate.

**Approval condition:** Watch the cut with the main action visible and the decorative labels temporarily hidden; freeze 6–10 frames before, at and after major handoffs. Identify every remaining element and say why it is still on-screen. If an unrelated object survives, rework the timeline. Passing JSON validation alone is not enough.
