"""Reusable 3D wall-contact demo: deterministic spring-damper reduced-order bodies.
Wall at x=0, x-positive free space. y and z are tangential. SI-like scene units.
No pairwise collision or gravity. Analytic ray/ellipsoid and ray/plane renderer.
"""
import argparse,json,math,subprocess,sys
from pathlib import Path
import numpy as np
from numba import njit,prange,set_num_threads
from PIL import Image,ImageDraw,ImageFont
from presets import resolve,recovery

def simulate(body, duration, hz=960):
    body=resolve(body)
    r=float(body['radius']);m=float(body.get('mass',1));k=float(body.get('stiffness',155));d=float(body.get('damping',5));p=np.array(body['position'],float);v=np.array(body['velocity'],float)
    if not (0<r<=2 and m>0 and k>0 and d>=0 and p[0]>=r and np.isfinite(np.r_[p,v,r,m,k,d]).all() and 0<duration<=30 and hz>=240 and k/m/hz**2<.01):raise ValueError('invalid contact setup or unstable step')
    n=math.ceil(duration*hz)+1;out=np.empty((n,9));events=[];contact=False;dt=1/hz;released=-1.;impact=0.;strength=0.
    for i in range(n):
        pen=max(0,r-p[0]);now=i/hz
        if pen>0 and not contact:events.append(now);impact=abs(v[0]);released=-1.
        if pen<=0 and contact:released=now;strength=min(1.,impact/5.)
        contact=pen>0
        wobble=0. if released<0 else recovery(now-released,body.get('recovery_amplitude',0)*strength,body.get('recovery_frequency',3.2),body.get('recovery_damping',.3))
        # keep the expanding body outside the wall; preserve volume in all phases
        a=max(.30*r,min(p[0],r-pen+r*wobble));b=math.sqrt(r**3/a);out[i]=[*p,a,b,b,*v]
        force=max(0,k*pen-d*v[0]) if contact else 0
        v[0]+=force/m*dt;p+=v*dt
        if p[0]<r*.3:p[0]=r*.3;v[0]=max(0,v[0])
    return out,events

def sample(track,t,hz=960):
    u=min(len(track)-1,max(0,t*hz));i=int(u);j=min(i+1,len(track)-1);return track[i]*(1-u+i)+track[j]*(u-i)

def bake_layer(body,track,duration,fps=60,pixels_per_unit=100,wall_x=160,center_y=640,rate=1):
    """Side-view compositor layer; x normal, z projected vertically. Wall screen x=wall_x."""
    r=body['radius'];ts=np.linspace(0,duration,round(duration*fps)+1);ss=[sample(track,t*rate) for t in ts]
    def keys(fn):return [[float(t),float(fn(q)),'linear'] for t,q in zip(ts,ss)]
    return dict(id=body['id'],kind='object3d',active=[0,duration],geometry='ellipsoid',material=body.get('material','ceramic'),color=body.get('color','#82beff'),w=2*r*pixels_per_unit,h=2*r*pixels_per_unit,depth=2*r*pixels_per_unit,x=keys(lambda q:wall_x+q[0]*pixels_per_unit),y=keys(lambda q:center_y+q[2]*pixels_per_unit),size_x=keys(lambda q:q[3]/r),size_y=keys(lambda q:q[5]/r),scale_z=keys(lambda q:q[4]/r),quality=1)

def unit(v):return v/np.linalg.norm(v)

def camera(w,h):
    eye=np.array([7.6,5.8,11.8]);f=unit(np.array([2.45,1.25,.35])-eye);right=unit(np.cross(f,[0,1,0]));up=np.cross(right,f)
    yy,xx=np.mgrid[:h,:w];u=(xx+.5-w/2)/h*.54;v=(h/2-yy-.5)/h*.54
    rays=f+u[...,None]*right+v[...,None]*up;rays/=np.linalg.norm(rays,axis=2)[...,None]
    return eye.astype(np.float32),rays.astype(np.float32)

@njit(cache=True)
def hit(o,d,c,s):
    a=0.;b=0.;cc=-1.
    for j in range(3):
        q=(o[j]-c[j])/s[j];v=d[j]/s[j];a+=v*v;b+=q*v;cc+=q*q
    q=b*b-a*cc
    if q<0:return 1e9
    t=(-b-math.sqrt(q))/a
    return t if t>0 else 1e9

