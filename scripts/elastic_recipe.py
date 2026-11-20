#!/usr/bin/env python3
"""Generate a validated, editable compositor plan: useful starting motions, not a fixed ad."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'starter'));sys.path.insert(0,str(ROOT/'starter/composite_film'))
import softbody
from compositor import validate
from volume import SHAPES,PRESETS
RECIPES={
 'bounce':[('squash',0,.95),('bend',.055,.23)],
 'pop':[('squash',0,-.7),('twist',.08,.18)],
 'wobble':[('bend',0,.65),('twist',.05,.45),('squash',.10,.32)],
 'settle':[('squash',0,.55),('bend',.04,.18)],
}
def build(recipe='bounce',preset='jelly',geometry='ellipsoid',material='ceramic',color='#ac89ff',strength=1.,duration=3.,impact=1.):
 if recipe not in RECIPES or preset not in softbody.PRESETS or geometry not in SHAPES or material not in PRESETS:raise ValueError('unknown recipe/preset/geometry/material')
 if not 0<strength<=1 or not .3<=impact<=duration-.5 or not 1<=duration<=30:raise ValueError('strength or timing invalid')
 events=[dict(mode=m,time=round(impact+dt,5),strength=a*strength) for m,dt,a in RECIPES[recipe]]
 hero=dict(id='hero',kind='object3d',geometry=geometry,material=material,color=color,w=350,h=350,depth=350,x=360,y=[[0,550],[impact,720,'in'],[impact+.24,635,'out'],[min(duration,impact+.6),660,'smooth']] if recipe=='bounce' else 640,active=[0,duration],yaw=[[0,-20],[duration,18,'sine']],pitch=7,light=[[0,.2],[duration,.75,'sine']],quality=1,antialias=1.5,softbody=dict(preset=preset,events=events))
 # This is stylized motion, not a collision solver. No wall/floor drawn.
 return dict(version=1,width=720,height=1280,fps=30,duration=duration,background='#171a23',grain=0,review_times=[0,impact,min(duration-.01,impact+.08),min(duration-.01,impact+.25),duration-.04],layers=[hero])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--recipe',choices=RECIPES,default='bounce');ap.add_argument('--preset',choices=softbody.PRESETS,default='jelly');ap.add_argument('--geometry',choices=SHAPES,default='ellipsoid');ap.add_argument('--material',choices=PRESETS,default='ceramic');ap.add_argument('--color',default='#ac89ff');ap.add_argument('--strength',type=float,default=1);ap.add_argument('--duration',type=float,default=3);ap.add_argument('--impact',type=float,default=1);a=ap.parse_args();p=build(a.recipe,a.preset,a.geometry,a.material,a.color,a.strength,a.duration,a.impact);validate(p,a.output.parent);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(p,indent=2)+'\n');print(a.output)
if __name__=='__main__':main()
