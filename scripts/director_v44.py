#!/usr/bin/env python3
"""Purposeful motion accents with stationary end tangents; safe opt-in property lanes."""
import argparse,copy,json,math
from pathlib import Path
from director_v43 import build as build43,RANGES,DEFAULT
from director_v40 import track,sample_times
from motion_workbench import allowed,number
from compositor import validate
from agent_session import write

PROFILES={'anticipate':([0,.22,1],[0,-.15,1]),'overshoot':([0,.72,1],[0,1.12,1]),'recoil':([0,.24,.53,.75,1],[0,1,-.30,.12,0]),'double_accent':([0,.22,.48,.68,1],[0,1,0,.52,0])}
FIELDS={'x','y','scale','scale_x','scale_y','rotate','pitch','yaw','light','glow','blur','opacity'}
def curve(name,u):
 ts,vs=PROFILES[name];u=max(0,min(1,u));i=next(i for i in range(len(ts)-1) if u<=ts[i+1]);s=(u-ts[i])/(ts[i+1]-ts[i]);s=s*s*(3-2*s);return vs[i]+(vs[i+1]-vs[i])*s

def compile_accents(p,recipes):
 if not isinstance(recipes,list) or len(recipes)>128:raise ValueError('motion_accents: list up to 128')
 by={l['id']:l for l in p['layers']};fps=p['fps']
 for r in recipes:
  if not isinstance(r,dict) or set(r)!={'profile','layer','start','end','delta'} or r['profile'] not in PROFILES:raise ValueError('accent requires profile, layer, start, end, delta')
  l=by.get(r['layer']);a=number(r['start'],'start');b=number(r['end'],'end');d=r['delta']
  if not l or not l['active'][0]<=a<b<=l['active'][1] or b-a<5/fps or not isinstance(d,dict) or not d:raise ValueError('invalid accent layer, duration (5+ frames) or delta')
  for k,raw in d.items():
   if k not in FIELDS or k not in allowed(l) or track(l.get(k)):raise ValueError(f'{l["id"]}.{k}: unsupported or occupied property; use separate group/lane')
   if k=='light' and l['kind']=='text' and l.get('material')!='metal':raise ValueError('light requires metal text')
   origin=number(l.get(k,DEFAULT[k]),k);delta=number(raw,k);lo,hi=RANGES[k];ts,vs=PROFILES[r['profile']]
   if any(not lo<=origin+delta*v<=hi for v in vs):raise ValueError(f'{k}: accent exceeds safe range including overshoot')
   l[k]=[[t,origin+delta*curve(r['profile'],(t-a)/(b-a)),'linear'] for t in sample_times(a,b,fps,[a+(b-a)*u for u in ts])]
 return p

def build(spec,base):
 s=copy.deepcopy(spec);r=s.pop('motion_accents',[]);p,e,n=build43(s,base);compile_accents(p,r);validate(p,base);e['motion_accents']=r;return p,e,n+[f'Compiled {len(r)} motion accents.']

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog');c=sub.add_parser('compile');c.add_argument('spec',type=Path);c.add_argument('output',type=Path);z=ap.parse_args()
 if z.cmd=='catalog':print(json.dumps({'profiles':list(PROFILES),'fields':sorted(FIELDS),'example':{'profile':'anticipate','layer':'hero','start':0,'end':1,'delta':{'x':180}}},indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent);write(z.output,p);print(json.dumps(n))
if __name__=='__main__':main()
