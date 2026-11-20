#!/usr/bin/env python3
"""CPU-only true 3D renderer: instanced extrusions, depth buffer, analytic metallic highlights."""
import argparse, json, math, pathlib, subprocess
import numpy as np
from numba import njit
from PIL import Image
from mesh import glyph
P=pathlib.Path
LAYOUTS={'grid','helix','torus','tunnel','sphere','scatter','custom'}
def validate(p):
    for k in ('width','height','fps'):
        if type(p.get(k)) is not int or p[k]<1:raise ValueError('Invalid '+k)
    if p['width']%2 or p['height']%2 or max(p['width'],p['height'])>4096 or p['fps']>120:raise ValueError('Invalid raster/FPS')
    at=0
    for s in p['scenes']:
        if s['start']!=at or type(s['end'])!=int or s['end']<=at:raise ValueError('Frame gap/overlap')
        at=s['end'];n=s['count']
        if type(n)!=int or not 1<=n<=10000 or not s['glyphs'] or any(c.isspace() or ord(c)>126 for c in s['glyphs']):raise ValueError('Invalid count/glyphs (ASCII nonspace)')
        for k in ('layout','to_layout'):
            if k in s and s[k] not in LAYOUTS:raise ValueError('Unknown layout')
            if s.get(k)=='custom' and (len(s.get('points',[]))!=n or any(len(v)!=3 or not all(math.isfinite(x) for x in v) for v in s['points'])):raise ValueError('Bad custom points')
        for k in ('from','to'):
            eye=s['eye_'+k];tar=s.get('target_'+k,[0,0,0]);
            if len(eye)!=3 or len(tar)!=3 or not all(math.isfinite(x) for x in eye+tar) or math.hypot(eye[0]-tar[0],eye[2]-tar[2])<.001:raise ValueError('Bad camera')
        if not 10<=s.get('fov',42)<=110 or not 0<=s.get('roughness',.22)<=1 or not 0<s.get('size',.3)<=10:raise ValueError('Bad optics')
    if not at:raise ValueError('No scenes')
    return at

