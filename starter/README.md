# Runnable 8-second silent technique demo
Requires Python 3, Pillow, FFmpeg with libx264, and a local TrueType font. No packages or fonts are bundled. The fictional FindNote UI is illustrative, not a real product. This is deliberately simple working 2D code for novice agents, not a full-quality NOIZ clone. Adapt scene content, motion, composition and actual audio; do not ship as-is.

From skill root:
```
python scripts/doctor.py
python scripts/check_shots.py starter/shot-plan.json
python starter/render.py --preview --output ./demo.mp4
python starter/render.py --frame 80 --output ./frame.png
ffprobe -v error -show_streams demo.mp4
ffmpeg -v error -xerror -i demo.mp4 -f null -
```
If font lookup fails, pass `--font /actual/path/to/your/authorized/font.ttf`. On Windows use a valid font path. `--preview` produces 540x960; omit for 1080x1920. `--frame` writes PNG and does not require FFmpeg. The script uses fixed frame math and no wall-clock timers. To add user audio, align frame count to measured duration first, then mux via FFmpeg per reference guide; this demo is explicitly silent. No audio/assets needed for the smoke test only.
