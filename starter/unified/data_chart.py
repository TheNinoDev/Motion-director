#!/usr/bin/env python3
"""Frame-accurate data storytelling graphics, driven by real/illustrative provenance."""
import argparse, json, math, subprocess, sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

def clamp(t):return min(1,max(0,t))
def ease(t):t=clamp(t);return 1-(1-t)**3

def fmt(v):
    return f'{v:,.0f}' if abs(v-round(v))<.000001 else f'{v:,.1f}'

def validate(d):
    w,h,fps=(d.get(k) for k in ('width','height','fps'))
    if not all(type(x)==int for x in (w,h,fps)) or w%2 or h%2 or not 160<=w<=2160 or not 160<=h<=3840 or not 1<=fps<=60:raise ValueError('Invalid raster/fps')
    shots=d.get('shots')
    if not isinstance(shots,list) or not shots:raise ValueError('At least one shot required')
    for s in shots:
        kind=s.get('kind');n=s.get('frames');prov=s.get('provenance')
        if kind not in ('line','bars','metric','logs') or type(n)!=int or not 4<=n<=1800:raise ValueError('Invalid shot type or frames')
        if prov not in ('illustrative','verified'):raise ValueError('provenance must be illustrative or verified')
        if prov=='verified' and not isinstance(s.get('evidence'),str):raise ValueError('Verified data requires evidence source')
        if prov=='verified' and not s.get('evidence','').strip():raise ValueError('Verified data source cannot be empty')
        if not isinstance(s.get('label'),str) or not s['label'].strip() or len(s['label'])>80:raise ValueError('Invalid label')
        if not isinstance(s.get('unit',''),str) or len(s.get('unit',''))>24:raise ValueError('Invalid unit')
        if kind in ('line','bars','metric'):
            vals=s.get('values')
            if not isinstance(vals,list) or not (1 if kind=='metric' else 2)<=len(vals)<=30 or not all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in vals):raise ValueError('Invalid numeric values')
            if max(vals)==0:raise ValueError('At least one value must be positive')
        if kind=='logs':
            vals=s.get('events')
            if not isinstance(vals,list) or not 1<=len(vals)<=12 or not all(isinstance(v,str) and 1<=len(v)<=95 for v in vals):raise ValueError('Invalid log events')
    return sum(s['frames'] for s in shots)

def frame(w,h,s,f,font_path):
    n=s['frames'];t=f/max(1,n-1);W,H=w,h;L=W*.09;R=W*.91;top=H*.34;bottom=H*.72
    im=Image.new('RGB',(w,h),'#090b0f');d=ImageDraw.Draw(im)
    def font(k):return ImageFont.truetype(str(font_path),max(10,round(W*k)))
    fg='#f5f5f3';muted='#8f949d';accent='#d3c5f4'
    d.text((L,H*.09),'VISUAL DATA / MOTION',font=font(.038),fill=muted)
    d.line((L,H*.15,R,H*.15),fill='#333743',width=max(1,int(W*.003)))
    size=.08
    while font(size).getlength(s['label'])>W*.82 and size>.035:size-=.004
    d.text((L,H*.20),s['label'],font=font(size),fill=fg)
    if s['kind'] in ('line','bars','metric'):
        values=s['values'];scale=max(values)*1.17
        progress=ease((t-.06)/.77)
        if s['kind']=='metric':
            v=values[-1]*progress
            text=fmt(v)
            fnt=font(.22)
            if fnt.getlength(text)>W*.85:fnt=font(.12)
            d.text((L,H*.43),text,font=fnt,fill=fg)
            d.text((L,H*.62),s.get('unit',''),font=font(.075),fill=muted)
        else:
            for i in range(5):
                y=bottom-(bottom-top)*i/4;d.line((L,y,R,y),fill='#292d36',width=1)
            if s['kind']=='line':
                pts=[(L+(R-L)*i/max(1,len(values)-1),bottom-(bottom-top)*v/scale) for i,v in enumerate(values)]
                pos=progress*(len(pts)-1);idx=min(int(pos),len(pts)-2);frac=pos-idx
                edge=(pts[idx][0]+(pts[idx+1][0]-pts[idx][0])*frac,pts[idx][1]+(pts[idx+1][1]-pts[idx][1])*frac)
                chain=pts[:idx+1]+[edge];d.line(chain,fill=accent,width=max(2,int(W*.008)),joint='curve');r=W*.013;d.ellipse((edge[0]-r,edge[1]-r,edge[0]+r,edge[1]+r),fill=fg)
                val=values[idx]+(values[idx+1]-values[idx])*frac
            else:
                gap=(R-L)/len(values)
                for i,v in enumerate(values):
                    q=ease((t-.06-i*.025)/.55);x=L+i*gap;y=bottom-(bottom-top)*v/scale*q
                    d.rounded_rectangle((x,y,x+gap*.70,bottom),radius=max(1,W*.005),fill=accent if i==len(values)-1 else '#656a77')
                val=values[-1]*progress
            text=fmt(val)+' '+s.get('unit','');d.text((L,H*.78),text.strip(),font=font(.075),fill=fg)
    else:
        events=s['events'];step=H*.055
        for i,event in enumerate(events):
            q=ease((t-i*.07)*9);a=int(96+156*q) if q>0 else 32
            # deliberate single visible motif: technical logs that build in density
            d.text((L,H*.34+i*step),f'{i+1:02d} / {event}',font=font(.037),fill=(a,a,a))
    if s['provenance']=='illustrative':
        d.text((L,H*.90),'ILLUSTRATIVE — NOT PRODUCT DATA',font=font(.032),fill='#bca9b3')
    else:
        d.text((L,H*.90),'SOURCE VERIFIED IN PRODUCTION BRIEF',font=font(.027),fill=muted)
    return im

def main():
    a=argparse.ArgumentParser();a.add_argument('plan',type=Path);a.add_argument('output',type=Path);a.add_argument('--font',required=True,type=Path);args=a.parse_args()
    doc=json.loads(args.plan.read_text(encoding='utf8'));n=validate(doc)
    if not args.font.is_file():raise ValueError('Font missing')
    W,H,fps=(doc[k] for k in ('width','height','fps'));args.output.parent.mkdir(parents=True,exist_ok=True)
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-pix_fmt','yuv420p','-crf','18',args.output],stdin=subprocess.PIPE)
    try:
        for s in doc['shots']:
            for i in range(s['frames']):proc.stdin.write(frame(W,H,s,i,args.font).tobytes())
        proc.stdin.close()
        if proc.wait():raise RuntimeError('Encoding failed')
    except BaseException:
        if proc.poll() is None:proc.kill();proc.wait()
        raise
    print(f'Rendered {n} data frames')

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,RuntimeError) as e:sys.exit('ERROR: '+str(e))
