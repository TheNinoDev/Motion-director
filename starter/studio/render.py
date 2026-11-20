#!/usr/bin/env python3
"""Studio sequences: configurable ray-marched hero, split typography, product reveal and lockup."""
import argparse,json,math,subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageColor
KINDS={'hero','kinetic','proof','lockup'}; SHAPES=['ring','links','wave','rounded']; MATS=['chrome','ceramic','tinted']

def validate(s):
    if s.get('kind') not in KINDS:raise ValueError('studio: unknown kind')
    if type(s.get('frames')) is not int or not 4<=s['frames']<=3600:raise ValueError('studio: invalid frames')
    for k in ('text','sub','brand'):
        if k in s and (not isinstance(s[k],str) or len(s[k])>160):raise ValueError('studio: invalid '+k)
    for k in ('accent','fg','bg'):
        if k in s:ImageColor.getrgb(s[k])
    if s['kind']=='hero':
        if s.get('headline_position','top') not in ('top','bottom'):raise ValueError('studio: invalid headline position')
        if type(s.get('contrast_scrim',.75)) not in (int,float) or not 0<=s.get('contrast_scrim',.75)<=1:raise ValueError('studio: invalid scrim')
        if s.get('shape','ring') not in SHAPES or s.get('material','chrome') not in MATS:raise ValueError('studio: invalid shape/material')
        for k,lo,hi in [('roughness',.03,.8),('quality',.25,1),('twist',0,.20),('bloom',0,.40),('grain',0,4)]:
            v=s.get(k,lo)
            if type(v) not in (int,float) or not lo<=v<=hi:raise ValueError('studio: invalid '+k)
        if type(s.get('floor',False)) is not bool:raise ValueError('studio: floor must be boolean')
        for k in ('zoom','panx','pany','pitch','yaw','roll','orbit','light'):
            if k in s:
                v=s[k];lo,hi=(.4,10) if k=='zoom' else (-10,10)
                if not isinstance(v,list) or not 2<=len(v)<=20:raise ValueError('studio: '+k+' must be keyframe list')
                prev=-1
                for a in v:
                    if not isinstance(a,list) or len(a)!=2 or type(a[0]) not in (float,int) or type(a[1]) not in (float,int) or not 0<=a[0]<=1 or not lo<=a[1]<=hi or a[0]<=prev:raise ValueError('studio: invalid '+k+' keyframe')
                    prev=a[0]
                if v[0][0]!=0 or v[-1][0]!=1:raise ValueError('studio: '+k+' must span 0..1')
    if s['kind']=='proof':
        if not Path(s.get('src','')).is_file():raise ValueError('studio: proof needs a real screenshot')
        c=s.get('crop',[.04,.24,.96,.65]);
        if not isinstance(c,list) or len(c)!=4 or not all(type(v) in (int,float) and 0<=v<=1 for v in c) or not c[0]<c[2] or not c[1]<c[3]:raise ValueError('studio: invalid crop')
    if s['kind']=='kinetic':
        if s.get('layout','stack') not in ('stack','carousel','cascade'):raise ValueError('studio: invalid kinetic layout')
        a=s.get('words',[])
        if not isinstance(a,list) or not 1<=len(a)<=5 or not all(isinstance(x,str) and 1<=len(x)<=30 for x in a):raise ValueError('studio: 1–5 words or short lines required')
    if s['kind']=='lockup' and not s.get('brand'):raise ValueError('studio: brand required')


def smooth(t):t=max(0.,min(1.,t));return t*t*(3-2*t)
def ease(t):return 1-(1-max(0.,min(1.,t)))**3
def mix(a,b,t):return a+(b-a)*t

def key(s,k,t,default):
    a=s.get(k,[[0,default],[1,default]])
    for i in range(1,len(a)):
        if t<=a[i][0]:return mix(a[i-1][1],a[i][1],smooth((t-a[i-1][0])/(a[i][0]-a[i-1][0])))
    return a[-1][1]

