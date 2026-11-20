#!/usr/bin/env python3
"""Deterministic, persistent, data-driven motion compositor. Design coordinates 720x1280.
All track times are seconds on the global picture clock. No shot clocks restart at cuts.
"""
import argparse, math, json, subprocess, sys
from pathlib import Path
from functools import lru_cache
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageColor
from optics import gradient, lens, directional, shaped_lens
from refinement import projected_exposure, shadow_pass, feather_mask
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import softbody
from numba import set_num_threads
set_num_threads(min(4, __import__("numba").config.NUMBA_NUM_THREADS))

def color(v): return ImageColor.getrgb(v) if isinstance(v,str) else tuple(v)
def clamp(v): return max(0.,min(1.,v))
def ease(v,k):
 v=clamp(v)
 if k=='linear':return v
 if k=='in':return v**3
 if k=='out':return 1-(1-v)**3
 if k=='sine':return .5-.5*math.cos(math.pi*v)
 if k=='quint':return v**3*(v*(v*6-15)+10)
 if k=='hold':return 0
 if k=='spring':return 1-math.exp(-7*v)*math.cos(11*v) if v<1 else 1
 if k=='back':return 1+2.1*(v-1)**3+1.1*(v-1)**2
 return v*v*(3-2*v)
def val(v,t):
 if not isinstance(v,list) or not v or not isinstance(v[0],list):return v
 if t<=v[0][0]:return v[0][1]
 for a,b in zip(v,v[1:]):
  if t<b[0]:
   q=ease((t-a[0])/(b[0]-a[0]),b[2] if len(b)>2 else 'smooth');return a[1]+(b[1]-a[1])*q
 return v[-1][1]
