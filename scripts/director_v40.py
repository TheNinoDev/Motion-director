#!/usr/bin/env python3
"""Continuous path and dependent-motion compiler, preserving existing authored tracks."""
import argparse,copy,json,math
from pathlib import Path
from director_v39 import build as build39
from motion_workbench import number,DEFAULTS
from compositor import val,validate

CATALOG={
 'continuous_path':{'layer':'hero','knots':[[0,360,640],[1,520,400],[2,360,250]],'tension':.25,'endpoint':'rest'},
 'velocity_follow':{'layer':'marker','source':'hero','offset':[0,90],'start':0,'end':2,'delay':0,'blend':.3},
 'tangent_turn':{'layer':'hero','source':'hero','start':0,'end':2,'offset':90,'max_turn':45,'lookahead':.08,'response':.12},
 'breathing_scale':{'layer':'hero','start':0,'end':2,'amount':.06,'cycles':2},
}
def track(v):return isinstance(v,list) and bool(v) and isinstance(v[0],list)
def sample_times(a,b,fps,extra=()):
 return sorted(set([a,b,*extra,*[i/(fps*4) for i in range(math.ceil(a*fps*4),math.floor(b*fps*4)+1)]]))
def hermite(knots,tension=0.25,endpoint='rest'):
 # Nonuniform-time cubic Hermite; each interior knot has a shared derivative.
 ts=[x[0] for x in knots];xy=[x[1:] for x in knots];vs=[]
 for i in range(len(ts)):
  if i==0 or i==len(ts)-1:
   if endpoint=='rest':vs.append([0,0]);continue
   a,b=(0,1) if i==0 else (i-1,i)
  else:a,b=i-1,i+1
  vs.append([(1-tension)*(xy[b][k]-xy[a][k])/(ts[b]-ts[a]) for k in (0,1)])
 def evaluate(t):
  if t<=ts[0]:return xy[0][:]
  if t>=ts[-1]:return xy[-1][:]
  i=next(j for j in range(len(ts)-1) if t<=ts[j+1]);h=ts[i+1]-ts[i];u=(t-ts[i])/h
  return [(2*u**3-3*u*u+1)*xy[i][k]+(u**3-2*u*u+u)*h*vs[i][k]+(-2*u**3+3*u*u)*xy[i+1][k]+(u**3-u*u)*h*vs[i+1][k] for k in (0,1)]
 return evaluate

