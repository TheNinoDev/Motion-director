#!/usr/bin/env python3
"""Create an editable 4-shot draft with a product-specific transformation; no made-up marketing claims."""
import argparse,json,shutil
from pathlib import Path
from render import validate,SHAPES,MATS
STYLES={
 'consolidate':('tiles','chrome','rounded','stripe', '#d5f28b'),
 'unfold':('ribbon','anodized','diagonal','stack','#f0b47d'),
 'clarify':('cube','glass','iris','mono','#becaff'),
 'focus':('aperture','obsidian','iris','stack','#e3e8f2'),
 'connect':('capsules','ceramic','split','stripe','#c6e9df'),
}
def build(style,hook,words,proof,brand,cta,src,frames,accent=None,quality=.6,width=720,fps=30,material=None):
    if style not in STYLES:raise ValueError('unknown story style')
    if len(frames)!=4 or any(type(n) is not int or not 4<=n<=3600 for n in frames):raise ValueError('four shot lengths required')
    if not all(isinstance(x,str) and 0<len(x)<=100 for x in (hook,proof,brand,cta)):raise ValueError('provide verified copy')
    shape,mat,mask,layout,ac=STYLES[style];ac=accent or ac;mat=material or mat
    common=dict(bg='#0b0c10',fg='#f6f5f1',accent=ac,shape=shape,material=mat,quality=quality,roughness=.09,bloom=.075,grain=.45)
    def shot(i,id,**c):return dict(id=id,engine='fusion',frames=frames[i],content=c)
    d=dict(version=1,width=width,height=width*16//9,fps=fps,shots=[
      shot(0,'metaphor',**common,kind='morph',text=hook,phase=[[0,0],[.15,0],[1,1]],zoom=[[0,3.3],[1,1.8]],pitch=[[0,.5],[1,.12]],yaw=[[0,-.6],[1,0]],roll=[[0,.28],[1,0]],light=[[0,-.5],[1,.45]]),
      shot(1,'turn',kind='type',words=words,layout=layout,bg=ac,fg='#101216',accent='#101216',grain=.4),
      shot(2,'product',**common,kind='bridge',src=src,mask=mask,phase=1,zoom=[[0,1.8],[.3,2.7],[1,2.7]],pitch=.12,yaw=0,roll=0,light=.45,text=proof),
      shot(3,'brand',kind='lockup',brand=brand,sub=cta,accent=ac,grain=.4)])
    # src may be relative to the project. File existence is checked after copying, by production controller.
    for s in d['shots']:
        if s['id']!='product':validate(dict(s['content'],frames=s['frames']))
    return d
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--style',choices=STYLES,required=True);p.add_argument('--hook',required=True);p.add_argument('--word',action='append',required=True);p.add_argument('--proof',required=True);p.add_argument('--brand',required=True);p.add_argument('--cta',required=True);p.add_argument('--screenshot',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--frames',nargs=4,type=int,required=True);p.add_argument('--accent');p.add_argument('--quality',type=float,default=.6);p.add_argument('--width',type=int,choices=(540,720,1080),default=720);p.add_argument('--material',choices=MATS);a=p.parse_args()
    if not a.screenshot.is_file() or a.out.exists():p.error('valid screenshot and new output path required')
    dest=a.out.parent/(a.out.stem+'-assets')/('product'+a.screenshot.suffix.lower());dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():p.error('destination exists')
    d=build(a.style,a.hook,a.word,a.proof,a.brand,a.cta,str(dest.relative_to(a.out.parent)),a.frames,a.accent,a.quality,a.width,material=a.material)
    shutil.copy2(a.screenshot,dest);validate(dict(d['shots'][2]['content'],src=str(dest),frames=a.frames[2]))
    a.out.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8');print('Draft only. Attach verified VO/music and inspect render.',a.out)
