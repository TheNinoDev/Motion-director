#!/usr/bin/env python3
"""Deterministic layered motion compositor. JSON, normalized 1080x1920 design space, no GUI."""
import argparse,json,math,subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
# Import also works when the controller loads this module by absolute path.
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from effects import Dynamic, validate_dynamic, shutter
from optical import Optical, KINDS, validate as validate_optical, distort

def clamp(x):return min(1,max(0,x))
def ease(t,k):
    t=clamp(t)
    if k=='out':return 1-(1-t)**3
    if k=='in':return t**3
    if k=='inout':return t*t*(3-2*t)
    if k=='back':return 1+2.4*(t-1)**3+1.4*(t-1)**2
    if k=='hold':return 0 if t<1 else 1
    return t

def value(v,f):
    if not isinstance(v,list):return v
    if not v or not isinstance(v[0],list):raise ValueError('keyframes must be [[frame,value,ease],...]')
    if f<=v[0][0]:return v[0][1]
    for a,b in zip(v,v[1:]):
        if f<=b[0]:return a[1]+(b[1]-a[1])*ease((f-a[0])/(b[0]-a[0]),b[2] if len(b)>2 else 'linear')
    return v[-1][1]

def rgba(s):
    s=s.lstrip('#');return tuple(int(s[i:i+2],16) for i in (0,2,4))+(int(s[6:8],16) if len(s)==8 else 255,)
