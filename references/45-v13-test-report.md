# v13 technical verification
- Reference 9: sampled 156 times at 0.25-second intervals; first ~35 seconds are ad. FFmpeg volumedetect on first 35 s: mean -15.8 dBFS, peak 0.0 dBFS. Combined soundtrack only, not isolated speech, and no claim of verified transcript.
- Unified demo: 10 shots, 6 backends, 300 decoded frames, 30 fps, 360x640, 10 seconds, no audio. Full decode passed. Midpoint contact sheet reviewed; palette caption overlap corrected and demo rerendered.
- Separate data adapter demo: 180 decoded frames, 30 fps, 6 seconds; technical pass. Data remains demo-only.
- Audio test: 60 frames at 30 fps, 2 seconds, low-level generated tone muxed and full decode passed. Not real VO or music; no marketing release claim.
- Negative tests: timeline gap and missing audio both rejected with nonzero exit.
- No full-resolution performance benchmark, audible assessment, full semantic ASR, weak-model independent production run, or visual parity claim. Technical tests are not creative release certification.
