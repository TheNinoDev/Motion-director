#!/usr/bin/env python3
"""Conservative image finishing for CFR clips, preserving audio and frame count. No cross-cut temporal filters."""
import argparse, json, math, subprocess
from fractions import Fraction
from pathlib import Path
import numpy as np
from render import linear,rgb8,gaussian

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(path)]))['streams']
def settings(p):
    defaults={'exposure':0,'bloom':.04,'threshold':.65,'radius':.012,'vignette':.04,'grain':0,'seed':120}
    if set(p)-set(defaults):raise ValueError('Unknown settings: '+str(set(p)-set(defaults)))
    p={**defaults,**p}
    for k,lo,hi in [('exposure',-.5,.5),('bloom',0,.25),('threshold',.35,.95),('radius',.003,.04),('vignette',0,.20),('grain',0,.018)]:
        if not isinstance(p[k],(int,float)) or not math.isfinite(p[k]) or not lo<=p[k]<=hi:raise ValueError('Invalid '+k)
    if type(p['seed']) is not int or not 0<=p['seed']<2**32:raise ValueError('Invalid seed')
    return p

def grade(im,p,v,frame):
    x=linear(im.astype(np.float32)/255)*2**p['exposure']; x*=v[...,None]
    if p['bloom']:
        lum=x@np.array([.2126,.7152,.0722],dtype=np.float32);weight=np.maximum(lum-p['threshold'],0)/np.maximum(lum,1e-6);x+=gaussian(x*weight[...,None],im.shape[1]*p['radius'])*p['bloom']
    if p['grain']:x+=np.random.default_rng(np.random.SeedSequence([p['seed'],frame])).normal(0,p['grain'],x.shape[:2]).astype(np.float32)[...,None]*np.sqrt(np.clip(x.mean(axis=2),0,1))[...,None]
    return rgb8(x)

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('input',type=Path);a.add_argument('output',type=Path);a.add_argument('--settings',type=Path,required=True);args=a.parse_args();p=settings(json.loads(args.settings.read_text()));src=args.input.resolve();out=args.output.resolve()
    if src==out:raise ValueError('Use a separate output path')
    streams=probe(src);v=next(s for s in streams if s['codec_type']=='video');w,h=v['width'],v['height'];fps=Fraction(v['avg_frame_rate']);count=int(v['nb_read_frames']);
    if not fps or fps>120 or w%2 or h%2 or max(w,h)>4096 or count<1:raise ValueError('Unsupported raster or rate')
    if Fraction(v['r_frame_rate'])!=fps or abs(float(v.get('duration',count/fps))-float(count/fps))>float(1/fps):raise ValueError('Normalize variable frame rate first')
    # Validate per-frame presentation timestamps before assuming a constant-rate timeline.
    ts=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(src)]))['frames'];t=[float(f['best_effort_timestamp_time']) for f in ts];tol=max(.002,float(1/fps)*.05)
    if len(t)!=count or any(abs(x-t[0]-i/float(fps))>tol for i,x in enumerate(t)):raise ValueError('Non-CFR timestamps; normalize first')
    out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_name(out.stem+'.tmp.mp4');Y,X=np.mgrid[:h,:w].astype(np.float32);vig=(1-p['vignette']*np.clip(((X-w/2)/(w/2))**2+((Y-h/2)/(h/2))**2,0,1));rate=str(fps)
    dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(src),'-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','-fps_mode','passthrough','-'],stdout=subprocess.PIPE)
    enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',rate,'-i','-','-i',str(src),'-map','0:v:0','-map','1:a?','-c:v','libx264','-threads','2','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
    i=0
    try:
        while True:
            b=dec.stdout.read(w*h*3)
            if not b:break
            if len(b)!=w*h*3:raise RuntimeError('Truncated decoded frame')
            x=np.frombuffer(b,np.uint8).reshape(h,w,3);enc.stdin.write(grade(x,p,vig,i).tobytes());i+=1
        dec.stdout.close();enc.stdin.close()
        if dec.wait() or enc.wait() or i!=count:raise RuntimeError('Decode/encode failed or wrong count')
        rr=probe(tmp);vv=next(s for s in rr if s['codec_type']=='video')
        if int(vv['nb_read_frames'])!=count or Fraction(vv['avg_frame_rate'])!=fps:raise RuntimeError('Changed timeline')
        if sum(s['codec_type']=='audio' for s in rr)!=sum(s['codec_type']=='audio' for s in streams):raise RuntimeError('Audio track lost')
        tmp.replace(out)
    except BaseException:
        for pr in (dec,enc):
            if pr.poll() is None:pr.kill();pr.wait()
        tmp.unlink(missing_ok=True);raise
    print(f'Finished {i} frames at {fps} fps; audio tracks retained; verify mix and visual quality.')
if __name__=='__main__':main()
