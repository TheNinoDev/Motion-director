"""Headless CPU signed-distance renderer. Real camera rays and reflected light directions.
Analytic studio environment, not path tracing; geometry and plane reflections are ray traced.
"""
import math
import numpy as np
from numba import njit,prange

@njit(cache=True,inline='always')
def rot(x,y,a):
    c=math.cos(a);s=math.sin(a);return c*x-s*y,s*x+c*y

@njit(cache=True,inline='always')
def torus(x,y,z,R,r,wave):
    ang=math.atan2(y,x); R+=wave*math.cos(3*ang)
    return math.sqrt((math.sqrt(x*x+y*y)-R)**2+z*z)-r

@njit(cache=True,inline='always')
def sdf(x,y,z,kind,ax,ay,az,twist):
    x,z=rot(x,z,-ay);y,z=rot(y,z,-ax);x,y=rot(x,y,-az)
    if kind==0:return torus(x,y,z,.75,.23,0.)
    if kind==1:
        a=torus(x+.36,y,z,.57,.17,0.)
        u,v=rot(y,z,1.12)
        b=torus(x-.36,u,v,.57,.17,0.)
        return min(a,b)
    if kind==2:
        # Lobed tube is a conservative distance estimate, not an exact SDF.
        return torus(x,y,z,.70,.17,twist)*.72
    # rounded rectilinear loop; square-like aperture
    qx=abs(x)-.53;qy=abs(y)-.53
    r=math.sqrt(max(qx,0)**2+max(qy,0)**2)+min(max(qx,qy),0)-.20
    return math.sqrt(r*r+z*z)-.15

@njit(cache=True,inline='always')
def unit(x,y,z):
    k=1/max(1e-12,math.sqrt(x*x+y*y+z*z));return x*k,y*k,z*k

@njit(cache=True,inline='always')
def trace(ox,oy,oz,dx,dy,dz,kind,ax,ay,az,twist):
    d=0.
    for i in range(76):
        x=ox+dx*d;y=oy+dy*d;z=oz+dz*d
        q=sdf(x,y,z,kind,ax,ay,az,twist)
        if q<.0012:return d,True
        d+=max(q*.86,.001)
        if d>12.:break
    return d,False

@njit(cache=True,inline='always')
def env(x,y,z,light,rough):
    # Long strip softboxes and dark negative fill: reflection direction selects intensity.
    x,z=rot(x,z,light)
    a=math.exp(-((x+.66)/(.19+rough*.55))**2-((y-.42)/(.85+rough*.5))**2) if z>-.35 else 0.
    b=math.exp(-((x-.50)/(.12+rough*.55))**2-((y-.30)/(.80+rough*.45))**2) if z>-.65 else 0.
    c=math.exp(-((y-.87)/(.17+rough*.55))**2)*(.6+.4*max(z,0.))
    d=math.exp(-((y+.55)/(.20+rough*.6))**2)*max(0.,z)*.22
    return (.003+3.2*a+2.5*b+1.5*c+d,.004+3.0*a+2.7*b+1.52*c+d,.006+2.8*a+3.1*b+1.55*c+d)

@njit(cache=True,inline='always')
def shade(x,y,z,dx,dy,dz,kind,ax,ay,az,twist,mat,rough,light,tint):
    e=.002
    nx,ny,nz=unit(sdf(x+e,y,z,kind,ax,ay,az,twist)-sdf(x-e,y,z,kind,ax,ay,az,twist),sdf(x,y+e,z,kind,ax,ay,az,twist)-sdf(x,y-e,z,kind,ax,ay,az,twist),sdf(x,y,z+e,kind,ax,ay,az,twist)-sdf(x,y,z-e,kind,ax,ay,az,twist))
    nd=dx*nx+dy*ny+dz*nz
    rx,ry,rz=dx-2*nd*nx,dy-2*nd*ny,dz-2*nd*nz
    er,eg,eb=env(rx,ry,rz,light,rough)
    diffuse=.13+.64*max(0.,nx*-.42+ny*.77+nz*.48)
    fres=(1-max(0.,-nd))**5
    if mat==0:return er*(.82+.18*fres),eg*(.84+.16*fres),eb*(.86+.14*fres)
    if mat==1:return er*(.30+.70*fres)+diffuse*.54,eg*(.30+.70*fres)+diffuse*.56,eb*(.30+.70*fres)+diffuse*.60
    return er*(.35+.65*fres)*tint[0]+diffuse*tint[0]*.17,eg*(.35+.65*fres)*tint[1]+diffuse*tint[1]*.17,eb*(.35+.65*fres)*tint[2]+diffuse*tint[2]*.17

@njit(cache=True,parallel=True)
def render(w,h,kind,ax,ay,az,twist,mat,rough,light,tint,zoom,panx,pany,orbit,floor,bg):
    out=np.empty((h,w,3),np.uint8)
    # Camera orbits target; horizontal/vertical lens shift is independent of orientation.
    ox=4.25*math.sin(orbit);oy=.22;oz=4.25*math.cos(orbit)
    fx,fy,fz=unit(-ox,-oy,-oz);ux,uy,uz=unit(-fz,0.,fx)
    vx,vy,vz=uy*fz-uz*fy,uz*fx-ux*fz,ux*fy-uy*fx
    for j in prange(h):
        for i in range(w):
            sx=((i+.5-w*.5)/h)*2/zoom+panx;sy=((h*.5-j-.5)/h)*2/zoom+pany
            dx,dy,dz=unit(fx+sx*ux+sy*vx,fy+sx*uy+sy*vy,fz+sx*uz+sy*vz)
            dist,hit=trace(ox,oy,oz,dx,dy,dz,kind,ax,ay,az,twist)
            fd=(-1.12-oy)/dy if floor and dy<-.0001 else 1e6
            glow=math.exp(-2.9*(sx*sx+sy*sy))*.0035
            r=bg[0]+glow;g=bg[1]+glow;b=bg[2]+glow
            if hit and dist<fd:
                r,g,b=shade(ox+dx*dist,oy+dy*dist,oz+dz*dist,dx,dy,dz,kind,ax,ay,az,twist,mat,rough,light,tint)
            elif fd<12.:
                x=ox+dx*fd;y=-1.119;z=oz+dz*fd
                shadow=math.exp(-1.7*(x*x+z*z));base=.008*(1-.76*shadow)
                r=bg[0]+base;g=bg[1]+base;b=bg[2]+base
                rd,ok=trace(x,y,z,dx,-dy,dz,kind,ax,ay,az,twist)
                if ok:
                    rr,gg,bb=shade(x+dx*rd,y-dy*rd,z+dz*rd,dx,-dy,dz,kind,ax,ay,az,twist,mat,rough,light,tint)
                    alpha=.26*(1-abs(dy))**2*math.exp(-rd*.15)
                    r+=rr*alpha;g+=gg*alpha;b+=bb*alpha
            # soft filmic shoulder, approximate sRGB transfer
            out[j,i,0]=min(255,255*(r/(r+.42))**(1/2.2));out[j,i,1]=min(255,255*(g/(g+.42))**(1/2.2));out[j,i,2]=min(255,255*(b/(b+.42))**(1/2.2))
    return out
