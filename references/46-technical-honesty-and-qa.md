# Release checklist: test outputs, do not mistake a decodable file for a good ad

## Automated checks (actually supported)
- Each engine returns a verifiable exact frame count, canvas, and clip; each concatenation/transition is checked.
- `--check` validates known structural fields and local image paths before starting expensive rendering.
- Re-runs can reuse cached per-shot files. The cache hashes configs, source files, fonts and same-folder Python renderer dependencies.
- `--final` refuses absent voice; silent `--preview` is always labeled preview.
- The combined soundtrack can include voice with music ducked under it, with a sample limiter and fixed output duration.
- A contact sheet plus `report.json` help the operator review key frames and technical quality.

## Tasks a script cannot prove
- That the audience likes the hook or voice acting; that the TTS speaker followed tag intent; that visuals look like a studio-quality NOIZ film; that the product UI depicts a functional feature; that a copyrighted song is cleared for public marketing; or that the final video has safe-area overlays in all apps.
- No ASR/forced aligner or online trend oracle is bundled; these require a connected provider/model or genuine user-supplied timestamps.
- Final video must be watched/listened to. Review first ~3s, all transitions, screen edges, final 2s and the full VO/music balance. Then run the old QA tools and save evidence, not synthetic green checkmarks.

## Regression tests
Run `python -m unittest discover -s tests -p 'test_unified.py'` from the skill root; if dependencies unavailable, doctor the environment first. Run an actual project preview and inspect video even when all tests pass. Demo content and generated tones may never be described as real product evidence.
