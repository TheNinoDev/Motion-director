#!/usr/bin/env python3
"""Validate exact frame coverage and declared shot attributes, not creative quality."""
import argparse,json,sys,math
from pathlib import Path

def check(p):
 e=[];w=[];prev=0;ids=set();families=[];prev_shot=None
 fps=p.get('fps'); total=p.get('total_frames'); shots=p.get('shots',[])
 if type(fps) is not int or fps<=0:e.append('fps must be positive integer')
 if type(total) is not int or total<=0:e.append('total_frames must be positive integer')
 if not isinstance(shots,list) or not shots:return e+['shots must be nonempty list'],w
 for s in shots:
  name=s.get('id'); a=s.get('start_frame');b=s.get('end_frame')
  if not name or name in ids:e.append(f'duplicate/missing id: {name}')
  ids.add(name)
  if type(a) is not int or type(b) is not int or a<0 or b<=a:e.append(f'{name}: invalid frame range');continue
  if a!=prev:e.append(f'{name}: expected start {prev}, got {a}')
  prev=b;families.append(s.get('family'))
  for k in ('family','purpose','focus','entry','exit','audio_cue','bridge_type'):
   if not s.get(k):e.append(f'{name}: missing {k}')
  for k in ('anchor_in','anchor_out'):
   v=s.get(k)
   if not isinstance(v,list) or len(v)!=2 or not all(type(x) in (int,float) and math.isfinite(x) and 0<=x<=1 for x in v):e.append(f'{name}: invalid {k}')
  if prev_shot and s.get('bridge_type')=='shared' and s.get('anchor_in')!=prev_shot.get('anchor_out'):e.append(f'{name}: shared anchor mismatch')
  motions=s.get('motion',[])
  if not motions and not s.get('intentional_hold'):e.append(f'{name}: needs motion or explicit intentional hold')
  for motion in motions:
   if not motion.get('object') or not motion.get('property') or not motion.get('easing'):e.append(f'{name}: incomplete motion')
   keys=motion.get('keyframes',[]);last=a-1
   if len(keys)<2:e.append(f'{name}: need at least two keyframes')
   for k in keys:
    f=k.get('frame')
    if type(f) is not int or not a<=f<=b or f<=last or 'value' not in k:e.append(f'{name}: invalid/non-increasing keyframe');continue
    last=f
  prev_shot=s
 if prev!=total:e.append(f'coverage {prev} != {total}')
 if len(shots)>=4 and len(set(families))<3:w.append('Low variety: inspect editorial intent')
 return e,w
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('file',type=Path);a=ap.parse_args()
 try:e,w=check(json.loads(a.file.read_text(encoding='utf8')))
 except (OSError,ValueError,TypeError,AttributeError) as x:e,w=[str(x)],[]
 print(json.dumps({'valid':not e,'errors':e,'warnings':w},indent=2));sys.exit(bool(e))
