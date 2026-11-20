#!/usr/bin/env python3
"""Bake actual music amplitude into selected decorative layers; no fabricated beat detection."""
import argparse,copy,json,subprocess,math
from pathlib import Path
import numpy as np

def envelope(audio,fps,frames):
    sr=12000
    # Decode enough audio only; pad shorter files with silence, never loop secretly.
    p=subprocess.run(['ffmpeg','-v','error','-i',str(audio),'-t',str(frames/fps),'-vn','-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True,check=True)
    a=np.frombuffer(p.stdout,dtype='<f4');a=np.pad(a[:math.ceil(frames*sr/fps)],(0,max(0,math.ceil(frames*sr/fps)-len(a))))
    e=np.array([np.sqrt(np.mean(a[round(i*sr/fps):round((i+1)*sr/fps)]**2)) for i in range(frames)])
    db=20*np.log10(np.maximum(e,1e-6));lo,hi=np.percentile(db,[20,95]);x=np.clip((db-lo)/max(8,hi-lo),0,1);v=0.;out=[]
    for q in x:v+=(q-v)*(.65 if q>v else .22);out.append(float(v))
    return out

def bake(project,env,shot_id,layer_id,prop,base,amount):
    if prop not in ('scale','glow','opacity'):raise ValueError('property must be scale, glow or opacity')
    if not all(math.isfinite(x) for x in (base,amount)) or not 0<=amount<=.25 or not 0<=base<=1.5:raise ValueError('invalid base/amount; use subtle motion')
    d=copy.deepcopy(project);offset=0;found=False
    for s in d['shots']:
        offset-=s.get('transition_in',{}).get('frames',0)
        if s['id']==shot_id:
            if s['engine']!='layers':raise ValueError('only layer engine supported')
            l=next((l for l in s['content']['layers'] if l['id']==layer_id),None)
            if l is None or l['kind'] in ('text','image'):raise ValueError('only non-text, non-product decorative layer allowed')
            if isinstance(l.get(prop),list):raise ValueError('refusing to overwrite existing keyframed motion')
            lo=0.01 if prop=='scale' else 0;hi=1 if prop=='opacity' else 2
            l[prop]=[[i,round(float(np.clip(base+amount*env[offset+i],lo,hi)),5),'linear'] for i in range(s['frames'])];found=True
        offset+=s['frames']
    if not found:raise ValueError('unknown shot')
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('audio',type=Path);p.add_argument('output',type=Path);p.add_argument('--shot',required=True);p.add_argument('--layer',required=True);p.add_argument('--property',choices=['scale','glow','opacity'],default='glow');p.add_argument('--base',type=float,default=.05);p.add_argument('--amount',type=float,default=.15);a=p.parse_args()
    if a.plan.resolve()==a.output.resolve() or a.plan.resolve().parent!=a.output.resolve().parent:p.error('write new project next to original')
    d=json.loads(a.plan.read_text());n=sum(s['frames']-s.get('transition_in',{}).get('frames',0) for s in d['shots']);env=envelope(a.audio,d['fps'],n);out=bake(d,env,a.shot,a.layer,a.property,a.base,a.amount);a.output.write_text(json.dumps(out,indent=2),encoding='utf8')
if __name__=='__main__':main()
