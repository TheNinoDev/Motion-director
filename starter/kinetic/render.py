#!/usr/bin/env python3
"""Frame-addressable editorial motion: projected glyph clouds, optical product crops, modular typography."""
import argparse, math, json, subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageColor
KINDS=('field','proof','type','lockup')
FIELDS=('vortex','wave','burst','helix','grid')
TRACKS={'spread':(0,1),'yaw':(-6.3,6.3),'pitch':(-1.5,1.5),'zoom':(.4,4),'focus':(0,1),'reveal':(0,1),'panx':(-1,1),'pany':(-1,1)}
def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def ease(x,k):return {'linear':lambda:x,'smooth':lambda:smooth(x),'out':lambda:1-(1-x)**3,'in':lambda:x**3}[k]()
def track(c,k,t,default):
    v=c.get(k,default)
    if not isinstance(v,list):return v
    if t<=v[0][0]:return v[0][1]
    for a,b in zip(v,v[1:]):
        if t<=b[0]:return a[1]+(b[1]-a[1])*ease((t-a[0])/(b[0]-a[0]),b[2] if len(b)==3 else 'smooth')
    return v[-1][1]
def validate(c):
    def need(ok,msg):
        if not ok:raise ValueError(msg)
    def num(x,a,b):return type(x) in (float,int) and math.isfinite(x) and a<=x<=b
    need(c.get('kind') in KINDS,'unknown kinetic kind');need(type(c.get('frames')) is int and 4<=c['frames']<=3600,'invalid frames')
    for k,(a,b) in TRACKS.items():
        if k not in c:continue
        v=c[k]
        if isinstance(v,list):
            need(len(v)>=2 and len(v)<=64,k+' key count');last=-1
            for q in v:
                need(isinstance(q,list) and len(q) in (2,3) and num(q[0],0,1) and q[0]>last and num(q[1],a,b) and (len(q)==2 or q[2] in ('linear','smooth','out','in')),k+' invalid key');last=q[0]
        else:need(num(v,a,b),k+' out of range')
    for k,a,b in [('count',100,6000),('seed',0,2**32-1),('samples',1,4),('shutter',0,1),('glow',0,.5),('grain',0,2),('size',.35,2)]:
        if k in c:need(num(c[k],a,b) and (k not in ('count','seed','samples') or type(c[k]) is int),k+' invalid')
    for k in ('bg','fg','accent'):
        if k in c:need(isinstance(c[k],str) and len(ImageColor.getrgb(c[k]))==3,k+' requires RGB')
    for k in ('text','sub','eyebrow','brand','glyph'):
        if k in c:need(isinstance(c[k],str) and len(c[k])<=100,k+' invalid')
    if c['kind']=='field':
        need(c.get('field','vortex') in FIELDS,'invalid field');need(c.get('sprite','mixed') in ('dot','shard','dash','mixed'),'invalid sprite');need(bool(c.get('glyph','A').strip()) and len(c.get('glyph','A'))<=12,'glyph required')
    if c['kind']=='proof':
        need(isinstance(c.get('src'),str) and Path(c['src']).is_file(),'actual image required')
        r=c.get('crop',[0,0,1,1]);need(isinstance(r,list) and len(r)==4 and all(num(x,0,1) for x in r) and r[0]<r[2] and r[1]<r[3],'invalid crop')
        need(c.get('mask','diagonal') in ('diagonal','iris','split','horizontal'),'invalid mask')
    if c['kind']=='type':
        words=c.get('words');need(isinstance(words,list) and 1<=len(words)<=5 and all(isinstance(x,str) and 0<len(x.strip())<=36 for x in words),'words must contain 1–5 phrases');need(c.get('layout','stack') in ('stack','split','track'),'invalid layout')
    if c['kind']=='lockup':need(bool(c.get('brand','').strip()),'brand required')
    return c
@lru_cache(maxsize=128)
def font(path,size):return ImageFont.truetype(path,max(1,int(size)))
def text_mask(text,path,size):
    f=font(path,size);b=f.getbbox(text);im=Image.new('L',(max(1,b[2]-b[0]+4),max(1,b[3]-b[1]+4)));ImageDraw.Draw(im).text((2-b[0],2-b[1]),text,font=f,fill=255);return im