KEYS={'x','y','scale','scale_x','scale_y','rotate','opacity','reveal','pitch','yaw','blur','light','trim','glow','mask_progress','strength','dispersion','shine','shadow_opacity','shadow_x','shadow_y','shadow_blur','mask_feather','radius','frost','tint_mix','edge_feather'}
KEYS.update({'depth','bevel3d','ior','roughness','transmission','absorption','twist3d','bend3d','scale_z','size_x','size_y','background_gap','reflection','phase3d'})
KINDS={'text3d','glass_object','object3d','text','image','rect','ellipse','line','path','group','mesh','gradient','lens'}
def validate(plan,base):
 if plan['fps'] not in (24,25,30,60) or plan['width']%2 or plan['height']%2 or abs(plan['width']/plan['height']-9/16)>.001:raise ValueError('even 9:16 canvas, supported fps required')
 if not 1/plan['fps']<=plan['duration']<=180:raise ValueError('duration out of range')
 ids=set(); order=[]
 for l in plan['layers']:
  i=l['id']; k=l['kind']; a,b=l['active'];
  if i in ids or k not in KINDS or not 0<=a<b<=plan['duration']+.001:raise ValueError(f'invalid layer {i}')
  if l.get('matte') and (l['matte'] not in ids or next(x for x in order if x['id']==l['matte'])['kind'] not in ('text','rect','ellipse','image','path')):raise ValueError(f'matte must be earlier drawable layer: {i}')
  if l.get('matte_mode','alpha') not in ('alpha','luma','alpha_invert','luma_invert'):raise ValueError(f'invalid matte mode: {i}')
  if l.get('points_keyframes'):
   frames=l['points_keyframes'];expected=len(l['points']);
   if len(frames)<2 or any(len(v)!=2 or len(v[1])!=expected for v in frames) or any(x[0]>=y[0] for x,y in zip(frames,frames[1:])):raise ValueError(f'bad point morph {i}')
  if l.get('parent') and (l['parent'] not in ids or next(x for x in order if x['id']==l['parent'])['kind']!='group'):raise ValueError(f'parent must be earlier group: {i}')
  if 'softbody' in l:
   if k not in ('glass_object','object3d','text3d'):raise ValueError('softbody on mesh belongs inside mesh config')
   softbody.validate(l['softbody'])
   if any(e.get('mode','squash') in ('dent','ripple') for e in l['softbody'].get('events',[])):raise ValueError('dent/ripple require triangle mesh')
  if k=='text3d':
   from text3d import MATERIALS
   if not isinstance(l.get('text'),str) or not l['text'].strip() or len(l['text'])>64 or '\n' in l['text'] or l.get('material','chrome') not in MATERIALS:raise ValueError('invalid 3D text')
   if not .2<=l.get('quality',.7)<=1 or not 8<=l.get('size',80)<=1000 or l.get('antialias',1) not in (1,1.5,2) or l.get('atlas_resolution',640) not in (320,640,960,1280):raise ValueError('3D text quality/size/antialias/atlas')
   for key,low,high in [('depth',1,400),('bevel3d',0,40),('size_x',.05,5),('size_y',.05,5),('scale_z',.05,5),('bend3d',-.8,.8),('twist3d',-2,2),('roughness',0,1)]:
    v=l.get(key);vs=[a[1] for a in v] if isinstance(v,list) else [v] if v is not None else []
    if any(not isinstance(a,(int,float)) or not low<=a<=high for a in vs):raise ValueError('invalid 3D text '+key)
   if l.get('matte') or l.get('matte_only') or l.get('blend','normal')!='normal':raise ValueError('3D text is an ordered solid pass')
  if k in ('glass_object','object3d'):
   from volume import SHAPES,PRESETS,RANGES
   if l.get('geometry','rounded_box') not in SHAPES or l.get('material','clear') not in PRESETS:raise ValueError(f'bad volume shape/material {i}')
   if not all(isinstance(l.get(q),(int,float)) and math.isfinite(l[q]) and 1<=l[q]<=1500 for q in ('w','h')):raise ValueError(f'bad volume size {i}')
   if not .2<=l.get('quality',.55)<=1 or l.get('antialias',1) not in (1,1.5,2):raise ValueError(f'bad volume quality {i}')
   for q,(lo,hi) in RANGES.items():
    if q not in l:continue
    vals=[x[1] for x in l[q]] if isinstance(l[q],list) else [l[q]]
    if not vals or any(not isinstance(v,(int,float)) or not lo<=v<=hi for v in vals):raise ValueError(f'bad volume {i}.{q}')
   if l.get('matte') or l.get('matte_only') or l.get('blend','normal')!='normal':raise ValueError(f'volume is ordered refractive pass: {i}')
  if k in ('gradient','lens'):
   if not all(isinstance(l.get(q),(int,float)) and math.isfinite(l[q]) and l[q]>0 for q in ('w','h')):raise ValueError(f'invalid optical dimensions: {i}')
   if k=='gradient':
    st=l.get('stops',[])
    if len(st)<2 or any(len(x)!=2 or not 0<=x[0]<=1 for x in st) or any(x[0]>=y[0] for x,y in zip(st,st[1:])):raise ValueError(f'invalid gradient stops: {i}')
   elif l.get('matte') or l.get('matte_only') or l.get('mask') or l.get('blend','normal')!='normal':raise ValueError(f'lens is a local adjustment pass, not a drawable/matte: {i}')
  if k=='lens' and l.get('shape','roundrect') not in ('roundrect','ellipse','diamond','squircle','capsule'):raise ValueError(f'invalid glass shape: {i}')
  if k=='image' and not (base/l['src']).is_file():raise ValueError(f'missing asset {i}')
  if l.get('blend','normal') not in ('normal','screen','add','multiply'):raise ValueError(f'bad blend {i}')
  if l.get('mask') not in (None,'iris','wipe','diagonal','shutter'):raise ValueError(f'bad mask {i}')
  for key,v in l.items():
   if key in KEYS and isinstance(v,list):
    if not v or any(len(x) not in (2,3) or not all(isinstance(z,(int,float)) and math.isfinite(z) for z in x[:2]) or (len(x)==3 and x[2] not in ('linear','in','out','smooth','sine','quint','hold','back','spring')) for x in v) or any(x[0]>=y[0] for x,y in zip(v,v[1:])):raise ValueError(f'bad track {i}.{key}')
  if l.get('projected_blur',0) and (not isinstance(l['projected_blur'],(int,float)) or not 0<=l['projected_blur']<=2):raise ValueError(f'bad projected_blur: {i}')
  if l.get('shadow') and k in ('lens','group'):raise ValueError(f'shadow requires drawable: {i}')
  ids.add(i);order.append(l)
 return plan
