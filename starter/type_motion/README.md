# Type Motion Engine (v11)
Headless Python/Pillow/NumPy/FFmpeg. No GUI or reference videos. Use installed licensed TTF/OTF, not an invented path. Run from skill root. This is a 2D/2.5D compositor; for true perspective geometry use `starter/scene3d`.

## Run unchanged first
```
python starter/type_motion/render.py starter/type_motion/demo.json work/type.mp4 --font /path/to/font.ttf --allow-synthetic-timing
python starter/type_motion/render.py starter/type_motion/demo.json work/type.png --font /path/to/font.ttf --frame 150 --allow-synthetic-timing
```
Create work first if needed. Demo is intentionally silent and timings are synthetic, not final audio. Copy JSON to work and replace all fictional text. Use 1080x1920 final, 540x960 preview. Frame indices are zero-based. Each shot starts a new canvas; use consistent anchors, colors and type across the cut. Attach aligned soundtrack via `starter/ui_engine/stitch.py`, not this renderer. `--frame` is global timeline index.

## Shot keys
Common: kind, frames, optional background, foreground, label. `hero`: text, optional subtitle, chrome true by default; `list`: text hero, items (1–12), optional chrome; `marquee`: items (1–100), optional title/subtitle; `carousel`: items, optional anchor and chrome; `counter`: from/to integer, optional subtitle/chrome; `words`: words [{text,frame,optional color}], timing_source. Each word cue is shot-local. For carousel keep dwell >= 8–15 frames if readable text matters; renderer refuses fewer than 4 per item. Grid is ambient only, never require every entry to be read. Keep list entries short and check final frame at phone size. CSS-style hex colors work. Font and platform-safe areas must be verified on actual output. Long single words fit horizontally but may become too small; shorten editorial text without changing locked spoken text. Chrome is a stylized gradient plus layered edge, not a physically rendered metal mesh. Counter numbers must reflect real claims or visibly labeled fictional demonstration.

## Verified word timings
```
python starter/type_motion/align.py work/words.json work/locked-script.txt work/word-plan.json --duration 12.4 --fps 30 --source verified_alignment --srt work/captions.srt
```
Input `words.json`: {"words":[{"text":"One","start":0.15,"end":0.34},...]}. Times are seconds relative to the actual audio being edited, including any leading trim/offset. Obtain them from a working forced aligner or ASR with word timestamps, verify script match and listen at boundaries. Normalize provider word segmentation manually when needed (do not invent missing timestamps). No alignment engine is bundled. `manual_verified` is allowed only if a human or agent actually checked each cue. `synthetic_demo` is allowed only in previews with explicit flag; the renderer refuses that source otherwise. Script must be clean spoken words without TTS tags; alignment compiler checks normalized token sequence, nonoverlap, bounds, and generates 10-word groups (split sooner if layout too tall). SRT is a separate caption track, not burned into the video. Inspect it before release; it uses up to 7 words, approximately 42 characters, <=3 seconds per group when possible. Timing source labels are declared by the operator, not proof of ASR accuracy.

## Recipe choice
A true product quantity → hero/list, visual argument → word reveal, many variants → carousel, abundance metaphor → marquee, real changing quantity → counter. Do not turn every ad into a count or a word wall. Use verified product footage for payoff. Reuse original motif at end with changed meaning. For transitions between arbitrary geometry use current UI/3D engines; no arbitrary glyph morphing is claimed.
