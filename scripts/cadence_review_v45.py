"""Decode the complete preview, measure per-frame visual changes and make beat evidence."""
import math,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from agent_session import sha,write
SIZE=(180,320)

def intervals(creative,fps,n):
 return [(max(0,math.ceil(b['start']*fps-1e-8)),min(n,math.ceil(b['end']*fps-1e-8))) for b in creative['beats']]

def metrics(deltas,black,fps):
 run=longest=0
 for v in deltas:
  run=run+1 if v<.12 else 0;longest=max(run,longest)
 flags=[]
 if longest>=math.ceil(.65*fps):flags.append('near-static interval >= 0.65 s; verify deliberate hold or missing action')
 if black>=max(1,math.ceil(.2*fps)):flags.append('near-black frames; inspect intended black or missing visual')
 if any(v>40 for v in deltas):flags.append('large within-beat image change; inspect intentional cut or discontinuity')
 return {'mean_rgb_delta':round(float(np.mean(deltas)) if deltas else 0.,3),'longest_near_static_s':round(longest/fps,3),'near_black_frames':black,'flags':flags}

def create(video,creative,out,fps,n):
 if out.exists():raise ValueError('new cadence directory required')
 original=sha(video);bounds=intervals(creative,fps,n)
 if not bounds or any(a>=b for a,b in bounds):raise ValueError('each beat must have decoded frames')
 cap=cv2.VideoCapture(str(video));selected={};stats=[{'deltas':[],'black':0} for _ in bounds];index=0;prev=None
 chosen=[sorted(set([a,(a+b-1)//2,b-1])) for a,b in bounds];wanted=set().union(*[set(x) for x in chosen]);all_delta=[]
 try:
  for i in range(n):
   ok,im=cap.read()
   if not ok:raise ValueError(f'decode interrupted at frame {i}')
   while index+1<len(bounds) and i>=bounds[index][1]:index+=1
   rgb=cv2.cvtColor(cv2.resize(im,SIZE,interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2RGB)
   d=float(np.mean(cv2.absdiff(rgb,prev))) if prev is not None else 0.;all_delta.append(d)
   if i>bounds[index][0]:stats[index]['deltas'].append(d)
   stats[index]['black']+=int(np.mean(rgb)<5 and np.percentile(rgb,95)<12)
   if i in wanted:selected[i]=rgb.copy()
   prev=rgb
  if cap.read()[0]:raise ValueError('unexpected extra decoded frames')
 finally:cap.release()
 out.mkdir();results=[]
 for j,((a,b),st,ids) in enumerate(zip(bounds,stats,chosen)):
  m=metrics(st['deltas'],st['black'],fps);sheet=Image.new('RGB',(SIZE[0]*len(ids),SIZE[1]+94),'#15202b');dr=ImageDraw.Draw(sheet)
  for k,i in enumerate(ids):sheet.paste(Image.fromarray(selected[i]),(k*SIZE[0],0));dr.text((k*SIZE[0]+6,SIZE[1]+4),f'{i/fps:.2f}s / f{i}',fill='white')
  x0=8;y0=SIZE[1]+35;w=sheet.width-16;h=48;dr.rectangle((x0,y0,x0+w,y0+h),outline='#617586');dr.text((x0,y0-13),'RGB change per frame (0-60 clipped)',fill='#c9ddf0')
  ds=st['deltas'];pts=[(x0+round(k/max(1,len(ds)-1)*w),y0+h-round(min(60,v)/60*h)) for k,v in enumerate(ds)]
  if len(pts)>1:dr.line(pts,fill='#80d7be',width=2)
  file=f'beat-{j:03d}.png';sheet.save(out/file);results.append({'beat':j,'start_frame':a,'end_frame_exclusive':b,'sample_frames':ids,'file':file,'sha256':sha(out/file),**m})
 if sha(video)!=original:raise ValueError('preview changed during scan')
 r={'video_sha256':original,'fps':fps,'frames':n,'analysis_size':list(SIZE),'results':results,'limitations':'Reduced-resolution RGB changes are hints, not subjective quality; static/black/cuts may be deliberate. Not motion magnitude, OCR, or object tracking.'};write(out/'report.json',r);return r

def verify(video,creative,out,fps,n):
 try:
  r=json.loads((out/'report.json').read_text());err=[]
  if r['video_sha256']!=sha(video) or r['fps']!=fps or r['frames']!=n:err.append('cadence source changed')
  want=intervals(creative,fps,n)
  if [(x['beat'],x['start_frame'],x['end_frame_exclusive']) for x in r['results']]!=[(j,a,b) for j,(a,b) in enumerate(want)]:err.append('cadence beat targets changed')
  for x in r['results']:
   f=out/f'beat-{x["beat"]:03d}.png'
   if x['file']!=f.name or sha(f)!=x['sha256']:err.append('cadence image changed')
  return {'valid':not err,'errors':err}
 except (OSError,ValueError,KeyError,TypeError,AttributeError) as e:return {'valid':False,'errors':['cadence evidence missing/invalid: '+str(e)]}
