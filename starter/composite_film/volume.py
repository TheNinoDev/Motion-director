"""Closed 3D volume objects on a live 2D compositor. CPU SDF, two interfaces,
background-plane sampling. Coordinates are local world units; not a global raytracer.
"""
import math
import numpy as np
import cv2
from numba import njit,prange
from PIL import ImageColor
SHAPES=('box','rounded_box','sphere','ellipsoid','capsule','cylinder','torus','diamond','cone')
PRESETS={
 'clear':dict(ior=1.45,roughness=.04,transmission=.96,tint='#edf7ff',dispersion=.008),
 'frosted':dict(ior=1.43,roughness=.45,transmission=.88,tint='#e4edff',dispersion=.003),
 'smoked':dict(ior=1.5,roughness=.08,transmission=.81,tint='#687386',dispersion=.006),
 'prism':dict(ior=1.58,roughness=.03,transmission=.97,tint='#ffffff',dispersion=.035),
 'acrylic':dict(ior=1.36,roughness=.12,transmission=.91,tint='#e7f7ff',dispersion=.002),
 'chrome':dict(ior=1.5,roughness=.08,transmission=0,tint='#e6e9f0',dispersion=0),
 'ceramic':dict(ior=1.45,roughness=.5,transmission=0,tint='#e8e6e2',dispersion=0)}
RANGES={'depth':(1,1500),'bevel3d':(0,.45),'ior':(1.01,2.3),'roughness':(0,1),'transmission':(0,1),'dispersion':(0,.08),'absorption':(0,5),'twist3d':(-2,2),'bend3d':(-.8,.8),'scale_z':(.05,5),'size_x':(.05,5),'size_y':(.05,5),'background_gap':(0,3),'reflection':(0,2),'phase3d':(0,1)}
@njit(cache=True)
def rot(a,b,t):
 c=math.cos(t);s=math.sin(t);return c*a-s*b,s*a+c*b
@njit(cache=True)
def norm(x,y,z):
 k=1/max(1e-8,math.sqrt(x*x+y*y+z*z));return x*k,y*k,z*k
@njit(cache=True)
def field(x,y,z,k,a,b,c,r,ax,ay,twist,bend,phase):
 x,z=rot(x,z,-ay);y,z=rot(y,z,-ax);x,z=rot(x,z,twist*y);x-=bend*y*y
 if k<=1:
  rr=min(r,min(a,b,c)*.88) if k==1 else 0.;qx=abs(x)-a+rr;qy=abs(y)-b+rr;qz=abs(z)-c+rr
  d=math.sqrt(max(qx,0.)**2+max(qy,0.)**2+max(qz,0.)**2)+min(max(qx,max(qy,qz)),0.)-rr
  e=(math.sqrt((x/a)**2+(y/b)**2+(z/c)**2)-1)*min(a,b,c);return (1-phase)*d+phase*e
 if k==2:return math.sqrt(x*x+y*y+z*z)-min(a,b,c)
 if k==3:return (math.sqrt((x/a)**2+(y/b)**2+(z/c)**2)-1)*min(a,b,c)
 if k==4:
  rr=min(a,b,c);return (math.sqrt((x/a)**2+(max(0.,abs(y)-(b-rr))/rr)**2+(z/c)**2)-1)*rr
 if k==5:
  u=(math.sqrt((x/a)**2+(z/c)**2)-1)*min(a,c);v=abs(y)-b;return math.hypot(max(u,0.),max(v,0.))+min(max(u,v),0.)
 if k==6:
  # elliptical ring, tube depth independently adjustable
  return (math.sqrt(((math.hypot(x/a,y/b)-.68)/.32)**2+(z/c)**2)-1)*min(a*.32,b*.32,c)
 if k==7:return (abs(x/a)+abs(y/b)+abs(z/c)-1)*min(a,b,c)*.57
 # capped cone, conservative distance (tip up in image)
 u=(math.hypot(x/a,z/c)-max(.02,min(1.,(y/b+1)*.5)))*min(a,c)*.65;v=abs(y)-b;return max(u,v)
