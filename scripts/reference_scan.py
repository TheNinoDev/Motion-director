#!/usr/bin/env python3
"""Sample actual visual change; not verified cuts, motion vectors or acoustic beats."""
import argparse,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
c=cv2.VideoCapture(str(a.video));fps=c.get(cv2.CAP_PROP_FPS);n=int(c.get(cv2.CAP_PROP_FRAME_COUNT));step=max(1,round(fps*.1));frames=[];diffs=[];prev=None;i=0
if not c.isOpened() or fps<=0:p.error('cannot decode video')
while True:
 ok,f=c.read()
 if not ok:break
 if i%step==0:
  f=cv2.resize(f,(108,192));g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)[10:174,10:98];t=i/fps
  if prev is not None:diffs.append((t,float(np.mean(cv2.absdiff(g,prev)))))
  prev=g;frames.append((t,cv2.cvtColor(f,cv2.COLOR_BGR2RGB)))
 i+=1
c.release()
if not frames:p.error('no decoded frames')
peaks=[]
for t,d in sorted(diffs,key=lambda x:-x[1]):
 if .7<t<n/fps-4 and all(abs(t-u)>2 for u,_ in peaks):peaks.append((t,d))
 if len(peaks)==5:break
peaks.sort();times=[0,.3,.6,1,1.5,2,2.5,3]+[t+offset for t,_ in peaks for offset in (-.3,0,.4)];img=Image.new('RGB',(8*116,3*218),'#202020');draw=ImageDraw.Draw(img)
for j,t in enumerate(times):
 tt,f=min(frames,key=lambda x:abs(x[0]-t));x=j%8*116;y=j//8*218;img.paste(Image.fromarray(f),(x,y));draw.text((x+2,y+194),f'{tt:.2f}s',fill='white')
img.save(a.out/'contact.jpg');(a.out/'metrics.json').write_text(json.dumps({'fps':fps,'duration':n/fps,'sample_step':step/fps,'candidate_pixel_changes':peaks,'warning':'Not exact cuts, audio beats or verified motion vectors.'},indent=2))
