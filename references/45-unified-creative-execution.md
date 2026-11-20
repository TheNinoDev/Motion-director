> **V59 SOURCE FIREWALL — CURRENT RULE:** Product websites, local projects, original HTML/CSS and reference clips are **INFORMATION ONLY**. Any screenshot, real UI capture, existing site image, logo, font, webpage-derived frame, layout or reference footage mentioned below is **NOT permitted in the output video** by default, even after cropping, recoloring or redrawing. Build ALL visible scenes from new original tool-generated art instead; factual source inspection remains allowed. A separately provided asset needs explicit inclusion authorization. This V59 rule overrides all conflicting examples below. See `references/117-source-firewall-v59.md` and root `SKILL.md`.

# Beginner-proof execution: map a good story to ONE JSON timeline

Read this when the model struggles to edit, animate, write code or estimate lengths. Do not compose an app, shader system, After Effects project, Blender scene or custom video library from scratch. Start from `starter/unified/quick_project.py` or copy `examples/brand-story-project.json`; edit only content, frame lengths and relevant camera/transition parameters.

## Model must do, in order (do not skip)

1. Intake: obtain a source repository, URL (if reachable), saved HTML/screenshot or a direct product brief. Make a two-column claims ledger: `confirmed by evidence` vs `not known`. Do not rely on the web being available or infer product data.
2. Write: three different human hooks each anchored in one genuine user's problem. Select one with the strongest feasible opening image and satisfying turn. Draft 1 coherent story, fewer than three supporting features, no indiscriminate feature laundry list.
3. Voice: produce clean spoken script and provider-specific tagged script; user-tested ElevenLabs prompt is saved verbatim in guide 24. Offer a brief tutorial only if they need it. Fish Audio tags differ, use guide 25 and compiler. Obtain the actual narration file (no guessing duration from character count).
4. Music: with user consent, choose fitting track by verified trends or timeless criteria. User supplies an authorized song file. No dependency on a particular downloading website if it changes.
5. Timing: use verified phrase/word alignment, convert seconds to frames with `round(time_s * fps)`. Group exact beats; do not assign identical 2-second scenes by default. Sum effective frames after overlaps and ensure narration is not cut.
6. Visual direction: select one core object or UI anchor; use one actual visual interaction, one payoff, a quiet beat, selective data/material effects. Plan 0–2 CGI sections max unless narrative requires otherwise.
7. JSON creation: `quick_project.py` if needed; remove placeholder captions and assets; verify `--check`. Maintain original product proportions and brand assets.
8. Preview -> view contact sheet -> inspect actual video playback -> adjust. Re-run with same build dir; shots cache automatically.
9. Final with narration/musical tracks; inspect actual audio and subtitles, check release gate. Export with real title/thumbnail/metadata.

## Decision table

| What script says | Choose | Avoid |
|---|---|---|
| Search, click, browse, customize | `ui` with real screenshot & cursor | fake functional UI |
| Short punchline, contradiction | `type` hero/words, `expressive` hold | floating generic blocks |
| Numerical assertion | `data` with verified evidence | invented metric count-up |
| Something grows from 1 to many | `scene3d` or data, short hero | CGI wall for every word |
| Value/exclusivity/status | `material` metal 1–2s | endless chrome |
| Witty reaction/plot twist | `expressive` character/hold | unmotivated glitch |
| Scene is complex or fails to render | honest `ui`/`type` substitute | pretending approximate 2D is perfect 3D |
| Real product example not accessible | user-supplied screenshot/HTML | AI-imagined screenshots as factual |

## Fix recipes by symptom

- `Audio mix duration mismatch`: do not truncate speech; check voice duration/locked frames and rerun. A normal silent endcard after voice is okay if deliberate.
- `Asset outside project folder`: copy the asset into a relative `assets/` subdirectory beside the JSON. No arbitrary network fetch from renderer.
- `transition too long`: use 3–8 overlap frames on short shots; maximum less than half adjacent shot length, or choose hard cut.
- `Missing audio.voice` on `--final`: request or generate genuine voice; do not create a fake release from scratch TTS demo.
- Poor text readability: shorten phrase, add line breaks, give it >0.6s visible, inspect at 360px width.
- Shot rendering fails: use `--check`, inspect `build/<project>/plans/<shot>.json` and the renderer manual. Fix shot config, do not modify engine internals as first response.
- Too many effects: remove secondary motion, keep one shared element with the preceding shot, use quiet holds and material motion.
- Weak voice acting: make fewer tags and regenerate one meaningful paragraph; tags may be ignored by particular voice/provider. Review audible result.
- Technical export done but still generic: replace template art direction with product-specific motif, more authentic UI, tighter hook/payoff structure, improve transitions.