@njit(cache=True)
def normal(x,y,z,k,a,b,c,r,ax,ay,twist,bend,phase):
 e=.0015;return norm(field(x+e,y,z,k,a,b,c,r,ax,ay,twist,bend,phase)-field(x-e,y,z,k,a,b,c,r,ax,ay,twist,bend,phase),field(x,y+e,z,k,a,b,c,r,ax,ay,twist,bend,phase)-field(x,y-e,z,k,a,b,c,r,ax,ay,twist,bend,phase),field(x,y,z+e,k,a,b,c,r,ax,ay,twist,bend,phase)-field(x,y,z-e,k,a,b,c,r,ax,ay,twist,bend,phase))
@njit(cache=True)
def refract(dx,dy,dz,nx,ny,nz,eta):
 q=-(dx*nx+dy*ny+dz*nz);v=1-eta*eta*(1-q*q)
 if v<0:return dx+2*q*nx,dy+2*q*ny,dz+2*q*nz,False
 f=eta*q-math.sqrt(v);return eta*dx+f*nx,eta*dy+f*ny,eta*dz+f*nz,True
@njit(cache=True,parallel=True)
def maps(X,Y,k,a,b,c,r,ax,ay,twist,bend,phase,ior,rough,light,gap):
 h,w=X.shape;out=np.zeros((h,w,6),np.float32);bound=math.sqrt(a*a+b*b+c*c)+abs(bend)*b*b+.06
 for j in prange(h):
  for i in range(w):
   x=X[j,i];y=Y[j,i];q=bound*bound-x*x-y*y
   if q<=0:continue
   end=math.sqrt(q);z=-end;hit=False
   for _ in range(100):
    d=field(x,y,z,k,a,b,c,r,ax,ay,twist,bend,phase)
    if d<.0015:hit=True;break
    z+=max(.0008,d*.66)
    if z>end:break
   if not hit:continue
   nx,ny,nz=normal(x,y,z,k,a,b,c,r,ax,ay,twist,bend,phase)
   tx,ty,tz,_=refract(0.,0.,1.,nx,ny,nz,1/ior);step=.006
   for _ in range(100):
    d=field(x+tx*step,y+ty*step,z+tz*step,k,a,b,c,r,ax,ay,twist,bend,phase)
    if d>=0 or step>4*bound:break
    step+=max(.002,-d*.66)
   ex,ey,ez=normal(x+tx*step,y+ty*step,z+tz*step,k,a,b,c,r,ax,ay,twist,bend,phase)
   ux,uy,uz,ok=refract(tx,ty,tz,-ex,-ey,-ez,ior)
   # grazing or total internal reflection uses environment rather than false extreme refraction
   fres=((ior-1)/(ior+1))**2;fres+=(1-fres)*(1-min(1.,abs(nz)))**5
   rx,ry,rz=-2*nz*nx,-2*nz*ny,1-2*nz*nz;rx,ry=rot(rx,ry,light)
   spec=.08+.82*math.exp(-((rx+.53)/(.16+rough*.38))**2-((ry+.10)/.76)**6)+.65*math.exp(-((ry+.72)/(.12+rough*.37))**2)+.38*math.exp(-((rx-.66)/(.11+rough*.5))**2)
   if not ok or uz<=.07:fres=max(fres,.85);ux=uy=0.;uz=1.
   travel=max(0.,end+gap*bound-(z+tz*step))/max(.15,uz)
   out[j,i,0]=max(-2*bound,min(2*bound,tx*step+ux*travel));out[j,i,1]=max(-2*bound,min(2*bound,ty*step+uy*travel));out[j,i,2]=fres;out[j,i,3]=spec;out[j,i,4]=step;out[j,i,5]=1.
 return out

