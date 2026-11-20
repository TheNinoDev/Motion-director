#!/usr/bin/env python3
"""Compile explicitly authored UI gestures into existing compositor tracks."""
import argparse,copy,json,math
from pathlib import Path
from director_v44 import build as build44
from director_v40 import track
from motion_workbench import number,allowed
from compositor import validate
from agent_session import write

CATALOG={
 'point':{'op':'point','target':'card','start':0.2,'end':0.7},
 'tap':{'op':'tap','target':'card','start':0.8,'end':1.4,'press':0.92},
 'drag':{'op':'drag','target':'card','start':1.5,'end':2.7,'to':[450,630]},
}

def compile_gestures(plan,programs):
 if not isinstance(programs,list) or len(programs)>16:raise ValueError('gestures: array up to 16 controllers')
 by={l['id']:l for l in plan['layers']};fps=plan['fps'];owners=set();controlled=set();events=[]
 def vec(v):
  if not isinstance(v,list) or len(v)!=2:raise ValueError('expected [x,y]')
  p=tuple(number(x,'coordinate') for x in v)
  if any(abs(x)>4000 for x in p):raise ValueError('coordinate outside supported range')
  return p
 def claim(l,k):
  ident=(l['id'],k)
  if ident in owners or k not in allowed(l) or track(l.get(k)):raise ValueError(f'{ident}: occupied or unsupported lane')
  owners.add(ident)
  return [[l['active'][0],number(l.get(k,1 if k=='scale' else (360 if k=='x' else 640)),k),'linear']]
 def add(lane,t,v,ease='smooth'):
  if t<lane[-1][0]-1e-8:raise ValueError('gesture lane overlap')
  if abs(t-lane[-1][0])<1e-8:
   if abs(v-lane[-1][1])>1e-7:raise ValueError('gesture discontinuity')
   return
  lane.append([t,v,ease])
 def hold(lanes,t):
  for lane in lanes:add(lane,t,lane[-1][1],'linear')
 def move(lanes,t,pt):
  for lane,v in zip(lanes,pt):add(lane,t,v,'quint')
 for prog in programs:
  if not isinstance(prog,dict) or set(prog)!={'pointer','steps'}:raise ValueError('gesture program requires pointer and steps')
  pointer=by.get(prog['pointer']);steps=prog['steps']
  if not pointer or pointer['kind'] not in ('ellipse','path','rect','image') or pointer['id'] in controlled or not isinstance(steps,list) or not 1<=len(steps)<=64:raise ValueError('invalid/duplicate pointer or steps')
  controlled.add(pointer['id']);lanes=[claim(pointer,k) for k in ('x','y','scale')];pbase=lanes[2][0][1]
  if not .05<=pbase<=5:raise ValueError('pointer scale unsupported')
  local={};prev=pointer['active'][0]
  for s in steps:
   if not isinstance(s,dict) or s.get('op') not in CATALOG or set(s)!=set(CATALOG[s['op']]):raise ValueError('malformed gesture; see catalog')
   op=s['op'];target=by.get(s['target']);a=number(s['start'],'start');b=number(s['end'],'end');d=b-a
   if not target or target is pointer or target['id'] in controlled or target['kind'] not in ('rect','ellipse','image','text','object3d','glass_object','mesh','group') or target.get('parent')!=pointer.get('parent'):raise ValueError('target must be drawable sibling, not another gesture pointer')
   if target['kind']=='group' and not any(l.get('parent')==target['id'] and l['kind']!='group' for l in plan['layers']):raise ValueError('group target needs a drawable child')
   ancestor=target.get('parent')
   while ancestor:
    parent=by[ancestor]
    if not parent['active'][0]<=a<b<=parent['active'][1]:raise ValueError('shared parent inactive during gesture')
    ancestor=parent.get('parent')
   # Same parent coordinate system; require pointer last for visibility. May still be covered by other layers.
   if plan['layers'].index(target)>=plan['layers'].index(pointer):raise ValueError('pointer must be later than target in layer order')
   if a<prev-1e-8 or d<(6 if op=='point' else 12)/fps-1e-8 or not pointer['active'][0]<=a<b<=pointer['active'][1] or not target['active'][0]<=a<b<=target['active'][1]:raise ValueError('gesture overlap, short duration or inactive target')
   if target['id'] not in local:
    if any(track(target.get(k)) for k in ('x','y')) or any((target['id'],k) in owners for k in ('x','y','scale')):raise ValueError('target position must be static or authored by this controller')
    local[target['id']]={'xy':vec([target.get('x',360),target.get('y',640)]),'tracks':{}}
   st=local[target['id']];pt=st['xy'];hold(lanes,a);arrive=b if op=='point' else a+d*.45;move(lanes[:2],arrive,pt)
   if op=='tap':
    f=number(s['press'],'press');
    if not .6<=f<=.99:raise ValueError('tap press must be .6–.99')
    if 'scale' not in st['tracks']:st['tracks']['scale']=claim(target,'scale')
    lane=st['tracks']['scale'];base=lane[-1][1];hit=a+d*.62;release=a+d*.84
    hold([lane,lanes[2]],arrive);add(lane,hit,base*f);add(lanes[2],hit,pbase*.76);add(lane,release,base);add(lanes[2],release,pbase);hold(lanes,b);hold([lane],b)
    events.append({'op':op,'target':target['id'],'time':hit})
   elif op=='drag':
    dest=vec(s['to']);release=a+d*.88
    for k in ('x','y'):
     if k not in st['tracks']:st['tracks'][k]=claim(target,k)
    tlanes=[st['tracks'][k] for k in ('x','y')];hold(tlanes,arrive);hold([lanes[2]],arrive);add(lanes[2],a+d*.53,pbase*.8)
    hold(lanes[:2],a+d*.53);hold(tlanes,a+d*.53);move(lanes[:2],release,dest);move(tlanes,release,dest);add(lanes[2],b,pbase);hold(lanes,b);hold(tlanes,b);st['xy']=dest
    events.extend([{'op':'grab','target':target['id'],'time':a+d*.53},{'op':'release','target':target['id'],'time':release}])
   prev=b
  for lid,st in local.items():by[lid].update(st['tracks'])
  pointer.update(dict(zip(('x','y','scale'),lanes)))
 return events

def build(spec,base):
 s=copy.deepcopy(spec);gestures=s.pop('gestures',[]);p,e,n=build44(s,base);events=compile_gestures(p,gestures);validate(p,base);e['gestures']=gestures;e['gesture_events']=events;return p,e,n+[f'Compiled {sum(len(x["steps"]) for x in gestures)} gestures; {len(events)} picture timing markers.']

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog');c=sub.add_parser('compile');c.add_argument('spec',type=Path);c.add_argument('output',type=Path);z=ap.parse_args()
 if z.cmd=='catalog':print(json.dumps({'gestures':CATALOG,'controller':{'pointer':'cursor','steps':list(CATALOG.values())},'rules':'Pointer and targets are sibling layers, center hotspot, pointer drawn later, free lanes only. Times in seconds. No actual product automation.'},indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent);write(z.output,p);print(json.dumps(n))
if __name__=='__main__':main()