class Engine:
 def __init__(self,p,base,backend=None):
  self.backend=backend
  self.p=p;self.base=base;self.w=p['width'];self.h=p['height'];self.s=self.w/720;self.layers=p['layers'];self.byid={l['id']:l for l in self.layers};self.textures={};self.shading={};self.fonts={};self._fonts={};self.meshes={};self.premult={};self.glyphs={}
  cv2.setNumThreads(1)
  for name,files in {'bold':['/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf'],'regular':['/usr/share/fonts/opentype/inter/Inter-Regular.otf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf'],'mono':['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','C:/Windows/Fonts/consola.ttf'],'heavy':['/usr/share/fonts/opentype/inter/InterDisplay-Black.otf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf']}.items():
   self.fonts[name]=str((base/p['fonts'][name]).resolve()) if name in p.get('fonts',{}) else next((x for x in files if Path(x).is_file()),None)
  for name,loc in p.get("fonts",{}).items():
   fp=(base/loc).resolve()
   if not fp.is_file():raise ValueError(f"font file not found: {name}")
   self.fonts[name]=str(fp)
  for l in self.layers:
   if l['kind']=='text3d':
    from text3d import prepare
    face=l.get("font","heavy");fp=self.fonts.get(face)
    if not fp:raise ValueError(f"missing font {face}")
    self.glyphs[l["id"]]=prepare(l["text"],fp,l.get("size",80),l.get("maxw"),l.get("atlas_resolution",640))
   elif l['kind']=='mesh':
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('md27mesh',Path(__file__).resolve().parents[1]/'mesh_motion'/'render.py');mod=module_from_spec(spec);spec.loader.exec_module(mod)
    config=dict(l['mesh']); config['frames']=max(4,round((l['active'][1]-l['active'][0])*p['fps']));
    if 'src' in config:config['src']=str((base/config['src']).resolve())
    mw=max(96,round(l['w']*self.s));mh=max(96,round(l['h']*self.s));self.meshes[l['id']]=mod.MeshMotion(mw,mh,config,self.fonts['bold'])
   elif l['kind'] not in ('group','lens','glass_object','object3d'):
    self.textures[l['id']]=self.texture(l)
    if l['kind']!='path' and l.get('material')!='metal' and 'reveal' not in l and not l.get('mask'):
     tex=self.textures[l['id']][0]; a=tex[:,:,3].astype(np.float32)/255;self.premult[l['id']]=np.dstack([np.uint8(tex[:,:,:3]*a[:,:,None]),tex[:,:,3]])
  rng=np.random.default_rng(p.get('seed',27));self.noise=rng.integers(-3,4,(self.h,self.w),dtype=np.int16)
 def font(self,face,size):
  key=(face,size)
  if key not in self._fonts:
   if not self.fonts.get(face):raise ValueError(f'missing font {face}')
   self._fonts[key]=ImageFont.truetype(self.fonts[face],size)
  return self._fonts[key]
 def texture(self,l):
  k=l['kind'];f=max(1.,self.s*1.5) # supersampled text/shape raster at output scale
  c=color(l.get('color','#f3f1ea'))
  if k=='gradient':
   w,h=l['w'],l['h'];return gradient(max(2,round(w*f)),max(2,round(h*f)),l['stops'],l.get('angle',0)),w,h
  if k=='image':
   im=Image.open(self.base/l['src']).convert('RGBA');
   if 'crop' in l:
    a,b,d,e=l['crop'];im=im.crop((round(a*im.width),round(b*im.height),round(d*im.width),round(e*im.height)))
   w=l.get('w',im.width);h=l.get('h',w*im.height/im.width);return np.asarray(im.resize((max(1,round(w*f)),max(1,round(h*f))),Image.Resampling.LANCZOS)).copy(),w,h
  if k=='text':
   text=l['text'];face=l.get('font','bold');sz=l.get('size',80);font=self.font(face,round(sz*f));
   length=max(font.getlength(line) for line in text.split('\n'))
   if l.get('maxw') and length>l['maxw']*f:font=self.font(face,max(8,int(font.size*l['maxw']*f/length)))
   if '\n' in text:
    spacing=max(1,round(font.size*.12));measure=ImageDraw.Draw(Image.new('RGBA',(1,1)));a,b,d,e=measure.multiline_textbbox((0,0),text,font=font,spacing=spacing,align='center');w,h=max(1,math.ceil(d-a+8)),max(1,math.ceil(e-b+8));im=Image.new('RGBA',(w,h));dr=ImageDraw.Draw(im);dr.multiline_text((4-a,4-b),text,font=font,fill=(*c,255),spacing=spacing,align='center')
   else:
    a,b,d,e=font.getbbox(text);w,h=max(1,d-a+8),max(1,e-b+8);im=Image.new('RGBA',(w,h));dr=ImageDraw.Draw(im);dr.text((4-a,4-b),text,font=font,fill=(*c,255),stroke_width=0)
   if l.get('outline'):
    m=im.getchannel('A');import PIL.ImageFilter as IF; r=max(1,round(l['outline']*f));inner=m.filter(IF.MinFilter(2*r+1));im.putalpha(Image.fromarray(np.maximum(0,np.asarray(m,dtype=np.int16)-np.asarray(inner,dtype=np.int16)).astype(np.uint8)))
   return np.asarray(im).copy(),w/f,h/f
  if k=='path':
   pts=np.asarray(l['points'],float); w=l.get('w',720);h=l.get('h',1280);return (pts,w,h)
  w,h=l['w'],l['h'];im=Image.new('RGBA',(max(1,round(w*f)),max(1,round(h*f))));d=ImageDraw.Draw(im);box=(0,0,im.width-1,im.height-1) if min(im.size)<3 else (1,1,im.width-2,im.height-2);th=round(l.get('stroke',0)*f)
  if k=='ellipse':d.ellipse(box,fill=None if th else (*c,255),outline=(*c,255) if th else None,width=max(1,th))
  else:d.rounded_rectangle(box,radius=round(l.get('radius',0)*f),fill=None if th else (*c,255),outline=(*c,255) if th else None,width=max(1,th))
  return np.asarray(im).copy(),w,h
 def material(self,l,tex,t):
  if l.get('material')!='metal':return tex
  key=l['id'];a=tex[:,:,3]
  if key not in self.shading:
   d=cv2.distanceTransform((a>127).astype(np.uint8),cv2.DIST_L2,3);z=np.minimum(1,d/max(1,l.get('bevel',8)*2));dx=cv2.Sobel(z,cv2.CV_32F,1,0,ksize=3)*.5;dy=cv2.Sobel(z,cv2.CV_32F,0,1,ksize=3)*.5;y,x=np.indices(a.shape,dtype=np.float32);self.shading[key]=(z,dx,dy,x/a.shape[1],y/a.shape[0])
  z,dx,dy,x,y=self.shading[key];q=val(l.get('light',.5),t);r=y+.29*x+dx*.3-dy*.45;v=.09+.84*np.exp(-((r-q)/.15)**2)+.47*np.exp(-((r-q+.37)/.04)**2)+.28*np.exp(-((r-.96)/.06)**2);v=np.clip(v*z+(1-z)*(.28+.6*np.maximum(dx-dy,0)),.035,1);out=tex.copy();out[:,:,:3]=np.uint8(np.stack([v*.95,v*.98,v],2)*255);return out
 def path_texture(self,l,t):
  p,w,h=self.textures[l['id']];
  if l.get('points_keyframes'):
   fs=l['points_keyframes'];p=np.asarray(fs[0][1],float)
   for a,b in zip(fs,fs[1:]):
    if t>=b[0]:p=np.asarray(b[1],float);continue
    if t>=a[0]:p=np.asarray(a[1])*(1-ease((t-a[0])/(b[0]-a[0]),'quint'))+np.asarray(b[1])*ease((t-a[0])/(b[0]-a[0]),'quint')
    break
  res=1;im=np.zeros((round(h*res),round(w*res),4),np.uint8);q=clamp(val(l.get('trim',1.),t));n=(len(p)-1)*q;idx=int(n);pp=p[:idx+1].copy();
  if idx<len(p)-1:pp=np.concatenate([pp,[p[idx]+(p[idx+1]-p[idx])*(n-idx)]])
  if len(pp)>1:cv2.polylines(im,[np.rint(pp*res).astype(np.int32)],False,(*color(l.get('color','#ffffff')),255),max(1,round(l.get('stroke',2)*res)),cv2.LINE_AA)
  return im,w,h
 def state(self,l,t):
  def g(k,d):return val(l.get(k,d),t)
  x,y=g('x',360),g('y',640);theta=math.radians(g('rotate',0));sc=g('scale',1);sx=sc*g('scale_x',1);sy=sc*g('scale_y',1);op=clamp(g('opacity',1));M=np.array([[math.cos(theta)*sx,-math.sin(theta)*sy,x],[math.sin(theta)*sx,math.cos(theta)*sy,y],[0,0,1]],float)
  if l.get('parent'):
   parent=self.byid[l['parent']];P,a=self.state(parent,t);M=P@M;op*=a if parent['active'][0]<=t<parent['active'][1] else 0
  return M,op
 def stamp(self,im,l,t,weight=1,matte_render=False):
  M,op=self.state(l,t);op*=weight
  if op<.002:return
  if 'softbody' in l:l=softbody.solid_layer(l,t,val)
  if l['kind']=='text3d':
   from text3d import draw
   draw(im,M,l,t,val,op,self.s,self.glyphs[l['id']],self.backend);return
  if l['kind'] in ('glass_object','object3d'):
   from volume import draw
   draw(im,M,l,t,val,op,self.s,self.backend);return
  if l['kind']=='lens':
   if 'shape' in l:
    A=M.copy();A[:2]*=self.s
    shaped_lens(im,A,l['w'],l['h'],shape=l['shape'],strength=val(l.get('strength',.16),t),dispersion=val(l.get('dispersion',.012),t),radius=val(l.get('radius',.23),t),opacity=op,tint=l.get('color','#dbe6ff'),shine=val(l.get('shine',.65),t),light=val(l.get('light',0),t),frost=max(0,min(25,val(l.get('frost',0),t)*self.s)),tint_mix=clamp(val(l.get('tint_mix',.08),t)),feather=max(.6,val(l.get('edge_feather',1.5),t)*self.s));return
   lens(im,M[0,2]*self.s,M[1,2]*self.s,l['w']*np.linalg.norm(M[:2,0])*self.s,l['h']*np.linalg.norm(M[:2,1])*self.s,strength=val(l.get('strength',.16),t),dispersion=val(l.get('dispersion',.012),t),radius=l.get('radius',.23),opacity=op,tint=l.get('color','#dbe6ff'),shine=val(l.get('shine',.65),t),light=val(l.get('light',0),t));return
  if l['kind']=='mesh':
   mesh=self.meshes[l['id']];idx=min(mesh.c['frames']-1,max(0,round((t-l['active'][0])*self.p['fps'])));raw=mesh.frame(idx);tex=np.dstack([raw,np.full(raw.shape[:2],255,np.uint8)]);w,h=l['w'],l['h']
  else:tex,w,h=self.path_texture(l,t) if l['kind']=='path' else self.textures[l['id']];tex=self.material(l,tex,t);
  q=clamp(val(l.get('reveal',1),t));mp=clamp(val(l.get('mask_progress',1),t));kind=l.get('mask');
  if matte_render and matte_render=='alpha':
   tex=tex.copy();tex[:,:,:3]=255 # white RGB, preserve the actual alpha silhouette
  if q<1 or (kind and mp<1):
   tex=tex.copy();a=tex[:,:,3];hh,ww=a.shape
   if q<1:a[:round(hh*(1-q))]=0 # vertical matte, fixed glyph layout
   if kind and mp<1:
    yy,xx=np.ogrid[:hh,:ww];X=xx/max(ww-1,1);Y=yy/max(hh-1,1)
    v={'iris':lambda:np.hypot(X-.5,Y-.5)/.71,'wipe':lambda:X,'diagonal':lambda:(X+Y*.45)/1.45,'shutter':lambda:(Y*8)%1}[kind]();a[:]=feather_mask(a,v,mp,val(l.get('mask_feather',.025),t))
  def projected(u):
   A,_=self.state(l,u);yaw=math.radians(val(l.get('yaw',0),u));pitch=math.radians(val(l.get('pitch',0),u));corn=np.array([[-w/2,-h/2],[w/2,-h/2],[w/2,h/2],[-w/2,h/2]],float);xx,yy=corn.T;zz=-xx*np.sin(yaw)+yy*np.sin(pitch);pers=1000/np.maximum(150,1000+zz);corn=np.column_stack([xx*np.cos(yaw)*pers,yy*np.cos(pitch)*pers]);return (np.column_stack([corn,np.ones(4)])@A.T)[:,:2]*self.s
  yaw=math.radians(val(l.get('yaw',0),t));pitch=math.radians(val(l.get('pitch',0),t));corn=projected(t);exposure=None
  if l.get('projected_blur') and not matte_render:
   dt=l['projected_blur']*.5/self.p['fps'];c0=projected(t-dt);c1=projected(t+dt)
   if np.max(abs(c1-c0))>.7:exposure=[projected(t+u*dt) for u in (-1,-.5,0,.5,1)]
  if not np.isfinite(corn).all():return
  blur=max(0,val(l.get('blur',0),t)*self.s);glow=max(0,val(l.get('glow',0),t));
  dx=dy=0
  if l.get('velocity_blur') and not l.get('projected_blur') and not matte_render:
   dt=.5/self.p['fps'];prev,_=self.state(l,t-dt);nxt,_=self.state(l,t+dt);dx,dy=np.clip((nxt[:2,2]-prev[:2,2])*self.s*l['velocity_blur'],-48,48)
  sb=max(0,val(l.get('shadow_blur',20),t)*self.s) if l.get('shadow') and not matte_render else 0; sx=val(l.get('shadow_x',0),t)*self.s;sy=val(l.get('shadow_y',12),t)*self.s; pad=math.ceil(3*blur+3+(14*self.s if glow else 0)+max(abs(dx),abs(dy))*.6+(3*sb+max(abs(sx),abs(sy)) if l.get('shadow') else 0));bounds=np.concatenate(exposure) if exposure is not None else corn;lo=np.maximum(0,np.floor(bounds.min(0)).astype(int)-pad);hi=np.minimum([self.w,self.h],np.ceil(bounds.max(0)).astype(int)+pad);W,H=hi-lo
  if W<=1 or H<=1 or abs(cv2.contourArea(corn.astype(np.float32)))<2:return
  if not matte_render and not l.get('matte') and not l.get('shadow') and exposure is None and l['kind']=='rect' and not l.get('radius') and not l.get('stroke') and not l.get('mask') and not l.get('material') and not glow and blur<.15 and abs(M[0,1])<1e-7 and abs(M[1,0])<1e-7 and abs(yaw)+abs(pitch)<1e-7 and not (dx or dy) and q==1 and l.get('blend','normal')=='normal':
   lx,ly=np.maximum(0,np.ceil(corn.min(0)).astype(int));hx,hy=np.minimum([self.w,self.h],np.floor(corn.max(0)).astype(int));
   if hx>lx and hy>ly:
    roi=im[ly:hy,lx:hx];cc=color(l.get('color','#f3f1ea'));roi[:]=cc if op>.998 else np.uint8(roi*(1-op)+np.asarray(cc)*op)
   return
  th,tw=tex.shape[:2];src=np.float32([[0,0],[tw-1,0],[tw-1,th-1],[0,th-1]]);dst=np.float32(corn-lo);T=cv2.getPerspectiveTransform(src,dst)
  # premultiplied alpha before filtering prevents dark halos on white type
  packed=None if matte_render else self.premult.get(l['id']);
  if packed is None:
   A=tex[:,:,3].astype(np.float32)/255;C=np.uint8(tex[:,:,:3]*A[:,:,None]);packed=np.dstack([C,tex[:,:,3]])
  v=projected_exposure(packed,src,[q-lo for q in exposure],(int(W),int(H))) if exposure is not None else cv2.warpPerspective(packed,T,(int(W),int(H)),flags=cv2.INTER_LINEAR);
  if dx or dy:v=directional(v,dx,dy)
  a=v[:,:,3:4].astype(np.float32)*(op/255);c=v[:,:,:3].astype(np.float32)*op
  if blur>.15:c=cv2.GaussianBlur(c,(0,0),blur);a=cv2.GaussianBlur(a,(0,0),blur);a=a.reshape(H,W,1)
  if l.get('matte') and not matte_render:
   ml=self.byid[l['matte']];mode=l.get('matte_mode','alpha');black=np.zeros_like(im)
   if ml['active'][0]<=t<ml['active'][1]:self.stamp(black,ml,t,matte_render=mode.split('_')[0])
   m=(black[lo[1]:hi[1],lo[0]:hi[0]].astype(np.float32) @ np.array([.2126,.7152,.0722],np.float32))/255
   if mode.endswith('_invert'):m=1-m
   a*=m[:,:,None];c*=m[:,:,None]
  roi=im[lo[1]:hi[1],lo[0]:hi[0]];r=roi.astype(np.float32);blend='normal' if matte_render else l.get('blend','normal')
  if l.get('shadow') and not matte_render:r=shadow_pass(r,a,sx,sy,sb,clamp(val(l.get('shadow_opacity',.35),t)),color(l.get('shadow_color','#000000')))
  if glow and not matte_render:
   g=cv2.GaussianBlur(a[:,:,0],(0,0),max(1.,5*self.s))[:,:,None]*glow;r=255-(255-r)*(1-g*np.array(color(l.get('glow_color','#ffffff')))/255)
  if blend=='normal':out=r*(1-a)+c
  elif blend=='add':out=r+c
  elif blend=='screen':out=255-(255-r)*(1-c/255)
  else:out=r*(1-a+c/255)
  roi[:]=np.uint8(np.clip(out,0,255))
 def frame(self,t,samples=1):
  bg=color(self.p.get('background','#090a0d'));im=np.empty((self.h,self.w,3),np.uint8);im[:]=bg
  for l in self.layers:
   if l['kind']=='group' or l.get('matte_only') or not l['active'][0]<=t<l['active'][1]:continue
   # Global clock; no frozen outgoing shot. Whole composite shutter in render_frame.
   self.stamp(im,l,t)
  grain=self.p.get('grain',0)
  if grain:im=np.uint8(np.clip(im.astype(np.int16)+np.roll(self.noise,round(t*self.p['fps'])*7,axis=0)[...,None]*grain,0,255))
  return im
 def render_frame(self,t,samples=1):
  if samples==1:return self.frame(t)
  # approximate linear-light exposure with gamma 2.2; apply only shot windows marked for shutter
  if not any(a<=t<b for a,b in self.p.get('shutter_windows',[])):return self.frame(t)
  times=np.linspace(-.5,.5,samples)*self.p.get('shutter',.45)/self.p['fps']+t;acc=None
  for u in times:
   a=(self.frame(max(0,min(self.p['duration']-1e-6,u))).astype(np.float32)/255)**2.2;acc=a if acc is None else acc+a
  return np.uint8(np.clip((acc/samples)**(1/2.2)*255,0,255))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--size',type=int);ap.add_argument('--fps',type=int,choices=(24,25,30,60));ap.add_argument('--samples',type=int,choices=(1,2,3),default=1);ap.add_argument('--stills',action='store_true');ap.add_argument('--audio',type=Path);ap.add_argument('--profile',choices=('preview','high','lossless'),default='preview');ap.add_argument('--check',action='store_true');ap.add_argument('--at',type=float,action='append',help='Native PNG at absolute time; repeatable');ap.add_argument('--range',type=float,nargs=2,metavar=('START','END'),help='Picture-only excerpt, absolute seconds');ap.add_argument('--backend',choices=('auto','cpu','cuda'),default='auto');ap.add_argument('--device',type=int,default=0);ap.add_argument('--gpu-tile-mib',type=int,default=64);a=ap.parse_args();p=json.loads(a.plan.read_text());base=a.plan.resolve().parent
 if a.size:p['width']=a.size;p['height']=round(a.size*16/9/2)*2
 if a.fps:p['fps']=a.fps
 if a.profile!='preview':
  for l in p['layers']:
   if l['kind']=='text3d':l.update(quality=1,antialias=max(l.get('antialias',1),1.5),atlas_resolution=max(l.get('atlas_resolution',640),960))
   elif l['kind'] in ('object3d','glass_object'):l.update(quality=1,antialias=max(l.get('antialias',1),1.5))
 validate(p,base)
 if a.at and (a.range or a.stills):ap.error('--at cannot be combined with --range or --stills')
 if a.at and any(not 0<=t<p['duration'] for t in a.at):ap.error('--at must lie within timeline')
 if a.range and (a.audio or a.stills):ap.error('--range is picture-only; do not use --audio or --stills')
 if a.range and not 0<=a.range[0]<a.range[1]<=p['duration']:ap.error('invalid excerpt interval')
 if a.check:print('VALID: '+str(len(p['layers']))+' layers');return
 from render_backend import Backend
 backend=Backend(a.backend,a.device,a.gpu_tile_mib);print(f'Rendering backend: {backend.selected}',flush=True)
 f=Engine(p,base,backend);a.out.mkdir(parents=True,exist_ok=True);fps=p['fps'];n=round(p['duration']*fps)
 if a.at:
  for i,t in enumerate(a.at):Image.fromarray(f.render_frame(t,a.samples)).save(a.out/f'still-{i:03d}-{t:.3f}s.png')
  backend.save(a.out/'render-backend.json');return
 start=0
 if a.range:
  start=math.ceil(a.range[0]*fps-1e-9);n=min(n,math.ceil(a.range[1]*fps-1e-9))-start
  if n<1:ap.error('excerpt contains no frame')
 times=([start/fps,(start+(n-1)/2)/fps,(start+n-1)/fps] if a.range else p.get('review_times',list(np.linspace(0,p['duration']-.1,24))));thumb=Image.new('RGB',(6*144,math.ceil(len(times)/6)*280),'#222222');d=ImageDraw.Draw(thumb)
 for i,t in enumerate(times):
  im=Image.fromarray(f.frame(float(t)));im.thumbnail((144,256));x=i%6*144;y=i//6*280;thumb.paste(im,(x,y));d.text((x+4,y+258),f'{t:.2f}s',fill='white')
 thumb.save(a.out/'contact-sheet.jpg',quality=94)
 backend.save(a.out/'render-backend.json')
 if a.stills:return
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{f.w}x{f.h}','-r',str(fps),'-i','-'];
 if a.audio:cmd+=['-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-af','apad','-c:a','aac','-b:a','192k']
 if a.profile=='lossless':cmd+=['-c:v','libx264rgb','-threads','4','-preset','ultrafast','-crf','0']
 elif a.profile=='high':cmd+=['-c:v','libx264','-threads','4','-preset','slow','-crf','12','-pix_fmt','yuv420p']
 else:cmd+=['-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p']
 cmd+=['-frames:v',str(n),'-t',str(n/fps),'-movflags','+faststart',str(a.out/'film.partial.mp4')]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for i in range(n):
  proc.stdin.write(f.render_frame((i+start)/fps,a.samples).tobytes())
  if i%(fps*3)==0:print(f'{i}/{n}',flush=True)
 proc.stdin.close()
 if proc.wait():raise RuntimeError('ffmpeg failed')
 (a.out/'film.partial.mp4').replace(a.out/'film.mp4')
 backend.save(a.out/'render-backend.json')
 (a.out/'render-interval.json').write_text(json.dumps({'start_frame':start,'frames':n,'fps':fps,'picture_only':not bool(a.audio)},indent=2))
if __name__=='__main__':main()
