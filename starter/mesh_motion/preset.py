#!/usr/bin/env python3
"""Generate an editable unified one-shot mesh plan, copying a supplied local asset."""
import argparse,json,shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('kind',choices=['ribbon','knot','sheet','obj']);p.add_argument('out',type=Path);p.add_argument('--asset',type=Path);p.add_argument('--material',choices=['chrome','satin','ceramic','ink','texture']);p.add_argument('--frames',type=int,default=60);p.add_argument('--crop',type=float,nargs=4);p.add_argument('--tint',default='#c9cddd');p.add_argument('--quality',type=float,default=.8);p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920);p.add_argument('--title',default='');a=p.parse_args()
 mat=a.material or ('texture' if a.kind=='sheet' and a.asset else 'chrome')
 c={'kind':a.kind,'material':mat,'tint':a.tint,'quality':a.quality,'resolution':96,'samples':1,'phase':[[0,0],[.78,1,'out'],[1,1]],'yaw':[[0,-.8],[.78,0,'out'],[1,0]],'pitch':[[0,.35],[1,0]],'roll':[[0,-.25],[1,0]],'zoom':[[0,1.35],[.78,1.02,'out'],[1,1.02]],'twist':[[0,1.6],[.78,0,'out'],[1,0]],'bend':[[0,1.8],[.78,0,'out'],[1,0]],'title':a.title,'bg':'#101112'}
 if mat=='texture' or a.kind=='obj':
  if not a.asset or not a.asset.is_file():p.error('local image or triangular OBJ required')
  target=a.out.parent/'assets'/('mesh-input'+a.asset.suffix.lower());target.parent.mkdir(parents=True,exist_ok=True)
  if target.resolve()!=a.asset.resolve():shutil.copy2(a.asset,target)
  c['src']=str(target.relative_to(a.out.parent))
 if a.crop:c['crop']=a.crop
 # validate before writing, retaining portable relative paths in final file
 from render import validate
 q=dict(c,frames=a.frames)
 if 'src' in q:q['src']=str(a.out.parent/q['src'])
 validate(q);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(dict(version=1,width=a.width,height=a.height,fps=30,shots=[dict(id='mesh',engine='mesh',frames=a.frames,content=c)]),indent=2))
if __name__=='__main__':main()
