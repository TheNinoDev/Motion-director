#!/usr/bin/env python3
"""Review EVERY second decoded source frame of the final actual MP4.

Requires ffmpeg, ffprobe, Pillow, numpy. Produces paginated contact sheets and a
factual frame-coverage report. Metrics only flag candidates for human review.

python scripts/two_frame_finish_v74.py video.mp4 --out review --every 2 [--plan plan.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


SCALE_W, SCALE_H = 150, 266


def probe(path: Path) -> dict:
    if not shutil.which('ffprobe') or not shutil.which('ffmpeg'):
        raise RuntimeError('ffmpeg and ffprobe are required')
    r = subprocess.run([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,avg_frame_rate,nb_frames',
        '-show_entries', 'format=duration', '-of', 'json', str(path),
    ], check=True, capture_output=True, text=True)
    data = json.loads(r.stdout)
    if not data.get('streams'):
        raise ValueError('no video stream')
    s = data['streams'][0]
    fps = float(Fraction(s['avg_frame_rate']))
    if fps <= 0 or not math.isfinite(fps):
        raise ValueError('invalid frame rate')
    return {
        'fps': fps, 'width': s['width'], 'height': s['height'],
        'duration': float(data['format']['duration']),
        'container_frame_claim': int(s['nb_frames']) if (s.get('nb_frames') or '').isdigit() else None,
    }


def decode_every_n(video: Path, every: int):
    """Decode ALL frames, retain source indices divisible by every."""
    if every < 1:
        raise ValueError('every must be >= 1')
    frame_size = SCALE_W * SCALE_H * 3
    command = [
        'ffmpeg', '-nostdin', '-loglevel', 'error', '-i', str(video),
        '-map', '0:v:0', '-vf', f'scale={SCALE_W}:{SCALE_H}:flags=bilinear',
        '-vsync', '0', '-an', '-sn', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'
    ]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    frames = []
    decoded = 0
    assert proc.stdout is not None
    try:
        while True:
            payload = proc.stdout.read(frame_size)
            if not payload:
                break
            if len(payload) != frame_size:
                raise RuntimeError(f'partial decoded frame {decoded}: {len(payload)} bytes')
            if decoded % every == 0:
                frame = np.frombuffer(payload, dtype=np.uint8).reshape(SCALE_H, SCALE_W, 3).copy()
                frames.append((decoded, frame))
            decoded += 1
    finally:
        proc.stdout.close()
    stderr = proc.stderr.read().decode('utf-8', errors='replace') if proc.stderr else ''
    if proc.stderr:
        proc.stderr.close()
    if proc.wait() != 0:
        raise RuntimeError(f'video decode failed: {stderr[:1000]}')
    if not decoded:
        raise RuntimeError('decoded no video frames')
    assert len(frames) == (decoded + every - 1) // every
    return decoded, frames


def diffs(frames, fps, every, still_threshold=1.25, jump_threshold=28):
    """Candidates, never creative pass/fail. Frame differences are 8-bit mean abs."""
    values = []
    for (index, current), (_, previous) in zip(frames[1:], frames[:-1]):
        d = float(np.abs(current.astype(np.int16) - previous.astype(np.int16)).mean())
        values.append({'source_frame': index, 'time': round(index / fps, 3), 'mean_absolute_difference': round(d, 3)})
    interval = every / fps
    still_runs = []
    start = None
    for i, item in enumerate(values):
        if item['mean_absolute_difference'] <= still_threshold and start is None:
            start = i
        if (item['mean_absolute_difference'] > still_threshold or i == len(values)-1) and start is not None:
            end = i if (i == len(values)-1 and item['mean_absolute_difference'] <= still_threshold) else i-1
            duration = (end-start+1)*interval
            if duration >= 0.7:
                still_runs.append({
                    'start': round(frames[start][0] / fps, 3),
                    'end': round(frames[end+1][0] / fps, 3),
                    'seconds': round(duration, 3),
                    'caveat': 'Review for intentional read-time; do not automatically reject holds.'
                })
            start = None
    jumps = [x for x in values if x['mean_absolute_difference'] >= jump_threshold]
    jumps.sort(key=lambda x:x['mean_absolute_difference'], reverse=True)
    return {'still_candidates': still_runs, 'jump_candidates': jumps[:30], 'analyzed_pairs': len(values)}


def _font():
    for name in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf']:
        try:
            return ImageFont.truetype(name, 13)
        except OSError:
            pass
    return ImageFont.load_default()


def build_pages(frames, fps, folder, per_page=36, cols=6):
    if per_page < 1 or cols < 1:
        raise ValueError('page size/columns must be >= 1')
    folder.mkdir(parents=True, exist_ok=True)
    rows = (per_page + cols - 1) // cols
    cell_h = SCALE_H + 21
    files = []
    font = _font()
    for pno in range(0, len(frames), per_page):
        batch = frames[pno:pno+per_page]
        canvas = Image.new('RGB',(cols*SCALE_W, rows*cell_h),(18,20,27))
        d = ImageDraw.Draw(canvas)
        for i, (frame_id, im) in enumerate(batch):
            x = (i % cols) * SCALE_W
            y = (i // cols) * cell_h
            canvas.paste(Image.fromarray(im),(x,y))
            d.text((x+3,y+SCALE_H+2),f'#{frame_id:04d} {frame_id/fps:06.2f}s',font=font,fill=(249,249,250))
        output = folder / f'frames-{len(files)+1:03d}.jpg'
        canvas.save(output,quality=92)
        files.append(output.name)
    return files


def planned_seams(plan, fps, frame_count, frames, folder):
    if plan is None:
        return None
    scenes = plan.get('scenes') or plan.get('shots')
    if not isinstance(scenes, list) or not scenes:
        raise ValueError('plan requires scenes or shots with end times')
    moments = []
    for i, scene in enumerate(scenes[:-1]):
        if not isinstance(scene.get('end'), (int, float)):
            raise ValueError(f'plan entry {i} has no numeric end')
        t = float(scene['end'])
        if not 0 < t < frame_count / fps:
            raise ValueError(f'plan entry {i}: seam outside film')
        moments.append(t)
    if not moments:
        return []
    frame_map = {k:v for k,v in frames}
    images = []
    for seam_no, t in enumerate(moments,1):
        center = round(t * fps)
        for offset in [-8,-4,-2,0,2,4,8]:
            frame_id = max(0,min(frame_count - 1, center + offset))
            frame_id -= frame_id % (frames[1][0] - frames[0][0] if len(frames)>1 else 1)
            frame_id = max(0,min(frame_id, max(frame_map)))
            images.append((frame_id,frame_map[frame_id]))
    pages=build_pages(images,fps,folder/'seam-neighborhoods',per_page=28,cols=7)
    return {'times': moments,'pages':pages}


def analyze(video: Path, out: Path, every=2, plan=None, per_page=36):
    if not video.is_file():
        raise FileNotFoundError(video)
    metadata=probe(video)
    count, frames=decode_every_n(video,every)
    out.mkdir(parents=True,exist_ok=True)
    pages=build_pages(frames,metadata['fps'],out/'pages',per_page=per_page)
    notes=diffs(frames,metadata['fps'],every)
    seams=planned_seams(plan,metadata['fps'],count,frames,out) if plan else None
    report={
        'tool':'two_frame_finish_v74', 'video':str(video),
        'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        **metadata, 'decoded_source_frames':count, 'sample_every_source_frames':every,
        'sampled_frames':len(frames), 'expected_sampled_frames':(count+every-1)//every,
        'first_source_frame':frames[0][0], 'last_sampled_source_frame':frames[-1][0],
        'page_files':pages,'total_pages':len(pages),'candidate_flags':notes,'seam_review':seams,
        'visual_review_done':False,
        'disclosure':'Pages were generated; a human or image-capable agent must actually inspect ALL pages and view actual playback. No automated aesthetic approval.',
        'unsampled_frame_warning':'Sampling every 2nd source frame does not inspect the intervening frames.'
    }
    (out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('video',type=Path)
    a.add_argument('--out',type=Path,required=True)
    a.add_argument('--every',type=int,default=2)
    a.add_argument('--per-page',type=int,default=36)
    a.add_argument('--plan',type=Path)
    args=a.parse_args()
    plan=json.loads(args.plan.read_text(encoding='utf8')) if args.plan else None
    data=analyze(args.video,args.out,args.every,plan,args.per_page)
    print(json.dumps({'decoded':data['decoded_source_frames'],'sampled':data['sampled_frames'],
      'pages':data['total_pages'],'stills':len(data['candidate_flags']['still_candidates']),
      'jumps':len(data['candidate_flags']['jump_candidates']),
      'report':str(args.out/'review.json')},indent=2))


if __name__=='__main__':
    main()
