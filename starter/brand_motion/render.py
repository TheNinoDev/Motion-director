#!/usr/bin/env python3
"""Original brand-story motion; exact frames, deterministic CPU rendering, no GUI."""
import argparse, json, math, subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np

def require(x,m):
    if not x: raise ValueError(m)
def ease(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)
def mix(a,b,p): return a+(b-a)*p
def validate(p,root):
    w,h,fps=(p[k] for k in ('width','height','fps'))
    require(all(type(v)==int and v>0 for v in (w,h,fps)) and w%2==h%2==0 and max(w,h)<=3840 and fps<=60,'bad raster/fps')
    require(isinstance(p['shots'],list) and p['shots'],'missing shots')
    for s in p['shots']:
        k=s.get('kind'); require(k in ('palette','collapse','badges','endcard','reset'),'bad kind')
        require(type(s.get('frames'))==int and 1<=s['frames']<=3600,'bad frames')
        if k in ('palette','collapse'):
            require((root/s['src']).is_file(),'missing screenshot')
        if k=='palette':
            require(s.get('illustrative') is True,'palette experiment must be declared illustrative')
            require(2<=len(s['hues'])<=12 and all(type(x) in (int,float) and math.isfinite(x) for x in s['hues']),'bad hues')
        if k=='collapse':
            require(1<=len(s['boxes'])<=60 and all(len(b)==4 and 0<=b[0]<b[2]<=1 and 0<=b[1]<b[3]<=1 for b in s['boxes']),'normalized screenshot boxes required')
        if k=='badges':
            require(s.get('illustrative') is True or bool(s.get('evidence_source')),'badge claims need source')
            require(1<=len(s['items'])<=6 and all(isinstance(x,str) and 1<=len(x)<=50 for x in s['items']),'bad items')
        if k=='endcard':
            require(bool(s.get('brand')) or bool(s.get('logo')),'brand or logo required')
            if s.get('logo'):require((root/s['logo']).is_file(),'missing logo')
        if k=='reset': require(s['frames']>=2,'reset needs >=2 frames')
    return sum(s['frames'] for s in p['shots'])
