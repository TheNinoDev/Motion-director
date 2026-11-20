#!/usr/bin/env python3
"""Sample authorized image mask into deterministic XYZ points for custom layouts."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image

def points(path,count,extent=5,seed=123,thickness=.15,channel='alpha'):
    im=Image.open(path).convert('RGBA'); a=np.asarray(im); mask=(a[:,:,3] if channel=='alpha' else np.asarray(im.convert('L')))>127
    ys,xs=np.nonzero(mask)
    if not len(xs):raise ValueError('Mask has no foreground')
    if channel=='alpha' and np.all(mask):raise ValueError('Alpha is fully opaque; use a transparent mask or --channel luma for white-on-black')
    rng=np.random.default_rng(seed); ids=rng.choice(len(xs),count,replace=count>len(xs)); x=xs[ids];y=ys[ids];h,w=mask.shape;scale=extent/max(w,h)
    return np.column_stack(((x-(w-1)/2)*scale,((h-1)/2-y)*scale,rng.uniform(-thickness/2,thickness/2,count))).round(5).tolist()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('image',type=Path);p.add_argument('output',type=Path);p.add_argument('--count',type=int,default=480);p.add_argument('--extent',type=float,default=5);p.add_argument('--seed',type=int,default=123);p.add_argument('--channel',choices=['alpha','luma'],default='alpha');a=p.parse_args()
    if not 1<=a.count<=10000 or not 0<a.extent<=100: p.error('invalid count or extent')
    a.output.write_text(json.dumps(points(a.image,a.count,a.extent,a.seed,channel=a.channel)));print(f'{a.count} custom points; paste array into scene points field')