def shape(k,s):
    N=s['count'];i=np.arange(N);u=(i+.5)/N;a=i*2.399963229728653;r=s.get('radius',3);h=s.get('height',8)
    if k=='grid':
        cols=math.ceil(math.sqrt(N));rows=math.ceil(N/cols);return np.column_stack(((i%cols/max(1,cols-1)-.5)*2*r,(.5-(i//cols)/max(1,rows-1))*h,np.zeros(N)))
    if k=='helix':
        a=u*2*np.pi*s.get('turns',4)+(i%3)*2*np.pi/3;return np.column_stack((np.cos(a)*r,(.5-u)*h,np.sin(a)*r))
    if k=='torus':
        b=a*1.618;t=s.get('tube',.65);R=r+t*np.cos(b);return np.column_stack((R*np.cos(a),t*np.sin(b),R*np.sin(a)))
    if k=='tunnel':
        per=s.get('per_ring',48);total=math.ceil(N/per);a=i%per/per*2*np.pi;return np.column_stack((r*np.cos(a),r*np.sin(a),(i//per-(total-1)/2)*h/max(1,total-1)))
    if k=='sphere':
        y=1-2*u;rr=np.sqrt(1-y*y);return r*np.column_stack((rr*np.cos(a),y,rr*np.sin(a)))
    if k=='scatter':return np.random.default_rng(s.get('seed',123)).uniform(-.5,.5,(N,3))*[r*3,h*1.6,r*3]
    if k=='custom':return np.asarray(s['points'],float)
    raise ValueError(k)
def rot(x,y,z):
    a,b,c=np.cos([x,y,z]);d,e,f=np.sin([x,y,z]);return np.array([[c,-f,0],[f,c,0],[0,0,1.]])@np.array([[b,0,e],[0,1,0],[-e,0,b]])@np.array([[1,0,0],[0,a,-d],[0,d,a]])
def unit(v):return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-12)
@njit
def raster(im,depth,tri,col):
    H,W=depth.shape
    for k in range(len(tri)):
        a,b,c=tri[k];x0,y0,z0=a;x1,y1,z1=b;x2,y2,z2=c
        if min(z0,z1,z2)<=.15:continue
        xmin=max(0,int(math.floor(min(x0,x1,x2))));xmax=min(W-1,int(math.ceil(max(x0,x1,x2))));ymin=max(0,int(math.floor(min(y0,y1,y2))));ymax=min(H-1,int(math.ceil(max(y0,y1,y2))))
        if xmin>xmax or ymin>ymax:continue
        den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(den)<1e-8:continue
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):
                u=((y1-y2)*(x+.5-x2)+(x2-x1)*(y+.5-y2))/den;v=((y2-y0)*(x+.5-x2)+(x0-x2)*(y+.5-y2))/den;w=1-u-v
                if min(u,v,w)<-1e-6:continue
                iz=u/z0+v/z1+w/z2
                if iz>depth[y,x]:
                    depth[y,x]=iz;im[y,x,0]=col[k,0];im[y,x,1]=col[k,1];im[y,x,2]=col[k,2]
    return im

def frame(s,t,meshes,w,h):
    ee=t*t*(3-2*t);mix=lambda a,b:np.array(a)*(1-ee)+np.array(b)*ee
    eye=mix(s['eye_from'],s['eye_to']);target=mix(s.get('target_from',[0,0,0]),s.get('target_to',[0,0,0]));forward=unit(target-eye);right=unit(np.cross(forward,[0,1,0]));up=np.cross(right,forward);cam=np.stack([right,up,forward],axis=1);f=h/(2*np.tan(np.deg2rad(s.get('fov',42))/2))
    pos=shape(s['layout'],s)
    if 'to_layout'in s:pos=mix(pos,shape(s['to_layout'],s))
    spin=s.get('spin',0)*t
    if s.get('orbit'):pos=pos@rot(0,spin,0).T
    rng=np.random.default_rng(s.get('seed',123));angles=rng.uniform(-.5,.5,(len(pos),3))*s.get('random_rotation',0);angles[:,1]+=spin;size=s.get('size',.3)*(1+rng.uniform(-.5,.5,len(pos))*s.get('size_variation',0));phase=s.get('light_phase',0)+t*s.get('light_sweep',2);q=95*(1-s.get('roughness',.22))+7*s.get('roughness',.22);l1=unit(np.array([np.cos(phase),.75,np.sin(phase)]));l2=unit(np.array([-.8,.05,.7]));tint=np.array(s.get('tint',[.42,.45,.58]));im=np.zeros((h,w,3),np.uint8);im[:]=[4,4,8];depth=np.zeros((h,w),np.float32)
    for i,p in enumerate(pos):
        ch=s['glyphs'][i%len(s['glyphs'])];v,n=meshes[ch];R=rot(*angles[i]);world=v@R.T*size[i]+p;nn=n@R.T;center=world.mean(axis=1);vv=unit(eye-center);refl=2*(nn*vv).sum(axis=1)[:,None]*nn-vv;spec=np.maximum(refl@l1,0)**q;spec2=np.maximum(refl@l2,0)**(q*.6);strip=np.maximum(1-np.abs(refl[:,1]-.25),0)**18*np.clip((refl[:,0]+.7)/1.1,0,1);rim=(1-np.maximum((nn*vv).sum(axis=1),0))**3
        rgb=tint*(.23+.16*np.maximum(nn[:,1],0))[:,None]+spec[:,None]*[1.9,1.8,1.9]+spec2[:,None]*[.35,.4,.85]+strip[:,None]*[.44,.46,.56]+rim[:,None]*.13;rgb*=np.exp(-np.linalg.norm(center-eye,axis=1)*.012)[:,None];rgb=(np.clip(rgb,0,1)**.82*255).astype(np.uint8)
        xyz=(world-eye)@cam;z=xyz[:,:,2];safe=np.maximum(z,.15);screen=np.stack([w/2+f*xyz[:,:,0]/safe,h/2-f*xyz[:,:,1]/safe,z],axis=-1);raster(im,depth,screen,rgb)
    return im

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('plan',type=P);a.add_argument('output',type=P);a.add_argument('--font',type=P,required=True);a.add_argument('--preview-dir',type=P);a.add_argument('--supersample',type=int,choices=[1,2],default=1);args=a.parse_args();p=json.loads(args.plan.read_text());total=validate(p);args.output.parent.mkdir(parents=True,exist_ok=True);w,h=p['width'],p['height'];meshes={}
    for c in sorted(set(''.join(s['glyphs'] for s in p['scenes']))):
        g=glyph(c,args.font,p.get('depth',.22),p.get('bevel',.02));v=np.array(g['vertices']).reshape(-1,3,6);meshes[c]=(v[:,:,:3],v[:,0,3:]);print(c,g['triangles'],g['beveled_components'],flush=True)
    tmp=args.output.with_name(args.output.stem+'.tmp.mp4');pr=args.preview_dir
    if pr:pr.mkdir(parents=True,exist_ok=True)
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w}x{h}','-framerate',str(p['fps']),'-i','-','-an','-c:v','libx264','-threads','2','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
    try:
        for s in p['scenes']:
            length=s['end']-s['start']
            for i in range(length):
                im=Image.fromarray(frame(s,i/max(1,length-1),meshes,w*args.supersample,h*args.supersample));im=im.resize((w,h),Image.Resampling.LANCZOS) if args.supersample>1 else im;proc.stdin.write(im.tobytes())
                if pr and i==length//2:im.save(pr/f'frame-{s["start"]+i:05}.png')
            print('Rendered through frame',s['end'],flush=True)
        proc.stdin.close()
        if proc.wait():raise RuntimeError('FFmpeg failed')
    except BaseException:
        proc.kill();proc.wait();tmp.unlink(missing_ok=True);raise
    count=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames','-of','default=nw=1:nk=1',str(tmp)]))
    if count!=total:tmp.unlink(missing_ok=True);raise RuntimeError(f'Frame count {count} != {total}')
    tmp.replace(args.output);print(f'{total} frames / {total/p["fps"]:.3f}s')
if __name__=='__main__':main()
