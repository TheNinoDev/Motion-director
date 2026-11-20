#!/usr/bin/env python3
"""Convert an original text silhouette or mask into stable custom-layout points."""
import argparse,json,pathlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--text');g.add_argument('--mask',type=pathlib.Path);p.add_argument('--font',type=pathlib.Path);p.add_argument('--count',type=int,default=600);p.add_argument('--width',type=float,default=5);p.add_argument('--depth',type=float,default=.35);p.add_argument('--seed',type=int,default=12);p.add_argument('-o','--output',required=True,type=pathlib.Path);a=p.parse_args()
if not 1<=a.count<=10000 or a.width<=0 or a.depth<0:p.error('Invalid count or dimensions')
if a.text:
    if not a.font:p.error('--text requires --font')
    f=ImageFont.truetype(str(a.font),140);l,t,r,b=f.getbbox(a.text);im=Image.new('L',(r-l+8,b-t+8));ImageDraw.Draw(im).text((4-l,4-t),a.text,font=f,fill=255)
else:im=Image.open(a.mask).convert('L')
y,x=np.where(np.array(im)>127)
if not len(x):p.error('Mask empty: use white subject on black background')
rng=np.random.default_rng(a.seed);i=rng.choice(len(x),a.count,replace=a.count>len(x));scale=a.width/max(1,x.max()-x.min());pts=np.column_stack(((x[i]-(x.min()+x.max())/2)*scale,-(y[i]-(y.min()+y.max())/2)*scale,rng.uniform(-a.depth/2,a.depth/2,a.count)));pts=pts[np.argsort(pts[:,1],kind='stable')];a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(np.round(pts,5).tolist()));print(f'{len(pts)} points')
