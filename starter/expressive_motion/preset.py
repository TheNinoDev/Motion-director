#!/usr/bin/env python3
"""Generate validated frame plans for common shots; no hand coding required."""
import argparse,json,pathlib,os
from render import validate,POSES
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('kind',choices=['reaction','masked-title','dot-title','wireframe','contrast']);p.add_argument('output',type=P);p.add_argument('--seconds',type=float,default=3);p.add_argument('--fps',type=int,default=30);p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920);p.add_argument('--text');p.add_argument('--color',default='#f6f4fa');p.add_argument('--background',default='#101018');p.add_argument('--character-color',default='#a384ed');p.add_argument('--image',type=P);p.add_argument('--boxes',type=P,help='JSON list of normalized [x0,y0,x1,y1] rectangles for real screenshot');a=p.parse_args();n=round(a.seconds*a.fps)
if n<12:p.error('at least 12 frames required')
s={'frames':n,'background':a.background,'color':a.color}
def keys(seq):
    return [[i,v] for i,v in sorted({round(t*(n-1)):v for t,v in seq}.items())]
if a.kind=='reaction':s.update(kind='character',character_color=a.character_color,poses=keys([(0,'curious'),(.15,'smirk'),(.35,'grin'),(.48,'grin'),(.53,'surprised'),(.60,'neutral'),(1,'neutral')]),zoom=keys([(0,.85),(.35,1.2),(.48,1.6),(.58,1),(1,1)]),squash=keys([(0,1),(.25,.9),(.35,1.12),(.46,1),(.55,.92),(.65,1)]))
elif a.kind=='wireframe':
    if not a.image or not a.boxes:p.error('--image and --boxes required')
    s.update(kind='wireframe',src=os.path.relpath(a.image.resolve(),a.output.resolve().parent),boxes=json.loads(a.boxes.read_text()))
else:
    if not a.text:p.error('--text required')
    s.update(kind={'masked-title':'type','dot-title':'dots','contrast':'hold'}[a.kind],text=a.text)
    if a.kind=='masked-title':s['reveal_frames']=max(1,min(n-1,round(a.fps*.33)))
d={'width':a.width,'height':a.height,'fps':a.fps,'shots':[s]};validate(d,a.output.resolve().parent);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2));print(a.output)
