#!/usr/bin/env python3
"""Offline real 3D signed-distance ray marcher. Original illustrative token, not a full ad.
Requires numpy, Pillow, ffmpeg. CPU only; use low resolution for animation tests.
"""
import argparse, math, subprocess, shutil
from pathlib import Path
import numpy as np
from PIL import Image

FLOOR=-.82

def unit(a): return a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), 1e-8)
def cyl(p,r,h,z):
    q=np.stack((np.linalg.norm(p[:,:2],axis=1)-r,np.abs(p[:,2]-z)-h),axis=1)
    return np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(np.max(q,axis=1),0)
def capsule(p,a,b,r):
    a=np.asarray(a,np.float32); b=np.asarray(b,np.float32); ab=b-a
    t=np.clip(((p-a)*ab).sum(1)/(ab@ab),0,1)
    return np.linalg.norm(p-a-t[:,None]*ab,axis=1)-r

def scene(p, material=False):
    radial=np.linalg.norm(p[:,:2],axis=1)
    body=cyl(p,.765,.105,0)-.045
    face=cyl(p,.655,.025,.138)-.009
    rim=np.sqrt((radial-.696)**2+(p[:,2]-.143)**2)-.026
    # Two rounded capsule strokes form an original abstract mark.
    mark=np.minimum(capsule(p,[-.28,-.04,.19],[.03,.27,.19],.045),capsule(p,[-.02,-.27,.19],[.29,.04,.19],.045))
    ds=np.stack((body,face,rim,mark),axis=1)
    return np.argmin(ds,axis=1) if material else ds.min(axis=1)

def trace(o,d):
    n=len(d); t=np.zeros(n,np.float32); hit=np.zeros(n,bool); active=np.arange(n)
    for _ in range(80):
        if not len(active): break
        s=scene(o[active]+d[active]*t[active,None]); close=s<.0012
        hit[active[close]]=True
        a=active[~close]; t[a]+=np.maximum(s[~close],.001)
        active=a[t[a]<9]
    return hit,t

def normal(p):
    e=.0015; eye=np.eye(3,dtype=np.float32)*e
    return unit(np.stack([scene(p+v)-scene(p-v) for v in eye],axis=1))

def env(r,phase):
    # Directional softbox reflections: broad gradients separated by negative fill.
    def box(direction,axis,w,h):
        center=unit(np.array(direction,np.float32)); u=unit(np.cross(center,np.array(axis,np.float32))); v=np.cross(u,center)
        c=np.maximum(r@center,0); x=(r@u)/np.maximum(c,.001); y=(r@v)/np.maximum(c,.001)
        return np.exp(-((x/w)**4+(y/h)**4))*c
    sweep=[math.sin(phase)*.55-.3,.75,.85]
    a=box(sweep,[0,1,0],.26,.95); b=box([.95,.25,-.45],[0,1,0],.18,1.55); c=box([-.6,-.15,.85],[0,1,0],.34,.45)
    front=box([-.36,.05,.94],[0,1,0],.32,.34)
    k=.008+1.8*a+1.15*b+.75*c+.85*front+.06*np.maximum(r[:,1],0)
    return k[:,None]*np.array([.96,.98,1.0],np.float32)[None,:]

def shade(p,d,phase):
    n=normal(p); r=unit(d-2*(d*n).sum(1)[:,None]*n); m=scene(p,True)
    refl=env(r,phase); diffuse=np.maximum(n@unit(np.array([-.4,.75,1],np.float32)),0)
    chrome=(m!=1); fres=(1-np.clip((-d*n).sum(1),0,1))**5
    out=refl*(.75+.25*fres[:,None])+.014*diffuse[:,None]
    out[~chrome]=.003+.014*diffuse[~chrome,None]+.09*refl[~chrome]+.035*fres[~chrome,None]
    return out

def render(w,h,t):
    ang=math.radians(32-24*t); cam=np.array([math.sin(ang)*4,.6+(.2*(1-t)),math.cos(ang)*4],np.float32)
    target=np.array([0,-.06,0],np.float32); f=unit(target-cam); right=unit(np.cross(f,[0,1,0])); up=unit(np.cross(right,f))
    x,y=np.meshgrid((np.arange(w)+.5-w/2)/h,(h/2-np.arange(h)-.5)/h)
    scale=3.2-.32*t
    o=(cam+x.reshape(-1,1)*right*scale+y.reshape(-1,1)*up*scale).astype(np.float32)
    d=np.broadcast_to(f,o.shape).astype(np.float32).copy(); hit,dist=trace(o,d)
    ft=(FLOOR-o[:,1])/np.minimum(d[:,1],-1e-6); floor=(ft>0)&((~hit)|(ft<dist))
    color=np.zeros((len(d),3),np.float32)+.00025
    if floor.any():
        idx=np.flatnonzero(floor); fp=o[idx]+d[idx]*ft[idx,None]; rd=d[idx].copy(); rd[:,1]*=-1; fp[:,1]+=.003
        rh,rt=trace(fp,rd); rgb=np.zeros((len(idx),3),np.float32)+.00045
        if rh.any():
            pp=fp[rh]+rd[rh]*rt[rh,None]; fade=np.exp(-rt[rh]*.65)
            rgb[rh]+=shade(pp,rd[rh],t*2.7)*fade[:,None]*.53
        color[idx]=rgb
    direct=hit&~floor
    if direct.any(): color[direct]=shade(o[direct]+d[direct]*dist[direct,None],d[direct],t*2.7)
    # Fixed display transfer, not auto-exposure. Keep blacks black and avoid clipping.
    color=np.power(np.clip(color/(1+color*.45),0,1),1/2.2)
    return Image.fromarray((color.reshape(h,w,3)*255+.5).astype(np.uint8),'RGB')

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--width',type=int,default=216); ap.add_argument('--height',type=int,default=384); ap.add_argument('--fps',type=int,default=30); ap.add_argument('--seconds',type=float,default=2); ap.add_argument('--still',action='store_true'); a=ap.parse_args()
    if min(a.width,a.height,a.fps,a.seconds)<=0 or a.width%2 or a.height%2: ap.error('positive values and even dimensions required')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if a.still: render(a.width,a.height,.55).save(a.out); return
    if not shutil.which('ffmpeg'): ap.error('ffmpeg required for MP4')
    n=max(1,round(a.fps*a.seconds)); cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{a.width}x{a.height}','-r',str(a.fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(a.out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(n): p.stdin.write(render(a.width,a.height,i/max(1,n-1)).tobytes())
    finally: p.stdin.close(); rc=p.wait()
    if rc: raise SystemExit(f'ffmpeg failed: {rc}')
if __name__=='__main__': main()
