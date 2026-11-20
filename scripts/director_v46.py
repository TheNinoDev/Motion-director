#!/usr/bin/env python3
"""Event-bound reactions and sound cues. Timing is compiled from actual gesture events."""
import argparse,copy,json,math
from pathlib import Path
from director_v45 import build as build45
from director_v43 import compile_programs,RANGES
from motion_workbench import number
from compositor import validate
from agent_session import write

# Explicit records avoid accidentally binding to the wrong event after editing a gesture.
PRESETS={'tap':('click',.10,-18),'grab':('click',.08,-24),'release':('impact',.20,-19)}

def anchor(events,r):
 i=r['event']
 if type(i) is not int or not 0<=i<len(events):raise ValueError('event index invalid; inspect event catalog')
 e=events[i]
 if e['op']!=r['expect_op'] or e['target']!=r['expect_target']:raise ValueError(f'event {i} changed identity; rebind explicitly')
 return e

def build(spec,base):
 s=copy.deepcopy(spec);reactions=s.pop('event_reactions',[]);sounds=s.pop('event_sounds',[]);p,e,notes=build45(s,base);events=e['gesture_events'];fps=p['fps'];n=round(p['duration']*fps)
 if not isinstance(reactions,list) or len(reactions)>128 or not isinstance(sounds,list) or len(sounds)>200:raise ValueError('invalid event arrays')
 programs=[]
 for r in reactions:
  if not isinstance(r,dict) or set(r)!={'event','expect_op','expect_target','layer','delay','duration','op','values','ease'}:raise ValueError('reaction fields: event, expect_op, expect_target, layer, delay, duration, op, values, ease')
  t=anchor(events,r)['time']+number(r['delay'],'delay');d=number(r['duration'],'duration');op=r['op']
  if op not in ('animate','pulse','relative') or d<2/fps or not 0<=t<t+d<=p['duration']+1e-8:raise ValueError('invalid reaction operation/time')
  k={'animate':'to','pulse':'offset','relative':'delta'}[op]
  programs.append({'layer':r['layer'],'start':t,'steps':[{'op':op,'end':t+d,k:r['values'],'ease':r['ease']}]})
 # Existing compiler refuses occupied lanes and duplicate targets; use one layer per reaction.
 compile_programs(p,programs);validate(p,base)
 cues=[];seen=set()
 for r in sounds:
  if not isinstance(r,dict) or set(r)!={'event','expect_op','expect_target','kind','gain_db','duration','pan','offset'}:raise ValueError('sound fields: event, expect_op, expect_target, kind, gain_db, duration, pan, offset')
  a=anchor(events,r);kind=r['kind'];gain=number(r['gain_db'],'gain_db');pan=number(r['pan'],'pan');offset=number(r['offset'],'offset');d=number(r['duration'],'duration');fr=round((a['time']+offset)*fps);dur=round(d*fps)
  if kind not in ('click','impact','whoosh','chime','riser','drop') or not -45<=gain<=-3 or not -1<=pan<=1 or not -1<=offset<=1 or not 1<=dur<=4*fps or not 0<=fr<fr+dur<=n:raise ValueError('sound timing, gain, pan or kind invalid')
  ident=(r['event'],kind,fr)
  if ident in seen:raise ValueError('duplicate sound cue')
  seen.add(ident);cues.append({'event':r['event'],'target':a['target'],'op':a['op'],'frame':fr,'duration_frames':dur,'kind':kind,'gain_db':gain,'pan':pan,'event_time':a['time']})
 e['event_reactions']=reactions;e['event_sounds']=sounds;e['sound_cues']=cues
 return p,e,notes+[f'Compiled {len(programs)} event reactions and {len(cues)} frame-locked sound cues.']

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog')
 for cmd in ('events','compile'):
  x=sub.add_parser(cmd);x.add_argument('spec',type=Path)
  if cmd=='compile':x.add_argument('output',type=Path)
 z=ap.parse_args()
 if z.cmd=='catalog':
  print(json.dumps({'reaction':{'event':0,'expect_op':'tap','expect_target':'card1','layer':'halo','delay':0,'duration':.4,'op':'pulse','values':{'opacity':.7},'ease':'smooth'},'sound':{'event':0,'expect_op':'tap','expect_target':'card1','kind':'click','gain_db':-18,'duration':.10,'pan':0,'offset':0},'preset_suggestions':PRESETS,'rules':'Inspect events first; selectors verify identity. Reactions support one free property program per layer, no overwrite. Seconds in source, frame-quantized sound.'},indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent)
 if z.cmd=='compile':write(z.output,p)
 print(json.dumps({'events':e['gesture_events'],'sound_cues':e['sound_cues'],'notes':n},indent=2))
if __name__=='__main__':main()
