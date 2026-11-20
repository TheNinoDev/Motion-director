"""Decoded optical-flow hints around all joins. Never treat flow as ground truth."""
import json,math
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from agent_session import sha,write
from transition_review_v43 import targets

SIZE=(240,426)
def measure(a,b):
 a=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY);b=cv2.cvtColor(b,cv2.COLOR_RGB2GRAY)
 def flow(x,y):return cv2.calcOpticalFlowFarneback(x,y,None,.5,3,19,3,5,1.2,0)
 f=flow(a,b);g=flow(b,a);yy,xx=np.indices(a.shape,dtype=np.float32);xx+=f[:,:,0];yy+=f[:,:,1];back=cv2.remap(g,xx,yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT);m=np.linalg.norm(f,axis=2);err=np.linalg.norm(f+back,axis=2);texture=cv2.Sobel(a,cv2.CV_32F,1,0)**2+cv2.Sobel(a,cv2.CV_32F,0,1)**2
 valid=(m>.5)&(err<1+.15*m)&(texture>100)&(xx>=0)&(yy>=0)&(xx<a.shape[1]-1)&(yy<a.shape[0]-1)
 v=f[valid];n=len(v);median=np.median(v,axis=0) if n else np.zeros(2);speed=float(np.median(m[valid])) if n else 0.;coherence=float(np.linalg.norm(np.mean(v/np.maximum(np.linalg.norm(v,axis=1)[:,None],1e-6),axis=0))) if n else 0.
 return {'support':round(n/a.size,5),'dx':round(float(median[0]),3),'dy':round(float(median[1]),3),'speed_px_frame':round(speed,3),'coherence':round(coherence,3)},f,valid

def compare(x,y):
 if min(x['support'],y['support'])<.012 or min(x['coherence'],y['coherence'])<.65 or min(x['speed_px_frame'],y['speed_px_frame'])<.8:return None
 a=np.array([x['dx'],x['dy']]);b=np.array([y['dx'],y['dy']]);den=np.linalg.norm(a)*np.linalg.norm(b)
 if den<.01:return None
 return round(math.degrees(math.acos(float(np.clip(np.dot(a,b)/den,-1,1)))),2)

def create(video,creative,out,fps,n):
 if out.exists():raise ValueError('new flow folder required')
 initial=sha(video);tt=targets(creative,fps,n);wanted=set()
 for q in tt:wanted.update(range(max(0,q['center']-3),min(n,q['center']+4)))
 cap=cv2.VideoCapture(str(video));frames={}
 try:
  for i in range(max(wanted)+1):
   ok,im=cap.read()
   if not ok:raise ValueError(f'decode stopped at {i}')
   if i in wanted:frames[i]=cv2.resize(cv2.cvtColor(im,cv2.COLOR_BGR2RGB),SIZE,interpolation=cv2.INTER_AREA)
 finally:cap.release()
 out.mkdir();results=[]
 for q in tt:
  fs=range(max(0,q['center']-3),min(n,q['center']+4));pairs=[];views=[]
  for i in list(fs)[:-1]:
   met,f,valid=measure(frames[i],frames[i+1]);pairs.append({'frame':i,**met});im=frames[i].copy()
   for y in range(10,SIZE[1],14):
    for x in range(10,SIZE[0],14):
     if valid[y,x]:
      dx,dy=f[y,x];cv2.arrowedLine(im,(x,y),(round(x+dx*3),round(y+dy*3)),(255,220,65),1,tipLength=.35)
   views.append(im)
  flags=[];angles=[]
  for x,y in zip(pairs,pairs[1:]):
   d=compare(x,y)
   if d is not None:
    angles.append({'frame':y['frame'],'degrees':d})
    if d>85:flags.append(f'coherent direction changes near frame {y["frame"]}; inspect intended turn or cut')
  if not any(p['support']>=.012 and p['coherence']>=.65 for p in pairs):flags.append('insufficient coherent motion evidence: inspect actual playback; static/complex motion may be intentional')
  sheet=Image.new('RGB',(SIZE[0]*max(1,len(views)),SIZE[1]+40),'#17212c');dr=ImageDraw.Draw(sheet)
  for j,(im,m) in enumerate(zip(views,pairs)):
   sheet.paste(Image.fromarray(im),(j*SIZE[0],0));dr.text((j*SIZE[0]+6,SIZE[1]+4),f'{m["frame"]/fps:.2f}s -> next | {m["speed_px_frame"]:.1f}px/f',fill='white');dr.text((j*SIZE[0]+6,SIZE[1]+20),f'coh {m["coherence"]:.2f} / support {m["support"]:.3f}',fill='white')
  file=f'flow-{q["id"]:03d}.png';sheet.save(out/file);results.append({'id':q['id'],'center':q['center'],'file':file,'sha256':sha(out/file),'pairs':pairs,'angles':angles,'flags':flags})
 if sha(video)!=initial:raise ValueError('video changed')
 r={'video_sha256':initial,'fps':fps,'frames':n,'size':list(SIZE),'results':results,'limitations':'Farneback flow, reduced resolution, textured moving pixels with forward/backward consistency. Vector arrows 3x for readability. No object tracking, no cut classification, no proof of smoothness.'};write(out/'report.json',r);return r

def verify(video,creative,out,fps,n):
 try:
  r=json.loads((out/'report.json').read_text());expected=targets(creative,fps,n);errs=[]
  if r['video_sha256']!=sha(video) or r['fps']!=fps or r['frames']!=n:errs.append('flow source changed')
  if [(x['id'],x['center']) for x in r['results']]!=[(x['id'],x['center']) for x in expected]:errs.append('flow targets changed')
  for x in r['results']:
   f=out/f'flow-{x["id"]:03d}.png'
   if x['file']!=f.name or sha(f)!=x['sha256']:errs.append('flow sheet changed')
  return {'valid':not errs,'errors':errs}
 except (ValueError,TypeError,OSError,KeyError) as e:return {'valid':False,'errors':['flow evidence missing/invalid: '+str(e)]}