@njit(cache=True,parallel=True)
def raster(o,rays,balls,colors):
    h,w,_=rays.shape;im=np.empty((h,w,3),np.uint8)
    for j in prange(h):
      for i in range(w):
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
            continue
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
    return im

def font(size,bold=False):
    names=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf'] if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf']
    for n in names:
        if Path(n).exists():return ImageFont.truetype(n,size)
    return ImageFont.load_default()

def encoder(w,h,fps,path):
    # RGB lossless master, no chroma subsampling; lossless compression is not raw uncompressed.
    return subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-c:v','libx264rgb','-crf','0','-preset','ultrafast','-threads','3','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('config',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--still',type=float);ap.add_argument('--backend',choices=('auto','cpu','cuda'),default='auto');ap.add_argument('--device',type=int,default=0);args=ap.parse_args();p=json.loads(args.config.read_text());w,h=p['width'],p['height'];fps=p['fps'];duration=p['duration'];rate=p.get('time_scale',1);bodies=[resolve(b) for b in p['bodies']];set_num_threads(4);tracks=[];events={}
    from PIL import ImageColor
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'composite_film'))
    from render_backend import Backend
    backend=Backend(args.backend,args.device);print(f'Rendering backend: {backend.selected}',flush=True)
    for b in bodies:
        tr,ev=simulate(b,duration*rate);tracks.append(tr);events[b['id']]=ev
    args.out.mkdir(parents=True,exist_ok=True);(args.out/'contacts.json').write_text(json.dumps(events,indent=2));(args.out/'compositor-layers.json').write_text(json.dumps([bake_layer(b,tr,duration,fps,rate=rate) for b,tr in zip(bodies,tracks)],indent=2));aa=p.get('antialias',1);o,rays=camera(round(w*aa),round(h*aa));colors=(np.array([ImageColor.getrgb(b['color']) for b in bodies],np.float32)/255)**2.2
    def frame(t):
        q=np.array([sample(tr,t*rate) for tr in tracks]);im=Image.fromarray(backend.run("contact",raster,o,rays,q,colors));im=im.resize((w,h),Image.Resampling.LANCZOS) if aa!=1 else im;draw=ImageDraw.Draw(im);s=h/720;F=lambda n,b=False:font(max(10,round(n*s)),b);draw.text((round(32*s),round(21*s)),p.get('label','MOTION LAB  /  034'),font=F(15,True),fill='#d9dce4');draw.text((round(32*s),round(46*s)),p.get('title','Elastic contact'),font=F(31,True),fill='white');draw.text((round(32*s),round(89*s)),f'{t*rate:05.2f} s simulated   /   {rate:.2f}× playback',font=F(14),fill='#d7dbe2');
        for j,b in enumerate(bodies):
            v=np.array(b['velocity']);angle=math.degrees(math.atan2(np.linalg.norm(v[1:]),abs(v[0])));x=round((32+j*260)*s);y=h-round(72*s);draw.ellipse((x,y,x+round(12*s),y+round(12*s)),fill=b['color']);draw.text((x+round(20*s),y-round(4*s)),f"{b['id'].upper()}  {np.linalg.norm(v):.1f} u/s  /  {angle:.0f}°",font=F(17,True),fill='white');draw.text((x+round(20*s),y+round(23*s)),f"compression  {100*(1-q[j,3]/b['radius']):.0f}%",font=F(13),fill='#dce1e7')
        return im
    if args.still is not None:frame(args.still).save(args.out/'still.png');backend.save(args.out/'render-backend.json');return
    proc=encoder(w,h,fps,args.out/'master.mp4');count=round(duration*fps)
    try:
        for i in range(count):
            im=frame(i/fps);proc.stdin.write(im.tobytes());
            if i%fps==0:print(f'{i}/{count}',flush=True)
            if i in (0,round(count*.35),round(count*.5),round(count*.7),count-1):im.save(args.out/f'frame-{i:04}.png')
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('encode failed')
    backend.save(args.out/'render-backend.json')
if __name__=='__main__':main()
