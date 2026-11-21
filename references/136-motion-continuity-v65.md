# 136 — Motion continuity and no accidental dead frames (v65)

## Evidence from the user's actual comparison

The uploaded 24.6-second v64 RobloxLARP film and the same-duration Claude protection film were compared at identical sampling settings. At 2 samples/second, 56.2% of the v64 film's consecutive samples changed by less than 2 grayscale units on average; Claude's version measured 25.0%. At 10 samples/second, the respective low-change transition figures were 84.5% and 60.8%. **These are diagnostics, not literal duplicate-frame counts or artistic quality scores.** The v64 film has candidate static stretches around 0.4–3.0s, 4.4–7.7s, 8.3–10.8s, and 19.6–24.5s. Inspect the actual film before attributing a cause.

## Rule: almost no *unintentional* static time

The user explicitly dislikes dead frames. For every beat, either the hero or its meaning develops, or a short purposeful hold serves comprehension, suspense, narration, or the brand payoff. Do not maintain unchanged text/icons for multiple seconds by habit. If a scene lasts >1.5 seconds, review its internal staging and changes before rendering. If roughly 0.85 seconds or more is near-static, flag it for real playback review, not automatic jitter. No imposed number of cuts or non-stop camera motion. Motion without meaning (pulsing logos, random particles, noise, perpetual zoom) is not a fix.

Use an editorial sequence like **setup → anticipate → move/change → impact → readable settle → carry into the next shot**. Objects have intentional acceleration, inertia, delayed secondary reactions and a changed destination. Different layers must not all use the same smoothstep and arrive at exactly the same instant. A static endcard must earn its duration and appear only after the emotional payoff; otherwise trim or introduce one revealing brand action.

## Audit actual encoded film

Use the new bundled script, not assertions about keyframes:

```bash
python scripts/hold_audit_v65.py work/rough.mp4 --fps 10 --max-hold 0.85 --report work/hold-audit.json
python scripts/hold_audit_v65.py work/final.mp4 --fps 10 --max-hold 0.85 --strict --allow work/intentional-holds.json
```

A deliberate hold allowlist uses `{"holds":[{"start":22.5,"end":24.2,"reason":"final URL legibility after narration ends"}]}`. No blanket allowlisting or invented review. For every flagged section examine full-speed playback, slowing it for stutter inspection where useful. Report time range, the visual problem, exact restaging, and verified repaired excerpt. A film can be deliberately minimalist and still be visually active.

## Transitions

Use one visual anchor across a cut: a code strip becomes a border; a pulled key becomes the next frame's shape; the moving copy carries the camera to the following stage. Favor intentional on-beat cuts over irrelevant wipes. Use masks, trim, deformation, depth and motion blur only when supported and meaningful. Keep type readable during motion. Do not reproduce another agent's exact film assets or style as a template.
