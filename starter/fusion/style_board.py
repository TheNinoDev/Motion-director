#!/usr/bin/env python3
"""Generate a real rendered candidate board, NOT fabricated aesthetic scores."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from render import Fusion,SHAPES,MATS

def board(out,font,shape,materials,phases=(0,.5,1),width=180):
    height=width*16//9;gap=12;label=28;col=len(phases);row=len(materials)
    img=Image.new('RGB',(gap+col*(width+gap),gap+row*(height+label+gap)),(20,22,25));d=ImageDraw.Draw(img);f=ImageFont.truetype(font,13)
    for y,mat in enumerate(materials):
        for x,phase in enumerate(phases):
            config=dict(kind='morph',frames=16,shape=shape,material=mat,phase=phase,pitch=.25,yaw=.25,roll=.05,zoom=1.55,quality=.65,samples=1,grain=0,roughness=.085,tint='#c7d5fc',bloom=.08)
            im=Image.fromarray(Fusion(width,height,config,font).frame(7));xx=gap+x*(width+gap);yy=gap+y*(height+label+gap);img.paste(im,(xx,yy));d.text((xx,yy+height+5),f'{mat} / {phase:.1f}',font=f,fill='white')
    out.parent.mkdir(parents=True,exist_ok=True);img.save(out)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--font',required=True);p.add_argument('--shape',choices=SHAPES,default='tiles');p.add_argument('--material',action='append',choices=MATS);a=p.parse_args();board(a.output,a.font,a.shape,a.material or ['chrome','glass','ceramic'])
