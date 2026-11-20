#!/usr/bin/env python3
"""Headless typography presets. Synthetic timings are preview-only."""
import argparse, functools, json, os, shutil, subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor

def check(x,msg):
    if not x: raise ValueError(msg)
def ease(t): return 1-(1-max(0,min(1,t)))**3
@functools.lru_cache(maxsize=256)
def mask(text,path,size,maxw):
    f=ImageFont.truetype(path,max(1,size)); b=f.getbbox(text)
    if b[2]-b[0]>maxw:
        f=ImageFont.truetype(path,max(1,int(size*maxw/(b[2]-b[0])))); b=f.getbbox(text)
    im=Image.new('L',(max(1,b[2]-b[0]+2),max(1,b[3]-b[1]+2))); ImageDraw.Draw(im).text((1-b[0],1-b[1]),text,font=f,fill=255);return im

def paste(im,text,path,size,x,y,w,fill,opacity=1,chrome=False,t=0,left=False):
    if not text or opacity<=0:return
    m=mask(str(text),path,int(size),int(w)); h,ww=m.height,m.width; xx=int(x if left else x-ww/2); yy=int(y-h/2); opacity=max(0,min(1,opacity)); alpha=m.point(lambda p:int(p*opacity))
    if chrome:
        depth=max(2,int(size*.04))
        for k in range(depth,0,-1):
            v=int(35+85*(1-k/depth)); im.paste((v,v,v+5),(xx+k,yy+k),alpha)
        Y,X=np.mgrid[0:h,0:ww]; q=Y/max(1,h-1); sweep=X/max(1,ww-1)+q*.45
        v=np.interp(q,[0,.17,.39,.50,.57,.78,1],[235,255,155,250,50,105,220]); v+=62*np.exp(-((sweep-(.15+1.1*t))/.12)**2)
        edge=np.maximum(0,np.asarray(m,dtype=float)-np.asarray(m.filter(ImageFilter.MinFilter(3)),dtype=float))/255
        v=np.clip(v+edge*95,0,255).astype('uint8'); rgb=np.stack([v,v,np.minimum(v.astype('int16')+5,255).astype('uint8')],axis=-1)
        im.paste(Image.fromarray(rgb),(xx,yy),alpha)
    else: im.paste(ImageColor.getrgb(fill),(xx,yy),alpha)

def validate(p):
    for k in ('width','height','fps'):check(type(p.get(k)) is int and p[k]>0,k+' must be positive integer')
    check(p['width']%2==p['height']%2==0 and 160<=p['width']<=2160 and 160<=p['height']<=3840 and p['fps']<=120,'unsupported dimensions/fps')
    check(isinstance(p.get('shots'),list) and p['shots'],'shots required')
    for i,s in enumerate(p['shots']):
        k=s.get('kind'); n=s.get('frames'); check(k in ('hero','list','marquee','carousel','words','counter'),f'shot {i}: unknown kind');check(type(n) is int and 1<=n<=7200,'invalid frame count')
        if k in ('hero','list'):check(isinstance(s.get('text'),str) and s['text'].strip(),'text required')
        if k in ('list','carousel','marquee'):
            items=s.get('items');check(isinstance(items,list) and 1<=len(items)<=100 and all(isinstance(x,str) and 0<len(x)<=100 for x in items),'invalid items')
            if k=='list':check(len(items)<=12,'list max 12 items')
            if k=='carousel':check(n>=len(items)*4,'carousel requires >=4 frames per item')
        if k=='counter':check(all(type(s.get(x)) is int and abs(s[x])<=10**12 for x in ('from','to')),'invalid counter values')
        if k=='words':
            words=s.get('words');check(isinstance(words,list) and 1<=len(words)<=60,'words required');last=-1
            for w in words:
                f=w.get('frame');check(isinstance(w.get('text'),str) and w['text'].strip() and type(f) is int and 0<=f<n and last<=f,'invalid word cue');last=f
            check(s.get('timing_source') in ('verified_alignment','manual_verified','synthetic_demo'),'explicit timing_source required')
    check(sum(s['frames'] for s in p['shots'])<=36000,'plan too long');return p

