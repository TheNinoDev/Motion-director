#!/usr/bin/env python3
"""Depth-tested mesh deformation, smooth shading and perspective-correct textures."""
import argparse, json, math, subprocess, sys
sys.path.insert(0,str(__import__("pathlib").Path(__file__).resolve().parents[1]))
import softbody
from pathlib import Path
import numpy as np
from numba import njit
from PIL import Image, ImageDraw, ImageFont, ImageColor
import cv2
KINDS=('ribbon','knot','sheet','obj'); MATS=('chrome','satin','ceramic','ink','texture')
RANGES={'phase':(0,1),'bend':(-2.4,2.4),'twist':(-3.2,3.2),'yaw':(-6.3,6.3),'pitch':(-1.3,1.3),'roll':(-3.2,3.2),'zoom':(.45,2.4),'panx':(-.8,.8),'pany':(-.8,.8),'light':(-6.3,6.3),'roughness':(.05,.85)}
def req(x,msg):
    if not x:raise ValueError(msg)
def num(x,a,b):return type(x) in (int,float) and math.isfinite(x) and a<=x<=b
def ease(t,k='smooth'):
    t=min(1,max(0,t));return t if k=='linear' else 1-(1-t)**3 if k=='out' else t**3 if k=='in' else t*t*(3-2*t)
def track(c,k,t,d):
    v=c.get(k,d)
    if not isinstance(v,list):return v
    for a,b in zip(v,v[1:]):
        if t<=b[0]:return a[1]+(b[1]-a[1])*ease((t-a[0])/(b[0]-a[0]),b[2] if len(b)==3 else 'smooth')
    return v[-1][1]
def validate(c):
    if 'softbody' in c:softbody.validate(c['softbody'])
    req(c.get('kind') in KINDS and c.get('material','chrome') in MATS,'mesh kind/material');req(type(c.get('frames')) is int and 4<=c['frames']<=3600,'mesh frames')
    for k,(a,b) in RANGES.items():
        if k not in c:continue
        v=c[k]
        if isinstance(v,list):
            req(2<=len(v)<=32,k+' key count');last=-1
            for q in v:
                req(isinstance(q,list) and len(q) in (2,3) and num(q[0],0,1) and q[0]>last and num(q[1],a,b) and (len(q)==2 or q[2] in ('linear','smooth','out','in')),k+' key');last=q[0]
            req(v[0][0]==0 and v[-1][0]==1,k+' endpoints')
        else:req(num(v,a,b),k+' range')
    for k,a,b,d in [('quality',.4,1,.75),('bloom',0,.25,.06),('shutter',0,1,.5),('grain',0,2,.3)]:req(num(c.get(k,d),a,b),k+' range')
    req(type(c.get('samples',1)) is int and 1<=c.get('samples',1)<=3,'samples 1..3');req(type(c.get('resolution',80)) is int and 24<=c.get('resolution',80)<=160,'resolution 24..160')
    for k in ('bg','fg','accent','tint'):req(len(ImageColor.getrgb(c.get(k,'#ffffff')))==3,'RGB only')
    if c.get('material')=='texture':req(c['kind']=='sheet' and Path(c.get('src','')).is_file(),'texture requires sheet and image')
    if c['kind']=='obj':req(c.get('material')!='texture' and Path(c.get('src','')).is_file() and Path(c['src']).suffix.lower()=='.obj','triangulated OBJ required')
    if 'crop' in c:
        r=c['crop'];req(isinstance(r,list) and len(r)==4 and all(num(x,0,1) for x in r) and r[0]<r[2] and r[1]<r[3],'bad crop')
    for k in ('title','caption','label'):req(isinstance(c.get(k,''),str) and len(c.get(k,''))<=90,'text limit')
    return c
def unit(x):return x/np.maximum(np.linalg.norm(x,axis=-1,keepdims=True),1e-8)
def faces(n,m,wrap=False):
    i,j=np.meshgrid(np.arange(n if wrap else n-1),np.arange(m-1),indexing='ij');a=(i*m+j).ravel();b=(((i+1)%n)*m+j).ravel();return np.concatenate([np.stack([a,b,a+1],1),np.stack([a+1,b,b+1],1)]).astype(np.int32)
