#!/usr/bin/env python3
"""Reusable, parameterized cue sequences on the existing frame-locked V47 compiler."""
import argparse, copy, json, re
from pathlib import Path
from director_v47 import build as build47, records
from director_v43 import RANGES, EASE
from motion_workbench import number
from agent_session import write


def action(slot,start,end,values,op='animate',ease='smooth'):
 return dict(slot=slot,start=start,end=end,values=values,op=op,ease=ease)
def sound(start,end,kind,gain_db=-20,pan=0):
 return dict(start=start,end=end,kind=kind,gain_db=gain_db,pan=pan)
PRESETS={
 'contact_feedback':{'slots':['halo'],'params':{'flash':.8,'grow':.12},'actions':[action('halo',0,1,{'opacity':'$flash','scale':'$grow'},'pulse')],'sounds':[]},
 'status_reveal':{'slots':['indicator','label'],'params':{},'actions':[action('indicator',0,1,{'opacity':1}),action('label',0,1,{'opacity':1})],'sounds':[]},
 'title_handoff':{'slots':['outgoing','incoming'],'params':{'exit_y':146,'enter_y':220},'actions':[action('outgoing',.12,1,{'opacity':0,'y':'$exit_y'}),action('incoming',0,.88,{'opacity':1,'y':'$enter_y'})],'sounds':[]},
 'completion_pair':{'slots':['first','second'],'params':{'grow':.08},'actions':[action('first',0,1,{'scale':'$grow'},'pulse'),action('second',0,1,{'scale':'$grow'},'pulse')],'sounds':[]},
 'arrival_accent':{'slots':['hero'],'params':{'grow':.08,'turn':5},'actions':[action('hero',0,1,{'scale':'$grow','rotate':'$turn'},'pulse','sine')],'sounds':[sound(0,.4,'impact',-24)]},
 'focus_exchange':{'slots':['outgoing','incoming'],'params':{'dim':.25,'defocus':6},'actions':[action('outgoing',0,1,{'opacity':'$dim','blur':'$defocus'}),action('incoming',0,1,{'opacity':1,'blur':0})],'sounds':[]},
 'impact_sound':{'slots':[],'params':{'gain':-19,'pan':0},'actions':[],'sounds':[sound(0,1,'impact','$gain','$pan')]},
 'click_sound':{'slots':[],'params':{'gain':-18,'pan':0},'actions':[],'sounds':[sound(0,1,'click','$gain','$pan')]},
}
ID=re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,47}\Z')
def ident(x):return isinstance(x,str) and bool(ID.fullmatch(x))
def scalar(v,params):
 if isinstance(v,str):
  if not v.startswith('$') or v[1:] not in params:raise ValueError('unknown sequence parameter '+v)
  return params[v[1:]]
 return number(v,'sequence value')
def definition(d):
 if not isinstance(d,dict) or set(d)!={'slots','params','actions','sounds'}:raise ValueError('sequence definition requires slots, params, actions, sounds')
 slots=d['slots'];params=d['params']
 if not isinstance(slots,list) or len(slots)>16 or not all(ident(x) for x in slots) or len(set(slots))!=len(slots):raise ValueError('invalid sequence slots')
 if not isinstance(params,dict) or len(params)>32 or not all(ident(x) for x in params):raise ValueError('invalid sequence parameters')
 params={k:number(v,k) for k,v in params.items()}
 a=records(d['actions'],'sequence actions',32);s=records(d['sounds'],'sequence sounds',16)
 if not a and not s:raise ValueError('empty sequence')
 used=set();usedparams=set()
 def param(v):
  if isinstance(v,str):usedparams.add(v[1:])
  return scalar(v,params)
 for r in a+s:
  if not 0<=number(r.get('start'),'start')<number(r.get('end'),'end')<=1:raise ValueError('sequence phase interval must be within 0..1')
 for r in a:
  if set(r)!={'slot','start','end','values','op','ease'} or r['slot'] not in slots or r['op'] not in ('animate','pulse','relative') or r['ease'] not in EASE or not isinstance(r['values'],dict) or not r['values']:raise ValueError('invalid sequence action')
  used.add(r['slot'])
  for k,v in r['values'].items():
   if k not in RANGES:raise ValueError('unsupported sequence property '+k)
   param(v)
 for r in s:
  if set(r)!={'start','end','kind','gain_db','pan'} or r['kind'] not in ('click','impact','whoosh','chime','riser','drop'):raise ValueError('invalid sequence sound')
  param(r['gain_db']);param(r['pan'])
 if used!=set(slots) or usedparams!=set(params):raise ValueError('unused sequence slots or parameters')
 return params

