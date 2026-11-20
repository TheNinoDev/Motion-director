"""Extract actual before/during/after picture evidence for named events."""
import json
from pathlib import Path
import cv2
from PIL import Image,ImageDraw
from agent_session import sha,write

def targets(e,fps,n):
 out=[]
 for name,f in e['named_markers'].items():
  actions=[a for a in e['cue_actions'] if a['marker']==name];sounds=[s for s in e['named_sound_cues'] if s['target']==name]
  if not actions and not sounds:continue
  aa=[a['start_frame'] for a in actions]+[s['frame'] for s in sounds];bb=[a['end_frame'] for a in actions]+[s['frame']+s['duration_frames'] for s in sounds]
  anchors=[f-2,f,min(aa),max(bb),(min(aa)+max(bb))//2,max(bb)+3];frames=sorted({max(0,min(n-1,v)) for v in anchors})
  out.append({'id':name,'frame':f,'frames':frames,'actions':actions,'sounds':sounds})
 return out

def create(video,e,out,fps,n):
 if out.exists():raise ValueError('use a new cue review folder')
 original=sha(video);tt=targets(e,fps,n);wanted={f for r in tt for f in r['frames']};cache={};cap=cv2.VideoCapture(str(video))
 try:
  for i in range(max(wanted,default=-1)+1):
   ok,img=cap.read()
   if not ok:raise ValueError(f'preview decode stopped at {i}')
   if i in wanted:cache[i]=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)).resize((180,320),Image.Resampling.LANCZOS)
 finally:cap.release()
 out.mkdir(parents=True);rows=[]
 for j,r in enumerate(tt):
  f=out/f'cue-{j:03d}.png';im=Image.new('RGB',(180*len(r['frames']),368),'#151c24');d=ImageDraw.Draw(im)
  d.text((8,8),f'{r["id"]}  |  {len(r["actions"])} actions, {len(r["sounds"])} sounds',fill='white')
  for k,frame in enumerate(r['frames']):
   im.paste(cache[frame],(k*180,23));d.text((k*180+6,349),f'{frame/fps:.3f}s / {frame}',fill='white')
  im.save(f);rows.append({**r,'file':f.name,'sha256':sha(f)})
 if sha(video)!=original:raise ValueError('preview changed')
 report={'video_sha256':original,'fps':fps,'frames':n,'results':rows,'note':'Sampled pictures only. Watch actual playback and listen; a sheet does not verify sound or intent.'};write(out/'report.json',report);return report

def verify(video,e,out,fps,n):
 try:
  r=json.loads((out/'report.json').read_text());err=[];tt=targets(e,fps,n)
  if r['video_sha256']!=sha(video) or r['fps']!=fps or r['frames']!=n:err.append('cue report belongs to different video/timing')
  if len(r['results'])!=len(tt):err.append('missing/extra cue rows')
  for j,(a,b) in enumerate(zip(r['results'],tt)):
   f=out/f'cue-{j:03d}.png'
   if any(a[k]!=v for k,v in b.items()) or a['file']!=f.name or sha(f)!=a['sha256']:err.append('changed cue evidence '+b['id'])
  return {'valid':not err,'errors':err}
 except (OSError,KeyError,ValueError,TypeError,AttributeError) as ex:return {'valid':False,'errors':['cue evidence invalid: '+str(ex)]}
