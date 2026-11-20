"""Reusable, deterministic 2D effects for the Layer Motion renderer.
No external assets or UI. Dynamic layers are built once, sampled at fractional frames.
"""
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SHAPES={'circle','square','diamond','star','ring','cross','text'}
LAYOUTS={'grid','ring','scatter','text','spiral'}

def shape_mask(name,w,h,text,fontpath):
    im=Image.new('L',(w,h));d=ImageDraw.Draw(im);cx=w/2;cy=h/2;r=min(w,h)*.40
    if name=='text':
        f=ImageFont.truetype(fontpath,max(8,int(min(w,h)*.8)))
        while True:
            b=d.textbbox((0,0),text,font=f)
            if b[2]-b[0]<=w*.86 and b[3]-b[1]<=h*.86 or f.size<=8:break
            f=ImageFont.truetype(fontpath,max(8,int(f.size*.9)))
        d.text((cx-(b[0]+b[2])/2,cy-(b[1]+b[3])/2),text,font=f,fill=255)
    elif name in ('circle','ring'):
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=255)
        if name=='ring':d.ellipse((cx-r*.66,cy-r*.66,cx+r*.66,cy+r*.66),fill=0)
    elif name=='square':d.rounded_rectangle((cx-r,cy-r,cx+r,cy+r),radius=max(1,int(r*.16)),fill=255)
    elif name=='cross':
        d.rounded_rectangle((cx-r*.30,cy-r,cx+r*.30,cy+r),radius=max(1,int(r*.12)),fill=255);d.rounded_rectangle((cx-r,cy-r*.30,cx+r,cy+r*.30),radius=max(1,int(r*.12)),fill=255)
    elif name in ('diamond','star'):
        n=4 if name=='diamond' else 10
        d.polygon([(cx+r*(.44 if name=='star' and i%2 else 1)*math.cos(i*math.tau/n-math.pi/2),cy+r*(.44 if name=='star' and i%2 else 1)*math.sin(i*math.tau/n-math.pi/2)) for i in range(n)],fill=255)
    else:raise ValueError('unknown shape '+name)
    return np.asarray(im)

def sdf(mask):
    m=(mask>127).astype(np.uint8)
    if not m.any() or m.all():raise ValueError('shape must have nonempty inside and outside')
    return cv2.distanceTransform(m,cv2.DIST_L2,5)-cv2.distanceTransform(1-m,cv2.DIST_L2,5)

def layout(name,n,w,h,seed,text,fontpath):
    rng=np.random.default_rng(seed);i=np.arange(n);u=(i+.5)/n;theta=i*math.tau/n
    if name=='ring':p=np.c_[.5+.36*np.cos(theta),.5+.36*np.sin(theta)]
    elif name=='spiral':p=np.c_[.5+.43*u*np.cos(u*math.tau*3),.5+.43*u*np.sin(u*math.tau*3)]
    elif name=='grid':
        cols=math.ceil(math.sqrt(n));rows=math.ceil(n/cols);p=np.c_[.12+.76*((i%cols+.5)/cols),.12+.76*((i//cols+.5)/rows)]
    elif name=='scatter':p=rng.uniform(.06,.94,(n,2))
    elif name=='text':
        yy,xx=np.where(shape_mask('text',w,h,text,fontpath)>127)
        if len(xx)<1:raise ValueError('empty text particle target')
        k=rng.choice(len(xx),n,replace=len(xx)<n);p=np.c_[xx[k]/w,yy[k]/h]
    else:raise ValueError('unknown layout '+name)
    # Stable angular order reduces random crossings without reassigning identities mid-flight.
    order=np.argsort(np.arctan2(p[:,1]-.5,p[:,0]-.5)+.025*np.linalg.norm(p-.5,axis=1));return p[order]

def validate_dynamic(l):
    k=l['kind']
    if k not in ('morph','swarm'):return
    names=SHAPES if k=='morph' else LAYOUTS
    if l.get('from') not in names or l.get('to') not in names:raise ValueError('invalid dynamic shape/layout')
    if not isinstance(l.get('text','X'),str) or not 1<=len(l.get('text','X'))<=18:raise ValueError('dynamic text must be 1..18 chars')
    if k=='swarm' and (type(l.get('count',300)) is not int or not 8<=l.get('count',300)<=1500):raise ValueError('swarm count must be 8..1500')
    for key,lo,hi in [('edge',.1,8),('outline',0,50),('dot',1,30),('arc',0,.5),('drag',0,1),('scatter',0,.5)]:
        if key in l and (type(l[key]) not in (float,int) or not math.isfinite(l[key]) or not lo<=l[key]<=hi):raise ValueError('bad '+key)

class Dynamic:
    def __init__(self,l,s,fontpath,color):
        self.l=l;self.s=s;self.w,self.h=[max(2,round(x*s)) for x in l['size']];self.color=color;self.kind=l['kind'];self.n=l.get('count',300);t=l.get('text','X');fp=l.get('font',fontpath)
        if self.kind=='morph':
            self.a=sdf(shape_mask(l['from'],self.w,self.h,l.get('from_text',t),fp));self.b=sdf(shape_mask(l['to'],self.w,self.h,t,fp))
        else:
            self.a=layout(l['from'],self.n,self.w,self.h,l.get('seed',13),l.get('from_text',t),fp);self.b=layout(l['to'],self.n,self.w,self.h,l.get('seed',13)+1,t,fp)
            rng=np.random.default_rng(l.get('seed',13));self.noise=rng.uniform(-1,1,(self.n,2));self.radius=rng.uniform(.65,1.25,self.n)
    def sample(self,p):
        p=float(np.clip(p,0,1));l=self.l;w,h=self.w,self.h;c=self.color
        out=np.zeros((h,w,4),np.uint8);out[:,:,:3]=c[:3]
        if self.kind=='morph':
            dist=(1-p)*self.a+p*self.b;soft=max(.5,l.get('edge',1.3)*self.s);border=l.get('outline',0)*self.s
            if border:dist=border/2-np.abs(dist)
            out[:,:,3]=np.uint8(np.clip(.5+dist/soft,0,1)*c[3])
        else:
            # Analytic particle trajectories with persistent IDs, damped arc and deterministic noise.
            q=p*p*(3-2*p);v=self.b-self.a;normal=np.c_[-v[:,1],v[:,0]];arc=math.sin(math.pi*p)*(1-l.get('drag',.25)*p)
            points=self.a+v*q+normal*(l.get('arc',.25)*arc)+self.noise*(l.get('scatter',.07)*arc)
            mask=np.zeros((h,w),np.uint8)
            for j,(x,y) in enumerate(points):
                r=max(1,round(l.get('dot',5)*self.s*self.radius[j]));cv2.circle(mask,(round(x*w),round(y*h)),r,int(c[3]),-1,cv2.LINE_AA)
            out[:,:,3]=mask
        return out

# sRGB transfer for actual scene samples; do not blend across edit boundaries.
_srgb=np.arange(256,dtype=np.float32)/255
LINEAR=np.where(_srgb<=.04045,_srgb/12.92,((_srgb+.055)/1.055)**2.4)
def shutter(frame,f,n,samples,amount):
    if samples==1 or amount==0:return frame(f)
    offsets=((np.arange(samples)+.5)/samples-.5)*amount
    acc=None
    for off in offsets:
        im=LINEAR[frame(float(np.clip(f+off,0,n-1)))];acc=im if acc is None else acc+im
    lin=acc/samples;sr=np.where(lin<=.0031308,12.92*lin,1.055*np.power(lin,1/2.4)-.055)
    return np.uint8(np.clip(sr*255+.5,0,255))
