#!/usr/bin/env python3
"""Build an editable studio story scaffold using a supplied verified product screenshot and copy.
No invented product features. Draft timing only unless caller supplies verified frame lengths.
"""
import argparse,json,shutil
from pathlib import Path

STYLES={
 'fragmentation':dict(shape='links',material='chrome',layout='cascade',bg='#e8e8df',fg='#111315',second='ring',accent='#c9f381'),
 'discovery':dict(shape='wave',material='ceramic',layout='stack',bg='#111019',fg='#f2edf9',second='rounded',accent='#bdb5f5'),
 'precision':dict(shape='rounded',material='chrome',layout='carousel',bg='#efeee9',fg='#18191b',second='ring',accent='#9fd7f0')}

def build(style,hook,words,proof,brand,cta,src,frames,accent=None,width=1080,height=1920,fps=30):
    if style not in STYLES:raise ValueError('unknown style')
    if len(frames)!=5 or any(type(n) is not int or not 4<=n<=3600 for n in frames):raise ValueError('five valid shot lengths needed')
    if not all(isinstance(x,str) and 1<=len(x)<=160 for x in (hook,proof,brand,cta)):raise ValueError('supply real hook, proof, brand, CTA')
    if not 1<=len(words)<=5 or not all(isinstance(x,str) and 1<=len(x)<=30 for x in words):raise ValueError('supply 1–5 short story phrases')
    z=STYLES[style];ac=accent or z['accent'];quality=1.0
    if not src:raise ValueError('verified screenshot path needed')
    def shot(i,k,**content):return {'id':k,'engine':'studio','frames':frames[i],'content':content}
    return {'version':1,'width':width,'height':height,'fps':fps,'shots':[
      shot(0,'hook',kind='hero',shape=z['shape'],material=z['material'],quality=quality,roughness=.07,accent=ac,text=hook,contrast_scrim=.83,zoom=[[0,5.2],[.35,4.5],[1,2.3]],pitch=[[0,.10],[1,.42]],yaw=[[0,-.45],[1,.2]],light=[[0,-.4],[1,.45]],bloom=.06),
      shot(1,'turn',kind='kinetic',words=words,layout=z['layout'],bg=z['bg'],fg=z['fg'],accent=ac),
      shot(2,'proof',kind='proof',src=src,text=proof,accent=ac),
      shot(3,'callback',kind='hero',shape=z['second'],material='tinted',accent=ac,quality=quality,roughness=.12,zoom=[[0,1.7],[1,2.6]],pitch=[[0,.5],[1,.18]],yaw=[[0,-.3],[1,.1]],light=[[0,.6],[1,-.3]],bloom=.05),
      shot(4,'brand',kind='lockup',brand=brand,sub=cta,accent=ac)]}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--style',choices=STYLES,required=True);p.add_argument('--hook',required=True);p.add_argument('--word',action='append',required=True);p.add_argument('--proof',required=True);p.add_argument('--brand',required=True);p.add_argument('--cta',required=True);p.add_argument('--screenshot',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--frames',nargs=5,type=int,default=[45,39,75,42,60]);p.add_argument('--accent');p.add_argument('--preview-resolution',action='store_true');a=p.parse_args()
    if not a.screenshot.is_file():p.error('screenshot does not exist')
    if a.out.exists():p.error('choose a new project file; no overwrites')
    a.out.parent.mkdir(parents=True,exist_ok=True);dest=a.out.parent/(a.out.stem+'-assets')/('product'+a.screenshot.suffix.lower());dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():p.error('asset destination already exists')
    wh=(720,1280) if a.preview_resolution else (1080,1920)
    d=build(a.style,a.hook,a.word,a.proof,a.brand,a.cta,str(dest.relative_to(a.out.parent)),a.frames,a.accent,*wh)
    shutil.copy2(a.screenshot,dest);a.out.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    print('DRAFT: attach real audio and adapt exact shot timings before final:',a.out)
if __name__=='__main__':main()