def normals(v,f):
    n=np.zeros_like(v);q=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
    for j in range(3):np.add.at(n,f[:,j],q)
    return unit(n)
def geom(c,t,aspect):
    n=c.get('resolution',80);phase=track(c,'phase',t,ease(t));bend=track(c,'bend',t,1.65*(1-phase));twist=track(c,'twist',t,1.6*(1-phase));kind=c['kind']
    if kind=='sheet':
        m=max(12,n//2);u,v=np.meshgrid(np.linspace(-1,1,n),np.linspace(-1,1,m),indexing='ij');x=u*1.45;y=v*1.45/aspect;z=np.zeros_like(x)
        if abs(bend)>1e-5:x=np.sin(u*bend)*1.45/bend;z=(1-np.cos(u*bend))*1.45/bend
        a=twist*u*.65;Y=y*np.cos(a)-z*np.sin(a);Z=y*np.sin(a)+z*np.cos(a);vtx=np.stack([x,Y,Z],-1).reshape(-1,3);uv=np.stack([(u+1)/2,(1-v)/2],-1).reshape(-1,2);f=faces(n,m);return vtx,f,normals(vtx,f),uv
    m=32;u=np.linspace(0,2*np.pi,n,endpoint=False);vv=np.linspace(0,2*np.pi,m);rad=1.03+.24*np.cos(3*u)*(1-phase);k=2 if kind=='knot' else 1;center=np.stack([rad*np.cos(k*u),rad*np.sin(k*u),.48*np.sin(3*u)*(1-.65*phase)],1);tangent=unit(np.roll(center,-1,axis=0)-np.roll(center,1,axis=0));side=unit(np.cross(tangent,[0,0,1.]));up=unit(np.cross(tangent,side));a=twist*np.sin(u*2)+u*k;s=side*np.cos(a[:,None])+up*np.sin(a[:,None]);r=unit(np.cross(tangent,s));w=.32 if kind=='ribbon' else .24;hh=.105 if kind=='ribbon' else .23;vtx=(center[:,None,:]+w*np.cos(vv)[None,:,None]*s[:,None,:]+hh*np.sin(vv)[None,:,None]*r[:,None,:]).reshape(-1,3);f=faces(n,m,True);nn=normals(vtx,f).reshape(n,m,3);nn[:,0]=nn[:,-1]=unit(nn[:,0]+nn[:,-1]);return vtx,f,nn.reshape(-1,3),np.zeros((len(vtx),2))
def load_obj(path):
    vs=[];fs=[]
    for line in Path(path).read_text().splitlines():
        q=line.split('#')[0].split()
        if not q:continue
        if q[0]=='v':vs.append([float(x) for x in q[1:4]]);req(len(vs)<=50000,'too many vertices')
        if q[0]=='f':
            req(len(q)==4,'triangular OBJ faces only');ids=[]
            for a in q[1:]:
                i=int(a.split('/')[0]);req(i!=0,'OBJ index 0');ids.append(i-1 if i>0 else len(vs)+i)
            fs.append(ids);req(len(fs)<=80000,'too many faces')
    v=np.array(vs,float);f=np.array(fs,np.int32);req(v.ndim==2 and v.shape[1]==3 and len(v)>2 and len(f)>0 and np.isfinite(v).all() and f.min()>=0 and f.max()<len(v),'invalid OBJ');v-=(v.max(0)+v.min(0))/2;sc=np.max(np.ptp(v,axis=0));req(sc>1e-8,'empty OBJ');v*=2.8/sc;return v,f,normals(v,f),np.zeros((len(v),2))
@njit
def raster(project,f,attr,h,w):
    zbuf=np.zeros((h,w),np.float32);buf=np.zeros((h,w,attr.shape[1]),np.float32)
    for tri in f:
        ia,ib,ic=tri;a,b,c=project[ia],project[ib],project[ic];x0,y0,z0=a;x1,y1,z1=b;x2,y2,z2=c
        if min(z0,z1,z2)<.15:continue
        den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(den)<1e-7:continue
        l=max(0,int(math.floor(min(x0,x1,x2))));r=min(w-1,int(math.ceil(max(x0,x1,x2))));top=max(0,int(math.floor(min(y0,y1,y2))));bot=min(h-1,int(math.ceil(max(y0,y1,y2))))
        for y in range(top,bot+1):
            for x in range(l,r+1):
                u=((y1-y2)*(x+.5-x2)+(x2-x1)*(y+.5-y2))/den;v=((y2-y0)*(x+.5-x2)+(x0-x2)*(y+.5-y2))/den;q=1-u-v
                if min(u,v,q)<-1e-6:continue
                u/=z0;v/=z1;q/=z2;iz=u+v+q
                if iz<=zbuf[y,x]:continue
                zbuf[y,x]=iz
                for k in range(attr.shape[1]):buf[y,x,k]=(u*attr[ia,k]+v*attr[ib,k]+q*attr[ic,k])/iz
    return zbuf,buf
def rot(y,p,r):
    a,b=np.cos(y),np.sin(y);c,d=np.cos(p),np.sin(p);e,f=np.cos(r),np.sin(r);return np.array([[e,-f,0],[f,e,0],[0,0,1.]])@np.array([[1,0,0],[0,c,-d],[0,d,c]])@np.array([[a,0,b],[0,1,0],[-b,0,a]])
def environment(r,phase,rough):
    x,y,z=(r@rot(phase,0,0).T).T;soft=.07+rough*.32;box=np.exp(-((x+.38)/(.28+rough*.3))**4-((y-.48)/soft)**2)*2.6;strip=np.exp(-((x-.58)/soft)**2-((y+.06)/.65)**4)*1.5;top=np.exp(-((y-.92)/(.16+rough*.2))**2)*1.8;edge=np.exp(-((x+.82)/(.18+rough*.2))**2-((y+.12)/.62)**2)*.85;return .035+box[:,None]*[1,.97,.91]+strip[:,None]*[.75,.83,1]+top[:,None]*.8+edge[:,None]*[.68,.82,1]
class MeshMotion:
    def __init__(self,w,h,c,font):
        self.w=w;self.h=h;self.c=validate(c);self.font=font;self.obj=load_obj(c['src']) if c['kind']=='obj' else None;self.tex=None;self.aspect=1.4
        if c.get('material')=='texture':
            im=Image.open(c['src']).convert('RGB');r=c.get('crop',[0,0,1,1]);im=im.crop(tuple(round(x*y) for x,y in zip(r,[im.width,im.height,im.width,im.height])));req(min(im.size)>=2,'tiny texture');self.tex=np.asarray(im);self.aspect=im.width/im.height
        self.bg=np.array(ImageColor.getrgb(c.get('bg','#08090d')))/255;self.tint=np.array(ImageColor.getrgb(c.get('tint','#b9c5e7')))/255;self.noise=np.random.default_rng(23).normal(0,1,(h,w,1)).astype(np.float32)
    def sample(self,t):
        c=self.c;w=max(96,round(self.w*c.get('quality',.75)));h=max(96,round(self.h*c.get('quality',.75)));v,f,n,uv=self.obj if self.obj is not None else geom(c,t,self.aspect)
        if 'softbody' in c:v=softbody.deform(v,c['softbody'],t);n=normals(v,f)
        R=rot(track(c,'yaw',t,.45*(1-t)),track(c,'pitch',t,.18*(1-t)),track(c,'roll',t,0));v=v@R.T;n=n@R.T;z=5-v[:,2];focal=w*1.53*track(c,'zoom',t,1);p=np.stack([w*(.5+track(c,'panx',t,0))+focal*v[:,0]/z,h*(.5+track(c,'pany',t,0))-focal*v[:,1]/z,z],1);depth,a=raster(p,f,np.column_stack([n,v,uv]),h,w);mask=depth>0;yy,xx=np.ogrid[:h,:w];halo=np.exp(-((xx/w-.5)**2+(yy/h-.44)**2)*9).astype(np.float32);base=(self.bg**2.2*(1+.65*halo[...,None])).astype(np.float32);data=a[mask];nn=unit(data[:,:3]);vv=unit(np.array([0,0,5])-data[:,3:6]);dot=np.sum(nn*vv,1);nn=np.where(dot[:,None]<0,-nn,nn);dot=np.abs(dot);ref=2*dot[:,None]*nn-vv;env=environment(ref,track(c,'light',t,t*1.8),track(c,'roughness',t,.19));diff=.19+.65*np.maximum(nn@unit(np.array([-.5,.8,.7])),0);fr=(1-dot)**4;mat=c.get('material','chrome');tint=self.tint**2.2
        if mat=='texture':
            u=np.clip(data[:,6],0,1)*(self.tex.shape[1]-1);v=np.clip(data[:,7],0,1)*(self.tex.shape[0]-1);ix=u.astype(int);iy=v.astype(int);fx=(u-ix)[:,None];fy=(v-iy)[:,None];jx=np.minimum(ix+1,self.tex.shape[1]-1);jy=np.minimum(iy+1,self.tex.shape[0]-1);rgb=((1-fy)*((1-fx)*self.tex[iy,ix]+fx*self.tex[iy,jx])+fy*((1-fx)*self.tex[jy,ix]+fx*self.tex[jy,jx]))/255;phase=track(c,'phase',t,ease(t));rgb=rgb**2.2*(phase+(1-phase)*(.45+.55*diff[:,None]))+env*.055*(1-phase)
        elif mat=='chrome':rgb=env*(.42+.58*tint)+.09*diff[:,None]
        elif mat=='satin':rgb=env*(.28+.40*tint)+diff[:,None]*tint*.55
        elif mat=='ceramic':rgb=diff[:,None]*tint+env*(.055+.22*fr[:,None])
        else:rgb=.06*diff[:,None]*tint+env*(.08+.44*fr[:,None])
        base[mask]=rgb;return base
    def frame(self,i):
        c=self.c;n=c['frames'];ss=c.get('samples',1);a=sum(self.sample(max(0,min(1,(i+((j+.5)/ss-.5)*c.get('shutter',.5))/(n-1)))) for j in range(ss))/ss;b=c.get('bloom',.06)
        if b:a+=b*cv2.GaussianBlur(np.maximum(a-1,0),(0,0),max(1,a.shape[1]*.013))
        if c.get('material')!='texture':a=a/(a+.68)
        a=cv2.resize(np.clip(a,0,1)**(1/2.2),(self.w,self.h),interpolation=cv2.INTER_CUBIC);im=Image.fromarray(np.clip(a*255+self.noise*c.get('grain',.3),0,255).astype(np.uint8));d=ImageDraw.Draw(im)
        def text(s,x,y,size,color):
            if not s:return
            f=ImageFont.truetype(self.font,max(8,round(size*self.w/720)));width=d.textlength(s,font=f)
            if width>.85*self.w:f=ImageFont.truetype(self.font,max(8,int(f.size*.85*self.w/width)))
            d.text((round(x*self.w),round(y*self.h)),s,font=f,fill=color,anchor='lt')
        ac=c.get('accent','#dce98b');text(c.get('label',''),.075,.09,17,ac)
        if i/(n-1)>.12:text(c.get('title',''),.075,.765,100,c.get('fg','#f0eee7'))
        if i/(n-1)>.22:text(c.get('caption',''),.075,.86,23,ac)
        return np.asarray(im)
def main():
    p=argparse.ArgumentParser();p.add_argument('plan');p.add_argument('out');p.add_argument('--font',required=True);p.add_argument('--frame',type=int);a=p.parse_args();d=json.loads(Path(a.plan).read_text());w,h,fps=(d[k] for k in ('width','height','fps'));req(w%2==h%2==0 and 96<=w<=2160 and 96<=h<=3840 and 1<=fps<=60,'raster');ss=[MeshMotion(w,h,c,a.font) for c in d['shots']]
    if a.frame is not None:req(0<=a.frame<ss[0].c['frames'],'frame');Image.fromarray(ss[0].frame(a.frame)).save(a.out);return
    out=Path(a.out);tmp=out.with_name(out.stem+'.tmp.mp4');proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
    try:
        for sh in ss:
            for i in range(sh.c['frames']):proc.stdin.write(sh.frame(i).tobytes())
        proc.stdin.close();req(proc.wait()==0,'ffmpeg failed');tmp.replace(out)
    except BaseException:
        proc.kill();proc.wait();tmp.unlink(missing_ok=True);raise
if __name__=='__main__':main()
