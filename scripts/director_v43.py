#!/usr/bin/env python3
"""Stateful multi-stage property lanes; deterministic, no replacement of earlier tracks."""
import argparse, copy, json, math
from pathlib import Path
from director_v42 import build as build42
from motion_workbench import allowed, number, DEFAULTS
from compositor import val, validate
from director_v40 import track
from agent_session import write

# Deliberately limit to controls that share actual compositor semantics.
RANGES={'x':(-4000,4000),'y':(-4000,4000),'scale':(.01,8),'scale_x':(.01,8),'scale_y':(.01,8),'rotate':(-1440,1440),'opacity':(0,1),'pitch':(-80,80),'yaw':(-80,80),'reveal':(0,1),'mask_progress':(0,1),'light':(0,1),'blur':(0,80),'glow':(0,80),'phase3d':(0,1),'shadow_opacity':(0,1)}
DEFAULT={**DEFAULTS,'blur':0,'glow':0,'shadow_opacity':.3}
EASE={'smooth','sine','quint','linear','in','out'}
CATALOG={
 'animate':{'op':'animate','end':1,'to':{'x':360,'scale':1.15},'ease':'quint'},
 'hold':{'op':'hold','end':1.4},
 'pulse':{'op':'pulse','end':2,'offset':{'scale':.12},'ease':'sine'},
 'relative':{'op':'relative','end':3,'delta':{'x':80},'ease':'smooth'},
}

def compile_programs(p,programs):
 by={l['id']:l for l in p['layers']};used=set()
 if not isinstance(programs,list) or len(programs)>128:raise ValueError('motion_programs: list, maximum 128')
 for program in programs:
  if not isinstance(program,dict) or set(program)!={'layer','start','steps'}:raise ValueError('program requires layer, start, steps')
  lid=program['layer'];l=by.get(lid)
  if l is None or lid in used:raise ValueError('one program per existing layer: '+str(lid))
  used.add(lid);a=number(program['start'],'start');steps=program['steps'];fps=p['fps']
  if not l['active'][0]<=a<l['active'][1] or not isinstance(steps,list) or not 1<=len(steps)<=64:raise ValueError('invalid program interval or step count')
  fields=set()
  for s in steps:
   if not isinstance(s,dict) or s.get('op') not in CATALOG or set(s)!=set(CATALOG[s['op']]):raise ValueError('unknown or malformed step')
   k={'animate':'to','relative':'delta','pulse':'offset'}.get(s['op'])
   if k:
    if not isinstance(s[k],dict) or not s[k] or s['ease'] not in EASE:raise ValueError('require values and supported ease')
    fields.update(s[k])
  if not fields:raise ValueError('program has no motion')
  def check(k,v):
   v=number(v,k);lo,hi=RANGES[k]
   if not lo<=v<=hi:raise ValueError(f'{lid}.{k} outside range [{lo},{hi}]')
   return v
  state={};lanes={}
  for k in sorted(fields):
   if k not in RANGES or k not in allowed(l) or track(l.get(k)):raise ValueError(f'{lid}.{k}: unsupported or already animated; separate group or property')
   if k=='mask_progress' and not l.get('mask'):raise ValueError('mask_progress requires mask')
   if k=='light' and l['kind']=='text' and l.get('material')!='metal':raise ValueError('light requires metallic 2D type')
   if k=='shadow_opacity' and not l.get('shadow'):raise ValueError('shadow_opacity requires shadow')
   state[k]=check(k,l.get(k,DEFAULT[k]));lanes[k]=[[a,state[k],'linear']]
  for s in steps:
   b=number(s['end'],'end');op=s['op'];ease=s.get('ease','linear')
   if not a+1/fps-1e-8<=b<=l['active'][1]+1e-8:raise ValueError('step must last at least one frame and fit active interval')
   for k in lanes:
    v=state[k];target=v
    if op=='animate' and k in s['to']:target=check(k,s['to'][k])
    if op=='relative' and k in s['delta']:target=check(k,v+number(s['delta'][k],k))
    if op=='pulse' and k in s['offset']:
     if b-a<2/fps-1e-8:raise ValueError('pulse requires at least two frames')
     lanes[k].append([(a+b)/2,check(k,v+number(s['offset'][k],k)),ease])
    lanes[k].append([b,target,ease]);state[k]=target
   a=b
  l.update(lanes)
 return p

def build(spec,base):
 s=copy.deepcopy(spec);programs=s.pop('motion_programs',[]);p,e,n=build42(s,base);compile_programs(p,programs);validate(p,base);e['motion_programs']=programs;return p,e,n+[f'Compiled {len(programs)} stateful multi-phase programs.']

def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);s.add_parser('catalog');b=s.add_parser('compile');b.add_argument('spec',type=Path);b.add_argument('output',type=Path);z=a.parse_args()
 if z.cmd=='catalog':print(json.dumps({'steps':CATALOG,'ranges':RANGES,'easing':sorted(EASE)},indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent);z.output.parent.mkdir(parents=True,exist_ok=True);write(z.output,p);print(json.dumps({'layers':len(p['layers']),'notes':n},indent=2))
if __name__=='__main__':main()
