---
name: motion-director
description: Produce original upload-ready marketing videos for websites and apps, with executable motion design, 2D/3D, audio and evidence-driven revision. No GUI editor or historic reference clips required.
---
# Motion Director 48 — start here

You are the producer. A video request requires actual verified media, not just a plan. User requirements and locked decisions take priority. Use this file and `references/85-sequence-direction-v48.md` as the single current route. Old version guides are feature manuals, not competing instructions. Read only the relevant sections.

## Decision route

- **Script only:** read phases 1–3 in `references/84-production-phases.md`; deliver copy and voice direction, no unnecessary rendering.
- **New advertisement:** inspect the real product or supplied proof; select ONE feature, one truthful result, and an earned CTA. Read phases 1–3 for voice, music and rights, then use V48. If essential media is unavailable, deliver the appropriate draft/preview honestly, not a final ad.
- **Revision:** inspect canonical source and last accepted output. Preserve unrelated text, assets, audio, effects and approved animation. Do not recreate a missing source from guesses. Compile into a new work directory; compare revisions and actual media.
- **Technical animation / test:** use the most relevant recipe or renderer; label as a study. Do not fabricate an advertisement or product claims.

## Execute

From the skill root:
```bash
python scripts/director_v48.py catalog
python scripts/director_v48.py inspect SOURCE.json
python scripts/production_v48.py start SOURCE.json CREATIVE.json WORK
python scripts/production_v48.py next WORK
```
For real ads pass `--audio AUTHORIZED_ALIGNED_BED.wav` at start. Replace placeholders with actual paths. Use examples/director-v48.json and examples/creative-v48.json only for syntax/tests. Execute the argv returned by `next`; never type placeholder/example content as final copy. See guide 85 for exact sequence schema and tools.

## Non-negotiable quality rules

1. Generate three genuinely distinct concepts; choose the one showing a visible product-specific cause and payoff. Do not copy the bundled studies. No compulsory glass, chrome, jelly or particles.
2. Plan each beat around a dominant subject, beginning state, action, result and incoming/outgoing anchor. Vary scale and composition, not random decoration. Show actual UI or evidence where applicable.
3. Render two typography/style candidates with the actual wording. Keep proof legible; use dimensional text only when it earns its place. Use the font catalog and legal local fonts; never claim a font is installed without checking.
4. Use named markers and reusable sequences for coupled motions. One writer per property; never erase functioning keys to make compilation pass. Use continuous paths for sustained movement. Match position, velocity and silhouette in smooth handoffs; intentional hard cuts are allowed.
5. Inspect complete preview playback and listen to actual audio when possible. Review native PNGs for type/CGI, inspect boundaries, event timing, visible layer contribution, cadence and optical flow. Do not pretend to see/hear media you cannot inspect. Keep those checks pending.
6. Fix the earliest cause with the smallest appropriate change; compare source changes and rerender. Keep strong sections. Compare all changed and adjacent intervals and protected work. Never bypass a gate or claim a review without evidence.
7. Export upload MP4 and optional lossless master only after review. Verify and re-inspect exported media. State actual resolution, backend and blockers. Passing tests are not a premium design certification.

For existing V47 and older projects consult `references/legacy-skill-v47.md` and the relevant version guide; continue their canonical source without forced migration. Full historical production phases and the supplied exact voice prompt are retained in `references/84-production-phases.md`.
