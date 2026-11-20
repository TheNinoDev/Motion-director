#!/usr/bin/env python3
"""Deterministic CPU material studies. Height-field bevels and analytic studio reflection, not full path tracing."""
import argparse, json, math, subprocess, sys
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

def smooth(x):
    x=np.clip(x,0,1); return x*x*(3-2*x)
def srgb(x): return np.where(x<=.0031308,12.92*x,1.055*np.maximum(x,0)**(1/2.4)-.055)
def linear(x): return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
def rgb8(x): return np.uint8(np.clip(srgb(np.maximum(x,0)),0,1)*255+.5)
def normalize(v): return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-6)
def gaussian(a,s): return cv2.GaussianBlur(a,(0,0),s) if s>.15 else a

def validate(p):
    for k,lo,hi in [('width',160,2160),('height',160,3840),('fps',1,60)]:
        if type(p.get(k)) is not int or not lo<=p[k]<=hi: raise ValueError('Invalid '+k)
    if p['width']%2 or p['height']%2: raise ValueError('Even dimensions required')
    if not isinstance(p.get('shots'),list) or not p['shots']: raise ValueError('No shots')
    for s in p['shots']:
        if s.get('kind') not in ('metal','macro','focus','emissive','portal'): raise ValueError('Unknown shot kind')
        if type(s.get('frames')) is not int or not 1<=s['frames']<=3600: raise ValueError('Invalid length')
        if not isinstance(s.get('text'),str) or not 1<=len(s['text'].strip())<=24: raise ValueError('Text required, 1–24 characters')
        for key,low,high in [('roughness',.06,.85),('bloom',0,.5),('reflection',0,.65),('bevel',.01,.20),('shutter',0,1)]:
            v=s.get(key,(low+high)/2)
            if not isinstance(v,(int,float)) or not math.isfinite(v) or not low<=v<=high: raise ValueError('Bad '+key)
        if not isinstance(s.get('caption',''),str) or len(s.get('caption',''))>100: raise ValueError('Caption too long')
    if sum(s['frames'] for s in p['shots'])>18000: raise ValueError('Plan too long')
    return p

