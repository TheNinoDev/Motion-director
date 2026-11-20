# V14 test and limits

- v13.1 source archive was extracted and all old paths retained; main SKILL, README and unified production controller are intentionally updated.
- Original v13 preview decoded at 360x640, 30fps, 132 frames; v14 first pass decoded at 1080x1920, 30fps, 180 frames; first pass had no low-motion intervals over the diagnostic threshold, unlike v13. Different films, so counts are not proof of creative improvement.
- Four new tests passed: easing, five mask variants, deterministic particle/gradient output, invalid plan rejection. All five existing unified tests passed. New layer + typography two-shot integration rendered 22 frames with a 2-frame dissolve at 12fps.
- V14 draft deliberately fictional, no voiceover, no licensed soundtrack, not upload-ready. A second visual pass targets more varied camera movement, moving background light, particle dissolution and a cleaner logo transition.
- No aesthetic percentage score is calculated. 2.5D planes, approximate materials, glow and directional echoes; not physically based CGI. Text audit checks approximate sprite bounds and configured size, not OCR or exact glyph positions. Sampled luminance QA misses brief defects and cannot judge creative intent. Manual inspection mandatory. New full-HD renderer prioritizes simplicity; generate low-res previews first, as CPU rendering is slower.
