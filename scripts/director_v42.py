#!/usr/bin/env python3
"""Higher-level choreography on the compiled V41 layer graph. No track overwrites."""
import argparse,copy,json,math
from pathlib import Path
from director_v41 import build as build41
from motion_workbench import number
from compositor import val,validate
from director_v40 import hermite,sample_times,track
from agent_session import write

CATALOG={
 'fan_out':dict(layers=['a','b','c'],start=0,end=2,center=[360,640],spacing=120,rise=70,angle=12,stagger=.1),
 'gather':dict(layers=['a','b','c'],start=2,end=4,center=[360,640],spacing=25,stagger=.08,scale=.65),
 'wave':dict(layers=['a','b','c'],start=0,end=2,amplitude=45,cycles=1,stagger=.1),
 'orbit_exchange':dict(layers=['a','b'],start=0,end=2,center=[360,640],radius=[160,100],degrees=180),
}

def compile_choreography(p,recipes):
 by={l['id']:l for l in p['layers']}; fps=p['fps'];
 if not isinstance(recipes,list):raise ValueError('choreography list required')
 for r in recipes:
  name=r.get('recipe');schema=CATALOG.get(name)
  if schema is None or set(r)!=set(schema)|{'recipe'}:raise ValueError('invalid choreography fields: '+str(name))
  ids=r['layers'];
  if not isinstance(ids,list) or not 2<=len(ids)<=24 or len(set(ids))!=len(ids) or any(i not in by for i in ids):raise ValueError('2–24 distinct existing layers required')
  ls=[by[i] for i in ids];n=len(ls);a=number(r['start'],'start');b=number(r['end'],'end');st=number(r.get('stagger',0),'stagger')
  if not 0<=st or b-a-st*(n-1)<2/fps:raise ValueError('insufficient choreography time')
  if len({l.get('parent') for l in ls})!=1:raise ValueError('shared parent coordinate system required')
  keys={'fan_out':('x','y','rotate'),'gather':('x','y','scale'),'wave':('y',),'orbit_exchange':('x','y')}[name]
  for l in ls:
   if l['kind']=='gradient' or not l['active'][0]<=a<b<=l['active'][1]:raise ValueError('choreography outside active interval or incompatible layer')
   if any(track(l.get(k)) for k in keys):raise ValueError(l['id']+': existing track; use a separate parent group or another property')
  def pair(k):
   v=r[k]
   if not isinstance(v,list) or len(v)!=2:raise ValueError(k+' pair required')
   return [number(x,k) for x in v]
  center=pair('center') if 'center' in r else None
  for i,l in enumerate(ls):
   t0=a+i*st;mid=i-(n-1)/2;initial={k:number(l.get(k,{'x':360,'y':640,'rotate':0,'scale':1}[k]),k) for k in keys};times=sample_times(t0,b,fps)
   if name=='fan_out':
    sp=number(r['spacing'],'spacing');rise=number(r['rise'],'rise');ang=number(r['angle'],'angle');end={'x':center[0]+mid*sp,'y':center[1]+rise*(mid/max(1,(n-1)/2))**2,'rotate':mid*ang}
   elif name=='gather':
    sp=number(r['spacing'],'spacing');sc=number(r['scale'],'scale');
    if sc<=0:raise ValueError('scale must be positive')
    end={'x':center[0]+mid*sp,'y':center[1],'scale':sc}
   elif name=='wave':
    amp=number(r['amplitude'],'amplitude');cy=number(r['cycles'],'cycles');
    if not .5<=cy<=8:raise ValueError('cycles out of range')
   else:
    rx,ry=pair('radius');deg=number(r['degrees'],'degrees');
    if min(rx,ry)<=0 or abs(deg)>720:raise ValueError('invalid orbit')
    px=(initial['x']-center[0])/rx;py=(initial['y']-center[1])/ry
    if abs(math.hypot(px,py)-1)>.015:raise ValueError('orbit layer must start on specified ellipse')
    theta=math.atan2(py,px)
   def value(k,q):
    u=(q-t0)/(b-t0);s=u*u*(3-2*u)
    if name=='wave':return initial[k]+amp*math.sin(math.pi*u)**2*math.sin(2*math.pi*cy*u)
    if name=='orbit_exchange':
     angle=theta+math.radians(deg)*s;return center[0]+rx*math.cos(angle) if k=='x' else center[1]+ry*math.sin(angle)
    return initial[k]+(end[k]-initial[k])*s
   for k in keys:l[k]=[[q,initial[k] if q==t0 else value(k,q),'linear'] for q in times]
 return p

def build(spec,base):
 s=copy.deepcopy(spec);r=s.pop('choreography',[]);p,e,n=build41(s,base);compile_choreography(p,r);validate(p,base);e['choreography']=r;return p,e,n+[f'Compiled {len(r)} ensemble choreography recipes.']
def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);s.add_parser('catalog');b=s.add_parser('compile');b.add_argument('spec',type=Path);b.add_argument('output',type=Path);z=a.parse_args()
 if z.cmd=='catalog':print(json.dumps({k:dict(recipe=k,**v) for k,v in CATALOG.items()},indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent);z.output.parent.mkdir(parents=True,exist_ok=True);write(z.output,p);print(json.dumps({'layers':len(p['layers']),'notes':n},indent=2))
if __name__=='__main__':main()
