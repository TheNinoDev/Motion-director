"""CUDA per-pixel kernels ported from the V34 CPU references. No fastmath.
Each thread owns one output pixel. Host compositing and physics stay unchanged.
Imported only when CUDA is selected. CPU parity tests guard the shared math.
"""
import math
from numba import cuda
@cuda.jit(device=True)
def rot(a,b,t):
 c=math.cos(t);s=math.sin(t);return c*a-s*b,s*a+c*b

@cuda.jit(device=True)
def norm(x,y,z):
 k=1/max(1e-8,math.sqrt(x*x+y*y+z*z));return x*k,y*k,z*k

@cuda.jit(device=True)
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

@cuda.jit(device=True)
def normal(x,y,z,k,a,b,c,r,ax,ay,twist,bend,phase):
 e=.0015;return norm(field(x+e,y,z,k,a,b,c,r,ax,ay,twist,bend,phase)-field(x-e,y,z,k,a,b,c,r,ax,ay,twist,bend,phase),field(x,y+e,z,k,a,b,c,r,ax,ay,twist,bend,phase)-field(x,y-e,z,k,a,b,c,r,ax,ay,twist,bend,phase),field(x,y,z+e,k,a,b,c,r,ax,ay,twist,bend,phase)-field(x,y,z-e,k,a,b,c,r,ax,ay,twist,bend,phase))

@cuda.jit(device=True)
def refract(dx,dy,dz,nx,ny,nz,eta):
 q=-(dx*nx+dy*ny+dz*nz);v=1-eta*eta*(1-q*q)
 if v<0:return dx+2*q*nx,dy+2*q*ny,dz+2*q*nz,False
 f=eta*q-math.sqrt(v);return eta*dx+f*nx,eta*dy+f*ny,eta*dz+f*nz,True

@cuda.jit
def volume_kernel(X, Y, k, a, b, c, r, ax, ay, twist, bend, phase, ior, rough, light, gap, out):
    i, j = cuda.grid(2)
    h, w = X.shape
    if j >= h or i >= w: return
    for ch in range(6): out[j,i,ch]=0.
    bound=math.sqrt(a*a+b*b+c*c)+abs(bend)*b*b+.06
    x=X[j,i];y=Y[j,i];q=bound*bound-x*x-y*y
    if q<=0:return
    end=math.sqrt(q);z=-end;hit=False
    for _ in range(100):
     d=field(x,y,z,k,a,b,c,r,ax,ay,twist,bend,phase)
     if d<.0015:hit=True;break
     z+=max(.0008,d*.66)
     if z>end:break
    if not hit:return
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

@cuda.jit(device=True)
def sdf(x,y,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist):
 x,z=rot(x,z,-yaw);y,z=rot(y,z,-pitch);x,z=rot(x,z,twist*y);x-=bend*y*y
 x/=sx;y/=sy;z/=sz
 u=x/pix+(atlas.shape[1]-1)*.5;v=y/pix+(atlas.shape[0]-1)*.5
 U=max(0.,min(atlas.shape[1]-1.001,u));V=max(0.,min(atlas.shape[0]-1.001,v));i=int(U);j=int(V);f=U-i;g=V-j
 a=((atlas[j,i]*(1-f)+atlas[j,i+1]*f)*(1-g)+(atlas[j+1,i]*(1-f)+atlas[j+1,i+1]*f)*g)*pix+math.hypot(u-U,v-V)*pix
 q=a+bevel;r=abs(z)-half+bevel
 return (math.hypot(max(q,0.),max(r,0.))+min(max(q,r),0.)-bevel)*min(sx,sy,sz)

@cuda.jit
def text_kernel(X, Y, atlas, pix, half, bevel, pitch, yaw, sx, sy, sz, bend, twist, bound, light, rough, mat, tint, out):
    i, j = cuda.grid(2)
    h, w = X.shape
    if j >= h or i >= w: return
    for ch in range(4): out[j,i,ch]=0.
    x=X[j,i];y=Y[j,i];rr=bound*bound-x*x-y*y
    if rr<=0:return
    end=math.sqrt(rr);z=-end;hit=False
    for it in range(160):
     d=sdf(x,y,z,atlas,pix,half,bevel,pitch,yaw,sx,sy,sz,bend,twist)
     if d<.00045:hit=True;break
     z+=max(.00022,d*.55)
     if z>end:break
    if not hit:return
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