@lru_cache(maxsize=128)
def font(path,size):return ImageFont.truetype(path,max(1,int(size)))
def sprite(l,sz,fontpath):
    typ=l['kind'];w,h=map(int,l.get('size',[500,200]));w=max(2,round(w*sz));h=max(2,round(h*sz))
    c=rgba(l.get('color','#ffffff')); im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im)
    if typ=='text':
        text=l['text']; fs=l.get('font_size',100)*sz;ft=font(l.get('font',fontpath),fs);spacing=round(l.get('spacing',5)*sz)
        while (d.multiline_textbbox((0,0),text,font=ft,spacing=spacing)[2]>w-4 or d.multiline_textbbox((0,0),text,font=ft,spacing=spacing)[3]>h-4) and fs>10:fs*=.94;ft=font(l.get('font',fontpath),fs)
        box=d.multiline_textbbox((0,0),text,font=ft,spacing=spacing,align=l.get('align','left'));tw=box[2]-box[0];th=box[3]-box[1]; x={'left':5,'center':(w-tw)/2,'right':w-tw-5}[l.get('align','left')];d.multiline_text((x-box[0],(h-th)/2-box[1]),text,font=ft,spacing=spacing,fill=c,align=l.get('align','left'))
    elif typ=='rect':
        radius=round(l.get('radius',24)*sz); outline=rgba(l['stroke']) if 'stroke' in l else None;d.rounded_rectangle((0,0,w-1,h-1),radius=min(radius,w//2,h//2),fill=c,outline=outline,width=max(1,round(l.get('stroke_width',2)*sz)))
    elif typ=='ring':d.ellipse((0,0,w-1,h-1),outline=c,width=max(1,round(l.get('stroke_width',3)*sz)))
    elif typ=='image':
        with Image.open(l['src']) as raw:
            img=raw.convert('RGBA')
            if 'crop' in l:
                a,b,cropx,cropy=l['crop'];iw,ih=img.size;img=img.crop((round(a*iw),round(b*ih),max(round(a*iw)+1,round(cropx*iw)),max(round(b*ih)+1,round(cropy*ih))))
            img.thumbnail((w,h),Image.Resampling.LANCZOS);im.alpha_composite(img,((w-img.width)//2,(h-img.height)//2))
        if l.get('radius'):
            m=Image.new('L',(w,h));ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),radius=round(l['radius']*sz),fill=255);im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel('A')),np.asarray(m))))
    elif typ=='grid':
        step=max(4,round(l.get('step',32)*sz));r=max(1,round(l.get('dot',1.5)*sz))
        for y in range(step//2,h,step):
            for x in range(step//2,w,step):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    elif typ=='particles':
        rng=np.random.default_rng(l.get('seed',7));count=int(l.get('count',100));
        for x,y,r in zip(rng.uniform(0,w,count),rng.uniform(0,h,count),rng.uniform(1,5,count)*sz):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    elif typ=='gradient':
        yy,xx=np.ogrid[:h,:w];dist=np.sqrt(((xx-w*.5)/(w*.5))**2+((yy-h*.5)/(h*.5))**2);a=np.clip(1-dist,0,1)**2;arr=np.zeros((h,w,4),np.uint8);arr[:,:,:3]=c[:3];arr[:,:,3]=np.uint8(a*c[3]);return arr
    elif typ=='line':d.line((0,h//2,w,h//2),fill=c,width=max(1,round(l.get('stroke_width',2)*sz)))
    else:raise ValueError('unknown kind '+typ)
    return np.array(im)

def validate(shot):
    n=shot['frames'];ids=set()
    if type(shot.get('samples',1)) is not int or not 1<=shot.get('samples',1)<=8:raise ValueError('samples must be 1..8')
    if not isinstance(shot.get('shutter',.5),(int,float)) or not 0<=shot.get('shutter',.5)<=1:raise ValueError('shutter must be 0..1')
    if not 1<=len(shot['layers'])<=100:raise ValueError('1..100 layers required')
    for l in shot['layers']:
        if l['id'] in ids:raise ValueError('duplicate layer id')
        ids.add(l['id']);
        if l['kind'] not in ['text','rect','ring','image','grid','line','gradient','particles','morph','swarm']+list(KINDS):raise ValueError('unknown layer kind')
        if not 0<=l.get('start',0)<l.get('end',n)<=n:raise ValueError('bad layer bounds')
        if not isinstance(l.get('size'),list) or len(l['size'])!=2 or any(type(x)!=int or not 2<=x<=2400 for x in l['size']):raise ValueError('bad layer size')
        validate_dynamic(l);validate_optical(l)
        for key,limit in (('feather',100),('distortion',40)):
            if key in l and (type(l[key]) not in (int,float) or not 0<=l[key]<=limit):raise ValueError('invalid '+key)
        if l.get('reveal_axis','x') not in ('x','y','radial','diagonal','dissolve'):raise ValueError('bad mask')
        if l.get('kind')=='particles' and not 1<=l.get('count',100)<=1000:raise ValueError('bad particle count')
        for k in ('x','y','scale','rotation','tilt','opacity','reveal','blur','glow','depth','sx','sy','metal','shadow','progress','pitch'):
            a=l.get(k)
            if isinstance(a,list):
                if not a or any(len(p) not in (2,3) or not isinstance(p[0],(int,float)) or not isinstance(p[1],(int,float)) or not math.isfinite(p[1]) for p in a) or any(b[0]<=a[0] for a,b in zip(a,a[1:])):raise ValueError('bad keyframes '+l['id']+' '+k)
                if any(len(p)==3 and p[2] not in ('linear','out','in','inout','back','hold') for p in a):raise ValueError('unknown easing')
        if l.get('kind')=='image':
            if not Path(l['src']).is_file():raise ValueError('missing image')
            if 'crop' in l:
                c=l['crop']
                if not isinstance(c,list) or len(c)!=4 or any(type(v) not in (int,float) or not 0<=v<=1 for v in c) or not (c[0]<c[2] and c[1]<c[3]):raise ValueError('crop requires normalized [left,top,right,bottom]')

def blend(dst,rgb,a,x,y):
    h,w=a.shape;H,W=dst.shape[:2];x0=max(0,x);y0=max(0,y);x1=min(W,x+w);y1=min(H,y+h)
    if x0>=x1 or y0>=y1:return
    yy=slice(y0-y,y1-y);xx=slice(x0-x,x1-x);alpha=a[yy,xx,None].astype(np.float32)/255;region=dst[y0:y1,x0:x1];region[:]=np.clip(region*(1-alpha)+rgb[yy,xx]*alpha,0,255).astype(np.uint8)

class Scene:
    def __init__(self,w,h,shot,fp):
        validate(shot);self.w=w;self.h=h;self.s=min(w/1080,h/1920);self.shot=shot;self.layers=[(l,Dynamic(l,self.s,fp,rgba(l.get('color','#ffffff'))) if l['kind'] in ('morph','swarm') else Optical(l,self.s,rgba(l.get('color','#ffffff'))) if l['kind'] in KINDS else sprite(l,self.s,fp)) for l in shot['layers']];self.bg=np.zeros((h,w,3),np.uint8);self.bg[:]=rgba(shot.get('background','#08090c'))[:3]
        if shot.get('ambient'):
            yy,xx=np.ogrid[:h,:w];a=shot['ambient'];v=np.exp(-(((xx-w*a.get('x',.5))/(w*.65))**2+((yy-h*a.get('y',.45))/(h*.48))**2)*3)*a.get('strength',.3);color=np.array(rgba(a.get('color','#243551'))[:3]);self.bg=np.clip(self.bg.astype(np.float32)+v[:,:,None]*color,0,255).astype(np.uint8)
    def render_frame(self,f):
        return shutter(self.frame,f,self.shot['frames'],self.shot.get('samples',1),self.shot.get('shutter',.5))
    def frame(self,f):
        dst=self.bg.copy();s=self.s;w,h=self.w,self.h;cam=self.shot.get('camera',{});cx=value(cam.get('x',0),f);cy=value(cam.get('y',0),f);zoom=value(cam.get('zoom',1),f)
        for l,raw in self.layers:
            if not l.get('start',0)<=f<l.get('end',self.shot['frames']):continue
            def v(k,default):return value(l.get(k,default),f)
            op=clamp(v('opacity',1));reveal=clamp(v('reveal',1));scale=max(.005,min(8,v('scale',1)));dep=v('depth',1);z=1+(zoom-1)*dep
            if op<=.001 or reveal<=.001:continue
            X=w/2+(v('x',540)-540+cx*dep)*s*z;Y=h/2+(v('y',960)-960+cy*dep)*s*z
            # Work on premultiplied sprite to avoid black fringe on masks and transforms.
            pic=raw.sample(v('progress',0)) if isinstance(raw,Dynamic) else raw.sample(v('progress',0),f) if isinstance(raw,Optical) else raw.copy();
            if l.get('distortion',0):pic=distort(pic,f,l['distortion'],s)
            H,W=pic.shape[:2];mask=pic[:,:,3];original_mask=mask.copy() if l.get('feather',0) and reveal<1 else None;
            if reveal<1:
                axis=l.get('reveal_axis','x')
                if axis=='y':mask[round(H*reveal):,:]=0
                elif axis=='radial':
                    yy,xx=np.ogrid[:H,:W];mask[((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2>2*reveal**2]=0
                elif axis=='diagonal':
                    yy,xx=np.ogrid[:H,:W];mask[(xx/W+yy/H)>2*reveal]=0
                elif axis=='dissolve':
                    yy,xx=np.ogrid[:H,:W];mask[((xx//max(1,round(12*s))*73856093 ^ yy//max(1,round(12*s))*19349663)%1009)/1009>reveal]=0
                else:mask[:,round(W*reveal):]=0
            if original_mask is not None:
                mask[:]=np.minimum(original_mask,cv2.GaussianBlur(mask.copy(),(0,0),max(.5,l['feather']*s)))
            metal=clamp(v('metal',0))
            if metal:
                yy,xx=np.ogrid[:H,:W];p=(xx/W*.6+yy/H*.7-f*.023)%1;light=(.25+.65*np.exp(-((p-.47)/.14)**2)+.18*np.cos(p*math.tau*2));pic[:,:,:3]=np.clip(pic[:,:,:3].astype(np.float32)*(1-metal)+255*light[:,:,None]*metal,0,255).astype(np.uint8)
            sx=scale*z*max(.05,v('sx',1));sy=scale*z*max(.05,v('sy',1));angle=math.radians(v('rotation',0));tilt=math.radians(max(-75,min(75,v('tilt',0))))
            base=np.array([[-W/2,-H/2],[W/2,-H/2],[W/2,H/2],[-W/2,H/2]],np.float32);base[:,0]*=sx;base[:,1]*=sy
            # Perspective yaw around vertical axis; depth varies across a plane.
            xx=base[:,0].copy();pers=1/(1+np.sin(tilt)*xx/(max(w,h)*1.7));base[:,0]=xx*np.cos(tilt)*pers;base[:,1]*=pers
            pitch=math.radians(max(-70,min(70,v('pitch',0))));yyy=base[:,1].copy();pers2=1/(1+np.sin(pitch)*yyy/(max(w,h)*1.7));base[:,1]=yyy*np.cos(pitch)*pers2;base[:,0]*=pers2
            rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]],np.float32);pts=base@rot.T
            blur=max(0,min(30,v('blur',0)))*s;glow=max(0,min(2,v('glow',0)));shadow=clamp(v('shadow',0));pad=int(max(3,blur*4,glow*20*s,shadow*34*s));lo=np.floor(pts.min(0)).astype(int)-pad;hi=np.ceil(pts.max(0)).astype(int)+pad;outw,outh=(hi-lo).tolist()
            if outw<1 or outh<1 or outw>5*w or outh>5*h:continue
            M=cv2.getPerspectiveTransform(np.array([[0,0],[W-1,0],[W-1,H-1],[0,H-1]],np.float32),(pts-lo).astype(np.float32));alpha=pic[:,:,3].astype(np.float32)/255;prem=np.dstack((pic[:,:,:3]*alpha[:,:,None],alpha*255)).astype(np.float32);war=cv2.warpPerspective(prem,M,(outw,outh),flags=cv2.INTER_LINEAR)
            if blur>.3:war=cv2.GaussianBlur(war,(0,0),blur)
            a=np.clip(war[:,:,3]*op,0,255).astype(np.uint8);rgb=np.clip(war[:,:,:3]*255/np.maximum(war[:,:,3,None],1e-5),0,255).astype(np.uint8);px=round(X+lo[0]);py=round(Y+lo[1]);
            if shadow>.01:
                sh=cv2.GaussianBlur(a,(0,0),max(1,15*s));blend(dst,np.zeros_like(rgb),np.uint8(sh*shadow),px+round(5*s),py+round(15*s))
            if glow>.01:
                ga=cv2.GaussianBlur(a,(0,0),max(1,8*s));gcol=np.empty_like(rgb);gcol[:]=rgba(l.get('glow_color',l.get('color','#ffffff')))[:3];blend(dst,gcol,np.uint8(np.clip(ga*glow*.65,0,255)),px,py)
            # Directional trails on chosen high-speed layers only; actual prior anchor displacement.
            if l.get('trail',0) and f>0:
                dx=(v('x',540)-value(l.get('x',540),f-1))*s;dy=(v('y',960)-value(l.get('y',960),f-1))*s
                if abs(dx)+abs(dy)>2:
                    for t in (1,.55):blend(dst,rgb,np.uint8(a*.13*l['trail']),px-round(dx*t),py-round(dy*t))
            blend(dst,rgb,a,px,py)
        return dst

def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('output',type=Path);p.add_argument('--font',required=True);p.add_argument('--frame',type=int);a=p.parse_args();d=json.loads(a.plan.read_text());w,h,fps=[d[k] for k in ('width','height','fps')];assert w%2==0 and h%2==0
    scenes=[Scene(w,h,s,a.font) for s in d['shots']];a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.frame is not None:Image.fromarray(scenes[0].render_frame(a.frame)).save(a.output);return
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for scene in scenes:
            for f in range(scene.shot['frames']):proc.stdin.write(scene.render_frame(f).tobytes())
    finally:proc.stdin.close();rc=proc.wait()
    if rc:raise RuntimeError('ffmpeg failed')
if __name__=='__main__':main()