def build(spec,base):
 s=copy.deepcopy(spec);recipes=s.pop('continuous_motion',[]);p,expanded,notes=build39(s,base);by={l['id']:l for l in p['layers']};fps=p['fps'];cues=s.get('cues',{})
 def t(v):return number(cues.get(v,v) if isinstance(v,str) else v,'time')
 def bound(v,a,b,name):
  v=number(v,name)
  if not a<=v<=b:raise ValueError(name+' outside range')
  return v
 def get(i):
  if i not in by:raise ValueError('unknown layer '+str(i))
  return by[i]
 def at(l,k,t):return val(l.get(k,DEFAULTS[k]),t)
 def interval(l,a,b):
  if not l['active'][0]<=a<b<=l['active'][1]:raise ValueError(l['id']+': time outside active interval')
 def put(l,keys,rows):
  for k in keys:
   if track(l.get(k)):raise ValueError(l['id']+'.'+k+': existing track; use an unused property')
  for j,k in enumerate(keys):l[k]=[[t,v[j],'linear'] for t,v in rows]
 def pair(l,s):
  if l.get('parent')!=s.get('parent'):raise ValueError('dependent layers need shared parent coordinates')
 if not isinstance(recipes,list):raise ValueError('continuous_motion must be list')
 # Source path first, then dependent tracks. Reject forward dependencies instead of silently sampling static source.
 for i,r in enumerate(recipes):
  name=r.get('recipe');args=CATALOG.get(name)
  if not args or set(r)!=set(args)|{'recipe'}:raise ValueError('unknown recipe or fields: '+str(name))
  l=get(r['layer']);kind=l['kind']
  if kind=='gradient':raise ValueError('animate a group rather than gradient with this tool')
  if name=='continuous_path':
   raw=r['knots']
   if not isinstance(raw,list) or not 2<=len(raw)<=32 or any(not isinstance(x,list) or len(x)!=3 for x in raw):raise ValueError('2–32 [time,x,y] knots required')
   knots=[[t(x[0]),number(x[1],'x'),number(x[2],'y')] for x in raw];a,b=knots[0][0],knots[-1][0];interval(l,a,b)
   if any(y[0]-x[0]<1/fps for x,y in zip(knots,knots[1:])):raise ValueError('knots must be at least one frame apart')
   if any(abs(at(l,k,a)-knots[0][j+1])>1e-5 for j,k in enumerate(('x','y'))):raise ValueError('first knot must equal authored starting position')
   endpoint=r['endpoint'];
   if endpoint not in ('rest','moving'):raise ValueError('endpoint rest or moving')
   fn=hermite(knots,bound(r['tension'],0,1,'tension'),endpoint)
   put(l,('x','y'),[(q,fn(q)) for q in sample_times(a,b,fps,[k[0] for k in knots])]);notes.append('Hermite path '+l['id']+': shared analytic tangents, sampled at 4x FPS; inspect overshoot.')
  else:
   a,b=t(r['start']),t(r['end']);interval(l,a,b);times=sample_times(a,b,fps)
   if name=='velocity_follow':
    src=get(r['source']);pair(l,src)
    if src is l or not any(track(src.get(k)) for k in ('x','y')):raise ValueError('author moving source first')
    delay=bound(r['delay'],0,b-a,'delay');blend=bound(r['blend'],1/fps,b-a,'blend');interval(src,a-delay,b-delay)
    off=r['offset'];
    if not isinstance(off,list) or len(off)!=2:raise ValueError('offset pair required')
    off=[number(v,'offset') for v in off];initial=[at(l,k,a) for k in ('x','y')];rows=[]
    for q in times:
     u=min(1,(q-a)/blend);u=u*u*(3-2*u);rows.append((q,[(1-u)*initial[j]+u*(at(src,k,q-delay)+off[j]) for j,k in enumerate(('x','y'))]))
    put(l,('x','y'),rows)
   elif name=='tangent_turn':
    src=get(r['source']);pair(l,src);interval(src,a,b)
    if not any(track(src.get(k)) for k in ('x','y')):raise ValueError('author moving source first')
    offset=number(r['offset'],'offset');cap=bound(r['max_turn'],0,180,'max_turn');look=bound(r['lookahead'],.01,1,'lookahead');response=bound(r['response'],.01,2,'response');origin=at(l,'rotate',a);angle=origin;last=a;rows=[]
    for q in times:
     lo=max(a,q-look);hi=min(b,q+look);dx=at(src,'x',hi)-at(src,'x',lo);dy=at(src,'y',hi)-at(src,'y',lo)
     target=angle if math.hypot(dx,dy)<.01 else origin+max(-cap,min(cap,(math.degrees(math.atan2(dy,dx))+offset-origin+180)%360-180));angle+=(target-angle)*(1-math.exp(-(q-last)/response));rows.append((q,[angle]));last=q
    put(l,('rotate',),rows)
   elif name=='breathing_scale':
    amount=bound(r['amount'],0,.3,'amount');cycles=bound(r['cycles'],.5,12,'cycles');origin=at(l,'scale',a)
    put(l,('scale',),[(q,[origin*(1+amount*math.sin(math.pi*(q-a)/(b-a))**2*math.sin(2*math.pi*cycles*(q-a)/(b-a)))]) for q in times])
 validate(p,base);expanded['continuous_motion']=recipes;return p,expanded,notes

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog');a=sub.add_parser('compile');a.add_argument('spec',type=Path);a.add_argument('output',type=Path);z=ap.parse_args()
 if z.cmd=='catalog':print(json.dumps({k:dict(recipe=k,**v) for k,v in CATALOG.items()},indent=2));return
 p,_,notes=build(json.loads(z.spec.read_text()),z.spec.resolve().parent);z.output.parent.mkdir(parents=True,exist_ok=True)
 with z.output.open('x') as f:json.dump(p,f,indent=2)
 print(json.dumps({'layers':len(p['layers']),'notes':notes},indent=2))
if __name__=='__main__':main()
