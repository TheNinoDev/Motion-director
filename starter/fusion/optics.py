"""Analytic 3D implicit geometry + two-interface approximate refraction. CPU, no GUI."""
import math
import numpy as np
from numba import njit, prange

@njit(cache=True)
def unit(x,y,z):
    s=1/max(1e-9,math.sqrt(x*x+y*y+z*z));return x*s,y*s,z*s
@njit(cache=True)
def rot(x,y,a):
    c=math.cos(a);s=math.sin(a);return x*c-y*s,x*s+y*c
@njit(cache=True)
def box(x,y,z,a,b,c,r):
    x=abs(x)-a;y=abs(y)-b;z=abs(z)-c
    return math.sqrt(max(x,0.)**2+max(y,0.)**2+max(z,0.)**2)+min(max(x,max(y,z)),0.)-r
@njit(cache=True)
def blend(a,b,k):
    h=max(k-abs(a-b),0.)/k
    return min(a,b)-h*h*k*.25
@njit(cache=True)
def shape(x,y,z,kind,p,twist):
    if kind==0: # fan of three rounded tablets merging into a single solid
        d=1e3
        for j in range(-1,2):
            q=1-p;xx,yy=rot(x-j*.57*q,y-j*.32*q,-j*.53*q);zz=z-j*.31*q
            a=box(xx,yy,zz,.53,.74,.085+.055*p,.105)
            d=blend(d,a,.055+.12*p)
        return d
    if kind==1: # twisted slab straightens; conservative distance step in tracer
        yy,zz=rot(y,z,twist*x*(1-p));return box(x,yy,zz,.94,.27+.20*p,.105,.12)
    if kind==2: # rounded cube flows into sphere
        a=box(x,y,z,.47,.47,.47,.15);b=math.sqrt(x*x+y*y+z*z)-.77
        return a*(1-p)+b*p
    if kind==3: # superelliptic frame changes to circular aperture
        q=abs(x)**4+abs(y)**4;rr=(q**.25)*(1-p)+math.sqrt(x*x+y*y)*p
        return (math.sqrt((rr-.68)**2+z*z)-.17)*.82
    # capsule assembly, separated in space then fused
    d=1e3
    for j in range(-1,2):
        xx,yy=rot(x-j*.46*(1-p),y,-j*.28*(1-p));zz=z-j*.30*(1-p)
        a=math.sqrt(xx*xx+max(0.,abs(yy)-.55)**2+zz*zz)-.22
        d=blend(d,a,.075+.10*p)
    return d
@njit(cache=True)
def field(x,y,z,kind,p,twist,ax,ay,az):
    x,z=rot(x,z,-ay);y,z=rot(y,z,-ax);x,y=rot(x,y,-az)
    return shape(x,y,z,kind,p,twist)
@njit(cache=True)
def normal(x,y,z,kind,p,twist,ax,ay,az):
    e=.0018
    return unit(field(x+e,y,z,kind,p,twist,ax,ay,az)-field(x-e,y,z,kind,p,twist,ax,ay,az),field(x,y+e,z,kind,p,twist,ax,ay,az)-field(x,y-e,z,kind,p,twist,ax,ay,az),field(x,y,z+e,kind,p,twist,ax,ay,az)-field(x,y,z-e,kind,p,twist,ax,ay,az))
@njit(cache=True)
def trace(ox,oy,oz,dx,dy,dz,kind,p,twist,ax,ay,az):
    # Enclosing sphere saves background rays. Radius covers all allowed shapes/poses.
    b=ox*dx+oy*dy+oz*dz;disc=b*b-(ox*ox+oy*oy+oz*oz-2.25**2)
    if disc<0:return 99.,False
    root=math.sqrt(disc);t=max(0.,-b-root);end=-b+root
    for _ in range(75):
        if t>end:return t,False
        q=field(ox+dx*t,oy+dy*t,oz+dz*t,kind,p,twist,ax,ay,az)
        if q<.0013:return t,True
        t+=max(q*.65,.001)
    return t,False
@njit(cache=True)
def env(x,y,z,light,rough):
    x,z=rot(x,z,light)
    # Offset rectangular-ish studio strips. Narrow dark gaps retain chrome contrast.
    a=math.exp(-((x+.67)/(.16+rough*.48))**2-((y-.33)/(.73+rough*.24))**6)
    b=math.exp(-((x-.58)/(.10+rough*.40))**2-((y-.05)/(.85+rough*.2))**8)
    c=math.exp(-((y-.88)/(.14+rough*.4))**2)*(.55+.45*max(z,0.))
    d=.12*math.exp(-((y+.64)/(.2+rough*.5))**2)
    return .008+3.4*a+2.0*b+1.8*c+d,.011+3.2*a+2.3*b+1.8*c+d,.017+2.9*a+2.7*b+1.9*c+d
