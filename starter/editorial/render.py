#!/usr/bin/env python3
"""Editorial motion: physical pixel-space layout, crop windows, per-glyph reveals.
Uses only Pillow, NumPy and FFmpeg; deterministic, GUI-free. No invented UI states.
"""
import argparse, json, math, subprocess
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps
import numpy as np
import cv2
KINDS=('wall','shutter','macro','folio','aperture','signature','poster','fold')
EASES=('linear','smooth','out','in')
RANGES={'progress':(0,1),'zoom':(.6,2.5),'drift':(-1,1),'density':(3,12),'grain':(0,3),'tracking':(-.08,.15),'bend':(-1.6,1.6),'yaw':(-1.2,1.2),'pitch':(-.8,.8),'shine':(0,.6),'samples':(1,3),'shutter':(0,1)}
def require(ok,msg):
    if not ok: raise ValueError(msg)
def number(x,a,b): return type(x) in (int,float) and math.isfinite(x) and a<=x<=b
def clamp(t): return min(1,max(0,t))
def ease(t,k='smooth'):
    t=clamp(t)
    return {'linear':lambda:t,'smooth':lambda:t*t*(3-2*t),'out':lambda:1-(1-t)**3,'in':lambda:t**3}[k]()
def tr(c,k,t,default):
    v=c.get(k,default)
    if not isinstance(v,list):return v
    if t<=v[0][0]:return v[0][1]
    for a,b in zip(v,v[1:]):
        if t<=b[0]:return a[1]+(b[1]-a[1])*ease((t-a[0])/(b[0]-a[0]),b[2] if len(b)>2 else 'smooth')
    return v[-1][1]
def validate(c):
    require(c.get('kind') in KINDS,'unknown editorial kind')
    require(type(c.get('frames')) is int and 4<=c['frames']<=3600,'invalid frame count')
    for k,(a,b) in RANGES.items():
        if k not in c:continue
        v=c[k]
        if isinstance(v,list):
            require(k in ('progress','zoom','drift','bend','yaw','pitch','shine') and 2<=len(v)<=64,k+' invalid track');last=-1
            for q in v:
                require(isinstance(q,list) and len(q) in (2,3) and number(q[0],0,1) and q[0]>last and number(q[1],a,b) and (len(q)==2 or q[2] in EASES),k+' invalid key');last=q[0]
        else:require(number(v,a,b) and (k not in ('density','samples') or type(v) is int),k+' invalid')
    for k in ('bg','fg','accent','accent2'):
        if k in c: require(isinstance(c[k],str) and len(ImageColor.getrgb(c[k]))==3,k+' invalid RGB')
    for k in ('text','sub','label','brand','repeat'):
        if k in c:require(isinstance(c[k],str) and len(c[k])<=100,k+' invalid')
    require(isinstance(c.get('lines',[]),list) and len(c.get('lines',[]))<=4 and all(isinstance(s,str) and 0<len(s.strip())<=40 for s in c.get('lines',[])),'invalid lines')
    if c['kind'] in ('wall','poster','aperture'):require(bool(c.get('lines')),'lines required')
    if c['kind']=='signature':require(bool(c.get('brand','').strip()),'brand required')
    if c['kind'] in ('macro','folio','aperture','shutter','fold'):require(isinstance(c.get('src'),str) and Path(c['src']).is_file(),'source image required')
    for k in ('crop','crop2'):
        if k in c:
            r=c[k];require(isinstance(r,list) and len(r)==4 and all(number(a,0,1) for a in r) and r[0]<r[2] and r[1]<r[3],k+' invalid bounds')
    require(c.get('layout','left') in ('left','center','right'),'invalid layout')
    require(c.get('reveal','slice') in ('slice','glyph','wipe','none'),'invalid reveal')
    return c
@lru_cache(maxsize=128)
def font(path,size):return ImageFont.truetype(path,max(5,int(size)))
@lru_cache(maxsize=256)
def mask(text,path,size,tracking,stroke=0):
    f=font(path,size);b=f.getbbox(text,stroke_width=stroke);space=max(-size*.08,min(size*.15,tracking*size));pad=stroke+4
    if abs(space)<.1:
        a=Image.new('L',(max(1,b[2]-b[0]+2*pad),max(1,b[3]-b[1]+2*pad)));ImageDraw.Draw(a).text((pad-b[0],pad-b[1]),text,font=f,fill=255,stroke_width=stroke,stroke_fill=255);return a
    widths=[f.getlength(s) for s in text];a=Image.new('L',(max(1,math.ceil(sum(widths)+space*max(0,len(text)-1)+pad*4)),max(1,b[3]-b[1]+2*pad)));d=ImageDraw.Draw(a);x=pad*2
    for ch,w in zip(text,widths):d.text((x,pad-b[1]),ch,font=f,fill=255,stroke_width=stroke,stroke_fill=255);x+=w+space
    return a
