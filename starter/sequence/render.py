#!/usr/bin/env python3
"""Continuous motif sequences on the existing cinematic compositing backend."""
import argparse, importlib.util, json, math, subprocess
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
spec=importlib.util.spec_from_file_location('cinematic',Path(__file__).resolve().parents[1]/'cinematic/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
KINDS={'consolidate','reveal','compare'}
def mix(a,b,t):return a+(b-a)*t
def validate(s):
    if s.get('kind') not in KINDS:raise ValueError('invalid sequence kind')
    if type(s.get('frames')) is not int or not 30<=s['frames']<=3600:raise ValueError('invalid frame count')
    for k in ('hook','turn','payoff','brand','cta'):
        if not isinstance(s.get(k),str) or not 1<=len(s[k])<=65 or len(s[k].splitlines())>(2 if k=='hook' else 1):raise ValueError('invalid '+k)
    m.validate(dict(s,kind='reframe'))
    if s['kind']=='compare' and not Path(s.get('alternate',{}).get('src','')).is_file():raise ValueError('compare needs alternate.src')
    b=s.get('beats',[round(s['frames']*x) for x in (0,.20,.39,.58,.82)])
    if not isinstance(b,list) or len(b)!=5 or not all(type(x) is int for x in b) or b[0]!=0 or min(y-x for x,y in zip(b,b[1:]+[s['frames']]))<4:raise ValueError('invalid beats')
    l=s.get('labels',['REFERENCE','NOTES','DRAFT','ASSETS','PROJECT'])
    if not isinstance(l,list) or not 2<=len(l)<=8 or not all(isinstance(x,str) and 1<=len(x)<=24 for x in l):raise ValueError('invalid labels')
    if s.get('motion','flow') not in ('flow','snap','quiet') or s.get('texture','grain') not in ('grain','grid','none') or s.get('samples',1) not in (1,2,3):raise ValueError('invalid motion, texture or samples')
    if 'paper' in s:m.rgb(s['paper'])
    if s.get('focus','brackets') not in ('brackets','lens','none'):raise ValueError('invalid focus')
    if s.get('transition','iris') not in ('iris','wipe','cut'):raise ValueError('invalid transition')
    if s.get('light',.18)<0 or s.get('light',.18)>.6:raise ValueError('invalid light')
class Sequence(m.Scene):
    def __init__(self,w,h,s,fp):
        validate(s);super().__init__(w,h,dict(s,kind='reframe'),fp);self.s=s;self.b=s.get('beats',[round(s['frames']*x) for x in (0,.2,.39,.58,.82)])+[s['frames']];self.labels=s.get('labels',['REFERENCE','NOTES','DRAFT','ASSETS','PROJECT']);self.paper=m.rgb(s.get('paper','#efefea'));self.alt=Image.open(s['alternate']['src']).convert('RGB') if s['kind']=='compare' else None
        c=s.get('crop',[.03,.23,.97,.66]);self.detail=self.source.crop(tuple(round(x*y) for x,y in zip(c,[self.source.width,self.source.height]*2)))
    def rect(self,im,b,c,o=None,r=0):ImageDraw.Draw(im).rounded_rectangle((*self.xy(*b[:2]),*self.xy(*b[2:])),radius=round(r*self.scale),fill=c,outline=o,width=max(1,round(self.scale)))
    def reveal(self,im,t,x,y,n,c,p,align='left'):
        if p<=0:return
        l=im.copy();self.text(l,t,x,y+40*(1-p),n,c,align=align);a,b=self.xy(0,y)[1],self.xy(0,y+n*1.65*p)[1];im.paste(l.crop((0,a,self.w,b)),(0,a))
    def stack(self,im,p,ink,bg,entry=1):
        n=len(self.labels)
        for i in range(n):
            off=i-(n-1)/2;x=360+off*mix(31,0,p);y=690+off*mix(min(98,440/n),9,p)+120*(1-m.ease(entry*2-i*.12));ww=mix(484,584,p);hh=150
            c=self.ac if i==n-1 else tuple(round(mix(a,b,.1+.055*i)) for a,b in zip(bg,ink));self.rect(im,(x-ww/2,y-hh/2,x+ww/2,y+hh/2),c,ink,14);self.text(im,f'{i+1:02d}',x-ww/2+18,y-51,15,self.bg if i==n-1 else ink,'mono');self.text(im,self.labels[i],x-ww/2+72,y-46,26,self.bg if i==n-1 else ink,width=ww-100)
    def rail(self,im,f,ink):
        self.line(im,(48,179),(672,179),ink);self.text(im,self.s['brand'].upper(),48,139,16,ink,'mono',width=390);self.text(im,f'{int(f)+1:03d} / {self.s["frames"]:03d}',672,139,16,ink,'mono','right',180);self.line(im,(48,1082),(672,1082),ink);self.line(im,(48,1082),(48+624*f/(self.s['frames']-1),1082),self.ac,3)
    def frame(self,f):
        f=max(0,min(self.s['frames']-1,f));i=next(i for i in range(5) if f<self.b[i+1]);t=(f-self.b[i])/max(1,self.b[i+1]-self.b[i]-1);s=self.s;p=m.ease(t) if s.get('motion')=='snap' else m.smooth(t);power=.65 if s.get('motion')=='quiet' else 1
        bg=self.paper if i==2 else self.bg;ink=self.bg if i==2 else self.fg;im=Image.new('RGB',(self.w,self.h),bg);align=s.get('layout','left');tx=360 if align=='center' else 48
        if s.get('texture')=='grid' or i==1 and s.get('texture','grain')!='none':
            c=tuple(round(mix(a,b,.09)) for a,b in zip(bg,ink))
            for x in range(0,721,36):self.line(im,(x,0),(x,1280),c)
            for y in range(-36,1280,36):self.line(im,(0,y+f%36),(720,y+f%36),c)
        if i<4:self.rail(im,f,ink)
        if i==0:
            for j,w in enumerate(s['hook'].splitlines()):self.reveal(im,w,tx,215+j*105,100,ink if j==0 else self.ac,m.ease(t*4-j*.55),align)
            self.stack(im,.15*m.ease(t*2),ink,bg,entry=t);self.text(im,' / '.join(self.labels[:2]),48,1020,18,ink,'mono')
        elif i==1:
            self.stack(im,mix(.15,1,p),ink,bg);self.reveal(im,s['turn'],tx,231,83,ink,m.ease(t*4),align)
            span=mix(318,306,p);cy=690
            for x,sg in [(360-span,1),(360+span,-1)]:
                for y,sy in [(cy-100,1),(cy+100,-1)]:self.line(im,(x+sg*22,y),(x,y),self.ac,2);self.line(im,(x,y),(x,y+sy*22),self.ac,2)
            self.text(im,f'{round(mix(len(self.labels),1,p)):02d}',48,928,92,ink);self.text(im,' / '+s['brand'],215,963,21,ink,'mono')
            if t>.80 and s.get('transition','iris')!='cut':
                q=m.smooth((t-.80)/.20);nextim=Image.new('RGB',im.size,self.paper);self.panel(nextim,self.detail,360,625,1062,0,-9);mask=Image.new('L',im.size);d=ImageDraw.Draw(mask);r=mix(50,800,q)
                if s.get('transition','iris')=='iris':d.ellipse((*self.xy(360-r,690-r),*self.xy(360+r,690+r)),fill=255)
                else:d.rectangle((0,0,self.w,round(self.h*q)),fill=255)
                im.paste(nextim,(0,0),mask)
        elif i==2:
            if s['kind']=='compare':
                self.panel(im,self.alt,360,625,640);edge=round(self.w*p);layer=im.copy();self.panel(layer,self.source,360,625,640);im.paste(layer.crop((0,0,edge,self.h)),(0,0));self.line(im,(720*p,355),(720*p,895),self.ac,3)
            else:self.panel(im,self.detail,360,625,642+420*(1-p)*power,0,-9*(1-p)*power)
            self.reveal(im,s['payoff'],tx,240,84,ink,m.ease(t*3),align);
            if s.get('focus','brackets')!='none':
                q=m.smooth(t);rx=128+90*q;ry=65+24*q;cx=360+80*(1-q);cy=625;d=ImageDraw.Draw(im)
                if s.get('focus','brackets')=='lens':d.ellipse((*self.xy(cx-rx,cy-ry),*self.xy(cx+rx,cy+ry)),outline=self.ac,width=max(1,round(2*self.scale)))
                else:
                    for x,sg in [(cx-rx,1),(cx+rx,-1)]:
                        for y,sy in [(cy-ry,1),(cy+ry,-1)]:self.line(im,(x+sg*16,y),(x,y),self.ac,2);self.line(im,(x,y),(x,y+sy*16),self.ac,2)
            self.rect(im,(48,934,672,1022),self.ac,r=8);self.text(im,s['brand'],66,945,44,self.bg,width=580)
        elif i==3:
            self.panel(im,self.source,360,mix(634,603,p),636+195*(1-p)*power,-5*(1-p)*power,14*(1-p)*power);self.reveal(im,s['payoff'],48,236,82,ink,m.ease(t*4))
            if s['kind']=='reveal':self.panel(im,self.detail,360,914,502)
            else:self.rect(im,(48,920,672,1012),self.ac,r=10);self.text(im,s['cta'],66,938,36,self.bg,width=580)
        else:
            self.rect(im,(48,mix(920,470,p),672,mix(1012,720,p)),self.ac,r=10*(1-p));self.text(im,s['brand'],360,mix(938,520,p),mix(36,124,p),self.bg,align='center',width=590);self.reveal(im,s['cta'],360,780,44,ink,m.ease((t-.25)*3),'center')
        a=np.asarray(im).copy()
        # Restrict moving light to bright highlight regions during transformation.
        strength=s.get('light',.18)
        if strength and i in (1,4):
            x=np.arange(self.w,dtype=np.float32)[None,:];y=np.arange(self.h,dtype=np.float32)[:,None];band=np.exp(-((x+.26*y-self.w*mix(-.3,1.5,t))/(self.w*.07))**2);v=np.maximum(a.astype(np.float32).max(axis=2)-100,0)/155;gain=band*v*strength*85;a=np.uint8(np.clip(a+gain[:,:,None],0,255))
        if s.get('texture','grain')=='grain':a=np.uint8(np.clip(a+np.roll(self.noise,int(f)%29,axis=0)[:,:,None]*1.1,0,255))
        return a
    def sample(self,f):
        n=self.s.get('samples',1)
        if n==1:return self.frame(f)
        i=next(i for i in range(5) if f<self.b[i+1]);a=[self.frame(max(self.b[i],min(self.b[i+1]-1,f+d))).astype(np.float32)/255 for d in np.linspace(-.25,.25,n)]
        return np.uint8(np.clip(np.mean([v**2.2 for v in a],axis=0)**(1/2.2)*255,0,255))
def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('output',type=Path);p.add_argument('--font',required=True);p.add_argument('--frame',type=int);a=p.parse_args();d=json.loads(a.plan.read_text());w,h,fps=(d[k] for k in ('width','height','fps'));scenes=[Sequence(w,h,s,a.font) for s in d['shots']];a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.frame is not None:Image.fromarray(scenes[0].sample(a.frame)).save(a.output);return
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],stdin=subprocess.PIPE)
    try:
        for s in scenes:
            for f in range(s.s['frames']):proc.stdin.write(s.sample(f).tobytes())
    finally:proc.stdin.close();rc=proc.wait()
    if rc:raise RuntimeError('ffmpeg failed')
if __name__=='__main__':main()
