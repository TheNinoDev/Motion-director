#!/usr/bin/env python3
"""Render actual material/deformation candidates, never an automated aesthetic rating."""
import argparse,copy,json
from pathlib import Path
from PIL import Image,ImageDraw
from render import MeshMotion

def main():
 p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('out',type=Path);p.add_argument('--font',required=True);p.add_argument('--shot',default='ribbon');a=p.parse_args();d=json.loads(a.project.read_text());s=next(v for v in d['shots'] if v['id']==a.shot);c=dict(s['content'],frames=s['frames']);assert s['engine']=='mesh';
 if 'src' in c:c['src']=str((a.project.parent/c['src']).resolve())
 board=Image.new('RGB',(4*200,3*380),'#151619');dr=ImageDraw.Draw(board)
 options=[('original',{}),('soft studio',{'roughness':.42,'light':.25}),('high contrast',{'roughness':.12,'light':-1.5}),('different angle',{'yaw':.55,'pitch':-.45})] if c.get('material')!='texture' else [('original',{}),('gentler curve',{'bend':[[0,.95],[1,0]]}),('different angle',{'yaw':[[0,.75],[1,0]]}),('closer landing',{'zoom':[[0,1.2],[1,1.08]]})]
 for j,(name,v) in enumerate(options):
  sh=MeshMotion(192,342,dict(c,**v),a.font)
  for i,t in enumerate((0,.45,1)):
   im=Image.fromarray(sh.frame(round(t*(c['frames']-1))));board.paste(im,(j*200,i*380));dr.text((j*200+4,i*380+345),f'{name} / {t:.0%}',fill='white')
 a.out.parent.mkdir(parents=True,exist_ok=True);board.save(a.out,quality=93)
if __name__=='__main__':main()