class Engine:
    def __init__(self,w,h,font,root): self.w=w;self.h=h;self.font=font;self.root=root;self.cache={}
    def txt(self,d,text,xy,size,color='#f3f3f4',width=.86):
        if not text:return
        f=ImageFont.truetype(self.font,max(10,int(size*self.w))); b=d.multiline_textbbox((0,0),text,font=f,spacing=4)
        if b[2]-b[0]>width*self.w:
            f=ImageFont.truetype(self.font,max(10,int(f.size*width*self.w/(b[2]-b[0]))))
        d.multiline_text(xy,text,font=f,fill=color,anchor='mm',align='center',spacing=4)
    def photo(self,path):
        if path not in self.cache:
            a=Image.open(self.root/path).convert('RGB');a.thumbnail((int(self.w*.88),int(self.h*.50)),Image.Resampling.LANCZOS); self.cache[path]=a
        return self.cache[path]
    def frame(self,s,i):
        w,h=self.w,self.h; p=i/max(1,s['frames']-1); k=s['kind']; im=Image.new('RGB',(w,h),s.get('background','#08090b'));d=ImageDraw.Draw(im); fg=s.get('foreground','#f5f5f5');accent=s.get('accent','#c2a1fa')
        if k in ('palette','collapse'):
            a=self.photo(s['src']); x=(w-a.width)//2;y=int(h*.43-a.height/2)
            if k=='palette':
                hue=s['hues'][min(len(s['hues'])-1,int(p*len(s['hues'])))]; hsv=np.asarray(a.convert('HSV')).copy(); mask=hsv[:,:,1]>45; hsv[:,:,0][mask]=(hsv[:,:,0][mask].astype(np.int32)+round(hue*255/360))%256; img=Image.fromarray(hsv,'HSV').convert('RGB');im.paste(img,(x,y));d=ImageDraw.Draw(im);self.txt(d,'COLOR STUDY / ILLUSTRATIVE',(w/2,h*.83),.028,fg)
            else:
                q=ease(p/.33); z=ease((p-.38)/.48)
                if q<1: im.paste(Image.blend(a,Image.new('RGB',a.size,s.get('background','#08090b')),q),(x,y))
                for j,b in enumerate(s['boxes']):
                    x1,y1,x2,y2=x+b[0]*a.width,y+b[1]*a.height,x+b[2]*a.width,y+b[3]*a.height
                    cx,cy=(x1+x2)/2,(y1+y2)/2; bx,by=mix(cx,w/2,z),mix(cy,h*.46,z); ww=mix(x2-x1,max(2,w*.004),z);hh=mix(y2-y1,h*.045,z); v=round(mix(42,220,max(q,z)));d.rounded_rectangle((bx-ww/2,by-hh/2,bx+ww/2,by+hh/2),radius=max(0,min(4,ww/2,hh/2)),fill=(v,v,v))
                if z>.995 and (i//10)%2:d.rectangle((w/2-2,h*.437,w/2+2,h*.483),fill=s.get('background','#08090b'))
            self.txt(d,s.get('caption',''),(w/2,h*.74),.05,fg)
        elif k=='reset':
            if (i//max(1,round(s.get('blink_frames',12))))%2==0:d.rectangle((w/2-1,h*.44,w/2+1,h*.49),fill=fg)
            self.txt(d,s.get('caption',''),(w/2,h*.72),.043,fg)
        elif k=='badges':
            self.txt(d,s.get('title',''),(w/2,h*.25),.064,fg)
            n=len(s['items']);rows=math.ceil(n/2);cw=int(w*.39);ch=int(h*.095)
            for j,t in enumerate(s['items']):
                z=ease((p-j*.075)/.32)
                if z<=0:continue
                cx=w*(.29 if j%2==0 else .71) if not(n%2 and j==n-1) else w*.5;cy=h*(.39+(j//2)*.115);cy+=h*.12*(1-z)
                d.rounded_rectangle((cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),radius=int(w*.018),fill='#17181c',outline=accent,width=max(1,w//350));self.txt(d,t,(cx,cy),.042,fg,.34)
            if s.get('illustrative'):self.txt(d,'ILLUSTRATIVE / NOT PRODUCT CLAIMS',(w/2,h*.80),.027,fg)
        elif k=='endcard':
            q=ease(p/.28); cy=mix(h*.48,h*.43,q)
            if s.get('logo'):
                logo=Image.open(self.root/s['logo']).convert('RGBA');logo.thumbnail((int(w*.72),int(h*.2)),Image.Resampling.LANCZOS);im.paste(logo,(round(w/2-logo.width/2),round(cy-logo.height/2)),logo)
            else:self.txt(d,s['brand'],(w/2,cy),.19,fg)
            if p>.20:self.txt(d,s.get('tagline',''),(w/2,h*.56),.071,fg)
            if p>.32:self.txt(d,s.get('url',''),(w/2,h*.64),.045,accent)
        return im

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--font',required=True);ap.add_argument('--frame',type=int);a=ap.parse_args();p=json.loads(a.plan.read_text());root=a.plan.resolve().parent;total=validate(p,root);w,h,fps=(p[k] for k in ('width','height','fps'));e=Engine(w,h,a.font,root);a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.frame is not None:
        require(0<=a.frame<total,'frame out of range');i=a.frame
        for s in p['shots']:
            if i<s['frames']:e.frame(s,i).save(a.output);return
            i-=s['frames']
    args=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart',str(a.output)]
    pr=subprocess.Popen(args,stdin=subprocess.PIPE)
    try:
        for s in p['shots']:
            for i in range(s['frames']):pr.stdin.write(e.frame(s,i).tobytes())
    finally:pr.stdin.close();rc=pr.wait()
    if rc:raise SystemExit(rc)
if __name__=='__main__':main()
