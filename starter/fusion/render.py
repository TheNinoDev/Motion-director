#!/usr/bin/env python3
"""Fusion: headless morph CGI, shape-driven product reveal and editorial type."""
import argparse,json,math,subprocess,sys
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageColor,ImageFilter,ImageChops
SHAPES=('tiles','ribbon','cube','aperture','capsules')
MATS=('chrome','ceramic','anodized','glass','obsidian')
KINDS=('morph','bridge','type','lockup')
RANGES={'phase':(0,1),'twist':(0,2.5),'pitch':(-6.3,6.3),'yaw':(-6.3,6.3),'roll':(-6.3,6.3),'light':(-6.3,6.3),'zoom':(.5,9),'panx':(-.7,.7),'pany':(-.7,.7),'orbit':(-6.3,6.3),'elevation':(-2,3),'exposure':(.2,3)}

def clamp(x):return max(0.,min(1.,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def ease(x):return 1-(1-clamp(x))**3
def mix(a,b,p):return a+(b-a)*p

def number(x,lo,hi):return type(x) in (int,float) and math.isfinite(x) and lo<=x<=hi

def validate(s):
    if s.get('kind') not in KINDS or type(s.get('frames')) is not int or not 4<=s['frames']<=3600:raise ValueError('fusion: invalid kind/frames')
    for k in ('bg','fg','accent','tint'):
        if k in s:ImageColor.getrgb(s[k])
    for k in ('text','sub','eyebrow','brand'):
        if k in s and (not isinstance(s[k],str) or len(s[k])>100):raise ValueError('fusion: invalid '+k)
    for k,lo,hi in [('quality',.2,1),('roughness',.03,.65),('ior',1.05,2.2),('bloom',0,.6),('grain',0,3),('shutter',0,1)]:
        if k in s and not number(s[k],lo,hi):raise ValueError('fusion: invalid '+k)
    if type(s.get('samples',1)) is not int or not 1<=s.get('samples',1)<=4:raise ValueError('fusion: samples 1..4')
    for k in ('floor','guides'):
        if k in s and type(s[k]) is not bool:raise ValueError('fusion: invalid '+k)
    if s.get('shape','tiles') not in SHAPES or s.get('material','chrome') not in MATS:raise ValueError('fusion: invalid shape/material')
    for k,(lo,hi) in RANGES.items():
        if k not in s:continue
        v=s[k]
        if number(v,lo,hi):continue
        if not isinstance(v,list) or not 2<=len(v)<=24:raise ValueError('fusion: invalid track '+k)
        prev=-1
        for a in v:
            if not isinstance(a,list) or len(a) not in (2,3) or not number(a[0],0,1) or not number(a[1],lo,hi) or a[0]<=prev or (len(a)==3 and a[2] not in ('linear','smooth','out')):raise ValueError('fusion: invalid key '+k)
            prev=a[0]
        if v[0][0]!=0 or v[-1][0]!=1:raise ValueError('fusion: track must span 0..1 '+k)
    if s['kind']=='bridge':
        if not Path(s.get('src','')).is_file():raise ValueError('fusion: bridge requires an actual screenshot')
        c=s.get('crop',[0,0,1,1]);
        if not isinstance(c,list) or len(c)!=4 or not all(number(x,0,1) for x in c) or c[0]>=c[2] or c[1]>=c[3]:raise ValueError('fusion: bad crop')
        if s.get('mask','rounded') not in ('rounded','split','iris','diagonal'):raise ValueError('fusion: bad mask')
        if not number(s.get('reveal_at',.26),.08,.72):raise ValueError('fusion: reveal_at')
    if s['kind']=='type':
        w=s.get('words');
        if not isinstance(w,list) or not 1<=len(w)<=4 or not all(isinstance(x,str) and 0<len(x)<=26 for x in w):raise ValueError('fusion: 1..4 short words')
        if s.get('layout','stack') not in ('stack','mono','stripe'):raise ValueError('fusion: bad layout')
    if s['kind']=='lockup' and not s.get('brand'):raise ValueError('fusion: brand required')

def key(s,k,t,default):
    v=s.get(k,default)
    if not isinstance(v,list):return v
    for i in range(1,len(v)):
        if t<=v[i][0]:
            u=clamp((t-v[i-1][0])/(v[i][0]-v[i-1][0]));mode=v[i][2] if len(v[i])==3 else 'smooth';return mix(v[i-1][1],v[i][1],u if mode=='linear' else ease(u) if mode=='out' else smooth(u))
    return v[-1][1]

class Fusion:
    def __init__(self,w,h,s,font):
        validate(s)
        if abs(w/h-9/16)>.02:raise ValueError('fusion: portrait 9:16 required')
        self.w=w;self.h=h;self.s=s;self.k=w/720;self.f=font
        self.bg=ImageColor.getrgb(s.get('bg','#090a0c'));self.fg=ImageColor.getrgb(s.get('fg','#f6f5f2'));self.ac=ImageColor.getrgb(s.get('accent','#d9f477'));self.tint=ImageColor.getrgb(s.get('tint',s.get('accent','#c4d8ff')))
        self.src=Image.open(s['src']).convert('RGB') if s['kind']=='bridge' else None
        self.noise=np.random.default_rng(220).normal(0,1,(h,w)).astype(np.float32)
    @lru_cache(maxsize=96)
    def font(self,px):return ImageFont.truetype(self.f,max(8,round(px*self.k)))
    def xy(self,x,y):return round(x*self.k),round(y*self.k)
    def text(self,im,txt,x,y,px,c=None,anchor='lt',maxw=630):
        if not txt:return
        d=ImageDraw.Draw(im);f=self.font(round(px));
        while d.textlength(txt,font=f)>maxw*self.k and px>9:px*=.94;f=self.font(round(px))
        d.text(self.xy(x,y),txt,font=f,fill=c or self.fg,anchor=anchor)
    def line(self,im,pts,col,width=1):ImageDraw.Draw(im).line([self.xy(x,y) for x,y in pts],fill=col,width=max(1,round(width*self.k)))
    def masktext(self,im,txt,x,y,px,p,c=None,maxw=630):
        p=clamp(p)
        if p<=0:return
        layer=Image.new('RGBA',im.size);self.text(layer,txt,x,y+40*(1-ease(p)),px,c,maxw=maxw)
        matte=Image.new('L',im.size);ImageDraw.Draw(matte).rectangle((0,round(y*self.k),self.w,round((y+px*1.16)*self.k)),fill=255)
        matte=ImageChops.multiply(matte,layer.getchannel('A')).point(lambda a:round(a*min(1,p*3)))
        im.paste(layer,(0,0),matte)
    def label(self,im,t):
        if not self.s.get('guides',False):return
        muted=tuple(round(mix(a,b,.55)) for a,b in zip(self.bg,self.fg))
        self.text(im,self.s.get('eyebrow','FORM STUDY'),42,84,18,muted,maxw=500)
        self.text(im,f'{round(t*100):02d} / 100',678,84,18,muted,'rt',160)
        self.line(im,[(42,119),(678,119)],muted)
        self.line(im,[(42,119),(42+636*t,119)],self.ac,2)
    def cg(self,t,frame,shutter=True):
        # Only temporal-sample the CG; overlay remains optically crisp and stable.
        from optics import render
        s=self.s;q=s.get('quality',.60);w=max(96,round(self.w*q));h=max(96,round(self.h*q));ss=s.get('samples',1) if shutter else 1;sh=s.get('shutter',.45);n=max(1,s['frames']-1)
        bg=tuple((v/255)**2.2*.40 for v in self.bg);tint=tuple((v/255)**2.2 for v in self.tint)
        out=np.zeros((h,w,3),np.float32)
        for i in range(ss):
            z=clamp(t+((i+.5)/ss-.5)*sh/n)
            params=[key(s,k,z,d) for k,d in [('phase',z),('twist',1.5),('pitch',.2),('yaw',.3),('roll',.0),('light',.0)]]
            cams=[key(s,k,z,d) for k,d in [('zoom',2.9),('panx',.0),('pany',.0),('orbit',.0),('elevation',.25)]]
            out+=render(w,h,SHAPES.index(s.get('shape','tiles')),*params[:5],MATS.index(s.get('material','chrome')),s.get('roughness',.09),params[5],tint,s.get('ior',1.45),*cams,bg,key(s,'exposure',z,1.),s.get('floor',False))
        out/=ss
        # Linear highlight blur, followed by filmic shoulder and display transfer.
        b=s.get('bloom',.09)
        if b:
            import cv2
            bright=np.maximum(0,out-.8);out+=b*cv2.GaussianBlur(bright,(0,0),max(1,w*.018))
        out=np.maximum(out,0);out=out/(out+.55)
        rgb=np.where(out<=.0031308,12.92*out,1.055*np.power(out,1/2.4)-.055)
        return Image.fromarray(np.uint8(np.clip(rgb*255,0,255))).resize((self.w,self.h),Image.Resampling.LANCZOS)
    def morph(self,t,i):
        im=self.cg(t,i);self.label(im,t)
        p=ease((t-.06)*5);self.masktext(im,self.s.get('text',''),42,178,90,p,maxw=636)
        if self.s.get('sub'):self.text(im,self.s['sub'],44,1075,27,self.fg,maxw=620)
        return im
    def bridge(self,t,i):
        s=self.s;at=s.get('reveal_at',.26);p=smooth((t-at)/(.72-at));im=self.cg(t,i) if p<1 else Image.new('RGB',(self.w,self.h),self.bg)
        # Zoom from actual product detail to context. The same panel stays on-screen.
        iw,ih=self.src.size;c=s.get('crop',[.48,.24,.95,.56]);cx=mix((c[0]+c[2])*.5*iw,iw*.5,p);cy=mix((c[1]+c[3])*.5*ih,ih*.46,p)
        z=mix(570/(iw*(c[2]-c[0])),636/iw,p)*self.k;tx=360*self.k-cx*z;ty=mix(630,650,p)*self.k-cy*z
        panel=self.src.transform(im.size,Image.Transform.AFFINE,(1/z,0,-tx/z,0,1/z,-ty/z),Image.Resampling.BICUBIC,fillcolor=self.bg)
        if p>0:
            matte=Image.new('L',im.size);d=ImageDraw.Draw(matte);rx=mix(5,740,p**1.6);ry=mix(5,965,p**1.6);cxp=360;cyp=640
            mode=s.get('mask','rounded');a=self.xy(cxp-rx,cyp-ry);b=self.xy(cxp+rx,cyp+ry)
            if mode=='rounded':d.rounded_rectangle([a,b],radius=round(mix(5,14,p)*self.k),fill=255)
            elif mode=='iris':d.ellipse([self.xy(cxp-rx*1.4,cyp-ry*1.5),self.xy(cxp+rx*1.4,cyp+ry*1.5)],fill=255)
            elif mode=='split':d.rectangle([self.xy(cxp-rx,mix(180,-2,p)),self.xy(cxp+rx,mix(1080,1282,p))],fill=255)
            else:d.polygon([self.xy(0,640-ry*1.6),self.xy(720,640-ry*.9),self.xy(720,640+ry*1.6),self.xy(0,640+ry*.9)],fill=255)
            if p>=1:matte=Image.new('L',im.size,255)
            im.paste(panel,(0,0),matte.filter(ImageFilter.GaussianBlur(max(.3,1.0*self.k))))
        self.label(im,t)
        self.masktext(im,s.get('text',''),42,171,86,ease((t-.65)*5),maxw=636)
        if s.get('sub') and t>.72:self.masktext(im,s['sub'],44,1055,27,ease((t-.72)*5),maxw=620)
        return im
    def type(self,t,i):
        s=self.s;im=Image.new('RGB',(self.w,self.h),self.bg);words=s['words'];n=len(words);mode=s.get('layout','stack');self.label(im,t)
        if mode=='stack':
            for j,word in enumerate(words):
                p=ease((t-j*.16)*5);y=320+j*min(170,560/n);self.masktext(im,word,42+(j%2)*48,y,145 if j==0 else 122,p,self.ac if j==n-1 else self.fg,maxw=636-(j%2)*48)
        elif mode=='mono':
            j=min(n-1,int(t*n));p=(t*n-j) if t<1 else 1;self.masktext(im,words[j],42,500,205,ease(p*5),self.fg,maxw=636)
        else:
            for j,word in enumerate(words):
                p=ease((t-j*.18)*5);y=320+j*min(176,540/n)
                if p>0:
                    d=ImageDraw.Draw(im);d.rectangle([self.xy(0,y-8),self.xy(720*p,y+133)],fill=self.ac if j%2==0 else self.fg)
                    self.masktext(im,word,42,y+10,108,p,self.bg,maxw=636)
        if s.get('sub'):self.text(im,s['sub'],44,1075,26,maxw=620)
        return im
    def lockup(self,t,i):
        s=self.s;im=Image.new('RGB',(self.w,self.h),self.bg);p=ease(t*4)
        self.masktext(im,s['brand'],42,482,200,p,self.fg,maxw=636)
        self.line(im,[(44,718),(44+632*ease((t-.15)*4),718)],self.ac,2)
        self.masktext(im,s.get('sub',''),44,755,39,ease((t-.25)*4),self.fg,maxw=620)
        if s.get('eyebrow'):self.text(im,s['eyebrow'],44,1060,20,self.ac,maxw=620)
        return im
    def frame(self,i):
        t=i/max(1,self.s['frames']-1);im=getattr(self,self.s['kind'])(t,i);arr=np.asarray(im);g=self.s.get('grain',.45)
        if g:return np.uint8(np.clip(arr.astype(np.float32)+np.roll(self.noise,i%23,axis=0)[:,:,None]*g,0,255))
        return arr

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('output',type=Path);p.add_argument('--font',required=True);p.add_argument('--frame',type=int);a=p.parse_args();d=json.loads(a.plan.read_text());w,h,fps=(d[k] for k in ('width','height','fps'));scenes=[Fusion(w,h,s,a.font) for s in d['shots']];a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.frame is not None:
        if not 0<=a.frame<scenes[0].s['frames']:raise ValueError('frame out of range')
        Image.fromarray(scenes[0].frame(a.frame)).save(a.output);return
    tmp=a.output.with_name(a.output.stem+'.work.mp4');proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
    try:
        for s in scenes:
            for i in range(s.s['frames']):proc.stdin.write(s.frame(i).tobytes())
        proc.stdin.close();rc=proc.wait()
        if rc:raise RuntimeError('ffmpeg failed')
        tmp.replace(a.output)
    except BaseException:
        if not proc.stdin.closed:proc.stdin.close()
        proc.terminate();proc.wait();tmp.unlink(missing_ok=True);raise
if __name__=='__main__':main()