class Kinetic:
    def __init__(self,w,h,c,fp):
        self.w=w;self.h=h;self.c=validate(c);self.fp=str(fp);self.s=w/720;self.n=c['frames'];self.bg=ImageColor.getrgb(c.get('bg','#101116'));self.fg=ImageColor.getrgb(c.get('fg','#f1efe6'));self.ac=ImageColor.getrgb(c.get('accent','#b4a5ff'));self.rng=np.random.default_rng(c.get('seed',21));self.x,self.y=np.meshgrid(np.linspace(-1,1,w,dtype=np.float32),np.linspace(-1,1,h,dtype=np.float32));self.base=np.clip(np.array(self.bg,dtype=np.float32)[None,None,:]+(1-np.minimum(1,(self.x**2+self.y**2)/2))[...,None]*7,0,255).astype(np.uint8)
        self.noise=self.rng.normal(0,1,(h,w,1)).astype(np.float32)
        if c['kind']=='field':self.setup_field()
        if c['kind']=='proof':self.src=Image.open(c['src']).convert('RGB')
    def setup_field(self):
        c=self.c;n=c.get('count',2400);rng=self.rng;m=np.asarray(text_mask(c.get('glyph','A'),self.fp,360));yy,xx=np.where(m>140);
        if len(xx)==0:raise ValueError('glyph has no visible pixels in selected font')
        idx=rng.choice(len(xx),n,replace=len(xx)<n);scale=max(m.shape);a=(xx[idx]-(m.shape[1]-1)/2)/scale*4.2;b=(yy[idx]-(m.shape[0]-1)/2)/scale*4.2;self.target=np.stack([a,b,rng.uniform(-.12,.12,n)],1);theta=rng.uniform(0,2*np.pi,n);z=rng.uniform(-1,1,n);r=rng.uniform(.5,2.7,n);f=c.get('field','vortex')
        if f=='vortex':x=r*np.cos(theta+z*3);y=r*np.sin(theta+z*3);z=z*3
        elif f=='helix':z=z*3;theta=z*3+theta*.18;x=1.65*np.cos(theta);y=z*.78;z=1.65*np.sin(theta)
        elif f=='wave':x=rng.uniform(-3,3,n);y=np.sin(x*2+z*3)*.65+z;z=rng.uniform(-2.2,2.2,n)
        elif f=='grid':q=int(np.ceil(np.sqrt(n)));x=(np.arange(n)%q/(q-1)-.5)*5;y=(np.arange(n)//q/(q-1)-.5)*5;z=z*.8
        else:x=r*np.sqrt(1-z*z)*np.cos(theta);y=r*np.sqrt(1-z*z)*np.sin(theta);z=r*z
        self.source=np.stack([x,y,z],1);self.rand=rng.uniform(0,1,n);self.jitter=rng.normal(0,.32,(n,3))
    def draw_text(self,img,t,x,y,size,color=None,maxw=.88,align='left',reveal=1):
        if not t:return
        size=max(6,int(size*self.s));m=text_mask(t,self.fp,size);cap=int(self.w*maxw)
        if m.width>cap:m=m.resize((cap,max(1,round(m.height*cap/m.width))),Image.Resampling.LANCZOS)
        if reveal<1:
            a=np.array(m);a[:,int(a.shape[1]*clamp(reveal)):]=0;m=Image.fromarray(a)
        px=int(x*self.w-(m.width/2 if align=='center' else m.width if align=='right' else 0));py=int(y*self.h);img.paste(color or self.fg,(px,py,px+m.width,py+m.height),m)
    def compose_field(self,t):
        c=self.c;p=track(c,'spread',t,smooth((t-.09)/.76));q=1-p;pts=self.source*q+self.target*p+self.jitter*(math.sin(math.pi*p)*.9);yaw=track(c,'yaw',t,.75*(1-p));pitch=track(c,'pitch',t,-.3*(1-p));x,y,z=pts.T;xx=x*np.cos(yaw)+z*np.sin(yaw);zz=z*np.cos(yaw)-x*np.sin(yaw);yy=y*np.cos(pitch)-zz*np.sin(pitch);zz=y*np.sin(pitch)+zz*np.cos(pitch);zoom=track(c,'zoom',t,1);dep=7+zz;scale=self.w*1.2*zoom/np.maximum(dep,1);px=self.w*(.5+track(c,'panx',t,0)*.25)+xx*scale;py=self.h*(.48+track(c,'pany',t,0)*.25)+yy*scale
        canvas=self.base.copy();order=np.argsort(zz)[::-1];light=np.clip(.35+.65*(.5+.5*np.cos(xx*2.1+zz*1.7-t*5)),.15,1);col=(np.array(self.fg)*(.65+.35*p))[None,:]*light[:,None];col=col*(1-self.rand[:,None]*.27)+np.array(self.ac)[None,:]*self.rand[:,None]*.27
        for i in order:
            if -8<px[i]<self.w+8 and -8<py[i]<self.h+8:
                rad=max(1,int(self.s*(1.0+2.1*self.rand[i])*7/dep[i]*c.get('size',1)));cc=tuple(map(int,col[i]));cx,cy=int(px[i]),int(py[i]);sprite=c.get('sprite','mixed');sprite=('dot' if self.rand[i]<.65 else 'shard') if sprite=='mixed' else sprite
                if sprite=='dot':cv2.circle(canvas,(cx,cy),rad,cc,-1,cv2.LINE_AA)
                else:
                    angle=self.rand[i]*6.28+t*3*(1-p);dx=math.cos(angle)*rad;dy=math.sin(angle)*rad
                    if sprite=='dash':cv2.line(canvas,(int(cx-dx*1.8),int(cy-dy*1.8)),(int(cx+dx*1.8),int(cy+dy*1.8)),cc,max(1,rad//2),cv2.LINE_AA)
                    else:cv2.fillConvexPoly(canvas,np.array([(cx+dx,cy+dy),(cx-dy*.6,cy+dx*.6),(cx-dx,cy-dy),(cx+dy*.6,cy-dx*.6)],np.int32),cc,cv2.LINE_AA)
                if self.rand[i]>.985 and p<.8:cv2.line(canvas,(int(px[i]),int(py[i])),(int(px[i]+rad*3),int(py[i])),cc,1,cv2.LINE_AA)
        g=c.get('glow',.12)
        if g:canvas=np.clip(canvas.astype(np.float32)+cv2.GaussianBlur(np.maximum(canvas.astype(np.float32)-150,0),(0,0),max(1,self.s*5))*g,0,255).astype(np.uint8)
        img=Image.fromarray(canvas);self.draw_text(img,c.get('text',''),.08,.16,64,reveal=smooth(t/.18));self.draw_text(img,c.get('sub',''),.08,.77,28,reveal=smooth((t-.63)/.2));return img
    def compose_proof(self,t):
        c=self.c;f=track(c,'focus',t,smooth(t/.8));r=np.array(c.get('crop',[0,0,1,1]));r=r*(1-f)+np.array([0,0,1,1])*f;sw,sh=self.src.size;roi=self.src.crop(tuple((r*np.array([sw,sh,sw,sh])).round().astype(int)));targetw=int(self.w*(.96-.11*f)*track(c,'zoom',t,1));targeth=max(1,int(targetw*roi.height/roi.width));maxh=int(self.h*.63)
        if targeth>maxh:targetw=max(2,int(targetw*maxh/targeth));targeth=maxh
        targetw=max(2,targetw);targeth=max(2,targeth);roi=np.asarray(roi.resize((targetw,targeth),Image.Resampling.LANCZOS));cx=self.w*(.5+track(c,'panx',t,0)*.22);cy=self.h*(.48+track(c,'pany',t,0)*.25);tilt=track(c,'yaw',t,.24*(1-f));skew=tilt*targetw*.22;dst=np.float32([[cx-targetw/2,cy-targeth/2+skew],[cx+targetw/2,cy-targeth/2-skew],[cx+targetw/2,cy+targeth/2+skew],[cx-targetw/2,cy+targeth/2-skew]]);mat=cv2.getPerspectiveTransform(np.float32([[0,0],[targetw-1,0],[targetw-1,targeth-1],[0,targeth-1]]),dst);warp=cv2.warpPerspective(roi,mat,(self.w,self.h));alpha=cv2.warpPerspective(np.ones((targeth,targetw),np.uint8)*255,mat,(self.w,self.h)).astype(np.float32)/255
        p=track(c,'reveal',t,smooth(t/.28));kind=c.get('mask','diagonal');metric={'diagonal':(self.x+self.y*.55+1.55)/3.1,'iris':np.sqrt(self.x**2+self.y**2)/1.4143,'split':np.abs(self.x),'horizontal':(self.y+1)/2}[kind];alpha*=np.clip((p-metric+.035)/.035,0,1);shadow=cv2.GaussianBlur(alpha,(0,0),max(2,self.s*18));base=self.base.astype(np.float32)*(1-shadow[...,None]*.48);img=Image.fromarray(np.clip(base*(1-alpha[...,None])+warp*alpha[...,None],0,255).astype(np.uint8));d=ImageDraw.Draw(img);a=int(14*self.s)
        if p>.9:
            for j,(x,y) in enumerate(dst):
                sx=1 if j in (0,3) else -1;sy=1 if j in (0,1) else -1;d.line([(x+sx*a,y),(x,y),(x,y+sy*a)],fill=self.ac,width=max(1,int(2*self.s)))
        self.draw_text(img,c.get('text',''),.08,.15,72,reveal=smooth(t/.22));self.draw_text(img,c.get('sub',''),.08,.79,30,reveal=smooth((t-.53)/.25));return img
    def compose_type(self,t):
        c=self.c;words=c['words'];img=Image.fromarray(self.base.copy());layout=c.get('layout','stack');d=ImageDraw.Draw(img)
        if layout=='track':
            for i in range(7):
                s=' / '.join(words)+' / ';m=text_mask(s,self.fp,int(49*self.s));step=max(1,m.width);off=int((t*(1 if i%2==0 else -1)*step+i*step*.14)%step)
                for x in range(-step-off,self.w,step):img.paste(tuple(int(v*.32) for v in self.fg),(x,int(self.h*(.24+i*.075))),m)
            d.rectangle((0,int(self.h*.39),self.w,int(self.h*.63)),fill=self.bg);self.draw_text(img,words[-1],.5,.45,108,align='center',reveal=smooth(t/.23))
        else:
            for i,word in enumerate(words):
                r=smooth((t-i*.13)/.24);y=.30+i*min(.13,.49/max(1,len(words)-1));x=.08 if layout=='stack' or i%2==0 else .92;self.draw_text(img,word,x,y,min(116 if i==0 else 90, int(145*4/max(4,len(words)))),self.fg if i%2==0 else self.ac,align='right' if x>.5 else 'left',reveal=r)
                if r>0:d.line([(int(self.w*.08),int((y-.025)*self.h)),(int(self.w*(.08+.84*r)),int((y-.025)*self.h))],fill=self.ac,width=max(1,int(self.s)))
        self.draw_text(img,c.get('sub',''),.08,.80,29,reveal=smooth((t-.6)/.22));return img
    def compose_lockup(self,t):
        img=Image.fromarray(self.base.copy());p=smooth(t/.4);self.draw_text(img,self.c['brand'],.08,.43,120,self.fg,reveal=p);d=ImageDraw.Draw(img);d.line([(int(self.w*.08),int(self.h*.57)),(int(self.w*(.08+.84*p)),int(self.h*.57))],fill=self.ac,width=max(1,int(2*self.s)));self.draw_text(img,self.c.get('sub',''),.08,.60,33,reveal=smooth((t-.25)/.3));return img
    def frame(self,i):
        c=self.c;n=self.n;samples=c.get('samples',1);f=lambda t:np.asarray(getattr(self,'compose_'+c['kind'])(clamp(t)))
        if samples>1 and c['kind']=='field':
            acc=np.mean([(f((i+(j/(samples-1)-.5)*c.get('shutter',.5))/(n-1)).astype(np.float32)/255)**2.2 for j in range(samples)],axis=0);arr=np.clip(acc**(1/2.2)*255,0,255).astype(np.uint8)
        else:arr=f(i/(n-1)).copy()
        img=Image.fromarray(arr);self.draw_text(img,c.get('eyebrow',''),.08,.095,18,maxw=.82);g=c.get('grain',.6);return np.clip(np.asarray(img).astype(np.float32)+self.noise*g,0,255).astype(np.uint8) if g else np.asarray(img)
def main():
    a=argparse.ArgumentParser();a.add_argument('plan');a.add_argument('out');a.add_argument('--font',required=True);a.add_argument('--frame',type=int);v=a.parse_args();p=json.loads(Path(v.plan).read_text());w,h,fps=[p[k] for k in ('width','height','fps')];shots=[Kinetic(w,h,c,v.font) for c in p['shots']];cv2.setNumThreads(2)
    if v.frame is not None:
        if not 0<=v.frame<shots[0].n:raise ValueError('frame out of range')
        Image.fromarray(shots[0].frame(v.frame)).save(v.out);return
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w}x{h}','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',v.out];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for shot in shots:
            for i in range(shot.n):proc.stdin.write(shot.frame(i).tobytes())
    finally:proc.stdin.close();code=proc.wait()
    if code:raise RuntimeError('ffmpeg failed')
if __name__=='__main__':main()
