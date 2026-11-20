#!/usr/bin/env python3
"""Kinetic film: independently timed visual events over measured speech phrases.
Uses only local media. Built-in scratch speech is never a final commercial voice."""
import argparse, json, math, sys, subprocess, os
from pathlib import Path
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw, ImageColor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'story_film'))
from film import audio
KINDS={'macro','tabs','type','counter','tunnel','cascade','field','aperture','reveal','detail','duo','cutout','lockup','mesh'}
TRANS={'cut','iris','shutter','match','wipe','prism'}

def ease(x):
 x=np.clip(x,0,1); return x*x*(3-2*x)
def out(x): return 1-(1-np.clip(x,0,1))**3
def rgb(c): return tuple(ImageColor.getrgb(c))
def validate(p,base):
 if p['fps'] not in (24,25,30,60) or p['width']%2 or p['height']%2 or abs(p['width']/p['height']-9/16)>.01: raise ValueError('even 9:16 dimensions/fps required')
 if not (base/p['image']).is_file(): raise ValueError('missing actual screenshot')
 for b in p['beats']:
  if not b['voice'].strip() or not 0.8<=b['min']<=12 or not b['shots']:raise ValueError('invalid speech beat')
  for s in b['shots']:
   if s['kind'] not in KINDS or s.get('transition','cut') not in TRANS or not math.isfinite(s['weight']) or s['weight']<=0:raise ValueError('invalid shot')
   if 'crop' in s and not (len(s['crop'])==4 and 0<=s['crop'][0]<s['crop'][2]<=1 and 0<=s['crop'][1]<s['crop'][3]<=1):raise ValueError('bad crop')
 return p

def schedule(p,meta):
 allshots=[]
 for b,m in zip(p['beats'],meta):
  weights=np.array([s['weight'] for s in b['shots']]); edges=np.rint(np.r_[0,np.cumsum(weights)/weights.sum()]*m['frames']).astype(int)
  for i,s in enumerate(b['shots']):
   n=int(edges[i+1]-edges[i]);
   if n<8:raise ValueError('shot shorter than 8 frames')
   allshots.append({**s,'start':m['start_frame']+int(edges[i]),'frames':n})
 return allshots

