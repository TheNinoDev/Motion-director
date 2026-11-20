#!/usr/bin/env python3
"""Continuous visual choreography. Real UI crops, persistent motifs and live boundary transitions.
No GUI. Scratch audio only unless authorized voice/music are provided.
"""
import argparse,json,math,subprocess,sys
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'kinetic_film'))
from render import Film, audio, rgb

KINDS={'gesture','proliferate','fold','compress','proof','track','return'}
def clamp(x):return max(0.,min(1.,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def mix(a,b,k):return a+(b-a)*k
def phase(u,a,b):return smooth((u-a)/(b-a))
def overshoot(x):x=clamp(x);return 1+(x-1)**3*2.3+(x-1)**2*1.3

def validate(p,base):
 if p['fps'] not in (24,25,30,60) or p['width']<240 or p['width']%2 or p['height']%2 or abs(p['width']/p['height']-9/16)>.01:raise ValueError('even portrait dimensions required')
 if not (base/p['image']).is_file():raise ValueError('missing product image')
 if len(p['items'])!=4 or len(p['proof_crops'])!=4:raise ValueError('this scaffold requires four motifs and proof crops')
 for crop in p['proof_crops']:
  if len(crop)!=4 or not (0<=crop[0]<crop[2]<=1 and 0<=crop[1]<crop[3]<=1):raise ValueError('invalid crop')
 for b in p['beats']:
  if b.get('transition','cut') not in {'cut','push','aperture','blend'} or b['kind'] not in KINDS or not b['voice'].strip() or not b['text'].strip() or not .8<=b['min']<=12:raise ValueError('invalid beat')
 return p

class Continuous(Film):
 def __init__(self,p,base):
  super().__init__(p,base);self.paper=rgb(p.get('paper','#e9e7df'));self.ink=(21,23,25);self.muted=(129,131,127);self.cards=[self.crop(c) for c in p['proof_crops']]
  self.Xpix=self.X*720;self.Ypix=self.Y*1280
 def rr(self,im,x,y,w,h,c,r=17,edge=None):
  # AA corner masks, no black clipped border.
  x,y,w,h,r=map(self.px,(x,y,w,h,r));r=max(1,min(r,w//2,h//2));
  if w<2 or h<2:return
  mask=np.zeros((h,w),np.uint8);cv2.rectangle(mask,(r,0),(w-r-1,h-1),255,-1);cv2.rectangle(mask,(0,r),(w-1,h-r-1),255,-1)
  for a,b in [(r,r),(w-r-1,r),(r,h-r-1),(w-r-1,h-r-1)]:cv2.circle(mask,(a,b),r,255,-1,cv2.LINE_AA)
  if edge:self.stamp(im,mask,x,y,edge); mask=cv2.erode(mask,np.ones((3,3),np.uint8))
  self.stamp(im,mask,x,y,c)
 def headline(self,im,lines,x,y,size,u,col=None,spacing=.9,maxw=630):
  # Fixed group anchors; vertically clipped movement instead of left-to-right type wipes.
  for i,t in enumerate(lines):
   q=phase(u,i*.075,i*.075+.24);m=self.glyph(t,size,'bold',maxw);h,w=m.shape; dy=round((1-q)*h*.8); mask=np.zeros_like(m)
   if dy<h:mask[dy:]=m[:h-dy]
   self.stamp(im,mask,self.px(x),self.px(y+i*size*spacing),col or self.fg,1 if q>0 else 0)
 def cursor(self,im,x,y,col=None,scale=1):
  a=np.array([[0,0],[0,30],[8,23],[15,35],[21,32],[14,20],[28,19]],float)*scale+[x,y]; pts=np.round(a*self.s).astype(np.int32); cv2.fillPoly(im,[pts],col or self.fg,cv2.LINE_AA);cv2.polylines(im,[pts],True,self.ink,1,cv2.LINE_AA)
 def rowcard(self,im,i,x,y,w,h,active=False,alpha=1):
  c=self.ac if active else (43,46,48);self.rr(im,x,y,w,h,c,min(16,h*.2)); ink=self.ink if active else self.fg
  self.text(im,f'{i+1:02}',x+19,y+h*.3,18,ink,'mono',maxw=45,alpha=alpha)
  self.text(im,self.p['items'][i],x+75,y+h*.27,29,ink,'regular',maxw=max(75,w-115),alpha=alpha)
 def fitcenter(self,im,src,cx,cy,w,angle=0,tilt=0,alpha=1):
  h=w*src.shape[0]/src.shape[1];self.image(im,src,cx-w/2,cy-h/2,w,h,angle,tilt,alpha)
 def drift(self,u):return math.sin(u*math.pi*2)
 def frame(self,b,u,idx):
  k=b['kind'];im=self.blank(); A=self.ac; F=self.fg; B=self.bg; I=self.ink; P=self.paper
  if k=='gesture':
   # A single interaction gets bigger, not a new slide per phrase.
   q=phase(u,.14,.52); r=phase(u,.56,.96); im=self.blank(P)
   self.text(im,'01 — THE REQUEST',46,105,17,I,'mono')
   self.headline(im,b['text'].split(' / '),46,240,116,u*2,I,maxw=630)
   bubble_y=mix(745,585,q);self.rr(im,47,bubble_y,626,106,I,24)
   self.text(im,self.p['items'][0],76,bubble_y+34,35,F,'regular',maxw=555,reveal=phase(u,.12,.40))
   self.cursor(im,mix(615,560,q),mix(1000,bubble_y+67,q),A,1.35)
   if u>.5:
    y=mix(bubble_y+118,bubble_y+125,r);self.rr(im,47,y,626,7,A,3)
    self.text(im,'...and?',48,y+43,49,I,'regular',alpha=r)
  elif k=='proliferate':
   # Same four labeled objects, deterministic entry and changing camera scale.
   self.text(im,'Attachments',47,155,24,F,'regular'); self.text(im,'04',666,155,20,self.muted,'mono',maxw=50,center=True)
   for i in range(4):
    q=phase(u,.07+i*.14,.25+i*.14);w=626-16*i; y=366+i*132+(1-q)*430; x=47+i*8+(1-q)*180
    if q>0:self.rowcard(im,i,x,y,w,97,i==0)
   self.text(im,b['text'],48,1015,74,F, maxw=620, reveal=phase(u,.35,.72))
   q=phase(u,.1,.85);self.cursor(im,610-170*q,365+440*q,A,1.1)
  elif k=='fold':
   # Cards fill frame and cascade down a continuous arc. A deliberate 4-to-1 foreshadowing.
   q=phase(u,.10,.88); im=self.blank(B)
   for i in reversed(range(4)):
    a=i-1.5; sweep=math.sin(math.pi*u);cx=360+a*mix(112,30,q)+75*sweep*math.sin(i*1.3);cy=650+a*mix(148,94,q);w=mix(570,630,q)-i*16
    self.fitcenter(im,self.cards[i],cx,cy,w,angle=(.23*a)*(1-q),tilt=.36*(1-q),alpha=1)
   self.headline(im,[b['text']],44,132,104,u*1.5,F)
   self.text(im,'01 / 04',46,1045,18,A,'mono');self.line(im,(46,1088),(46+628*u,1088),self.muted,1)
  elif k=='compress':
   # Collapse four persistent motif rows into one. Accent fills screen only on the narrative pivot.
   q=phase(u,.15,.66);r=phase(u,.68,.98); im=self.blank(B)
   for i in reversed(range(4)):
    y=mix(405+i*108,610,q); x=mix(47,47+i*4,q);w=mix(626,626-i*8,q)
    self.rowcard(im,i,x,y,w,90,i==0)
   if r>0:
    # A moving rounded aperture is attached to the merged bar: shared anchor.
    half=round(55+800*r); m=(abs(self.Ypix-655)<half)&(abs(self.Xpix-360)<(315+120*r));im[m]=A
    self.headline(im,[b['text']],47,460,220,phase(u,.68,.87),I)
  elif k=='proof':
   # One moving camera through real screenshot. No fake product rows.
   q=phase(u,0,.30);z=phase(u,.48,1); im=self.blank(A)
   cx=mix(360,430,z);cy=mix(755,760,z);w=mix(710,1040,z)
   self.fitcenter(im,self.ui,cx,cy,w,angle=-.035*(1-q),tilt=.16*(1-q))
   self.rect(im,0,0,720,312,A);self.headline(im,[b['text']],47,163,93,u*2,I)
   self.text(im,'01 / WORK',46,1070,20,I,'mono');self.line(im,(46,1110),(674,1110),I)
  elif k=='track':
   # Continuous camera travel between second project and contact crop; no UI text overlays.
   im=self.blank(B);q=phase(u,.22,.87); ix,iy=self.ui.shape[1],self.ui.shape[0]; a=self.p['proof_crops'][1];b2=self.p['proof_crops'][2]; center=lambda c:((c[0]+c[2])/2,(c[1]+c[3])/2)
   ax,ay=center(a);bx,by=center(b2); cx=mix(ax,bx,q);cy=mix(ay,by,q);ww=mix(1380,1200,q);hh=ww*iy/ix
   self.image(im,self.ui,360-cx*ww,610-cy*hh,ww,hh)
   # matte areas for readable editorial type, not busy chrome chrome overlays.
   self.rect(im,0,0,720,292,B);self.rect(im,0,950,720,330,B)
   self.headline(im,[b['text']],44,158,89,u*2,F)
   self.text(im,'02 / CONTACT',46,1025,20,A,'mono');self.cursor(im,560-190*q,800-85*q,A)
  elif k=='return':
   # The exact same request composition returns with a single answer.
   im=self.blank(P); q=phase(u,.08,.39);r=phase(u,.48,.75); self.text(im,'NEXT TIME',46,105,17,I,'mono');self.headline(im,[b['text']],46,240,102,u*2,I)
   self.rr(im,47,585,626,106,I,24);self.text(im,self.p['name'].lower()+' / portfolio',76,620,36,F,'regular',maxw=555,reveal=q);self.cursor(im,mix(615,560,q),mix(990,652,q),A,1.35)
   if r>0:
    self.rect(im,0,1280-1280*r,720,1280*r,B)
    if r>.7:self.text(im,self.p['name'],360,565,160,F,center=True,reveal=phase(u,.65,.83));self.text(im,self.p['domain'],360,735,20,A,'mono',center=True,alpha=phase(u,.73,.88))
  return im
 def moving_blend(self,prev,cur,q,mode):
  # Both sources are rendered at distinct times. No frozen exit plate.
  if mode=='cut' or q>=1:return cur
  if q<=0:return prev
  q=smooth(q)
  if mode=='push':
   n=int(q*self.w);return np.concatenate([prev[:,n:],cur[:,:n]],axis=1)
  if mode=='aperture':
   d=np.hypot(self.Xpix-360,self.Ypix-655); a=np.clip((q*850-d)/18+.5,0,1).astype(np.float32)[...,None];return np.uint8(prev*(1-a)+cur*a)
  return cv2.addWeighted(prev,1-q,cur,q,0)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--size',type=int);ap.add_argument('--voice-dir',type=Path);ap.add_argument('--music',type=Path);ap.add_argument('--stills-only',action='store_true');ap.add_argument('--fps',type=int,choices=(24,25,30,60));ap.add_argument('--samples',type=int,choices=(1,2,3),default=1);args=ap.parse_args();base=args.plan.resolve().parent;p=json.loads(args.plan.read_text());
 if args.size:p['width']=args.size;p['height']=round(args.size*16/9/2)*2
 if args.fps:p['fps']=args.fps
 validate(p,base);out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);cv2.setNumThreads(1);f=Continuous(p,base);fps=p['fps'];meta=audio(p,base,out,args.voice_dir.resolve() if args.voice_dir else None,args.music.resolve() if args.music else None); shots=[{**b,'frames':m['frames'],'start':m['start_frame']} for b,m in zip(p['beats'],meta)];(out/'visual-timeline.json').write_text(json.dumps(shots,indent=2));
 sheet=Image.new('RGB',(7*144,3*280),'#222222');d=ImageDraw.Draw(sheet)
 for i,s in enumerate(shots):
  for row,u in enumerate((.2,.52,.9)):
   frame=Image.fromarray(f.frame(s,u,i));frame.thumbnail((144,256));x=i*144;y=row*280;sheet.paste(frame,(x,y));d.text((x+4,y+259),f'{s["kind"]} {u:.2f}',fill='white')
 sheet.save(out/'contact-sheet.jpg',quality=94)
 if args.stills_only:return
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{f.w}x{f.h}','-r',str(fps),'-i','-','-i',str(out/'mix.wav'),'-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(out/'film.mp4')],stdin=subprocess.PIPE)
 span=max(2,round(.20*fps))
 def compose(i,j):
  s=shots[i]; leading=span if i and s.get('transition','cut')!='cut' else 0
  j=max(0,min(s['frames']-1,j));u=(leading+(s['frames']-1-leading)*j/max(1,s['frames']-1))/max(1,s['frames']-1)
  frame=f.frame(s,u,i)
  if i+1<len(shots) and j>=s['frames']-span:
   nxt=shots[i+1]; mode=nxt.get('transition','cut')
   if mode!='cut':
    k=j-(s['frames']-span);nu=k/max(1,nxt['frames']-1)
    frame=f.moving_blend(frame,f.frame(nxt,nu,i+1),(k+1)/span,mode)
  return frame
 for i,s in enumerate(shots):
  for j in range(s['frames']):
   # Local shutter samples on moving boundaries only, avoid blurring static reading holds.
   if args.samples>1 and ((i and j<span and s.get('transition','cut')!='cut') or (i+1<len(shots) and j>=s['frames']-span and shots[i+1].get('transition','cut')!='cut')):
    images=[compose(i,j+float(x)).astype(np.float32) for x in np.linspace(-.22,.22,args.samples)];frame=np.uint8(np.clip(np.sqrt(np.mean([a*a for a in images],axis=0)),0,255))
   else:frame=compose(i,j)
   proc.stdin.write(frame.tobytes())
  print(i+1,len(shots),s['kind'],flush=True)
 proc.stdin.close();assert proc.wait()==0
 (out/'script.txt').write_text('\n'.join(m['voice'] for m in meta));
 def fmt(t):
  n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
 (out/'captions.srt').write_text('\n'.join(f'{i+1}\n{fmt(m["voice_start"])} --> {fmt(m["voice_end"])}\n{m["voice"]}\n' for i,m in enumerate(meta)))
if __name__=='__main__':main()