def expand(spec):
 s=copy.deepcopy(spec);custom=s.pop('sequence_library',{});uses=s.pop('sequences',[])
 if not isinstance(custom,dict) or len(custom)>24 or any(not ident(k) or k in PRESETS for k in custom):raise ValueError('invalid/duplicate custom sequence name')
 lib={**PRESETS,**custom};defaults={k:definition(v) for k,v in lib.items()}
 fps=number(s['fps'],'fps'); duration=number(s['duration'],'duration')
 if fps<=0 or duration<=0:raise ValueError('fps/duration must be positive')
 a=records(s.get('cue_actions',[]),'cue_actions',128);q=records(s.get('cue_sounds',[]),'cue_sounds',200);s['cue_actions']=a;s['cue_sounds']=q
 schedule=[];ids=set()
 for u in records(uses,'sequences',64):
  if set(u)!={'id','recipe','marker','offset','duration','bind','params'} or not ident(u['id']) or u['id'] in ids or not isinstance(u['recipe'],str) or u['recipe'] not in lib or not ident(u['marker']):raise ValueError('invalid sequence instance')
  ids.add(u['id']);d=lib[u['recipe']];bind=u['bind'];params=u['params']
  if not isinstance(bind,dict) or set(bind)!=set(d['slots']) or not all(isinstance(x,str) and x for x in bind.values()) or len(set(bind.values()))!=len(bind):raise ValueError('bind every sequence slot to a distinct layer ID')
  if not isinstance(params,dict) or set(params)-set(defaults[u['recipe']]):raise ValueError('unknown sequence parameter override')
  values={**defaults[u['recipe']],**{k:number(v,k) for k,v in params.items()}}
  f0=round(number(u['offset'],'offset')*fps);length=round(number(u['duration'],'duration')*fps)
  if not 1<=length<=round(duration*fps):raise ValueError('sequence duration outside picture or rounds to zero')
  act0=len(a);snd0=len(q)
  for r in d['actions']+d['sounds']:
   first=round(r['start']*length);last=round(r['end']*length)
   if last-first<(2 if r.get('op')=='pulse' else 1):raise ValueError(f"{u['id']}: normalized phase too short at {fps} fps; increase duration")
   t={'marker':u['marker'],'offset':(f0+first)/fps,'duration':(last-first)/fps}
   if 'slot' in r:a.append({**t,'layer':bind[r['slot']],'op':r['op'],'ease':r['ease'],'values':{k:scalar(v,values) for k,v in r['values'].items()}})
   else:q.append({**t,'kind':r['kind'],'gain_db':scalar(r['gain_db'],values),'pan':scalar(r['pan'],values)})
  schedule.append({'id':u['id'],'recipe':u['recipe'],'marker':u['marker'],'offset_frames':f0,'duration_frames':length,'action_indices':list(range(act0,len(a))),'sound_indices':list(range(snd0,len(q))),'bindings':bind})
 return s,schedule

def build(spec,base):
 s,seq=expand(spec);p,e,notes=build47(s,base)
 n=round(p['duration']*p['fps'])
 for x in seq:
  x['start_frame']=e['named_markers'][x['marker']]+x['offset_frames'];x['end_frame']=x['start_frame']+x['duration_frames']
  if not 0<=x['start_frame']<x['end_frame']<=n:raise ValueError('sequence window exceeds picture: '+x['id'])
 e['sequences']=seq
 return p,e,notes+[f'Expanded {len(seq)} reusable cue sequences.']

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog')
 for name in ('inspect','compile'):
  a=sub.add_parser(name);a.add_argument('spec',type=Path)
  if name=='compile':a.add_argument('output',type=Path)
 z=ap.parse_args()
 if z.cmd=='catalog':print(json.dumps({'recipes':PRESETS,'instance':{'id':'feedback1','recipe':'contact_feedback','marker':'arrival','offset':0,'duration':.5,'bind':{'halo':'halo1'},'params':{'flash':.7}},'custom':'sequence_library maps names to definitions with same schema'},indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent)
 if z.cmd=='compile':write(z.output,p)
 print(json.dumps({'sequences':e['sequences'],'markers':e['named_markers'],'actions':e['cue_actions'],'sounds':e['sound_cues'],'notes':n},indent=2))
if __name__=='__main__':main()
