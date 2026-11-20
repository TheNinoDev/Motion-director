#!/usr/bin/env python3
"""Headless editorial shot renderer. Coordinates are normalized to a 720x1280 artboard.
No external assets beyond a product screenshot and installed fonts; deterministic frames.
"""
import argparse,json,math,subprocess,functools
from pathlib import Path
import numpy as np, cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(1)
KINDS={'impact','artifact','filmstrip','detail','lockup','typewall','split','reframe'}

def ease(t): t=max(0,min(1,t));return 1-(1-t)**3
def smooth(t): t=max(0,min(1,t));return t*t*(3-2*t)
def rgb(s): return tuple(bytes.fromhex(s.lstrip('#')))

def validate(s):
    if s.get('kind') not in KINDS: raise ValueError('unknown cinematic kind')
    if type(s.get('frames')) is not int or not 4<=s['frames']<=3600: raise ValueError('invalid frame count')
    for k in ('headline','label','brand','sub','cta'):
        if k in s and (not isinstance(s[k],str) or len(s[k])>120):raise ValueError('invalid '+k)
    for k in ('background','foreground','accent'):
        if k in s and (not isinstance(s[k],str) or len(s[k])!=7 or not s[k].startswith('#')):raise ValueError('invalid color')
        if k in s:rgb(s[k])
    if s['kind'] in {'filmstrip','detail','split','reframe'} and not Path(s.get('src','')).is_file():raise ValueError('product screenshot required')
    if 'crop' in s:
        c=s['crop'];
        if len(c)!=4 or not all(0<=x<=1 for x in c) or not (c[0]<c[2] and c[1]<c[3]):raise ValueError('bad normalized crop')
    for k in ('grain','bloom','chromatic','vignette'):
        if k in s and (not isinstance(s[k],(int,float)) or not 0<=s[k]<=1):raise ValueError('invalid '+k)
    if s.get('layout','left') not in {'left','center'}:raise ValueError('invalid layout')
    for k,lo,hi in [('camera_strength',0,2),('text_scale',.65,1.25),('panel_scale',.65,1.35),('artifact_scale',.5,1.5)]:
        if k in s and (not isinstance(s[k],(int,float)) or not lo<=s[k]<=hi):raise ValueError('invalid '+k)
    if s.get('material','chrome') not in {'chrome','glass','ceramic'}:raise ValueError('bad material')
    if s.get('shape','ring') not in {'ring','sphere','disc'}:raise ValueError('bad shape')

@functools.lru_cache(maxsize=256)
def font(path,size):return ImageFont.truetype(path,max(8,int(size)))

def find_font(primary,style):
    p=Path(primary); options={'regular':['InterDisplay-Regular.otf','Inter-Regular.otf','DejaVuSans.ttf','arial.ttf'],'mono':['DejaVuSansMono.ttf','Consolas.ttf'],'heavy':['InterDisplay-Black.otf','Inter-Black.otf','DejaVuSans-Bold.ttf','arialbd.ttf']}
    for directory in [p.parent,Path('/usr/share/fonts/opentype/inter'),Path('/usr/share/fonts/truetype/dejavu')]:
        for n in options[style]:
            if (directory/n).is_file():return str(directory/n)
    return str(p)

