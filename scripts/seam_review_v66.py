#!/usr/bin/env python3
"""Generate objective cut/seam review strips from video, NOT an aesthetic validator.

Requires ffmpeg, Pillow. No new editing engine, no footage modification.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

W, H = 160, 284


def extract(path: Path, fps: int):
    if not path.is_file():
        raise FileNotFoundError(path)
    if not shutil.which('ffmpeg'):
        raise RuntimeError('ffmpeg is required for video decoding')
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(path),
            '-vf', f'fps={fps},scale={W}:{H}:flags=area', '-an', '-pix_fmt', 'rgb24',
            '-f', 'rawvideo', '-']
    job = subprocess.run(args, capture_output=True, check=False)
    if job.returncode:
        raise RuntimeError(f'ffmpeg decode failed: {job.stderr.decode(errors="replace")[-700:]}')
    chunk = W*H*3
    if len(job.stdout) < chunk or len(job.stdout) % chunk:
        raise ValueError('Video decoded to zero or partial RGB frames')
    return [Image.frombytes('RGB', (W, H), job.stdout[i:i+chunk])
            for i in range(0, len(job.stdout), chunk)]


def scores(frames):
    gs = [f.convert('L') for f in frames]
    return [0.] + [float(ImageStat.Stat(ImageChops.difference(a, b)).mean[0])
                     for a, b in zip(gs[:-1], gs[1:])]


def auto_peaks(s, fps, top, min_diff):
    candidates = [(i, s[i]) for i in range(1, len(s)-1)
                  if s[i] >= min_diff and s[i] >= s[i-1] and s[i] >= s[i+1]]
    candidates.sort(key=lambda x: -x[1])
    chosen = []
    for i, val in candidates:
        if all(abs(i - other) > 0.65*fps for other in chosen):
            chosen.append(i)
        if len(chosen) >= top:
            break
    return sorted(chosen)


def parse_cuts(cuts, fps, length):
    if not cuts: return None
    result = []
    for term in cuts.split(','):
        t = float(term.strip())
        if not 0 < t < (length/fps):
            raise ValueError(f'Cut time {t} outside video duration')
        idx = max(1, min(length-1, round(t*fps)))
        if idx not in result: result.append(idx)
    return sorted(result)


def make_sheet(frames, positions, fps, output):
    offsets = [-0.4, -0.1, 0.1, 0.4]
    cellw, cellh, pad, header = 160, 284, 5, 37
    canvas = Image.new('RGB', (len(offsets)*(cellw+pad), len(positions)*(cellh+header+pad)), '#14171c')
    dr = ImageDraw.Draw(canvas)
    for row, i in enumerate(positions):
        y = row*(cellh+header+pad)
        dr.text((5,y+5), f'SEAM {row+1} | candidate {i/fps:.2f}s | visual continuity: review manually',fill='white')
        for col,dt in enumerate(offsets):
            at = min(len(frames)-1,max(0,i+round(dt*fps)))
            x=col*(cellw+pad)
            canvas.paste(frames[at],(x,y+header))
            dr.text((x+4,y+21),f'{at/fps:.2f}s',fill='#b8d5e3')
    output.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(output)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('video',type=Path)
    p.add_argument('--cuts',help='Comma-separated transition timecodes in seconds. If omitted, inspect strongest image changes.')
    p.add_argument('--fps',type=int,default=10)
    p.add_argument('--top',type=int,default=10)
    p.add_argument('--min-diff',type=float,default=18.)
    p.add_argument('--report',type=Path)
    p.add_argument('--sheet',type=Path)
    a=p.parse_args(argv)
    if a.fps < 4 or a.fps > 30: p.error('--fps must be between 4 and 30')
    if a.top < 1 or a.top > 80: p.error('--top must be 1..80')
    frames=extract(a.video,a.fps)
    s=scores(frames)
    positions = parse_cuts(a.cuts,a.fps,len(frames))
    if positions is None:
        positions = auto_peaks(s,a.fps,a.top,a.min_diff)
    seams = []
    for i in positions:
        seams.append({'time_s':round(i/a.fps,3),'sampled_change_0_255':round(s[i],2),
                      'questions':['What focal subject persists or what editorial contrast motivates this cut?',
                                   'Do the outgoing and incoming motion directions/curves look intentional?',
                                   'Does the incoming scene answer the previous action or line?']})
    report={'video':str(a.video),'fps_sampled':a.fps,'frames_sampled':len(frames),
            'method':'RGB-to-grayscale mean absolute consecutive-frame change; peaks only select review candidates',
            'caveat':'Neither continuity nor smoothness nor aesthetic quality can be inferred from pixel-change score. Watch full seams at 1x and 0.5x.',
            'seams':seams}
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if a.sheet:
        if not positions: raise ValueError('No seam candidate found; provide --cuts or reduce --min-diff')
        make_sheet(frames,positions,a.fps,a.sheet)
    print(json.dumps({'video':str(a.video),'seams':[{k:v for k,v in x.items() if k!='questions'} for x in seams],
                      'sheet':str(a.sheet) if a.sheet else None,'report':str(a.report) if a.report else None},indent=2))

if __name__=='__main__':main()
