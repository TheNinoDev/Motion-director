#!/usr/bin/env python3
"""Render counterfactual images: final minus one layer, with all other passes intact.
This measures visible contribution, not actual alpha coverage or aesthetic quality."""
import argparse,json,math,copy
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from agent_session import sha,write
from production_v39 import snapshot
from compositor import Engine,validate
from scene_audit_v41 import world

def measure(full,without,threshold=10):
 d=np.max(np.abs(full.astype(np.int16)-without.astype(np.int16)),axis=2);m=d>=threshold;ys,xs=np.where(m);h,w=m.shape
 box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
 safe=np.zeros_like(m);safe[round(h*.10):round(h*.84),round(w*.07):round(w*.88)]=True
 return {'changed_pixels':int(m.sum()),'fraction':float(m.mean()),'bbox':box,'outside_default_safe_fraction':float((m&~safe).sum()/max(1,m.sum()))},m

def review(plan,out,requests,size=360):
 p=json.loads(plan.read_text());base=plan.resolve().parent;validate(p,base);before=snapshot(plan,p)
 if size not in (360,540,720,1080):raise ValueError('unsupported review width')
 if not isinstance(requests,list) or not 1<=len(requests)<=32:raise ValueError('1–32 frame/layer requests')
 by={l['id']:l for l in p['layers']};seen=set();nn=round(p['duration']*p['fps'])
 for r in requests:
  if set(r)!={'frame','layer'} or type(r['frame'])!=int or not 0<=r['frame']<nn or r['layer'] not in by:raise ValueError('invalid request')
  if by[r['layer']]['kind']=='group' or by[r['layer']].get('matte_only'):raise ValueError('select visible drawable, not group/matte-only')
  key=(r['frame'],r['layer']);
  if key in seen:raise ValueError('duplicate request')
  seen.add(key)
 p['width']=size;p['height']=round(size*16/9/2)*2;engine=Engine(p,base);out.mkdir(parents=True,exist_ok=False);all_layers=engine.layers;full_cache={};results=[]
 for i,r in enumerate(requests):
  f=r['frame'];t=f/p['fps'];l=by[r['layer']];engine.layers=all_layers
  if f not in full_cache:full_cache[f]=engine.frame(t)
  full=full_cache[f];engine.layers=[x for x in all_layers if x['id']!=l['id']];without=engine.frame(t);metrics,m=measure(full,without)
  # Preserve byid and all textures: a visible matte's use by another layer remains intact.
  nominal=world(l,by,t)[1];flag=[]
  if nominal>.1 and metrics['changed_pixels']==0:flag.append('no_measurable_contribution: inspect occlusion, contrast or reveal')
  if l['kind'] in ('text','text3d') and metrics['outside_default_safe_fraction']>.05:flag.append('text pixel contribution outside default safe area: inspect intended crop')
  overlay=full.copy();overlay[m]=np.uint8(overlay[m]*.35+np.array([255,90,60])*.65)
  img=Image.fromarray(np.concatenate([full,without,overlay],axis=1));file=f'{i:02d}-frame-{f:04d}.png';img.save(out/file)
  results.append({**r,'time':t,**metrics,'nominal_opacity':nominal,'flags':flag,'file':file,'sha256':sha(out/file)})
 engine.layers=all_layers
 if snapshot(plan,json.loads(plan.read_text()))!=before:raise ValueError('input changed during review')
 report={'inputs':before,'width':size,'threshold_rgb':10,'backend':'cpu','results':results,'limitations':'Single-time actual RGB contribution, with the selected drawable omitted but matte dependencies intact. Refractive passes may cause non-local differences. Low contrast, intentional masks and occlusion can all cause small differences; not proof of readability, geometry coverage or aesthetic quality. Default safe margins are conservative and platform-dependent.'};write(out/'report.json',report);return report

def verify(plan,out):
 r=json.loads((out/'report.json').read_text());p=json.loads(plan.read_text());errors=[]
 if snapshot(plan,p)!=r['inputs']:errors.append('input changed')
 for x in r['results']:
  f=out/x['file']
  if not f.is_file() or sha(f)!=x['sha256']:errors.append('missing or changed '+x['file'])
 return {'valid':not errors,'errors':errors}

def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);b=s.add_parser('render');b.add_argument('plan',type=Path);b.add_argument('requests',type=Path);b.add_argument('out',type=Path);b.add_argument('--size',type=int,default=360);b=s.add_parser('verify');b.add_argument('plan',type=Path);b.add_argument('out',type=Path);z=a.parse_args();r=review(z.plan,z.out,json.loads(z.requests.read_text()),z.size) if z.cmd=='render' else verify(z.plan,z.out);print(json.dumps(r,indent=2));raise SystemExit(2 if z.cmd=='verify' and not r['valid'] else 0)
if __name__=='__main__':main()
