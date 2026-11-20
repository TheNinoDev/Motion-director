#!/usr/bin/env python3
"""Convert verified word timestamps into reveal frames and clean SRT. No ASR claims."""
import argparse,json,math,re
from pathlib import Path

def normalize(s):return re.sub(r'[^\w]+','',s.casefold())
def compile_cues(data,script,fps,duration,source):
    if fps<=0 or not math.isfinite(duration) or duration<=0:raise ValueError('invalid fps/duration')
    if source not in ('verified_alignment','manual_verified','synthetic_demo'):raise ValueError('unrecognized timing source')
    words=data['words'];expected=[normalize(x) for x in script.split() if normalize(x)]
    if not words or [normalize(w['text']) for w in words]!=expected:raise ValueError('aligned words differ from locked script; correct alignment before editing')
    prev=0.;frames=math.ceil(duration*fps);out=[]
    for w in words:
        start=float(w['start']);end=float(w['end'])
        if not (math.isfinite(start) and math.isfinite(end) and 0<=start<end<=duration and start>=prev-1e-6):raise ValueError('overlapping or invalid word timing')
        prev=end;out.append({'text':w['text'],'frame':min(frames-1,int(start*fps+0.5))})
    return out,frames

def srt_time(sec):
    ms=round(sec*1000); h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def main():
    a=argparse.ArgumentParser();a.add_argument('alignment');a.add_argument('script');a.add_argument('output');a.add_argument('--fps',type=int,default=30);a.add_argument('--duration',type=float,required=True);a.add_argument('--source',required=True,choices=['verified_alignment','manual_verified','synthetic_demo']);a.add_argument('--srt');args=a.parse_args()
    try:
        data=json.loads(Path(args.alignment).read_text(encoding='utf8'));script=Path(args.script).read_text(encoding='utf8');words,frames=compile_cues(data,script,args.fps,args.duration,args.source)
        # split into stable short visual groups; never estimate timings from text length
        groups=[];start=0
        for i in range(0,len(words),10):
            part=words[i:i+10];end=words[i+10]['frame'] if i+10<len(words) else frames
            if end<=start or part[-1]['frame']>=end:raise ValueError('group boundary shares frame; adjust grouping/timing')
            groups.append({'kind':'words','frames':end-start,'timing_source':args.source,'words':[dict(w,frame=w['frame']-start) for w in part]});start=end
        p={'width':1080,'height':1920,'fps':args.fps,'shots':groups};Path(args.output).write_text(json.dumps(p,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        if args.srt:
            rows=[];ws=data['words'];i=0
            while i<len(ws):
                j=i+1
                while j<len(ws) and j-i<7 and len(' '.join(w['text'] for w in ws[i:j+1]))<=42 and ws[j]['end']-ws[i]['start']<=3:j+=1
                rows.append(f"{len(rows)+1}\n{srt_time(ws[i]['start'])} --> {srt_time(ws[j-1]['end'])}\n"+' '.join(w['text'] for w in ws[i:j]));i=j
            Path(args.srt).write_text('\n\n'.join(rows)+'\n',encoding='utf8')
        print(f'{len(words)} words, {frames} frames, {len(groups)} groups; source={args.source}')
    except (ValueError,KeyError,TypeError,AttributeError,OSError) as e:a.exit(2,f'ERROR: {e}\n')
if __name__=='__main__':main()