class Scene:
    def __init__(self,w,h,shot,fp):
        validate(shot);self.w=w;self.h=h;self.s=shot;self.scale=min(w/720,h/1280);self.ox=(w-720*self.scale)/2;self.oy=(h-1280*self.scale)/2
        self.fonts={'heavy':find_font(fp,'heavy'),'regular':find_font(fp,'regular'),'mono':find_font(fp,'mono')};self.fonts['main']=str(fp)
        self.bg=rgb(shot.get('background','#08090b'));self.fg=rgb(shot.get('foreground','#f3f4f6'));self.ac=rgb(shot.get('accent','#c6c9fa'));self.source=Image.open(shot['src']).convert('RGB') if 'src' in shot else None
        self.src_crop=self.source
        if self.source and 'crop' in shot:
            sw,sh=self.source.size; self.src_crop=self.source.crop(tuple(round(a*b) for a,b in zip(shot['crop'],[sw,sh,sw,sh])))
        yy,xx=np.ogrid[:h,:w];self.vig=np.clip(((xx-w/2)/(w*.7))**2+((yy-h/2)/(h*.7))**2,0,1).astype(np.float32)
        self.noise=np.random.default_rng(17).normal(0,1,(h,w)).astype(np.float32)
        self.base=Image.new('RGB',(w,h),self.bg)
    def xy(self,x,y):return (round(x*self.scale+self.ox),round(y*self.scale+self.oy))
    def text(self,im,s,x,y,size=80,color=None,style='heavy',align='left',width=620):
        if not s:return
        if style=='heavy':size*=self.s.get('text_scale',1)
        d=ImageDraw.Draw(im);f=font(self.fonts[style],size*self.scale)
        while max(d.textlength(q,font=f) for q in s.split('\n'))>width*self.scale and f.size>9:f=font(self.fonts[style],f.size-1)
        d.multiline_text(self.xy(x,y),s,font=f,fill=color or self.fg,anchor={'left':'la','center':'ma','right':'ra'}[align],spacing=round(size*.025*self.scale),align=align)
    def line(self,im,a,b,color=None,width=1):ImageDraw.Draw(im).line([self.xy(*a),self.xy(*b)],fill=color or self.fg,width=max(1,round(width*self.scale)))
    def micro(self,im,label,y=144):
        self.text(im,label,48,y,15,self.ac,'mono',width=620);self.line(im,(48,y+35),(672,y+35),tuple(int(a*.24+b*.76) for a,b in zip(self.fg,self.bg)))
    def panel(self,im,img,cx,cy,ww,angle=0,pitch=0,shadow=True):
        # Real image (not fabricated UI); perspective homography with smooth antialiasing.
        tw=max(8,round(ww*self.scale*self.s.get('panel_scale',1)));th=max(8,round(tw*img.height/img.width)); pic=np.array(img.resize((tw,th),Image.Resampling.LANCZOS));W,H=self.w,self.h
        X,Y=self.xy(cx,cy);a=math.radians(angle);p=math.radians(pitch);base=np.array([[-tw/2,-th/2],[tw/2,-th/2],[tw/2,th/2],[-tw/2,th/2]],np.float32);xx=base[:,0].copy();q=1/(1+np.sin(p)*xx/max(tw*2,1));base[:,0]=xx*np.cos(p)*q;base[:,1]*=q;rot=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]);corners=(base@rot.T+[X,Y]).astype(np.float32)
        M=cv2.getPerspectiveTransform(np.float32([[0,0],[tw-1,0],[tw-1,th-1],[0,th-1]]),corners);mask=np.full((th,tw),255,np.uint8);mask=cv2.warpPerspective(mask,M,(W,H));war=cv2.warpPerspective(pic,M,(W,H));dst=np.array(im);alpha=mask[:,:,None]/255.
        if shadow: sh=cv2.GaussianBlur(mask,(0,0),max(1,13*self.scale));dst=(dst*(1-.50*sh[:,:,None]/255)).astype(np.uint8)
        dst=(dst*(1-alpha)+war).clip(0,255).astype(np.uint8);im.paste(Image.fromarray(dst));ImageDraw.Draw(im).line([tuple(c) for c in corners]+[tuple(corners[0])],fill=tuple(int(a*.35+b*.65) for a,b in zip(self.fg,self.bg)),width=max(1,round(self.scale)))
    def artifact(self,im,t,cx=360,cy=635,r=253):
        # Analytic sphere normals; hole/disc cut in view space. Studio environment is artistic, not path traced.
        size=max(12,round(r*2*self.scale*self.s.get('artifact_scale',1)));axis=(np.arange(size,dtype=np.float32)+.5-size/2)/(size*.5);x,y=np.meshgrid(axis,axis);ang=.22+.55*math.sin(t*math.pi);X=x*np.cos(ang)+y*np.sin(ang);Y=(-x*np.sin(ang)+y*np.cos(ang))/(.72+.17*math.cos(t*math.pi));rad=np.sqrt(X*X+Y*Y);shape=self.s.get('shape','ring');
        if shape=='ring': q=(rad-.67)/.30;z=np.sqrt(np.maximum(0,1-q*q));nx=q*X/np.maximum(rad,.001);ny=q*Y/np.maximum(rad,.001);nz=z;mask=np.clip((1-np.abs(q))*size*.18,0,1)
        else: z=np.sqrt(np.maximum(0,1-rad**2));nx=X;ny=Y;nz=z;mask=np.clip((1-rad)*size*.6,0,1)
        if shape=='disc':nz=np.clip(z*3,0,1);norm=np.sqrt(nx*nx+ny*ny+nz*nz);nx/=np.maximum(norm,.001);ny/=np.maximum(norm,.001);nz/=np.maximum(norm,.001)
        rx=2*nz*nx;ry=2*nz*ny;rz=2*nz*nz-1
        # broad softboxes, very dark negative fill, curved reflected strips
        strip=np.exp(-((rx-(.32-.60*t))/.13)**4)*np.clip((ry+.80)*1.8,0,1);strip2=np.exp(-((rx+.65)/.19)**4)*np.clip((.9-ry)*1.3,0,1);top=np.exp(-((ry+.65)/.30)**4);fres=(1-nz)**3
        mat=self.s.get('material','chrome');L=.012+1.10*strip+.66*strip2+.46*top+.09*np.maximum(rz,0)+.16*fres
        if mat=='glass':L=.025+.52*strip+.27*strip2+.15*top+.65*fres; tint=np.array([.71,.83,1.0]);
        elif mat=='ceramic': L=.11+.55*nz+.20*strip+.16*top;tint=np.array([.88,.90,.96])
        else:tint=np.array([.96,.98,1.0]);
        col=(np.clip(L[:,:,None]*tint,0,1)**.69*255).astype(np.uint8);a=(mask*255).astype(np.uint8);pic=Image.fromarray(np.dstack((col,a)));im.paste(pic,(self.xy(cx,cy)[0]-size//2,self.xy(cx,cy)[1]-size//2),pic)
    def frame(self,f):
        s=self.s;n=s['frames'];t=f/max(1,n-1);p=ease(t*2.8);motion=s.get('camera_strength',1);kind=s['kind'];im=self.base.copy();head=s.get('headline','');label=s.get('label','');sub=s.get('sub','');brand=s.get('brand','');
        if kind=='impact':
            # Stable typographic anchor; decisive line reveal instead of opacity-only slide.
            self.micro(im,label);lines=head.split('\n');center=s.get('layout')=='center';tx=360 if center else 48;
            for i,word in enumerate(lines):
                q=ease((t-.10*i)*4);layer=Image.new('RGB',im.size,self.bg);self.text(layer,word,tx,390+i*142+65*(1-q),132,self.fg if i==0 else self.ac,align='center' if center else 'left',width=624);box=(0,self.xy(0,390+i*142)[1],self.w,self.xy(0,390+i*142+155)[1]);im.paste(layer.crop(box),box[:2]);
            self.text(im,sub,50,975,24,self.fg,'regular');self.line(im,(48,1040),(48+624*p,1040),self.ac,2)
        elif kind=='artifact':
            self.micro(im,label);self.artifact(im,t,360,640,280+120*(1-p)*motion);self.text(im,head,360,940,72,align='center');self.text(im,sub,360,1037,20,self.ac,'mono','center')
        elif kind=='filmstrip':
            self.micro(im,label);shift=360*smooth(t)*motion;sw,sh=self.source.size;left=self.source.crop((int(sw*.03),int(sh*.25),int(sw*.52),int(sh*.62)));right=self.source.crop((int(sw*.52),int(sh*.25),int(sw*.97),int(sh*.62)));self.panel(im,left,10+shift,640,475,-9,18);self.panel(im,right,640-shift*.44,875,465,7,-14);self.text(im,head,48,218,76,width=625);self.text(im,sub,48,1100,23,self.ac,'regular')
        elif kind=='detail':
            self.micro(im,label); # macro proof, no simulated interaction
            self.panel(im,self.src_crop,360,560,670+100*(1-p)*motion,0,0);self.text(im,head,48,910,74,width=625);self.text(im,sub,48,1070,19,self.ac,'mono')
        elif kind=='split':
            self.micro(im,label);self.text(im,head,48,265,93,width=620);self.panel(im,self.source,360+70*(1-p),735,638,4*(1-p),18*(1-p));self.text(im,sub,48,1060,23,self.ac,'regular')
        elif kind=='reframe':
            self.micro(im,label);self.panel(im,self.source,360,640,650+(1-p)*720*motion,0,0,False);self.text(im,head,48,1000,64,width=620);self.text(im,sub,48,1090,20,self.ac,'mono')
        elif kind=='typewall':
            for i in range(13):
                v=(t*450*(1 if i%2 else -1)+i*110)%680;self.text(im,(head+'   ')*2,-v,125+i*74,64,tuple(int(a*.18+b*.82) for a,b in zip(self.fg,self.bg)),width=1800)
            d=ImageDraw.Draw(im);d.rectangle((*self.xy(0,510),*self.xy(720,750)),fill=self.bg);self.text(im,sub or head,360,555,80,align='center');self.micro(im,label)
        elif kind=='lockup':
            self.text(im,brand or head,360,530-22*(1-p),155,align='center',width=620);self.line(im,(360-250*p,755),(360+250*p,755),self.ac);self.text(im,sub,360,795,28,self.fg,'regular','center');self.text(im,s.get('cta',''),360,1010,21,self.ac,'mono','center')
        a=np.array(im);g=s.get('grain',.12);b=s.get('bloom',0);c=s.get('chromatic',0);v=s.get('vignette',.10)
        if b:
            bright=np.maximum(a.astype(np.float32)-200,0);a=np.clip(a+cv2.GaussianBlur(bright,(0,0),max(1,8*self.scale))*b,0,255)
        if c:
            shift=max(1,round(4*c*self.scale));a=a.copy();a[:,:,0]=np.roll(a[:,:,0],shift,axis=1);a[:,:,2]=np.roll(a[:,:,2],-shift,axis=1)
        return np.clip(a*(1-self.vig[:,:,None]*v)+np.roll(self.noise,f%29,axis=0)[:,:,None]*g*5,0,255).astype(np.uint8)

def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('output',type=Path);p.add_argument('--font',required=True);p.add_argument('--frame',type=int);a=p.parse_args();d=json.loads(a.plan.read_text());w,h,fps=(d[k] for k in ('width','height','fps'));scenes=[Scene(w,h,s,a.font) for s in d['shots']];a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.frame is not None:Image.fromarray(scenes[0].frame(a.frame)).save(a.output);return
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],stdin=subprocess.PIPE)
    try:
        for s in scenes:
            for f in range(s.s['frames']):proc.stdin.write(s.frame(f).tobytes())
    finally:proc.stdin.close();rc=proc.wait()
    if rc:raise RuntimeError('ffmpeg failed')
if __name__=='__main__':main()
