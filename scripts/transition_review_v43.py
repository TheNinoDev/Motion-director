#!/usr/bin/env python3
"""Actual decoded preview boundary evidence. Metrics are prompts, never conclusions."""
import json, math, argparse
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from agent_session import sha,write

def targets(creative,fps,n):
 # Review all joins. Also show opening and closing, including single-beat films.
 beats=creative['beats'];times=[0]+[b['start'] for b in beats[1:]]+[(n-1)/fps];out=[]
 for j,t in enumerate(times):
  f=max(0,min(n-1,round(t*fps)));offsets=[-round(fps*.2),-2,-1,0,1,2,round(fps*.2)];frames=sorted({max(0,min(n-1,f+x)) for x in offsets});out.append({'id':j,'center':f,'frames':frames,'outgoing':beats[j-1]['outgoing_anchor'] if j else None,'incoming':beats[j]['incoming_anchor'] if j<len(beats) else None})
 return out

def metrics(a,b):
 d=np.abs(a.astype(np.int16)-b.astype(np.int16));return {'mean_rgb_delta':round(float(d.mean()),4),'changed_fraction':round(float((d.max(axis=2)>24).mean()),4)}

def create(video,creative,out,fps,n):
 if out.exists():raise ValueError('new review folder required')
 h=sha(video);tt=targets(creative,fps,n);wanted={f for q in tt for f in q['frames']};cap=cv2.VideoCapture(str(video));cache={};i=0
 try:
  while i<=max(wanted):
   ok,frame=cap.read()
   if not ok:raise ValueError(f'preview decode stopped at {i}')
   if i in wanted:
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB);cache[i]=np.asarray(Image.fromarray(frame).resize((180,320),Image.Resampling.LANCZOS))
   i+=1
 finally:cap.release()
 out.mkdir(parents=True);results=[]
 for q in tt:
  fs=q['frames'];sheet=Image.new('RGB',(180*len(fs),350),'#10151b');draw=ImageDraw.Draw(sheet);pairs=[]
  for j,f in enumerate(fs):
   sheet.paste(Image.fromarray(cache[f]),(j*180,0));draw.text((j*180+8,329),f'{f/fps:.3f}s / {f}',fill='#ffffff')
   if j and f-fs[j-1]==1:pairs.append({'from':fs[j-1],'to':f,**metrics(cache[fs[j-1]],cache[f])})
  flags=[]
  if any(x['changed_fraction']>.65 and x['mean_rgb_delta']>35 for x in pairs):flags.append('large adjacent-frame change: intentional cut or accidental jump?')
  if q['outgoing'] and q['incoming'] and q['outgoing']!=q['incoming']:flags.append('different declared anchors: inspect match or intentional contrast')
  filename=f'boundary-{q["id"]:03d}.png';sheet.save(out/filename);results.append({**q,'file':filename,'sha256':sha(out/filename),'adjacent_metrics':pairs,'flags':flags})
 if sha(video)!=h:raise ValueError('preview changed during decoding')
 r={'video_sha256':h,'fps':fps,'frames':n,'results':results,'limitations':'Decoded 180×320 samples; changes may be intentional. Not optical flow or proof of smooth movement. Watch full preview and inspect final native output.'};write(out/'report.json',r);return r

def verify(video,creative,out,fps,n):
 try:
  r=json.loads((out/'report.json').read_text());errs=[]
  if r['video_sha256']!=sha(video) or r['fps']!=fps or r['frames']!=n:errs.append('transition video or timing changed')
  tt=targets(creative,fps,n)
  if len(r['results'])!=len(tt):errs.append('missing boundaries')
  for a,b in zip(r['results'],tt):
   if any(a[k]!=b[k] for k in b):errs.append('boundary target changed')
   f=out/f'boundary-{b["id"]:03d}.png'
   if a['file']!=f.name or not f.is_file() or sha(f)!=a['sha256']:errs.append('missing/changed '+f.name)
  return {'valid':not errs,'errors':errs}
 except (OSError,ValueError,KeyError,TypeError) as e:return {'valid':False,'errors':['transition evidence invalid: '+str(e)]}