class Editorial:
    def __init__(self,w,h,c,fp):
        self.w=w;self.h=h;self.c=validate(c);self.n=c['frames'];self.fp=str(fp);self.s=w/720
        self.bg=ImageColor.getrgb(c.get('bg','#101110'));self.fg=ImageColor.getrgb(c.get('fg','#f0eee7'));self.ac=ImageColor.getrgb(c.get('accent','#d8e986'));self.ac2=ImageColor.getrgb(c.get('accent2','#c3c9f3'));self.gap=.075
        self.img=Image.open(c['src']).convert('RGB') if c.get('src') else None
        self.noise=np.random.default_rng(22).normal(0,1,(h,w,1)).astype(np.float32)
    def xy(self,x,y):return round(x*self.w),round(y*self.h)
    def rect(self,im,box,col):ImageDraw.Draw(im).rectangle((*self.xy(*box[:2]),*self.xy(*box[2:])),fill=col)
    def line(self,im,a,b,col,width=1):ImageDraw.Draw(im).line([self.xy(*a),self.xy(*b)],fill=col,width=max(1,round(width*self.s)))
    def label(self,im,text,x,y,size=16,col=None,align='left',maxw=.85):
        self.text(im,text,x,y,size,maxw,col,align,reveal=1)
    def text(self,im,text,x,y,size,maxw=.85,col=None,align='left',reveal=1,style='none',stroke=False,texture=None,maxh=None):
        if not text:return
        fsize=round(size*self.s);track=self.c.get('tracking',-.035) if size>=60 else 0
        m=mask(text,self.fp,fsize,track).copy();cap=max(1,round(maxw*self.w));ratio=min(1,cap/m.width,(maxh*self.h/m.height if maxh else 1))
        if ratio<1:m=m.resize((max(1,int(m.width*ratio)),max(1,int(m.height*ratio))),Image.Resampling.LANCZOS)
        if stroke:
            from PIL import ImageFilter, ImageChops
            m=ImageChops.subtract(m.filter(ImageFilter.MaxFilter(3)),m.filter(ImageFilter.MinFilter(3)))
        a=np.array(m);reveal=clamp(reveal)
        if style=='glyph':
            # staggered character-width groups; approximate proportional-font boundaries.
            f=font(self.fp,fsize);ends=np.cumsum([max(.1,f.getlength(ch)+track*fsize) for ch in text]);edges=np.r_[0,np.rint(ends/ends[-1]*a.shape[1]).astype(int)];
            for j,(left,right) in enumerate(zip(edges[:-1],edges[1:])):
                v=ease((reveal*1.35-.35*j/max(1,len(text)-1)));a[:int((1-v)*a.shape[0]),left:right]=0
        elif style=='wipe':a[:,int(a.shape[1]*reveal):]=0
        elif style=='slice':
            a[:int((1-reveal)*a.shape[0]),:]=0
        elif reveal<1:a=(a.astype(float)*reveal).astype(np.uint8)
        px,py=self.xy(x,y);px-=round(m.width*(.5 if align=='center' else 1 if align=='right' else 0));m=Image.fromarray(a)
        if texture is None:im.paste(col or self.fg,(px,py,px+m.width,py+m.height),m)
        else:im.paste(texture.crop((px,py,px+m.width,py+m.height)),(px,py),m)
    def rule(self,im,y,p=1):self.line(im,(.075,y),(.075+.85*clamp(p),y),self.fg,1)
    def crop(self,r):
        a=self.img;return a.crop(tuple(round(v*q) for v,q in zip(r,(a.width,a.height,a.width,a.height))))
    def panel(self,im,src,box,zoom=1,dx=0,dy=0):
        x1,y1,x2,y2=(*self.xy(*box[:2]),*self.xy(*box[2:]));w=max(1,x2-x1);h=max(1,y2-y1)
        tw=max(w,round(w*zoom));th=max(h,round(h*zoom));a=ImageOps.fit(src,(tw,th),method=Image.Resampling.LANCZOS,centering=(clamp(.5+dx),clamp(.5+dy)));a=a.crop(((tw-w)//2,(th-h)//2,(tw-w)//2+w,(th-h)//2+h));im.paste(a,(x1,y1))
    def header(self,im,t):
        if self.c.get('label'):self.label(im,self.c['label'],.075,.095,17,maxw=.83)
    def wall(self,t):
        c=self.c;im=Image.new('RGB',(self.w,self.h),self.bg);p=tr(c,'progress',t,ease(t/.68));n=c.get('density',8);rowh=.73/n;rep=c.get('repeat','NOISE / ');dr=tr(c,'drift',t,.4);mut=tuple(round(a*.78+b*.22) for a,b in zip(self.bg,self.fg))
        # Full-bleed moving poster wall, the middle clearing creates the focal point.
        for i in range(n):
            yy=.12+i*rowh;direction=1 if i%2 else -1;x=-.25+((dr*t*direction+i*.137)% .55);off=(i-n/2)*p*.035
            self.text(im,rep*3,x,yy+off,82,2.25,mut,stroke=(i%3==0),reveal=1)
        opening=ease((t-.10)/.38);center=.49;rh=.22*opening
        self.rect(im,(0,center-rh,1,center+rh),self.bg);self.rect(im,(.075,center-rh,.075+.85*opening,center-rh+.003),self.ac)
        lines=c['lines'];base=.5-(len(lines)-1)*.065-.055;align=c.get('layout','left');anchor={'left':.075,'center':.5,'right':.925}[align]
        for i,word in enumerate(lines):
            q=ease((t-.10-i*.095)/.28,'out');self.text(im,word,anchor,base+i*.115+(.025*(1-q)),145,.85,self.fg if i==0 else self.ac,align=align,reveal=q,style=c.get('reveal','slice'),maxh=.108)
        if c.get('sub'):self.label(im,c['sub'],.075,.805,24,self.fg)
        self.header(im,t);return im
    def shutter(self,t):
        c=self.c;p=tr(c,'progress',t,ease(t/.85));im=Image.new('RGB',(self.w,self.h),self.ac);r=c.get('crop',[0,0,1,1]);src=self.crop(r);n=c.get('density',8)
        # Keep source aspect, no accidental text collisions or cropped product label.
        maxw=self.w;maxh=round(self.h*.52);scale=min(maxw/src.width,maxh/src.height);ww=max(2,round(scale*src.width));hh=max(2,round(scale*src.height));virtual=src.resize((ww,hh),Image.Resampling.LANCZOS);cell=math.ceil(hh/n);dy=round(.47*self.h-hh/2);dx=(self.w-ww)//2
        self.line(im,(.075,.245),(.925,.245),self.bg,2);self.line(im,(.075,.72),(.925,.72),self.bg,2)
        for i in range(n):
            if i*cell>=hh:break
            q=ease((p-i*.018)/max(.7,1-i*.018));a=virtual.crop((0,i*cell,ww,min((i+1)*cell,hh)));off=round((1-q)*self.w*(.58 if i%2 else -.58));im.paste(a,(dx+off,dy+i*cell))
        self.label(im,c.get('label',''),.075,.098,18,self.bg);self.text(im,c.get('text',''),.075,.78,100,.85,self.bg,reveal=ease((t-.18)/.25),style='slice',maxh=.085)
        self.line(im,(.075,.75),(.075+.85*p,.75),self.bg,2)
        return im
    def macro(self,t):
        c=self.c;im=Image.new('RGB',(self.w,self.h),self.bg);p=tr(c,'progress',t,ease(t/.72));r=np.array(c.get('crop',[0,0,1,1]));r2=np.array(c.get('crop2',r.tolist()));src=self.crop((r*(1-p)+r2*p).tolist());zz=tr(c,'zoom',t,1.06-.06*p)
        # Scale within bounded viewport so text outside the artwork remains clean.
        mw=int(.96*self.w);mh=int(.48*self.h);sc=min(mw/src.width,mh/src.height)*min(1,max(.6,zz));ww=max(2,round(src.width*sc));hh=max(2,round(src.height*sc))
        base=src.resize((ww,hh),Image.Resampling.LANCZOS);im.paste(base,((self.w-ww)//2,round(.46*self.h-hh/2)))
        self.rect(im,(0,.14,1,.215),self.ac2);self.label(im,c.get('label',''),.075,.163,20,self.bg);self.rule(im,.725,ease(t/.3));self.text(im,c.get('text',''),.075,.75,97,.85,self.fg,reveal=ease((t-.08)/.33),style=c.get('reveal','slice'),maxh=.09)
        if c.get('sub'):self.label(im,c['sub'],.075,.85,24,self.ac,maxw=.80)
        return im
    def folio(self,t):
        c=self.c;im=Image.new('RGB',(self.w,self.h),self.bg);p=tr(c,'progress',t,ease(t/.65));self.header(im,t)
        title=c.get('text','');self.text(im,title,.075,.166,120,.85,self.fg,reveal=ease(t/.25),style=c.get('reveal','slice'),maxh=.105)
        # Detail strips settle into a full-width product capture. Keep aspect and hold the proof.
        r1=c.get('crop',[0,0,.5,1]);r2=c.get('crop2',[.5,0,1,1]);a=self.crop(r1);b=self.crop(r2)
        xoff=.21*(1-p);self.panel(im,a,(.075-xoff,.29,.49-xoff,.435),1);self.panel(im,b,(.51+xoff,.29,.925+xoff,.435),1)
        self.line(im,(.075,.46),(.925,.46),self.ac,2);self.label(im,'01',.075,.475,20,self.ac);self.label(im,'02',.925,.475,20,self.ac,align='right')
        maxw=.94*self.w;maxh=.38*self.h;scale=min(maxw/self.img.width,maxh/self.img.height);ww=max(1,round(self.img.width*scale));hh=max(1,round(self.img.height*scale));src=self.img.resize((ww,hh),Image.Resampling.LANCZOS);y=int(self.h*(.51+.025*(1-p)));im.paste(src,((self.w-ww)//2,y));return im
    def fold(self,t):
        c=self.c;im=Image.new('RGB',(self.w,self.h),self.bg);p=tr(c,'progress',t,ease(t/.74));bend=tr(c,'bend',t,1.25*(1-p));yaw=tr(c,'yaw',t,.78*(1-p));pitch=tr(c,'pitch',t,-.24*(1-p));shine=tr(c,'shine',t,.18);zoom=tr(c,'zoom',t,1);crop=self.crop(c.get('crop',[0,0,1,1]));tex=np.asarray(crop.resize((960,max(2,round(960*crop.height/crop.width))),Image.Resampling.LANCZOS));ar=crop.height/crop.width;ar=min(2,ar);half=.92;hh=half*ar;cam=4.;focal=self.w*1.88*zoom;cx=.5*self.w;cy=.46*self.h
        def point(x,y):
            if abs(bend)>.0001:X=math.sin(x*bend)/bend;Z=(math.cos(x*bend)-1)/bend
            else:X=x;Z=0.
            X,Z=X*math.cos(yaw)+Z*math.sin(yaw),-X*math.sin(yaw)+Z*math.cos(yaw);Y,Z=y*math.cos(pitch)-Z*math.sin(pitch),y*math.sin(pitch)+Z*math.cos(pitch);return (cx+X*focal/(cam+Z),cy+Y*focal/(cam+Z),Z)
        n=c.get('density',12);items=[]
        for j in range(n):
            u0=-half+2*half*j/n;u1=-half+2*half*(j+1)/n;coords=[point(u0,-hh),point(u1,-hh),point(u1,hh),point(u0,hh)];vertices=np.array([v[:2] for v in coords],np.float32);depth=sum(v[2] for v in coords)/4;items.append((depth,j,vertices,(u0+u1)*.5))
        arr=np.array(im);th,tw=tex.shape[:2]
        # Painter order for non-self-intersecting curved plane. Every strip shares exact edge positions.
        for depth,j,verts,u in sorted(items,key=lambda v:v[0],reverse=True):
            left=math.floor(float(verts[:,0].min()));top=math.floor(float(verts[:,1].min()));right=math.ceil(float(verts[:,0].max()))+1;bottom=math.ceil(float(verts[:,1].max()))+1
            x0=max(0,left);y0=max(0,top);x1=min(self.w,right);y1=min(self.h,bottom)
            if x1<=x0 or y1<=y0:continue
            a=int(j*tw/n);b=min(tw,int((j+1)*tw/n)+1);patch=tex[:,a:b].copy();pw=patch.shape[1]
            # Controlled specular-like sweep, fades to exact source colors on landing.
            light=(.88+.12*math.cos(u*bend+yaw))*(1-p)+p;glint=shine*(1-p)*math.exp(-((u-(-.95+1.9*t))/.21)**2);patch=np.clip(patch.astype(np.float32)*light+glint*180,0,255).astype(np.uint8)
            src=np.float32([[0,0],[pw-1,0],[pw-1,th-1],[0,th-1]]);dst=verts-np.float32([x0,y0]);m=cv2.getPerspectiveTransform(src,dst);target=cv2.warpPerspective(patch,m,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE);alpha=cv2.warpPerspective(np.ones((th,pw),np.uint8)*255,m,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR).astype(np.float32)/255;region=arr[y0:y1,x0:x1];arr[y0:y1,x0:x1]=(target*alpha[...,None]+region*(1-alpha[...,None])).astype(np.uint8)
        im=Image.fromarray(arr);self.header(im,t);self.text(im,c.get('text',''),.075,.73,112,.85,self.fg,reveal=ease((t-.16)/.28),style=c.get('reveal','slice'),maxh=.11);self.line(im,(.075,.855),(.075+.85*p,.855),self.ac,2);self.label(im,c.get('sub',''),.075,.87,21,self.ac);return im
    def aperture(self,t):
        c=self.c;im=Image.new('RGB',(self.w,self.h),self.bg);tex=Image.new('RGB',(self.w,self.h),self.bg);p=tr(c,'progress',t,ease(t/.75));src=self.crop(c.get('crop',[0,0,1,1]));self.panel(tex,src,(0,.18,1,.78),tr(c,'zoom',t,1.05),dx=.15*(1-p))
        for i,word in enumerate(c['lines']):
            y=.24+i*min(.17,.47/max(1,len(c['lines'])-1));self.text(im,word,.5,y,215,.90,self.fg,'center',reveal=ease((t-i*.12)/.3),style='slice',texture=tex,maxh=.16)
        self.rule(im,.78,p);self.label(im,c.get('sub',''),.075,.81,26,self.fg);self.header(im,t);return im
    def poster(self,t):
        c=self.c;im=Image.new('RGB',(self.w,self.h),self.ac);lines=c['lines'];self.label(im,c.get('label',''),.075,.10,18,self.bg)
        align=c.get('layout','left');anchor={'left':.075,'center':.5,'right':.925}[align];step=min(.19,.49/max(1,len(lines)));
        for i,word in enumerate(lines):
            q=ease((t-i*.14)/.28,'out');y=.25+i*step;self.text(im,word,anchor,y,190,.85,self.bg,align=align,reveal=q,style=c.get('reveal','slice'),maxh=step*.8);self.line(im,(.075,y+step*.9),(.075+.85*q,y+step*.9),self.bg,1)
        self.label(im,c.get('sub',''),.075,.82,22,self.bg);return im
    def signature(self,t):
        c=self.c;im=Image.new('RGB',(self.w,self.h),self.bg);p=tr(c,'progress',t,.25+.75*ease(t/.42));self.header(im,t)
        # Corner-to-center line travel, short brand lock, no decorative fake status UI.
        x=.075;self.line(im,(x,.37),(x+.85*p,.37),self.ac,3);self.text(im,c['brand'],.075,.425,180,.85,self.fg,reveal=p,style='slice',maxh=.16);self.line(im,(x,.59),(x+.85*p,.59),self.ac,3);self.text(im,c.get('sub',''),.075,.65,53,.85,self.ac,reveal=ease((t-.15)/.24),style='wipe',maxh=.08);return im
    def frame(self,i):
        c=self.c;f=lambda t:np.asarray(getattr(self,c['kind'])(clamp(t)),np.uint8);samples=c.get('samples',1)
        if samples>1:
            frames=[f((i+(j/(samples-1)-.5)*c.get('shutter',.6))/(self.n-1)).astype(np.float32)/255 for j in range(samples)];a=(np.mean([x**2.2 for x in frames],axis=0)**(1/2.2)*255).astype(np.uint8)
        else:a=f(i/(self.n-1))
        return np.clip(a.astype(np.float32)+self.noise*c.get('grain',.4),0,255).astype(np.uint8) if c.get('grain',.4) else a

def main():
    p=argparse.ArgumentParser();p.add_argument('plan');p.add_argument('out');p.add_argument('--font',required=True);p.add_argument('--frame',type=int);a=p.parse_args();d=json.loads(Path(a.plan).read_text());w,h,fps=(d[k] for k in ('width','height','fps'));shots=[Editorial(w,h,c,a.font) for c in d['shots']]
    if a.frame is not None:
        require(0<=a.frame<shots[0].n,'invalid frame');Image.fromarray(shots[0].frame(a.frame)).save(a.out);return
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',a.out];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for sh in shots:
            for i in range(sh.n):proc.stdin.write(sh.frame(i).tobytes())
    finally:proc.stdin.close();code=proc.wait()
    if code:raise RuntimeError('ffmpeg failed')
if __name__=='__main__':main()
