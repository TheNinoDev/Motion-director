#!/usr/bin/env python3
"""Standalone deterministic motion primitives. Pillow + NumPy + FFmpeg, no GUI.
Use --frame to inspect direct nonsequential rendering. All timing is frame-based.
"""
import argparse, json, math, pathlib, shutil, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor
P=pathlib.Path
KINDS={'type','wireframe','dots','character','hold'}
POSES={'neutral':(0,0,0.0,0.0,1.0),'curious':(.25,.12,.05,-.2,1.0),'smirk':(.65,.55,.15,.2,1.03),'grin':(1,.95,.3,.5,1.12),'surprised':(-.4,.15,.85,-.1,1.04),'blink':(0,0,0,0,.08)}
def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,t):return a+(b-a)*t
def require(ok,msg):
    if not ok:raise ValueError(msg)
def validate(d,root):
    for k in ('width','height','fps'):require(type(d.get(k))==int and 0<d[k]<= (120 if k=='fps' else 4096),'invalid '+k)
    require(d['width']%2==d['height']%2==0,'even raster required')
    require(isinstance(d.get('shots'),list) and d['shots'],'shots required')
    for s in d['shots']:
        k=s.get('kind');require(k in KINDS,'unknown shot type');n=s.get('frames');require(type(n)==int and n>0,'positive integer frames required')
        for c in ('background','color','character_color'):
            if c in s:ImageColor.getrgb(s[c])
        if k in ('type','dots','hold'):require(isinstance(s.get('text'),str) and 0<len(s['text'])<=180,'text required (max 180 chars)')
        if k=='type':require(type(s.get('reveal_frames',12))==int and s.get('reveal_frames',12)>0,'invalid reveal_frames')
        if k=='wireframe':
            require((root/s['src']).is_file(),'missing image');require(isinstance(s.get('boxes'),list) and 1<=len(s['boxes'])<=100,'boxes required')
            for b in s['boxes']:require(len(b)==4 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in b) and 0<=b[0]<b[2]<=1 and 0<=b[1]<b[3]<=1,'boxes must be normalized x0,y0,x1,y1')
        if k=='character':
            keys=s.get('poses',[]);require(keys and all(len(a)==2 and type(a[0])==int and 0<=a[0]<n and a[1] in POSES for a in keys),'invalid poses');require(keys[0][0]==0 and [a[0] for a in keys]==sorted(set(a[0] for a in keys)),'poses must start at 0 and increase')
            for prop in ('zoom','squash'):
                keys=s.get(prop,[[0,1]]);require(keys and all(len(a)==2 and type(a[0])==int and 0<=a[0]<n and isinstance(a[1],(int,float)) and math.isfinite(a[1]) and .2<=a[1]<=3 for a in keys),'invalid '+prop);require([a[0] for a in keys]==sorted(set(a[0] for a in keys)),'keys must increase')
    return sum(s['frames'] for s in d['shots'])
def sample(keys,f,convert=lambda x:x):
    if f<=keys[0][0]:return convert(keys[0][1])
    for a,b in zip(keys,keys[1:]):
        if f<=b[0]:return lerp(convert(a[1]),convert(b[1]),smooth((f-a[0])/(b[0]-a[0])))
    return convert(keys[-1][1])
def fit_text(text,font,w,h,frac=.15):
    size=max(10,int(w*frac));dr=ImageDraw.Draw(Image.new('L',(1,1)))
    while size>=10:
        ft=ImageFont.truetype(font,size);b=dr.multiline_textbbox((0,0),text,font=ft,spacing=int(size*.07),align='center')
        if b[2]-b[0]<=w*.88 and b[3]-b[1]<=h*.65:break
        size-=2
    require(size>=10,'text will not fit: shorten or add line break')
    m=Image.new('L',(w,h));ImageDraw.Draw(m).multiline_text(((w-(b[2]-b[0]))/2-b[0],(h-(b[3]-b[1]))/2-b[1]),text,font=ft,fill=255,spacing=int(size*.07),align='center');return m

