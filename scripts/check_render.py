#!/usr/bin/env python3
"""Probe a render; optional full decode and black/freeze/loudness diagnostics. Manual QA remains required."""
import argparse,json,subprocess,sys,math
from fractions import Fraction
from pathlib import Path

def run(args): return subprocess.run(args,capture_output=True,text=True)
def check(path, width, height, fps, duration, audio, decode, diagnostics):
    e=[]; w=[]; out={'file':str(path),'manual_review_required':True}
    p=run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)])
    if p.returncode: return {'valid':False,'errors':['ffprobe: '+p.stderr.strip()]}
    m=json.loads(p.stdout); v=next((s for s in m['streams'] if s['codec_type']=='video' and not s.get('disposition',{}).get('attached_pic')),None); a=[s for s in m['streams'] if s['codec_type']=='audio']
    out['metadata']=m
    if not v: e.append('No video stream')
    else:
        for key,expected in [('width',width),('height',height)]:
            if expected is not None and v.get(key)!=expected: e.append(f'{key} mismatch: {v.get(key)} vs {expected}')
        try: actual_fps=float(Fraction(v.get('avg_frame_rate','0/1')))
        except (ZeroDivisionError,ValueError): actual_fps=0
        if fps and abs(actual_fps-fps)>.03: e.append(f'fps mismatch: {actual_fps} vs {fps}')
        if v.get('pix_fmt')!='yuv420p': w.append('Check playback compatibility of pixel format')
    if audio and not a: e.append('No audio stream')
    try: actual=float(m.get('format',{}).get('duration',0))
    except (ValueError,TypeError): actual=0
    if not math.isfinite(actual) or actual<=0: e.append('Invalid duration')
    if duration is not None and abs(actual-duration)>max(.12,2/(fps or 30)): e.append(f'Duration mismatch: {actual} vs {duration}')
    if decode:
        r=run(['ffmpeg','-v','error','-xerror','-i',str(path),'-map','0:v?','-map','0:a?','-f','null','-']);out['full_decode']='pass' if r.returncode==0 else 'fail'
        if r.returncode: e.append('Decode failed: '+r.stderr.strip()[-2000:])
    else: out['full_decode']='not-run'
    if diagnostics and v:
        r=run(['ffmpeg','-hide_banner','-i',str(path),'-vf','blackdetect=d=0.3:pix_th=0.08,freezedetect=n=-60dB:d=0.7','-an','-f','null','-'])
        out['black_freeze_candidates']=[line.strip() for line in r.stderr.splitlines() if 'black_start:' in line or 'freeze_start:' in line or 'freeze_end:' in line or 'freeze_duration:' in line]
        if r.returncode: w.append('Video diagnostics failed')
        if out['black_freeze_candidates']: w.append('Review black/freeze candidates manually; intentional holds may be valid')
    if diagnostics and a:
        r=run(['ffmpeg','-hide_banner','-i',str(path),'-vn','-af','loudnorm=print_format=json','-f','null','-'])
        try:
            s=r.stderr; report=json.loads(s[s.rfind('{'):s.rfind('}')+1]);out['loudness']=report
            if float(report['input_tp'])>-1: w.append('True peak above suggested -1 dBTP; review master')
        except (ValueError,KeyError): w.append('Loudness diagnostics unavailable')
    out.update(valid=not e,errors=e,warnings=w);return out

def main():
    p=argparse.ArgumentParser();p.add_argument('media',type=Path);p.add_argument('--width',type=int);p.add_argument('--height',type=int);p.add_argument('--fps',type=float);p.add_argument('--duration',type=float);p.add_argument('--allow-no-audio',action='store_true');p.add_argument('--decode',action='store_true');p.add_argument('--diagnostics',action='store_true');p.add_argument('-o','--output',type=Path);a=p.parse_args()
    try: out=check(a.media,a.width,a.height,a.fps,a.duration,not a.allow_no_audio,a.decode,a.diagnostics)
    except (OSError,ValueError,KeyError) as ex: p.exit(1,f'Check failed: {ex}\n')
    s=json.dumps(out,indent=2)+'\n'; a.output.write_text(s,encoding='utf-8') if a.output else print(s,end='');sys.exit(not out['valid'])
if __name__=='__main__': main()
