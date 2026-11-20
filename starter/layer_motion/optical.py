"""V16 procedural graphic elements. CPU, deterministic, transparent layers, no GUI."""
import math
import numpy as np
import cv2
KINDS={'orbit','ribbons','network','scanner','halftone','waves','aperture','sparkfield'}

def validate(l):
    if l['kind'] not in KINDS:return
    for k,lo,hi in [('count',3,360),('speed',-4,4),('stroke_width',.5,30),('amplitude',0,1),('seed',0,2**31-1)]:
        if k in l:
            v=l[k]
            if type(v) not in (int,float) or not math.isfinite(v) or not lo<=v<=hi or k in ('count','seed') and type(v)!=int:raise ValueError('invalid optical '+k)

class Optical:
    def __init__(self,l,s,color):
        validate(l);self.l=l;self.w,self.h=[max(2,round(j*s)) for j in l['size']];self.s=s;self.color=color
        self.rng=np.random.default_rng(l.get('seed',9));self.n=l.get('count',36);self.pts=self.rng.uniform(.08,.92,(self.n,2));self.phase=self.rng.uniform(0,math.tau,self.n)
    def sample(self,p,f):
        l=self.l;w,h=self.w,self.h;kind=l['kind'];c=self.color;out=np.zeros((h,w,4),np.uint8);out[:,:,:3]=c[:3];a=np.zeros((h,w),np.uint8)
        n=self.n;t=f/30*l.get('speed',1);p=float(np.clip(p,0,1));r=min(w,h)*.43;cx=w/2;cy=h/2;th=max(1,round(l.get('stroke_width',2)*self.s));amp=l.get('amplitude',.55)
        def poly(x,y,alpha=255,closed=False,thick=th):
            pts=np.round(np.c_[x,y]).astype(np.int32);cv2.polylines(a,[pts],closed,int(np.clip(alpha,0,255)),max(1,thick),cv2.LINE_AA)
        def dot(x,y,rad,alpha):cv2.circle(a,(round(x),round(y)),max(1,round(rad)),int(np.clip(alpha,0,255)),-1,cv2.LINE_AA)
        theta=np.linspace(0,math.tau,241)
        if kind=='orbit':
            # Project real 3D points onto an image plane; depth controls size and luminance.
            for j in range(3):
                angle=theta+t*.7+j*.76;X=np.cos(angle);Y=np.sin(angle)*math.cos(.95+j*.43);Z=np.sin(angle)*math.sin(.95+j*.43);k=1/(1+.30*Z);rot=j*1.047+t*.12
                xx=cx+r*k*(X*np.cos(rot)-Y*np.sin(rot));yy=cy+r*k*(X*np.sin(rot)+Y*np.cos(rot));poly(xx,yy,82+j*24,True)
                for i in np.argsort(-Z[::8]):
                    q=i*8;dot(xx[q],yy[q],(1.8+2.8*(1-Z[q])*.5)*self.s,110+130*(1-Z[q])*.5)
        elif kind=='ribbons':
            u=np.linspace(-1,1,200)
            for j in range(min(n,30)):
                q=j/max(1,min(n,30)-1);x=cx+u*w*.47;y=cy+(q-.5)*h*.66+np.sin(u*math.pi*1.7+t*2+q*3)*h*.13*amp+np.cos(u*math.pi*3-t+q*2)*h*.04
                poly(x,y,55+170*math.sin(math.pi*q)**.6)
        elif kind=='network':
            xy=self.pts+np.c_[np.sin(self.phase+t),np.cos(self.phase+t*.83)]*.04*amp;xy=.5+(xy-.5)*(.35+.65*p);xy*=np.array([w,h]);dist=np.linalg.norm(xy[:,None,:]-xy[None,:,:],axis=2)
            for i in range(n):
                for j in np.argsort(dist[i])[1:4]:
                    if dist[i,j]<r*.75:cv2.line(a,tuple(xy[i].astype(int)),tuple(xy[j].astype(int)),int(100*(1-dist[i,j]/(r*.8))),th,cv2.LINE_AA)
                dot(*xy[i],(2+2*np.sin(self.phase[i]+t)**2)*self.s,190)
        elif kind=='scanner':
            yy,xx=np.ogrid[:h,:w];pos=(.1+.8*p)*h;beam=np.exp(-((yy-pos)/max(2,h*.025))**2);fade=np.clip(1-np.abs(xx-cx)/(w*.5),0,1);a[:]=np.uint8(beam*fade*160);cv2.line(a,(round(w*.05),round(pos)),(round(w*.95),round(pos)),230,th,cv2.LINE_AA)
            for j in range(1,9):
                y=round(h*j/10);cv2.line(a,(0,y),(round(w*.04),y),100,th,cv2.LINE_AA);cv2.line(a,(round(w*.96),y),(w-1,y),100,th,cv2.LINE_AA)
        elif kind=='halftone':
            cols=max(4,min(35,round(math.sqrt(n)*1.5)));rows=max(4,round(cols*h/w));step=min(w/cols,h/rows)
            for j in range(rows):
                for i in range(cols):
                    x=(i+.5)*w/cols;y=(j+.5)*h/rows;d=math.hypot((x-cx)/w,(y-cy)/h);v=.5+.5*math.cos(d*17-t*3);dot(x,y,step*(.06+.28*v)*(.4+.6*p),55+170*v)
        elif kind=='waves':
            for j in range(5):
                q=(p+j/5)%1;rad=r*(.15+.85*q);deform=1+amp*.08*np.sin(theta*5+t*3+j);poly(cx+rad*deform*np.cos(theta),cy+rad*deform*np.sin(theta),210*(1-q)**.7,True,th)
        elif kind=='aperture':
            for j in range(8):
                q=j*math.tau/8+t*.15;inner=r*(.15+.65*p);outer=r;angles=np.array([q,q+.50,q+.92,q+.38]);rad=np.array([inner,outer,outer,inner]);pts=np.round(np.c_[cx+rad*np.cos(angles),cy+rad*np.sin(angles)]).astype(np.int32);cv2.fillConvexPoly(a,pts,65+j*17,cv2.LINE_AA);cv2.polylines(a,[pts],True,200,th,cv2.LINE_AA)
        elif kind=='sparkfield':
            for i,(x,y) in enumerate(self.pts):
                v=(.65+.35*math.sin(t*2+self.phase[i]))**3;x=(x+.045*math.sin(t+self.phase[i]))%1;y=(y-.05*t)%1;rad=(1.2+3*v)*self.s;dot(x*w,y*h,rad,190*v)
                if i%9==0:
                    cv2.line(a,(round(x*w-rad*3),round(y*h)),(round(x*w+rad*3),round(y*h)),int(120*v),1,cv2.LINE_AA);cv2.line(a,(round(x*w),round(y*h-rad*3)),(round(x*w),round(y*h+rad*3)),int(120*v),1,cv2.LINE_AA)
        out[:,:,3]=np.uint8(a.astype(np.float32)*c[3]/255);return out

def distort(pic,f,amount,scale):
    if amount<=0:return pic
    h,w=pic.shape[:2];yy,xx=np.mgrid[:h,:w].astype(np.float32);dx=np.sin(yy/max(10,90*scale)+f*.12)*amount*scale;dy=np.sin(xx/max(10,130*scale)-f*.095)*amount*scale
    alpha=pic[:,:,3:4].astype(np.float32)/255;prem=np.concatenate([pic[:,:,:3]*alpha,pic[:,:,3:4]],axis=2).astype(np.float32);war=cv2.remap(prem,xx+dx,yy+dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT);a=war[:,:,3:4];return np.uint8(np.clip(np.concatenate([war[:,:,:3]*255/np.maximum(a,1e-5),a],axis=2),0,255))