def tinted(base,mask,col):base.paste(col,(0,0),mask);return base

def sphere(size,col):
    yy,xx=np.mgrid[-1:1:complex(size),-1:1:complex(size)];r=xx*xx+yy*yy;z=np.sqrt(np.maximum(0,1-r));light=np.maximum(0,-.44*xx-.52*yy+.73*z);bright=.26+.72*light;spec=np.maximum(0,-.35*xx-.45*yy+.82*z)**36;rgb=np.array(ImageColor.getrgb(col)[:3]);arr=np.clip(bright[...,None]*rgb+spec[...,None]*95,0,255).astype('uint8');a=np.clip((1-r)*size/4*255,0,255).astype('uint8');return Image.fromarray(np.dstack((arr,a)))
def face(base,raw,s,f,w,h):
    brow,smile,open_,tilt,eye=sample(s['poses'],f,lambda x:np.array(POSES[x]));zoom=sample(s.get('zoom',[[0,1]]),f);squash=sample(s.get('squash',[[0,1]]),f);N=raw.width;im=raw.copy();d=ImageDraw.Draw(im);u=N/400
    def box(x,y,a,b):return tuple(round(q*u) for q in (x,y,a,b))
    def line(points,fill,width):d.line([(round(x*u),round(y*u)) for x,y in points],fill=fill,width=max(1,round(width*u)),joint='curve')
    # Face landmarks remain anchored; eyelids, brows, smile and pupil move independently.
    eyeh=max(3,40*eye-10*brow)
    for side in (-1,1):
        x=200+side*65;y=153+side*tilt*7
        d.ellipse(box(x-31,y-eyeh/2,x+31,y+eyeh/2),fill='#f6f4ff',outline='#443955',width=max(1,round(2*u)))
        if eye>.12:
            px=x+side*4+tilt*7;d.ellipse(box(px-9,y-9*eye,px+9,y+9*eye),fill='#292141');d.ellipse(box(px-4,y-5*eye,px,y-1*eye),fill='white')
        line([(x-33,y-35-side*brow*10),(x-7,y-42),(x+32,y-36+side*brow*17)],'#302044',7)
    if smile>.12:
        width=55+smile*52;cy=245;depth=8+smile*49+open_*18
        xs=np.linspace(-1,1,60);top=[(200+x*width,cy+10*(1-x*x)-tilt*x*9) for x in xs];bottom=[(200+x*width,cy+depth*(1-x*x)-tilt*x*9) for x in xs[::-1]]
        d.polygon([(round(x*u),round(y*u)) for x,y in top+bottom],fill='#241333')
        if smile>.48:
            for x in np.linspace(-width*.8,width*.8,9):
                y=cy+10*(1-(x/width)**2)-tilt*x/width*9
                d.rounded_rectangle(box(200+x-7,y+2,200+x+7,y+min(13,depth*.30)),radius=max(1,round(3*u)),fill='#fff5ee')
    elif open_>.35:d.ellipse(box(185,235,215,235+open_*42),fill='#302044')
    else:line([(180,252),(200,254),(220,252)],'#302044',5)
    target=int(w*.69*zoom);im=im.resize((max(1,int(target/squash**.5)),max(1,int(target*squash))),Image.Resampling.LANCZOS);im=im.rotate(-tilt*5,Image.Resampling.BICUBIC,expand=True);base.paste(im,((w-im.width)//2,(h-im.height)//2),im);return base

def prepare(s,w,h,root,font):
    k=s['kind'];c={}
    if k in ('type','dots','hold'):c['mask']=fit_text(s['text'],font,w,h,s.get('size_fraction',.16))
    if k=='wireframe':
        im=Image.open(root/s['src']).convert('RGB');im.thumbnail((int(w*.83),int(h*.70)),Image.Resampling.LANCZOS);c['img']=im
    if k=='character':c['face']=sphere(min(1000,max(400,w)),s.get('character_color','#a384ed'))
    return c

def frame(s,c,f,w,h):
    bg=s.get('background','#101018');col=s.get('color','#f5f4f8');base=Image.new('RGB',(w,h),bg);k=s['kind'];p=f/max(1,s['frames']-1)
    if k in ('type','hold'):
        mask=c['mask'].copy()
        if k=='type':
            # Reveal horizontal bands in reading order without text reflow.
            y0=mask.getbbox()[1];y1=mask.getbbox()[3];edge=round(y0+(y1-y0)*smooth(f/max(1,s.get('reveal_frames',12))));ImageDraw.Draw(mask).rectangle((0,edge,w,h),fill=0) if edge<y1 else None
        return tinted(base,mask,col)
    if k=='dots':
        q=smooth((p-.18)/.28);r=smooth((p-.62)/.35);m=c['mask'];a=np.array(m);step=max(4,round(w*.018));dr=ImageDraw.Draw(base);scale=lerp(1,.46,r)
        if q<1:base=tinted(base,m.point(lambda x:round(x*(1-q))),col)
        rgb=np.array(ImageColor.getrgb(col)[:3]);br=np.array(ImageColor.getrgb(bg)[:3]);dot=tuple(np.round(lerp(br,rgb,q)).astype(int))
        for y in range(0,h,step):
            for x in range(0,w,step):
                if a[y,x]>100:
                    X=w/2+(x-w/2)*scale;Y=h/2+(y-h/2)*scale;rad=max(1,step*.24*scale);dr.ellipse((X-rad,Y-rad,X+rad,Y+rad),fill=dot)
        return base
    if k=='wireframe':
        im=c['img'];iw,ih=im.size;x=(w-iw)/2;y=(h-ih)/2;q=smooth(p/.40);collapse=smooth((p-.5)/.5);base.paste(Image.blend(im,Image.new('RGB',im.size,bg),q),(round(x),round(y)));dr=ImageDraw.Draw(base);linecol=tuple(np.round(lerp(np.array(ImageColor.getrgb(bg)[:3]),np.array(ImageColor.getrgb(col)[:3]),q*.8)).astype(int));end=(w*.38,h*.38,w*.62,h*.62)
        for b in s['boxes']:
            old=(x+b[0]*iw,y+b[1]*ih,x+b[2]*iw,y+b[3]*ih);a=tuple(lerp(i,j,collapse) for i,j in zip(old,end));dr.rectangle(a,outline=linecol,width=max(1,round(w*.0025)))
        if collapse>.85:dr.line((end[0],end[1],end[2],end[3]),fill=linecol,width=1);dr.line((end[2],end[1],end[0],end[3]),fill=linecol,width=1)
        return base
    return face(base,c['face'],s,f,w,h)

def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=P);p.add_argument('output',type=P);p.add_argument('--font',default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf');p.add_argument('--frame',type=int);args=p.parse_args();d=json.loads(args.plan.read_text());root=args.plan.resolve().parent;n=validate(d,root);w,h,fps=(d[k] for k in ('width','height','fps'));require(P(args.font).is_file(),'font missing; pass --font');args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.frame is not None:
        require(0<=args.frame<n,'frame outside timeline');f=args.frame
        for s in d['shots']:
            if f<s['frames']:frame(s,prepare(s,w,h,root,args.font),f,w,h).save(args.output);return
            f-=s['frames']
    require(shutil.which('ffmpeg'),'ffmpeg missing');require(args.output.suffix.lower()=='.mp4','movie output must be .mp4')
    # Atomic destination: failed render must not leave a seemingly successful export.
    with tempfile.TemporaryDirectory(dir=args.output.parent) as td:
        tmp=P(td)/'render.mp4';proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','fast','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
        try:
            for s in d['shots']:
                c=prepare(s,w,h,root,args.font)
                for f in range(s['frames']):proc.stdin.write(frame(s,c,f,w,h).tobytes())
            proc.stdin.close();require(proc.wait()==0,'ffmpeg failed');tmp.replace(args.output)
        except BaseException:
            if proc.poll() is None:proc.kill();proc.wait()
            raise
    print(f'{n} frames, {n/fps:.3f}s: {args.output}')
if __name__=='__main__':main()