@cuda.jit(device=True)
def hit(o,d,c,s):
    a=0.;b=0.;cc=-1.
    for j in range(3):
        q=(o[j]-c[j])/s[j];v=d[j]/s[j];a+=v*v;b+=q*v;cc+=q*q
    q=b*b-a*cc
    if q<0:return 1e9
    t=(-b-math.sqrt(q))/a
    return t if t>0 else 1e9

@cuda.jit
def contact_kernel(o, rays, balls, colors, im):
    i, j = cuda.grid(2)
    h, w, _ = rays.shape
    if j >= h or i >= w: return
    d=rays[j,i];t=1e8;kind=-1;px=0.;py=0.;pz=0.
    if d[1]<-1e-6:
        t=-o[1]/d[1];kind=0
    if d[0]<-1e-6:
        q=-o[0]/d[0];y=o[1]+q*d[1];z=o[2]+q*d[2]
        if q<t and 0<=y<=3.0 and abs(z)<=3.4:t=q;kind=1
    if d[2]<-1e-6:
        q=(3.4-o[2])/d[2];x=o[0]+q*d[0];y=o[1]+q*d[1]
        if 0<q<t and -.22<=x<=0 and 0<=y<=3:t=q;kind=1
    if d[1]<-1e-6:
        q=(3-o[1])/d[1];x=o[0]+q*d[0];z=o[2]+q*d[2]
        if 0<q<t and -.22<=x<=0 and abs(z)<=3.4:t=q;kind=1
    for a in range(len(balls)):
        q=hit(o,d,balls[a,:3],balls[a,3:6]);
        if q<t:t=q;kind=a+2
    if kind<0:
        for c in range(3):im[j,i,c]=int(34+18*(1-j/h)+c*3)
        return
    px=o[0]+t*d[0];py=o[1]+t*d[1];pz=o[2]+t*d[2]
    if kind<2:
        # matte cyclorama surfaces, subtle ruler markings, soft local contact shadows
        base=.12 if kind==0 else .32
        if kind==0:base*=.84+.16*math.exp(-.10*((px-2)**2+pz*pz))
        else:base*=.93+.07*py/3
        if kind==1 and abs(px)>.001:base*=.72
        shadow=1.
        for a in range(len(balls)):
            b=balls[a];
            if kind==0:
                dd=((px-b[0]-.12)**2/(b[3]+.25)**2+(pz-b[2]+.1)**2/(b[5]+.25)**2);amount=.35*math.exp(-.65*max(0,b[1]-b[4]))
            else:
                dd=((py-b[1])**2/(b[4]+.25)**2+(pz-b[2])**2/(b[5]+.25)**2);amount=.58*math.exp(-2*max(0,b[0]-b[3]))
            shadow*=1-amount*math.exp(-2*dd)
        if kind==1 and abs(py-.18)<.013:base*=.58
        if kind==1 and py<.19 and py>.10 and abs(pz-round(pz*2)/2)<.014:base*=.55
        for c in range(3):im[j,i,c]=int(255*min(1,base*shadow*(.90+.06*c))**(1/2.2))
    else:
        a=kind-2;b=balls[a];nx=(px-b[0])/b[3]**2;ny=(py-b[1])/b[4]**2;nz=(pz-b[2])/b[5]**2;ln=math.sqrt(nx*nx+ny*ny+nz*nz);nx/=ln;ny/=ln;nz/=ln
        nd=nx*d[0]+ny*d[1]+nz*d[2];rx=d[0]-2*nd*nx;ry=d[1]-2*nd*ny;rz=d[2]-2*nd*nz
        diffuse=.15+.68*max(0.,nx*.42+ny*.82+nz*.39);rim=(1-max(0,-nd))**4
        spec=.9*math.exp(-((rx+.22)/.34)**4-((ry-.75)/.18)**2)+.42*math.exp(-((rz+.65)/.18)**2-((ry-.28)/.62)**4)+.11*rim
        for c in range(3):
            q=colors[a,c]*diffuse+spec*.44+rim*.12;im[j,i,c]=int(255*min(1,q)**(1/2.2))