class Studio:
    def __init__(self,w,h,font):
        self.w,self.h,self.font=w,h,font; yy,xx=np.mgrid[:h,:w].astype(np.float32); self.X=xx; self.Y=yy
        self.bg=np.repeat((.002+.005*np.exp(-(((xx-w*.5)/(w*.5))**2+((yy-h*.46)/(h*.45))**2)))[...,None],3,axis=2)
        self.cache={}
    def geometry(self,text,bevel):
        key=(text,bevel)
        if key in self.cache:return self.cache[key]
        size=440; f=ImageFont.truetype(self.font,size); b=f.getbbox(text); w=b[2]-b[0];h=b[3]-b[1]
        if w>850:
            size=max(12,int(size*850/w));f=ImageFont.truetype(self.font,size);b=f.getbbox(text);w=b[2]-b[0];h=b[3]-b[1]
        pad=12; im=Image.new('L',(w+2*pad,h+2*pad)); ImageDraw.Draw(im).text((pad-b[0],pad-b[1]),text,font=f,fill=255)
        a=np.asarray(im,np.float32)/255; d=cv2.distanceTransform(np.uint8(a>.5),cv2.DIST_L2,5); r=max(2,h*bevel); z=np.sqrt(np.maximum(0,1-(1-np.clip(d/r,0,1))**2))*r
        z=gaussian(z,1.35); gy,gx=np.gradient(z); n=normalize(np.stack([-gx,-gy,np.ones_like(z)],-1)); yy,xx=np.mgrid[:a.shape[0],:a.shape[1]].astype(np.float32)
        V=normalize(np.stack([(a.shape[1]/2-xx)/max(h*2,1),(a.shape[0]/2-yy)/max(h*2,1),np.ones_like(z)],-1)); R=2*np.sum(n*V,axis=-1,keepdims=True)*n-V
        self.cache[key]=(a,R,np.sum(n*V,axis=-1)); return self.cache[key]
    def material(self,s,t):
        a,R,nv=self.geometry(s['text'],s.get('bevel',.065)); r=s.get('roughness',.18); angle=(t-.5)*2.3
        # broad softboxes in reflection direction; negative fill between strips; edge fresnel
        x=R[...,0]*np.cos(angle)+R[...,2]*np.sin(angle); y=R[...,1]; z=R[...,2]*np.cos(angle)-R[...,0]*np.sin(angle)
        band=np.exp(-((y-.30-.20*x)/(.09+r*.65))**4)*(.28+.72*smooth((z+.35)/.7)); strip=np.exp(-((x+.72)/(.035+r*.22))**2)*smooth((y+.7)/.5); fill=np.exp(-((y+.60)/(.15+r*.55))**2)*.22
        inten=.009+band*.83+strip*.52+fill+.09*(1-np.clip(nv,0,1))**3
        if s['kind']=='emissive': inten=np.full_like(inten,1.1)
        col=np.stack([inten*.93,inten*.97,inten*1.04],-1).astype(np.float32)
        return np.dstack([col*a[...,None],a]).astype(np.float32)
    def layer(self,canvas,rgba,cx,cy,width,blur=0,flip=False,opacity=1):
        H,W=rgba.shape[:2]; scale=width/W; th=max(1,int(H*scale)); tw=max(1,int(width)); x=int(round(cx-tw/2));y=int(round(cy-th/2)); arr=cv2.resize(rgba,(tw,th),interpolation=cv2.INTER_LINEAR if scale>1 else cv2.INTER_AREA)
        if flip:
            arr=arr[::-1].copy();arr*=np.exp(-np.arange(th,dtype=np.float32)[:,None,None]/max(1,th*.34))
        # Pad before blur so alpha feather is not clipped at the layer boundary.
        if blur>.15:
            pad=int(math.ceil(3*blur));arr=np.pad(arr,((pad,pad),(pad,pad),(0,0)));arr=gaussian(arr,blur);x-=pad;y-=pad;th,tw=arr.shape[:2]
        x0=max(0,x);y0=max(0,y);x1=min(self.w,x+tw);y1=min(self.h,y+th)
        if x1<=x0 or y1<=y0:return
        a=arr[y0-y:y1-y,x0-x:x1-x]*opacity; dst=canvas[y0:y1,x0:x1];dst[:]=a[:,:,:3]+dst*(1-a[:,:,3:4])
    def text(self,im,text,y,size,fill=235):
        if not text:return im
        f=ImageFont.truetype(self.font,max(10,int(self.w*size))); b=f.getbbox(text)
        if b[2]-b[0]>self.w*.84: f=ImageFont.truetype(self.font,max(10,int(self.w*size*self.w*.84/(b[2]-b[0]))));b=f.getbbox(text)
        ImageDraw.Draw(im).text(((self.w-b[2]+b[0])/2-b[0],y-(b[3]-b[1])/2-b[1]),text,font=f,fill=(fill,fill,fill));return im
    def sample(self,s,t):
        w,h=self.w,self.h; k=s['kind']; a=self.material(s,t); canvas=self.bg.copy(); q=float(smooth(t)); cx=w*.5;cy=h*.43; width=w*.78; blur=0
        if k=='macro': width=w*(1.9-1.12*q);cx=w*(.75-.25*q)
        if k=='focus': width=w*1.05;cy=h*.35;blur=w*.018
        if k=='portal': width=w*(.76+1.75*q);cx=w*(.5+.12*q)
        th=a.shape[0]*width/a.shape[1]; floor=cy+th*.46
        if k=='metal':
            shadow=np.exp(-((self.X-cx)/(w*.30))**2-((self.Y-floor)/(h*.014))**2);canvas*=1-shadow[...,None]*.65
            self.layer(canvas,a,cx,floor+th*.50,width,blur=w*.003,flip=True,opacity=s.get('reflection',.3))
        self.layer(canvas,a,cx,cy,width,blur=blur,opacity=.5 if k=='focus' else 1)
        return canvas
    def frame(self,s,i,samples):
        n=s['frames']; shutter=s.get('shutter',.45); fs=np.linspace(-shutter/2,shutter/2,samples) if samples>1 else [0]; acc=None
        for dt in fs:
            t=np.clip((i+dt)/max(1,n-1),0,1); x=self.sample(s,t);acc=x if acc is None else acc+x
        acc/=len(fs); bloom=s.get('bloom',.11)
        if bloom: acc+=gaussian(np.maximum(acc-.52,0),self.w*.014)*bloom*3
        im=Image.fromarray(rgb8(acc)); self.text(im,s.get('caption',''),self.h*.72,.055);return np.asarray(im)

def encode(p,out,font,samples=3,preview=None):
    w,h=p['width'],p['height']; studio=Studio(w,h,font); out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_name(out.stem+'.tmp.mp4')
    if preview:preview=Path(preview);preview.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(p['fps']),'-i','-','-an','-c:v','libx264','-threads','2','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);count=0
    try:
        for j,s in enumerate(p['shots']):
            for i in range(s['frames']):
                f=studio.frame(s,i,samples);proc.stdin.write(f.tobytes());count+=1
                if preview and i==s['frames']//2:Image.fromarray(f).save(preview/f'{j:02}-{s["kind"]}.png')
        proc.stdin.close()
        if proc.wait():raise RuntimeError('Encoding failed')
        actual=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames','-of','csv=p=0',str(tmp)]))
        if actual!=count:raise RuntimeError('Frame count mismatch')
        tmp.replace(out)
    except BaseException:
        if proc.poll() is None:proc.kill();proc.wait()
        tmp.unlink(missing_ok=True);raise
    print(f'{count} frames rendered')

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('plan',type=Path);a.add_argument('output',type=Path);a.add_argument('--font',required=True);a.add_argument('--samples',type=int,choices=[1,3,5],default=3);a.add_argument('--preview-dir'); args=a.parse_args();encode(validate(json.loads(args.plan.read_text())),args.output,args.font,args.samples,args.preview_dir)
if __name__=='__main__':main()
