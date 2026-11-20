"""True beveled glyph extrusion from a high-resolution signed distance atlas.
CPU orthographic ray marcher. Preserves counters; no copied font distributions.
"""
import math
import numpy as np, cv2
from PIL import Image,ImageDraw,ImageFont,ImageColor
from numba import njit,prange
from volume import rot,norm
MATERIALS=('chrome','satin','ceramic','obsidian','gold')
def prepare(text,font_path,size,maxw,atlas_resolution=640):
 font=ImageFont.truetype(font_path,atlas_resolution);a,b,c,d=font.getbbox(text);w=c-a;h=d-b
 if min(w,h)<1 or w>24000:raise ValueError('empty or oversized glyph atlas')
 pad=max(40,atlas_resolution//8);im=Image.new('L',(w+2*pad,h+2*pad));ImageDraw.Draw(im).text((pad-a,pad-b),text,font=font,fill=255)
 mask=(np.asarray(im)>127).astype(np.uint8);dist=cv2.distanceTransform(1-mask,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)-cv2.distanceTransform(mask,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
 dist=cv2.GaussianBlur(dist,(0,0),3.5)
 factor=size/atlas_resolution
 if maxw and w*factor>maxw:factor=maxw/w
 return dist.astype(np.float32),factor,w*factor,h*factor
@njit(cache=True)
def sdf(x,y,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist):
 x,z=rot(x,z,-yaw);y,z=rot(y,z,-pitch);x,z=rot(x,z,twist*y);x-=bend*y*y
 x/=sx;y/=sy;z/=sz
 u=x/pix+(atlas.shape[1]-1)*.5;v=y/pix+(atlas.shape[0]-1)*.5
 U=max(0.,min(atlas.shape[1]-1.001,u));V=max(0.,min(atlas.shape[0]-1.001,v));i=int(U);j=int(V);f=U-i;g=V-j
 a=((atlas[j,i]*(1-f)+atlas[j,i+1]*f)*(1-g)+(atlas[j+1,i]*(1-f)+atlas[j+1,i+1]*f)*g)*pix+math.hypot(u-U,v-V)*pix
 q=a+bevel;r=abs(z)-half+bevel
 return (math.hypot(max(q,0.),max(r,0.))+min(max(q,r),0.)-bevel)*min(sx,sy,sz)
@njit(cache=True,parallel=True)
def render(X,Y,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist,bound,light,rough,mat,tint):
 h,w=X.shape;out=np.zeros((h,w,4),np.float32)
 for j in prange(h):
  for i in range(w):
   x=X[j,i];y=Y[j,i];rr=bound*bound-x*x-y*y
   if rr<=0:continue
   end=math.sqrt(rr);z=-end;hit=False
   for it in range(160):
    d=sdf(x,y,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist)
    if d<.00045:hit=True;break
    z+=max(.00022,d*.55)
    if z>end:break
   if not hit:continue
   e=max(.002,pix*5.5);nx,ny,nz=norm(sdf(x+e,y,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist)-sdf(x-e,y,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist),sdf(x,y+e,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist)-sdf(x,y-e,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist),sdf(x,y,z+e,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist)-sdf(x,y,z-e,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist))
   rx,ry,rz=-2*nz*nx,-2*nz*ny,1-2*nz*nz;rx,ry=rot(rx,ry,light)
   # broad softboxes, black flags, narrow strip highlights; spatial gradient on face.
   u=rx+.42*x;v=ry+.55*y
   key=2.2*math.exp(-((u+.30)/(.34+rough*.3))**4-((v+.42)/(.16+rough*.55))**2)
   fill=.8*math.exp(-((u-.53)/(.22+rough*.4))**2-((v-.12)/.72)**4)
   rim=1.8*math.exp(-((v+.88)/(.10+rough*.24))**2)+.42*math.exp(-((u+.85)/(.14+rough*.4))**2)
   # A finite, graded strip light makes flat faces exhibit readable dark/light bands.
   band=y+.23*x+.42*ny+.13*math.sin(light);broad=1.45*math.exp(-((band+.28)/(.19+rough*.30))**4);narrow=.8*math.exp(-((band-.18)/(.055+rough*.10))**2);base=.018+broad+narrow+key*.6+fill*.6+rim;diff=.22+.70*max(0.,-.44*nx-.65*ny-.60*nz);fres=(1-min(1.,abs(nz)))**4
   for k in range(3):
    rgb=base*tint[k]
    if mat==1:rgb=(base*.52+diff*.52)*tint[k]
    if mat==2:rgb=(diff+base*(.05+.22*fres))*tint[k]
    if mat==3:rgb=(diff*.08+base*(.12+.42*fres))*tint[k]
    out[j,i,k]=min(1.,max(0.,rgb/(rgb+.43)))**(1/2.2)*255
   out[j,i,3]=255
 return out

def draw(im,M,l,t,val,op,scale,prepared,backend=None):
 atlas,factor,w,h=prepared;g=lambda k,d:val(l.get(k,d),t);unit=max(w,h,1)/2;depth=g('depth',36);sx=g('size_x',1);sy=g('size_y',1);sz=g('scale_z',1);bend=g('bend3d',0);twist=g('twist3d',0)
 bound=(math.sqrt((w*sx/2)**2+(h*sy/2)**2+(depth*sz/2)**2)+abs(bend)*unit+factor*15)/unit
 A=M.copy();A[:2]*=scale;B=bound*unit;corn=np.array([[-B,-B,1],[B,-B,1],[B,B,1],[-B,B,1]])@A.T;lo=np.maximum(0,np.floor(corn[:,:2].min(0)).astype(int)-2);hi=np.minimum([im.shape[1],im.shape[0]],np.ceil(corn[:,:2].max(0)).astype(int)+2);W,H=hi-lo
 if W<2 or H<2 or abs(np.linalg.det(A[:2,:2]))<1e-7:return
 quality=l.get('quality',.7)*l.get('antialias',1);rw=max(2,round(W*quality));rh=max(2,round(H*quality));xx,yy=np.meshgrid((lo[0]-.5+(np.arange(rw,dtype=np.float32)+.5)*W/rw),(lo[1]-.5+(np.arange(rh,dtype=np.float32)+.5)*H/rh));I=np.linalg.inv(A);X=((I[0,0]*xx+I[0,1]*yy+I[0,2])/unit).astype(np.float32);Y=((I[1,0]*xx+I[1,1]*yy+I[1,2])/unit).astype(np.float32)
 material=l.get('material','chrome');tint=np.array(ImageColor.getrgb(l.get('color',{'gold':'#ecc17c','obsidian':'#686e80'}.get(material,'#e3e8f5'))),dtype=np.float32)/255
 run=render if backend is None else lambda *a:backend.run("text",render,*a)
 r=run(X,Y,atlas,factor/unit,depth/(2*unit),min(g('bevel3d',4),depth*.45)/unit,math.radians(g('pitch',0)),math.radians(g('yaw',0)),sx,sy,sz,bend,twist,bound,g('light',0),g('roughness',.18),MATERIALS.index(material),tint**2.2)
 alpha=r[:,:,3:4]/255;mp=g('mask_progress',1);reveal=g('reveal',1);kind=l.get('mask');U=X/(2*bound)+.5;V=Y/(2*bound)+.5;feather=max(.001,g('mask_feather',.025));q={'iris':np.hypot(U-.5,V-.5)/.71,'wipe':U,'diagonal':(U+V*.45)/1.45,'shutter':(V*8)%1}.get(kind)
 if kind and mp<1:alpha[:,:,0]*=np.clip((mp-q)/feather+.5,0,1) if mp>0 else 0
 if reveal<1:alpha[:,:,0]*=np.clip((reveal-(1-V))/feather+.5,0,1) if reveal>0 else 0
 interp=cv2.INTER_AREA if rw>W or rh>H else cv2.INTER_LINEAR;C=cv2.resize(r[:,:,:3]*alpha,(W,H),interpolation=interp);a=cv2.resize(alpha,(W,H),interpolation=interp)[:,:,None];roi=im[lo[1]:hi[1],lo[0]:hi[0]]
 if l.get('shadow'):
  from refinement import shadow_pass
  roi[:]=np.uint8(np.clip(shadow_pass(roi.astype(np.float32),a,g('shadow_x',0)*scale,g('shadow_y',12)*scale,g('shadow_blur',20)*scale,g('shadow_opacity',.35)*op,ImageColor.getrgb(l.get('shadow_color','#000000'))),0,255))
 roi[:]=np.uint8(np.clip(roi*(1-a*op)+C*op,0,255))