@njit(cache=True)
def refract(dx,dy,dz,nx,ny,nz,eta):
    cosi=-(dx*nx+dy*ny+dz*nz);k=1-eta*eta*(1-cosi*cosi)
    if k<0:return dx+2*cosi*nx,dy+2*cosi*ny,dz+2*cosi*nz,False
    a=eta*cosi-math.sqrt(k);return eta*dx+a*nx,eta*dy+a*ny,eta*dz+a*nz,True
@njit(cache=True)
def glass_through(x,y,z,dx,dy,dz,nx,ny,nz,kind,p,twist,ax,ay,az,ior,light,rough,tint):
    tx,ty,tz,ok=refract(dx,dy,dz,nx,ny,nz,1/ior)
    # Walk to the first exit from the solid, avoiding a second self-intersection.
    d=.009
    for _ in range(64):
        q=field(x+tx*d,y+ty*d,z+tz*d,kind,p,twist,ax,ay,az)
        if q>=0 or d>5:break
        d+=max(-q*.65,.004)
    ex,ey,ez=normal(x+tx*d,y+ty*d,z+tz*d,kind,p,twist,ax,ay,az)
    tx,ty,tz,ok=refract(tx,ty,tz,-ex,-ey,-ez,ior)
    r,g,b=env(tx,ty,tz,light,rough)
    return r*math.exp(-d*(1-tint[0])*.8),g*math.exp(-d*(1-tint[1])*.8),b*math.exp(-d*(1-tint[2])*.8)
@njit(cache=True)
def shade(x,y,z,dx,dy,dz,kind,p,twist,ax,ay,az,material,rough,light,tint,ior):
    nx,ny,nz=normal(x,y,z,kind,p,twist,ax,ay,az);nd=dx*nx+dy*ny+dz*nz
    rx,ry,rz=dx-2*nd*nx,dy-2*nd*ny,dz-2*nd*nz
    r,g,b=env(rx,ry,rz,light,rough);f=(1-max(0.,-nd))**5
    diff=.04+.70*max(0.,nx*-.38+ny*.83+nz*.41)
    if material==0:return r,g,b
    if material==1: # ceramic
        return r*(.10+.35*f)+diff*.76,g*(.10+.35*f)+diff*.78,b*(.10+.35*f)+diff*.82
    if material==2: # anodized metal
        return r*(.24+.76*tint[0]),g*(.24+.76*tint[1]),b*(.24+.76*tint[2])
    if material==3: # two-interface glass approximation
        tr,tg,tb=glass_through(x,y,z,dx,dy,dz,nx,ny,nz,kind,p,twist,ax,ay,az,ior,light,rough,tint)
        f0=((ior-1)/(ior+1))**2;f=f0+(1-f0)*f
        return r*f+tr*(1-f)*.85,g*f+tg*(1-f)*.85,b*f+tb*(1-f)*.85
    return r*(.07+.72*f)+diff*.025,g*(.07+.72*f)+diff*.029,b*(.07+.72*f)+diff*.035
@njit(cache=True,parallel=True)
def render(w,h,kind,p,twist,ax,ay,az,material,rough,light,tint,ior,zoom,panx,pany,orbit,elevation,bg,exposure,floor):
    output=np.empty((h,w,3),np.float32);ox=4.7*math.sin(orbit);oz=4.7*math.cos(orbit);oy=elevation
    fx,fy,fz=unit(-ox,-oy,-oz);ux,uy,uz=unit(-fz,0.,fx);vx,vy,vz=uy*fz-uz*fy,uz*fx-ux*fz,ux*fy-uy*fx
    for j in prange(h):
        for i in range(w):
            sx=(i+.5-w*.5)*2/h/zoom+panx;sy=(h*.5-j-.5)*2/h/zoom+pany
            dx,dy,dz=unit(fx+sx*ux+sy*vx,fy+sx*uy+sy*vy,fz+sx*uz+sy*vz)
            dist,ok=trace(ox,oy,oz,dx,dy,dz,kind,p,twist,ax,ay,az)
            fd=(-1.75-oy)/dy if floor and dy<-.0001 else 1e5
            halo=.003*math.exp(-5*(sx*sx+sy*sy));r=bg[0]+halo;g=bg[1]+halo;b=bg[2]+halo
            if ok and dist<fd:r,g,b=shade(ox+dx*dist,oy+dy*dist,oz+dz*dist,dx,dy,dz,kind,p,twist,ax,ay,az,material,rough,light,tint,ior)
            elif fd<12:
                xx=ox+dx*fd;zz=oz+dz*fd;sh=.007*(1-.75*math.exp(-1.4*(xx*xx+zz*zz)));r+=sh;g+=sh;b+=sh
                rd,hit=trace(xx,-1.749,zz,dx,-dy,dz,kind,p,twist,ax,ay,az)
                if hit:
                    rr,gg,bb=shade(xx+dx*rd,-1.749-dy*rd,zz+dz*rd,dx,-dy,dz,kind,p,twist,ax,ay,az,material,rough,light,tint,ior);a=.18*(1-abs(dy))**2
                    r+=rr*a;g+=gg*a;b+=bb*a
            output[j,i,0]=r*exposure;output[j,i,1]=g*exposure;output[j,i,2]=b*exposure
    return output
