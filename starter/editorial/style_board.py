#!/usr/bin/env python3
"""Render candidates from the actual project, not from fixed example text."""
import argparse,copy,json,sys
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.append(str(Path(__file__).resolve().parents[1]/'unified'))
import production
from render import Editorial

def main():
 p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('shot');p.add_argument('out',type=Path);a=p.parse_args();pr,d,font,_=production.validate(a.project);s=next((s for s in d['shots'] if s['id']==a.shot),None)
 if not s or s['engine']!='editorial':p.error('choose an editorial shot ID')
 c=dict(production.resolve_assets(s['content'],pr.parent),frames=s['frames']);kind=c['kind'];variants=[]
 if kind in ('wall','poster'):
  variants=[('left / slice',dict(layout='left',reveal='slice')),('center / stagger',dict(layout='center',reveal='glyph')),('right / wipe',dict(layout='right',reveal='wipe')),('left / opacity',dict(layout='left',reveal='none'))]
 elif kind=='fold':variants=[('subtle',dict(bend=[[0,.5],[1,0]],yaw=[[0,.35],[1,0]],shine=.1)),('curved',dict(bend=[[0,1.3],[1,0]],yaw=[[0,.8],[1,0]],shine=.24)),('reverse',dict(bend=[[0,-1.2],[1,0]],yaw=[[0,-.7],[1,0]],shine=.12)),('flat',dict(bend=0,yaw=0,pitch=0,shine=0))]
 elif kind=='shutter':variants=[(f'{n} slats',dict(density=n)) for n in (3,5,8,12)]
 elif kind in ('macro','aperture'):variants=[('original',{}),('close-to-wide',dict(zoom=[[0,1.2],[1,1]])),('wide-to-close',dict(zoom=[[0,.8],[1,1]])),('quick reveal',dict(progress=[[0,0],[.5,1,'out'],[1,1]]))]
 else:variants=[('original',{}),('quiet',dict(grain=0)),('early land',dict(progress=[[0,0],[.3,1,'out'],[1,1]])),('later land',dict(progress=[[0,0],[.8,1,'smooth'],[1,1]]))]
 w,h=225,400;board=Image.new('RGB',(w*3,len(variants)*(h+30)),(15,15,16));draw=ImageDraw.Draw(board)
 for j,(label,patch) in enumerate(variants):
  sh=Editorial(w,h,dict(c,**patch),font)
  for i,t in enumerate((.2,.5,.95)):
   f=round(t*(sh.n-1));board.paste(Image.fromarray(sh.frame(f)),(w*i,j*(h+30)));draw.text((w*i+8,j*(h+30)+h+6),f'{label} / {round(t*100)}%',fill='white')
 board.save(a.out,quality=93);a.out.with_suffix('.json').write_text(json.dumps([{'label':l,'content_patch':p} for l,p in variants],indent=2));print('Compare actual candidate frames; choose a patch only after review.')
if __name__=='__main__':main()