def draw(im,M,l,t,val,op,scale,backend=None):
 g=lambda k,d:val(l.get(k,d),t);preset=PRESETS[l.get('material','clear')];w=l['w']*g('size_x',1);h=l['h']*g('size_y',1);depth=g('depth',min(w,h)*.65)*g('scale_z',1);unit=max(w,h,depth)/2
 a,b,c=w/(2*unit),h/(2*unit),depth/(2*unit);bend=g('bend3d',0);bound=(math.sqrt(a*a+b*b+c*c)+abs(bend)*b*b+.06)*unit
 A=M.copy();A[:2]*=scale;corn=(np.array([[-bound,-bound,1],[bound,-bound,1],[bound,bound,1],[-bound,bound,1]])@A.T)[:,:2];lo=np.maximum(0,np.floor(corn.min(0)).astype(int)-2);hi=np.minimum([im.shape[1],im.shape[0]],np.ceil(corn.max(0)).astype(int)+2);W,H=hi-lo
 if W<2 or H<2 or abs(np.linalg.det(A[:2,:2]))<1e-7:return
 quality=l.get('quality',.55)*l.get('antialias',1);rw=max(2,round(W*quality));rh=max(2,round(H*quality));xx,yy=np.meshgrid(lo[0]-.5+(np.arange(rw,dtype=np.float32)+.5)*W/rw,lo[1]-.5+(np.arange(rh,dtype=np.float32)+.5)*H/rh);I=np.linalg.inv(A);X=(I[0,0]*xx+I[0,1]*yy+I[0,2])/unit;Y=(I[1,0]*xx+I[1,1]*yy+I[1,2])/unit
 rough=g('roughness',preset['roughness']);ior=g('ior',preset['ior']);trans=g('transmission',preset['transmission']);disp=g('dispersion',preset['dispersion']);tint=np.asarray(ImageColor.getrgb(l.get('color',preset['tint'])),np.float32)/255
 run=maps if backend is None else lambda *a:backend.run("volume",maps,*a)
 m=run(X,Y,SHAPES.index(l.get('geometry','rounded_box')),a,b,c,g('bevel3d',.13),math.radians(g('pitch',0)),math.radians(g('yaw',0)),g('twist3d',0),bend,g('phase3d',0),ior,rough,g('light',0),g('background_gap',.45));alpha=m[:,:,5:6].copy();mp=g('mask_progress',1);kind=l.get('mask');reveal=g('reveal',1)
 if kind or reveal<1:
  U=X*unit/(2*bound)+.5;V=Y*unit/(2*bound)+.5;feather=max(.001,g('mask_feather',.025));
  q={'iris':np.hypot(U-.5,V-.5)/.71,'wipe':U,'diagonal':(U+V*.45)/1.45,'shutter':(V*8)%1}.get(kind,np.zeros_like(U));
  if kind and mp<1:alpha[:,:,0]*=np.clip((mp-q)/feather+.5,0,1) if mp>0 else 0
  if reveal<1:alpha[:,:,0]*=np.clip((reveal-(1-V))/feather+.5,0,1) if reveal>0 else 0
 dx=(A[0,0]*m[:,:,0]+A[0,1]*m[:,:,1])*unit;dy=(A[1,0]*m[:,:,0]+A[1,1]*m[:,:,1])*unit
 # sample only live composited pixels, then add studio reflections in linear light
 src=cv2.GaussianBlur(im,(0,0),rough*8*scale) if rough>.025 and trans>0 else im
 def sample(q):return cv2.remap(src,(xx+dx*q).astype(np.float32),(yy+dy*q).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
 img=sample(1).astype(np.float32)/255
 if disp>0 and trans>0:img[:,:,0]=sample(1+disp*2)[:,:,0]/255;img[:,:,2]=sample(1-disp*2)[:,:,2]/255
 f=m[:,:,2:3];spec=m[:,:,3:4]*g('reflection',1);absor=np.exp(-m[:,:,4:5]*(1-tint)*g('absorption',1.6));C=(img**2.2)*absor*trans*(1-f)+spec*(f+(1-trans)*(.8 if l.get('material')=='chrome' else .3))*tint+(1-trans)*(.04+.26*(1-rough))*tint*(1-f)
 C=np.clip(C,0,1)**(1/2.2)*255
 interp=cv2.INTER_AREA if rw>W or rh>H else cv2.INTER_LINEAR;C=cv2.resize(np.clip(C*alpha,0,255),(W,H),interpolation=interp);alpha=cv2.resize(alpha,(W,H),interpolation=interp)[:,:,None];roi=im[lo[1]:hi[1],lo[0]:hi[0]];
 if l.get('shadow'):
  from refinement import shadow_pass
  roi[:]=np.uint8(np.clip(shadow_pass(roi.astype(np.float32),alpha,g('shadow_x',0)*scale,g('shadow_y',12)*scale,max(0,g('shadow_blur',20)*scale),max(0,min(1,g('shadow_opacity',.35)))*op,ImageColor.getrgb(l.get('shadow_color','#000000'))),0,255))
 roi[:]=np.uint8(np.clip(roi*(1-alpha*op)+C*op,0,255))