class Film:
 def __init__(self,p,base):
  self.p=p;self.w=p['width'];self.h=p['height'];self.s=self.w/720;self.bg=rgb(p['background']);self.fg=rgb(p['foreground']);self.ac=rgb(p['accent']);self.ui=np.asarray(Image.open(base/p['image']).convert('RGB')); self.cache={};self.base=base;self.mesh={};self.proof_crops=p.get("proof_crops",[[.035,.27,.52,.61],[.54,.27,.97,.61]])
  self.fonts={}; self.faces={}
  for k,opts in {'bold':['/usr/share/fonts/opentype/inter/Inter-Black.otf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf'],'regular':['/usr/share/fonts/opentype/inter/Inter-Regular.otf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf'],'mono':['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','C:/Windows/Fonts/consola.ttf']}.items():
   self.faces[k]=str((base/p['fonts'][k]).resolve()) if k in p.get('fonts',{}) else next((x for x in opts if Path(x).is_file()),None)
   if not self.faces[k]:raise ValueError('missing font '+k)
  self.X,self.Y=np.meshgrid(np.arange(self.w,dtype=np.float32)/self.w,np.arange(self.h,dtype=np.float32)/self.h)
  self.rng=np.random.default_rng(25); self.points=self.rng.uniform(-1,1,(1000,3)).astype(np.float32)
 def px(self,x):return round(x*self.s)
 def blank(self,c=None):
  a=np.empty((self.h,self.w,3),np.uint8);a[:]=c or self.bg;return a
 @lru_cache(maxsize=512)
 def glyph(self,text,size,face='bold',maxw=650):
  sz=self.px(size); f=ImageFont.truetype(self.faces[face],max(8,sz)); length=f.getlength(text)
  if length>self.px(maxw):f=ImageFont.truetype(self.faces[face],max(8,int(sz*self.px(maxw)/length)))
  x,y,z,w=f.getbbox(text); im=Image.new('L',(max(1,z-x+4),max(1,w-y+4)));ImageDraw.Draw(im).text((2-x,2-y),text,font=f,fill=255);return np.asarray(im)
 def stamp(self,img,mask,x,y,col,alpha=1):
  x,y=int(x),int(y);mh,mw=mask.shape;x0=max(0,x);y0=max(0,y);x1=min(self.w,x+mw);y1=min(self.h,y+mh)
  if x0>=x1 or y0>=y1 or alpha<=0:return
  a=mask[y0-y:y1-y,x0-x:x1-x].astype(np.float32)[...,None]*(alpha/255); r=img[y0:y1,x0:x1]; cc=np.asarray(col,dtype=np.float32)
  if cc.ndim==3:cc=cc[y0-y:y1-y,x0-x:x1-x]
  r[:]=np.uint8(np.clip(r*(1-a)+cc*a,0,255))
 def text(self,img,text,x,y,size,col=None,face='bold',maxw=650,center=False,reveal=1,alpha=1):
  if not text:return
  m=self.glyph(str(text),size,face,maxw); xx=self.px(x)-(m.shape[1]//2 if center else 0);yy=self.px(y)
  if reveal<1:
   # mask grows from left without reflow
   m=m.copy();m[:,round(m.shape[1]*max(0,reveal)):]=0
  self.stamp(img,m,xx,yy,col or self.fg,alpha)
 def line(self,img,a,b,c=None,th=1):cv2.line(img,tuple(map(self.px,a)),tuple(map(self.px,b)),c or self.fg,max(1,self.px(th)),cv2.LINE_AA)
 def rect(self,img,x,y,w,h,c,th=-1):cv2.rectangle(img,(self.px(x),self.px(y)),(self.px(x+w),self.px(y+h)),c,th if th<0 else max(1,self.px(th)),cv2.LINE_AA)
 def crop(self,r):
  if r is None:return self.ui
  x,y,z,w=r;ih,iw=self.ui.shape[:2];return self.ui[round(y*ih):round(w*ih),round(x*iw):round(z*iw)]
 def image(self,img,src,x,y,w,h,angle=0,tilt=0,alpha=1,shadow=False):
  # Actual project screenshots, projected into a quadrilateral. No fabricated UI.
  x,y,w,h=[self.px(q) for q in (x,y,w,h)]; cs=np.array([[-w/2,-h/2],[w/2,-h/2],[w/2,h/2],[-w/2,h/2]],np.float32);cs[:,1]+=np.array([-1,1,-1,1])*h*tilt*.16; cs[:,0]*=np.array([1-tilt*.13,1+tilt*.13,1+tilt*.13,1-tilt*.13]);a=angle;cs=cs@np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]],np.float32);cs+=np.array([x+w/2,y+h/2],np.float32)
  lo=np.maximum(0,np.floor(cs.min(axis=0)).astype(int)-2);hi=np.minimum([self.w,self.h],np.ceil(cs.max(axis=0)).astype(int)+2);ww,hh=hi-lo
  if ww<=0 or hh<=0:return
  sh,sw=src.shape[:2]; tr=cv2.getPerspectiveTransform(np.float32([[0,0],[sw-1,0],[sw-1,sh-1],[0,sh-1]]),cs-lo.astype(np.float32)); warped=cv2.warpPerspective(src,tr,(int(ww),int(hh)),flags=cv2.INTER_LINEAR); mask=cv2.warpPerspective(np.full((sh,sw),255,np.uint8),tr,(int(ww),int(hh)),flags=cv2.INTER_LINEAR)
  self.stamp(img,mask,*lo,warped,alpha)
 def fit(self,img,src,x,y,w,**kw):self.image(img,src,x,y,w,w*src.shape[0]/src.shape[1],**kw)
 def metal(self,img,text,x,y,size,u,maxw=670,center=True):
  m=self.glyph(text,size,'bold',maxw);h,w=m.shape;xx=self.px(x)-(w//2 if center else 0); yy=self.px(y); 
  # stylized extruded glyph with moving highlights, not physical 3D
  for k in range(self.px(15),0,-3):self.stamp(img,m,xx-k//3,yy+k,(36+int(15*(1-k/max(1,self.px(15)))),)*3)
  key=('metal',m.shape,text,size,maxw)
  if key not in self.cache:
   dist=cv2.distanceTransform((m>127).astype(np.uint8),cv2.DIST_L2,3);bevel=np.clip(dist/(self.px(4)+1),0,1);dx=cv2.Sobel(bevel,cv2.CV_32F,1,0,ksize=3)*.25;dy=cv2.Sobel(bevel,cv2.CV_32F,0,1,ksize=3)*.25;ys,xs=np.mgrid[0:h,0:w].astype(np.float32);self.cache[key]=(bevel,dx,dy,xs/max(w,1),ys/max(h,1))
  b,dx,dy,X,Y=self.cache[key];v=.13+.76*np.exp(-((Y+X*.2-(.15+u*.75))/.16)**2)+.28*np.exp(-((Y+X*.5-.93)/.045)**2);v=np.clip(v*b+(1-b)*(.45+dx*.6-dy*.4),.035,1); col=np.stack([v*.94,v*.97,v],2)*255;self.stamp(img,m,xx,yy,col)
 def label(self,img,text,y=145,col=None):self.text(img,text,38,y,17,col or (150,153,154),'mono',maxw=590)
 def frame(self,s,u,idx):
  k=s['kind'];t=s.get('text','');sub=s.get('sub','');a=out(u*3);e=ease(u);im=self.blank(); A=self.ac;F=self.fg;B=self.bg
  if k=='macro':
   src=self.crop(s.get('crop'));ww=1260-650*e; hh=ww*src.shape[0]/src.shape[1];self.image(im,src,360-ww/2,570-hh/2,ww,hh,-.09*(1-e),.15*(1-e));self.text(im,t,35,245,83,F,maxw=650,reveal=out(u*3)); self.line(im,(45,1015),(45+630*e,1015),A,2)
  elif k=='tabs':
   self.label(im,'LOCAL FILES / 04');items=s.get('items',[]);p=min(len(items),int(u*len(items)*1.65)+1)
   for i,it in enumerate(items[:p]):
    y=365+i*110; off=(1-out((u-i*.13)*5))*210;self.rect(im,45+off,y,630,86,(24,25,27));self.rect(im,61+off,y+17,44,48,A);self.text(im,it,127+off,y+27,27,F,'mono',maxw=510);self.text(im,'↗',610,y+25,26,A)
   self.text(im,t,38,975,89,F,reveal=a); self.line(im,(38,1084),(682,1084),(73,75,78))
  elif k=='type':
   style=s.get('style','hero');
   if style=='inverse':
    im=self.blank(A); words=t.split();mid=max(1,len(words)//2); self.text(im,' '.join(words[:mid]),40,430,118,B,maxw=640,reveal=a);self.text(im,' '.join(words[mid:]),40,565,118,B,maxw=640,reveal=out((u-.12)*4));self.line(im,(40,725),(40+630*e,725),B,3)
   elif style=='tiny':self.text(im,t,360,620,24+14*e,F,'regular',center=True,reveal=a);self.rect(im,360+min(290,len(t)*8),617,3,36,F)
   else:self.text(im,t,360,565,135,F,center=True,reveal=a)
  elif k=='counter':
   end=s.get('end'); text=end if end and u>.48 else t;size=395+105*(1-e) if not end else 440-40*e;self.metal(im,text,360,330,size,u);self.label(im,'LINK / COUNT',180);self.text(im,sub,360,885,62,F,center=True,reveal=out((u-.22)*3));self.line(im,(90,982),(90+540*e,982),A,2)
  elif k=='tunnel':
   # Spatial card flythrough, actual crop textures, projected each frame.
   for j in reversed(range(10)):
    z=(j+1-u*2.8)%10+0.7; w=355/z; q=j*2.399+u*1.8; x=360+math.cos(q)*310/z-w/2;y=600+math.sin(q)*600/z-w*.32;src=self.crop(self.proof_crops[j%2]); self.fit(im,src,x,y,w,angle=q*.12,tilt=.5,alpha=.85)
   self.text(im,t,360,970,65,F,center=True,reveal=a)
  elif k=='cascade':
   items=s.get('items',[]);self.label(im,'OPEN / CLOSE / REPEAT')
   for j in range(18):
    q=(j*.105+u*.92)%1;y=150+q*1040; x=42+math.sin(j*2.4+u*4)*65; col=(30,32,34) if j%3 else (63,65,67);self.rect(im,x,y,635,53,col);self.text(im,items[j%len(items)],x+15,y+13,24,(175,177,178),'mono',maxw=500);self.text(im,'×',x+585,y+11,24,A)
   self.rect(im,0,535,720,170,B);self.text(im,t,360,584,65,F,center=True,reveal=a)
  elif k=='field':
   m=self.glyph(t,420,'bold');ys,xs=np.where(m>127);rng=np.random.default_rng(71);ids=rng.integers(0,len(xs),len(self.points));dest=np.stack([(xs[ids]-m.shape[1]/2)/self.s,(ys[ids]-m.shape[0]/2)/self.s],axis=1);r=self.points; spin=u*2.4; q=np.stack([r[:,0]*310*np.cos(spin)-r[:,2]*340*np.sin(spin),r[:,1]*525],axis=1); blend=ease((u-.06)/.50); pts=q*(1-blend)+dest*blend; depth=(r[:,2]*.5+.5)
   for j in np.argsort(depth):
    x,y=pts[j]+[360,610];c=int(95+150*depth[j]);cv2.circle(im,(self.px(x),self.px(y)),max(1,self.px(1+depth[j]*1.6)),(c,c,min(255,c+10)),-1,cv2.LINE_AA)
   self.label(im,'04 → 01',1010,A)
  elif k=='mesh':
   if idx not in self.mesh:
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('md25_mesh',Path(__file__).resolve().parents[1]/'mesh_motion'/'render.py');mod=module_from_spec(spec);spec.loader.exec_module(mod)
    config={'kind':'sheet','material':'texture','src':str((self.base/self.p['image']).resolve()),'frames':s['frames'],'resolution':68,'quality':.8,'samples':1,'bg':self.p['background'],'phase':[[0,0],[1,1]],'bend':[[0,2.2],[1,0]],'twist':[[0,1.45],[1,0]],'yaw':[[0,.8],[1,0]],'roll':[[0,-.5],[1,0]],'pitch':[[0,.35],[1,0]],'zoom':[[0,1.9],[1,1.05]],'grain':.2,**s.get('mesh',{})};config['frames']=s['frames']
    self.mesh[idx]=mod.MeshMotion(min(self.w,540),round(min(self.w,540)*16/9/2)*2,config,self.faces['bold'])
   raw=np.asarray(self.mesh[idx].frame(round(u*(s['frames']-1))));im=cv2.resize(raw,(self.w,self.h),interpolation=cv2.INTER_CUBIC)
   if t:self.text(im,t,360,985,70,F,center=True,reveal=out((u-.55)*3))
  elif k=='aperture':
   src=self.crop(None);self.fit(im,src,20,340,680);r=60+770*e;mask=(np.hypot((self.X-.5)*720,(self.Y-.47)*1280)<=r).astype(np.uint8);im*=mask[...,None];cv2.circle(im,(self.px(360),self.px(602)),self.px(r),A,max(1,self.px(2)),cv2.LINE_AA);self.text(im,t,360,980,62,F,center=True,reveal=a)
  elif k=='reveal':
   src=self.crop(None);w=1130-465*e;h=w*src.shape[0]/src.shape[1];self.image(im,src,360-w/2,570-h/2,w,h,angle=-.11*(1-e),tilt=.35*(1-e));self.text(im,t,38,177,104,F,reveal=a);self.line(im,(38,1070),(682,1070),(100,102,105));self.label(im,'PRODUCT / WORKSPACE',1085)
  elif k=='detail':
   src=self.crop(s.get('crop'));w=950-285*e;h=w*src.shape[0]/src.shape[1];self.fit(im,src,360-w/2,590-h/2,w);y=590+h/2+42;self.text(im,t,38,min(1010,y),61,F,reveal=a); xx=48+620*e;self.line(im,(xx,330),(xx,845),A,1);self.label(im,'DETAIL / VERIFIED CAPTURE',205)
  elif k=='duo':
   first=self.crop(self.proof_crops[0]);second=self.crop(self.proof_crops[1]);im=self.blank(B);self.rect(im,0,0,720,640,A);self.text(im,t,40,150,87,B,reveal=a);self.fit(im,first,40+120*(1-a),285,640,angle=-.06*(1-e));self.text(im,sub,40,710,76,F,reveal=out((u-.22)*4));self.fit(im,second,40-120*(1-out((u-.12)*3)),860,640,angle=.05*(1-e))
  elif k=='cutout':
   src=self.crop(self.proof_crops[1]);m=self.glyph(t,245,'bold',710);ww=900-250*e; self.fit(im,src,360-ww/2,430,ww); field=self.blank();xx=(self.w-m.shape[1])//2;yy=self.px(535);mm=np.zeros((self.h,self.w),np.uint8);mm[yy:yy+m.shape[0],xx:xx+m.shape[1]]=m;field[:]=np.uint8(im*(mm[...,None]/255));im=field;self.line(im,(60,800),(660,800),A,1)
  elif k=='lockup':
   self.metal(im,self.p['name'],360,470,240,min(1,u*1.5),maxw=605);self.text(im,t,360,740,70,F,center=True,reveal=out(u*3));self.text(im,self.p['domain'],360,835,20,A,'mono',center=True);self.text(im,'FICTIONAL PRODUCT STUDY' if self.p.get('fictional') else '',360,1070,16,(135,137,139),'mono',center=True)
  return im
 def transition(self,prev,cur,mode,u):
  if mode=='cut' or u>=1:return cur
  q=ease(u)
  if mode=='iris':mask=np.hypot((self.X-.5)*self.w,(self.Y-.47)*self.h)<q*math.hypot(self.w/2,self.h*.55)
  elif mode=='shutter':mask=((self.Y*8)%1)<q
  elif mode=='wipe':mask=self.X+.25*self.Y<q*1.25
  elif mode=='prism':
   amount=math.sin(q*math.pi)*self.px(12); mat=np.float32([[1,0,amount],[0,1,0]]); blend=cv2.addWeighted(prev,1-q,cur,q,0); blend[:,:,0]=cv2.warpAffine(blend[:,:,0],mat,(self.w,self.h),borderMode=cv2.BORDER_REFLECT);mat[0,2]=-amount;blend[:,:,2]=cv2.warpAffine(blend[:,:,2],mat,(self.w,self.h),borderMode=cv2.BORDER_REFLECT); return cv2.GaussianBlur(blend,(0,0),max(.1,amount*.15))
  else:
   r=1+.15*(1-q); M=cv2.getRotationMatrix2D((self.w/2,self.h/2),0,r);cur=cv2.warpAffine(cur,M,(self.w,self.h));return cv2.addWeighted(prev,1-q,cur,q,0)
  return np.where(mask[...,None],cur,prev)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--size',type=int);ap.add_argument('--voice-dir',type=Path);ap.add_argument('--music',type=Path);ap.add_argument('--stills-only',action='store_true');args=ap.parse_args();base=args.plan.resolve().parent;p=validate(json.loads(args.plan.read_text()),base);o=args.output.resolve();o.mkdir(parents=True,exist_ok=True)
 if args.size:p['width']=args.size;p['height']=round(args.size*16/9/2)*2
 meta=audio(p,base,o,args.voice_dir.resolve() if args.voice_dir else None,args.music.resolve() if args.music else None); shots=schedule(p,meta);(o/'visual-timeline.json').write_text(json.dumps(shots,indent=2));f=Film(p,base);fps=p['fps'];cv2.setNumThreads(1)
 sheet=Image.new('RGB',(6*144,math.ceil(len(shots)/6)*280),'#222222');d=ImageDraw.Draw(sheet)
 for i,s in enumerate(shots):
  frame=Image.fromarray(f.frame(s,.65,i));frame.thumbnail((144,256));x=i%6*144;y=i//6*280;sheet.paste(frame,(x,y));d.text((x+3,y+257),f'{s["start"]/fps:.1f}s {s["kind"]}',fill='white')
 sheet.save(o/'contact-sheet.jpg',quality=94)
 if args.stills_only:return
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{f.w}x{f.h}','-r',str(fps),'-i','-','-i',str(o/'mix.wav'),'-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(o/'film.mp4')],stdin=subprocess.PIPE)
 prev=None
 for i,s in enumerate(shots):
  for j in range(s['frames']):
   im=f.frame(s,j/max(1,s['frames']-1),i)
   if prev is not None and j<6:im=f.transition(prev,im,s.get('transition','cut'),j/6)
   proc.stdin.write(im.tobytes())
  prev=im;print(i+1,len(shots),s['kind'],flush=True)
 proc.stdin.close();assert proc.wait()==0
 def fmt(v):
  n=round(v*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
 (o/'captions.srt').write_text('\n'.join(f'{i+1}\n{fmt(m["voice_start"])} --> {fmt(m["voice_end"])}\n{m["voice"]}\n' for i,m in enumerate(meta)));(o/'script.txt').write_text('\n'.join(m['voice'] for m in meta))
if __name__=='__main__':main()