def frame(p,s,f,path):
    W,H=p['width'],p['height'];n=s['frames'];t=f/max(1,n-1);k=s['kind'];fg=s.get('foreground',p.get('foreground','#f6f5f1'));im=Image.new('RGB',(W,H),s.get('background',p.get('background','#090a0c')));mx=W*.86
    def txt(text,size,x,y,width=mx,fill=fg,op=1,metal=False,left=False):paste(im,text,path,W*size,x,y,width,fill,op,metal,t,left)
    if s.get('label'):txt(s['label'],.026,W*.07,H*.105,fill='#8d929b',left=True)
    if k=='hero':
        q=ease(f/max(1,min(n*.33,18)));txt(s['text'],.52*(.83+.17*q),W*.5,H*.39,metal=s.get('chrome',True))
        if s.get('subtitle'):txt(s['subtitle'],.083,W*.5,H*.65,op=ease((t-.17)*5))
    elif k=='list':
        txt(s['text'],.22,W*.5,H*.24,metal=s.get('chrome',True));items=s['items'];step=min(H*.049,H*.43/len(items))
        for j,item in enumerate(items):
            q=ease((f-j*max(1,int(n*.55/len(items))))/7);txt(item,.058,W*.12+(1-q)*W*.06,H*.39+j*step,op=q,left=True)
    elif k=='marquee':
        items=s['items'];step=W*.47
        for r in range(6):
            shift=f*W*.006*(1 if r%2==0 else -1)+r*step*.53; cell=int(shift//step);offset=shift%step
            for c in range(-2,4):txt(items[(c-cell+r*3)%len(items)],.059,c*step+offset,H*(.34+r*.064),width=step*.89,fill='#54565e',left=True)
        if s.get('title'):txt(s['title'],.13,W*.5,H*.22)
        if s.get('subtitle'):txt(s['subtitle'],.054,W*.5,H*.78)
    elif k=='carousel':
        items=s['items'];pos=f*len(items)/n;j=min(len(items)-1,int(pos));q=pos-j;a=ease(q*4)
        if j>0 and q<.25:txt(items[j-1],.13,W*.5-W*.11*a,H*.43,op=1-a)
        txt(items[j],.14,W*.5+W*.11*(1-a) if j else W*.5,H*.43,op=a if j else 1,metal=s.get('chrome',False))
        if s.get('anchor'):txt(s['anchor'],.1,W*.5,H*.55,metal=True)
        txt(f'{j+1:02d} / {len(items):02d}',.034,W*.5,H*.72,fill='#888a92')
    elif k=='counter':
        value=round(s['from']+(s['to']-s['from'])*ease(t));txt(f'{value:,}',.38,W*.5,H*.43,metal=s.get('chrome',True))
        if s.get('subtitle'):txt(s['subtitle'],.075,W*.5,H*.62)
    elif k=='words':
        words=s['words'];size=int(W*.092);gap=int(W*.023);lines=[[]];used=0
        for i,w in enumerate(words):
            tw=mask(w['text'],path,size,int(mx)).width
            if used and used+tw>mx:lines.append([]);used=0
            lines[-1].append((i,used));used+=tw+gap
        check(len(lines)<=6 and H*.28+(len(lines)-1)*W*.13<H*.78,'word shot too tall: split')
        for r,row in enumerate(lines):
            for i,x in row:
                w=words[i];q=ease((f-w['frame']+1)/5);txt(w['text'],size/W,W*.07+x,H*.28+r*W*.13+(1-q)*W*.025,fill=w.get('color',fg),op=q,left=True)
    return im

def main():
    a=argparse.ArgumentParser();a.add_argument('plan');a.add_argument('output');a.add_argument('--font',required=True);a.add_argument('--frame',type=int);a.add_argument('--allow-synthetic-timing',action='store_true');args=a.parse_args()
    try:
        p=validate(json.loads(Path(args.plan).read_text(encoding='utf-8')));ImageFont.truetype(args.font,32)
        check(args.allow_synthetic_timing or all(s.get('timing_source')!='synthetic_demo' for s in p['shots']),'synthetic timing preview only; explicit flag required')
        for s in p['shots']:frame(p,s,s['frames']-1,args.font)
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
        if args.frame is not None:
            i=args.frame;check(i>=0,'negative frame')
            for s in p['shots']:
                if i<s['frames']:frame(p,s,i,args.font).save(out);return
                i-=s['frames']
            raise ValueError('frame out of range')
        check(shutil.which('ffmpeg') and out.suffix.lower()=='.mp4','ffmpeg required and output must be .mp4')
        with tempfile.TemporaryDirectory(dir=out.parent) as td:
            tmp=Path(td)/'out.mp4';cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f"{p['width']}x{p['height']}",'-r',str(p['fps']),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
            try:
                for s in p['shots']:
                    for f in range(s['frames']):proc.stdin.write(frame(p,s,f,args.font).tobytes())
                proc.stdin.close();check(proc.wait()==0,'ffmpeg failed');os.replace(tmp,out)
            finally:
                if proc.poll() is None:proc.kill();proc.wait()
        print('Rendered',sum(s['frames'] for s in p['shots']),'frames',out)
    except (ValueError,KeyError,TypeError,OSError,AttributeError) as e:a.exit(2,f'ERROR: {e}\n')
if __name__=='__main__':main()