class Studio:
    def __init__(self,w,h,s,font):
        validate(s);
        if abs(w/h-9/16)>.02:raise ValueError('studio: portrait 9:16 required')
        self.s=s;self.w=w;self.h=h;self.f=font;self.k=w/720
        self.bg=ImageColor.getrgb(s.get('bg','#08090b'));self.fg=ImageColor.getrgb(s.get('fg','#f5f4ee'));self.ac=ImageColor.getrgb(s.get('accent','#d6f477'))
        self.src=Image.open(s['src']).convert('RGB') if s['kind']=='proof' else None
        self.noise=np.random.default_rng(12).normal(0,1,(h,w)).astype(np.float32)
    @lru_cache(maxsize=64)
    def font(self,px):return ImageFont.truetype(self.f,max(10,round(px*self.k)))
    def text(self,im,txt,x,y,px,color=None,anchor='lt',maxw=640,tracking=0):
        if not txt:return
        d=ImageDraw.Draw(im);font=self.font(round(px));limit=maxw*self.k
        while d.textlength(txt,font=font)>limit and px>10:px*=.94;font=self.font(round(px))
        d.text((round(x*self.k),round(y*self.k)),txt,font=font,fill=color or self.fg,anchor=anchor,stroke_width=0)
    def rect(self,im,box,fill,outline=None,width=1):ImageDraw.Draw(im).rectangle(tuple(round(z*self.k) for z in box),fill=fill,outline=outline,width=max(1,round(width*self.k)))
    def line(self,im,pts,fill,width=1):ImageDraw.Draw(im).line([(round(x*self.k),round(y*self.k)) for x,y in pts],fill=fill,width=max(1,round(width*self.k)))
    def mask_text(self,im,txt,x,y,px,p,color=None,maxw=650):
        layer=Image.new('RGBA',im.size);self.text(layer,txt,x,y+33*(1-ease(p)),px,color,maxw=maxw)
        mask=Image.new('L',im.size);ImageDraw.Draw(mask).rectangle((0,round(y*self.k),self.w,round((y+px*1.4)*self.k)),fill=255)
        from PIL import ImageChops
        mask=ImageChops.multiply(mask,layer.getchannel('A'));mask=mask.point(lambda v:round(v*min(1,p*3)))
        im.paste(layer,(0,0),mask)
    def hero(self,t):
        from optics import render
        s=self.s;quality=s.get('quality',.6);w=max(96,round(self.w*quality));h=max(96,round(self.h*quality));bg=tuple((v/255)**2.2*.7 for v in self.bg);tint=tuple((v/255)**2.2 for v in self.ac)
        a=render(w,h,SHAPES.index(s.get('shape','ring')),key(s,'pitch',t,.28),key(s,'yaw',t,.4),key(s,'roll',t,.0),s.get('twist',.12),MATS.index(s.get('material','chrome')),s.get('roughness',.12),key(s,'light',t,0.),tint,key(s,'zoom',t,3.),key(s,'panx',t,0.),key(s,'pany',t,0.),key(s,'orbit',t,0.),s.get('floor',False),bg)
        im=Image.fromarray(a).resize((self.w,self.h),Image.Resampling.LANCZOS)
        strength=s.get('bloom',.08)
        if strength:
            from PIL import ImageChops
            light=im.point(lambda v:max(0,(v-180)*3)).filter(ImageFilter.GaussianBlur(8*self.k));im=ImageChops.add(im,light,scale=1,offset=0) if strength==1 else Image.blend(im,ImageChops.add(im,light),strength)
        if s.get('text'):
            bottom=s.get('headline_position','top')=='bottom';y=985 if bottom else 116
            # Feathered contrast field only where text needs it; no opaque pill.
            yy=np.arange(self.h)/self.k;alpha=np.clip(1-np.abs(yy-(y+60))/210,0,1)**1.4*s.get('contrast_scrim',.75)
            mask=Image.fromarray(np.uint8(np.tile(alpha[:,None]*255,(1,self.w))));im.paste((0,0,0),(0,0,self.w,self.h),mask)
            self.mask_text(im,s['text'],50,y,104,ease(t*5+.18),maxw=620)
        if s.get('sub'):self.text(im,s['sub'],52,1095,25,anchor='lt',maxw=610)
        return im
    def kinetic(self,t):
        s=self.s;im=Image.new('RGB',(self.w,self.h),self.bg);words=s['words'];n=len(words);mode=s.get('layout','stack')
        if mode=='stack':
            size=min(160,840/max(n,1));y=640-n*size*.48
            for i,word in enumerate(words):
                p=ease((t-i*.12)*3.8);self.mask_text(im,word,48+18*(i%2),y+i*size,size,p,self.ac if i==n-1 else self.fg)
        elif mode=='cascade':
            # A different scale at every entry with a stable baseline grid and final collective hold.
            gap=min(200,640/n);base=280+(3-n)*40
            for i,word in enumerate(words):
                p=ease((t-i*.20)*7);x=48+16*(i%2)
                self.mask_text(im,word,x,base+i*gap,155 if i==0 else (112 if i==1 else 172),p,self.ac if i==n-1 else self.fg)
                if p>.95:self.line(im,[(48,base+i*gap+174),(mix(48,670,p),base+i*gap+174)],tuple(round(mix(a,b,.20)) for a,b in zip(self.bg,self.fg)),1)
        else:
            i=min(n-1,int(t*n));p=(t*n)%1 if t<1 else 1
            self.mask_text(im,words[i],48,480,205,ease(p*4),self.ac if i==n-1 else self.fg)
            # Cropped oversized echo moves in opposite direction, never obscures hero line.
            self.text(im,words[i],670,790+70*p,94,tuple(round(mix(a,b,.22)) for a,b in zip(self.bg,self.fg)),anchor='rt')
        if s.get('sub'):self.text(im,s['sub'],48,1080,25,maxw=620)
        return im
    def proof(self,t):
        s=self.s;im=Image.new('RGB',(self.w,self.h),self.bg);iw,ih=self.src.size;c=s.get('crop',[.04,.24,.96,.65]);p=smooth(t*1.30);cx0=(c[0]+c[2])/2*iw;cy0=(c[1]+c[3])/2*ih;cx=mix(cx0,iw/2,p);cy=mix(cy0,ih/2,p)
        initial=720/(iw*(c[2]-c[0]));final=610/iw;z=mix(initial,final,p)*self.k
        # Preserve source geometry; one continuous affine camera, not a crossfade of different crops.
        tx=360*self.k-cx*z;ty=mix(620,650,p)*self.k-cy*z
        panel=self.src.transform(im.size,Image.Transform.AFFINE,(1/z,0,-tx/z,0,1/z,-ty/z),Image.Resampling.BICUBIC,fillcolor=self.bg)
        mask=Image.new('L',im.size);d=ImageDraw.Draw(mask);d.rectangle((round(max(0,tx)),round(max(0,ty)),round(min(self.w,tx+iw*z)),round(min(self.h,ty+ih*z))),fill=255)
        shadow=mask.filter(ImageFilter.GaussianBlur(24*self.k));im.paste((0,0,0),(0,0,self.w,self.h),shadow);im.paste(panel,(0,0),mask)
        if s.get('text'):self.mask_text(im,s['text'],48,145,98,ease((t-.52)*5),self.fg,maxw=625)
        if s.get('sub'):self.mask_text(im,s['sub'],48,1040,33,ease((t-.60)*5),self.fg)
        if s.get('brackets',True) and t<.42:
            alpha=1-smooth((t-.1)/.32);col=tuple(round(mix(a,b,alpha)) for a,b in zip(self.bg,self.ac))
            for x,sg in [(50,1),(670,-1)]:
                for y,sy in [(500,1),(740,-1)]:self.line(im,[(x+sg*24,y),(x,y),(x,y+sy*24)],col,2)
        return im
    def lockup(self,t):
        s=self.s;im=Image.new('RGB',(self.w,self.h),self.bg);p=ease(t*3);cx=360;cy=560
        # Four precise corner strokes converge into one wordmark; no generic CTA box.
        radius=mix(390,135,p);col=self.ac
        if t<.65:
            for j in range(4):
                a=math.pi/4+j*math.pi/2+t*.6;x=cx+radius*math.cos(a);y=cy+radius*math.sin(a);self.line(im,[(x-8,y),(x+8,y)],col,2)
        self.text(im,s['brand'],cx,cy+22*(1-p),150,self.fg,anchor='mm',maxw=610)
        if s.get('sub'):self.text(im,s['sub'],cx,cy+145,29,self.ac,anchor='mt',maxw=620)
        return im
    def frame(self,i):
        t=i/max(1,self.s['frames']-1);im=getattr(self,self.s['kind'])(t);grain=self.s.get('grain',.7)
        if grain:
            a=np.asarray(im).astype(np.float32);a+=np.roll(self.noise,i%31,axis=0)[:,:,None]*grain;return np.uint8(np.clip(a,0,255))
        return np.asarray(im)

def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('output',type=Path);p.add_argument('--font',required=True);p.add_argument('--frame',type=int);a=p.parse_args();d=json.loads(a.plan.read_text());w,h,fps=(d[k] for k in ('width','height','fps'));scenes=[Studio(w,h,s,a.font) for s in d['shots']];a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.frame is not None:Image.fromarray(scenes[0].frame(a.frame)).save(a.output);return
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],stdin=subprocess.PIPE)
    try:
        for s in scenes:
            for f in range(s.s['frames']):proc.stdin.write(s.frame(f).tobytes())
    finally:proc.stdin.close();rc=proc.wait()
    if rc:raise RuntimeError('ffmpeg failed')
if __name__=='__main__':main()
