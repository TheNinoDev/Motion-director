#!/usr/bin/env python3
"""Named picture-clock cues, dependent markers, and repeatable non-overlapping reaction lanes."""
import argparse,copy,json,re
from collections import defaultdict
from pathlib import Path
from director_v46 import build as build46,anchor
from director_v43 import compile_programs,RANGES,EASE
from motion_workbench import number
from compositor import validate
from agent_session import write

CATALOG={
 'markers':[{'id':'arrival','gesture':{'event':2,'expect_op':'release','expect_target':'card1'}},{'id':'answer','after':'arrival','offset':.3},{'id':'opening','time':.2}],
 'cue_actions':[{'marker':'arrival','layer':'halo1','offset':0,'duration':.4,'op':'pulse','values':{'opacity':.75},'ease':'smooth'}],
 'cue_sounds':[{'marker':'arrival','offset':0,'duration':.2,'kind':'impact','gain_db':-20,'pan':0}],
 'rules':'Times are seconds, quantized to nearest picture frame. Marker dependencies must be acyclic. Each property lane may have sequential actions; overlapping actions or preexisting animation on that lane fail. Independent lanes may overlap.'}

def records(v,name,limit):
 if not isinstance(v,list) or len(v)>limit or any(not isinstance(x,dict) for x in v):raise ValueError(f'{name}: expected list of at most {limit} records')
 return v

def resolve_markers(raw,events,fps,n):
 by={};done={};visiting=set()
 for x in records(raw,'markers',32):
  name=x.get('id')
  if not isinstance(name,str) or not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]{0,47}',name) or name in by:raise ValueError('marker id invalid or duplicate')
  if set(x) not in ({'id','time'},{'id','gesture'},{'id','after','offset'}):raise ValueError('marker fields invalid; see catalog')
  by[name]=x
 def get(name):
  if not isinstance(name,str) or name not in by:raise ValueError('unknown marker '+str(name))
  if name in done:return done[name]
  if name in visiting:raise ValueError('marker dependency cycle at '+name)
  visiting.add(name);x=by[name]
  if 'time' in x:f=round(number(x['time'],'time')*fps)
  elif 'gesture' in x:
   g=x['gesture']
   if not isinstance(g,dict) or set(g)!={'event','expect_op','expect_target'}:raise ValueError('gesture selector fields invalid')
   f=round(anchor(events,g)['time']*fps)
  else:f=get(x['after'])+round(number(x['offset'],'offset')*fps)
  if not 0<=f<n:raise ValueError('marker outside picture: '+name)
  visiting.remove(name);done[name]=f;return f
 for name in by:get(name)
 return {name:done[name] for name in by}

def compile_cues(p,marks,raw,raw_sounds,existing):
 fps=p['fps'];n=round(p['duration']*fps);by={x['id']:x for x in p['layers']};lanes=defaultdict(list);actions=[];sounds=[]
 def timing(r):
  if not isinstance(r['marker'],str) or r['marker'] not in marks:raise ValueError('unknown cue marker')
  a=marks[r['marker']]+round(number(r['offset'],'offset')*fps);d=round(number(r['duration'],'duration')*fps)
  if not 0<=a<a+d<=n:raise ValueError('cue interval outside picture or rounds to zero')
  return a,a+d
 for r in records(raw,'cue_actions',128):
  if set(r)!={'marker','layer','offset','duration','op','values','ease'}:raise ValueError('cue action fields invalid')
  a,b=timing(r);lid=r['layer'];op=r['op'];values=r['values']
  if not isinstance(lid,str) or lid not in by or op not in ('animate','relative','pulse') or r['ease'] not in EASE or not isinstance(values,dict) or not values:raise ValueError('cue action layer/op/values/ease invalid')
  if op=='pulse' and b-a<2:raise ValueError('pulse requires two frames')
  if not by[lid]['active'][0]<=a/fps+1e-9 or b/fps>by[lid]['active'][1]+1e-9:raise ValueError('cue exceeds layer active interval: '+lid)
  for k,v in values.items():
   if k not in RANGES:raise ValueError('unsupported cue property '+k)
   lanes[lid,k].append((a,b,op,number(v,k),r['ease']))
  actions.append({**r,'start_frame':a,'end_frame':b})
 for (lid,k),items in lanes.items():
  items.sort(key=lambda x:x[0]);prev=items[0][0];steps=[]
  for a,b,op,v,ease in items:
   if a<prev:raise ValueError(f'overlapping cue actions on {lid}.{k}')
   if a>prev:steps.append({'op':'hold','end':a/fps})
   steps.append({'op':op,'end':b/fps,{'animate':'to','relative':'delta','pulse':'offset'}[op]:{k:v},'ease':ease});prev=b
  compile_programs(p,[{'layer':lid,'start':items[0][0]/fps,'steps':steps}])
 seen={(x['frame'],x['kind'],x['target']) for x in existing}
 for r in records(raw_sounds,'cue_sounds',200):
  if set(r)!={'marker','offset','duration','kind','gain_db','pan'}:raise ValueError('cue sound fields invalid')
  a,b=timing(r);gain=number(r['gain_db'],'gain_db');pan=number(r['pan'],'pan');name=r['marker'];kind=r['kind'];ident=(a,kind,name)
  if kind not in ('click','impact','whoosh','chime','riser','drop') or not -45<=gain<=-3 or not -1<=pan<=1 or b-a>4*fps or ident in seen:raise ValueError('cue sound parameters invalid or duplicate')
  seen.add(ident);sounds.append({'event':None,'target':name,'op':'marker','frame':a,'duration_frames':b-a,'kind':kind,'gain_db':gain,'pan':pan,'event_time':marks[name]/fps})
 return actions,sounds

def build(spec,base):
 s=copy.deepcopy(spec);m=s.pop('markers',[]);a=s.pop('cue_actions',[]);q=s.pop('cue_sounds',[]);p,e,notes=build46(s,base);fps=p['fps'];n=round(p['duration']*fps)
 marks=resolve_markers(m,e['gesture_events'],fps,n);actions,sounds=compile_cues(p,marks,a,q,e['sound_cues']);validate(p,base)
 e['named_markers']=marks;e['cue_actions']=actions;e['named_sound_cues']=sounds;e['sound_cues']+=sounds
 return p,e,notes+[f'Compiled {len(marks)} named markers, {len(actions)} cue actions, {len(sounds)} named sound cues.']

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog')
 for name in ('inspect','compile'):
  a=sub.add_parser(name);a.add_argument('spec',type=Path)
  if name=='compile':a.add_argument('output',type=Path)
 z=ap.parse_args()
 if z.cmd=='catalog':print(json.dumps(CATALOG,indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent)
 if z.cmd=='compile':write(z.output,p)
 print(json.dumps({'markers':e['named_markers'],'actions':e['cue_actions'],'sounds':e['sound_cues'],'notes':n},indent=2))
if __name__=='__main__':main()
