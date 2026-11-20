#!/usr/bin/env python3
"""State-aware choreography. Expand into existing, validated primitive tracks."""
import argparse, copy, json, math
from pathlib import Path
from director_v38 import expand, diagnose
from motion_workbench import compile_spec, number, DEFAULTS, ALL_OPS, SOLIDS, FLAT
from compositor import val

RECIPES = {
 'glide_to':dict(layer='card',to=[360,640],scale=1,rotation=0),
 'arrange_row':dict(layers=['card1','card2','card3'],center=[360,640],spacing=[120,0],stagger=.2,angle=0,scale=.8),
 'follow_offset':dict(layer='marker',source='card',offset=[0,-100],delay=.1,blend_in=.2,samples=24),
 'spotlight':dict(layer='card',others=['card2','card3'],scale=1.1,dim=.35,blur=5),
 'depth_turn':dict(layer='solid',angles=[30,-15],light=.8,scale=1.0),
 'elastic_settle':dict(layer='solid',to=[360,640],preset='jelly',strength=.35,impact_fraction=.65),
 'quiet_exit':dict(layer='card',offset=[0,-90],scale=.9),
 'mask_continue':dict(layer='card',mask='iris',to=1),
}

def build(spec,base):
 s=copy.deepcopy(spec); blocks=s.pop('state_motion',[]);s=expand(s,base);a=s.setdefault('actions',[]);cues=s.get('cues',{})
 if not isinstance(blocks,list):raise ValueError('state_motion must be an array')
 follow_checks=[]
 def time(v):return number(cues[v] if isinstance(v,str) and v in cues else v,'time')
 def vec(v):
  if not isinstance(v,list) or len(v)!=2:raise ValueError('expected two components')
  return [number(x,'component') for x in v]
 def bounded(v,lo,hi,name):
  v=number(v,name)
  if not lo<=v<=hi:raise ValueError(f'{name} must be {lo}–{hi}')
  return v
 def ordered(r):return time(r['start'])
 for r in sorted(blocks,key=ordered):
  name=r.get('recipe');params=RECIPES.get(name)
  if params is None:raise ValueError('unknown state recipe '+str(name))
  required=set(params)|{'recipe','start','end'}
  if required-set(r) or set(r)-required-{'ease'}:raise ValueError(f'{name}: missing {sorted(required-set(r))}, unknown {sorted(set(r)-required-{"ease"})}')
  start,end=time(r['start']),time(r['end']);d=end-start;ease=r.get('ease','quint')
  if not 0<=start<end<=s['duration']:raise ValueError('state recipe outside timeline')
  # Compile all previous operations, including source motion that extends beyond this block.
  p,_=compile_spec(s,base);ls={l['id']:l for l in p['layers']}
  def get(i,kinds=None):
   if i not in ls:raise ValueError('unknown layer '+str(i))
   l=ls[i]
   if kinds is not None and l['kind'] not in kinds:raise ValueError(f'{i}: incompatible layer kind')
   return l
  def at(i,k,t):return val(get(i).get(k,DEFAULTS.get(k,{'blur':0}.get(k,0))),t)
  def coords(i,t):return [at(i,'x',t),at(i,'y',t)]
  def op(i,k,dest,lo=start,hi=end,e=ease):
   l=get(i);channels=ALL_OPS[k];src=[at(i,c,lo) for c in channels];src=src[0] if len(src)==1 else src
   a.append(dict(op=k,layer=i,start=lo,end=hi,ease=e,**{'from':src,'to':dest}))
  def same_parent(ids):
   if len({get(i).get('parent') for i in ids})!=1:raise ValueError('layers must share parent coordinates')
  def distinct(ids):
   if not isinstance(ids,list) or not 1<=len(ids)<=16 or len(ids)!=len(set(ids)):raise ValueError('expected 1–16 distinct layer ids')
   return ids
  i=r.get('layer')
  if name=='glide_to':
   get(i,FLAT|SOLIDS|{'group','lens'});op(i,'slide',vec(r['to']));op(i,'zoom',r['scale']);op(i,'turn',r['rotation'])
  elif name=='arrange_row':
   ids=distinct(r['layers']);same_parent(ids);c=vec(r['center']);sp=vec(r['spacing']);st=bounded(r['stagger'],0,.75,'stagger')
   for j,k in enumerate(ids):
    get(k,FLAT|SOLIDS);q=j-(len(ids)-1)/2;lo=start+d*st*j/max(1,len(ids)-1)
    op(k,'slide',[c[0]+q*sp[0],c[1]+q*sp[1]],lo, end);op(k,'zoom',r['scale'],lo,end);op(k,'turn',number(r['angle'],'angle')*q,lo,end)
  elif name=='follow_offset':
   source=r['source'];get(i,FLAT|SOLIDS|{'lens'});src=get(source);same_parent([i,source]);
   if source==i:raise ValueError('cannot follow self')
   off=vec(r['offset']);delay=bounded(r['delay'],0,d,'delay');blend=bounded(r['blend_in'],.05,1,'blend_in');n=r['samples']
   if type(n)!=int or not 8<=n<=120:raise ValueError('samples 8–120')
   if start-delay<src['active'][0]-1e-8 or end-delay>src['active'][1]+1e-8:raise ValueError('source not active over delayed interval')
   initial=coords(i,start);last=initial
   for j in range(1,n+1):
    u=j/n;t=start+d*u;b=min(1,u/blend);b=b*b*(3-2*b);q=coords(source,t-delay);follow_checks.append((source,t-delay,q));dest=[initial[k]*(1-b)+(q[k]+off[k])*b for k in (0,1)]
    a.append(dict(op='slide',layer=i,start=start+d*(j-1)/n,end=t,ease='linear',**{'from':last,'to':dest}));last=dest
  elif name=='spotlight':
   get(i,FLAT);ids=distinct(r['others']);dim=bounded(r['dim'],0,1,'dim');blur=bounded(r['blur'],0,40,'blur')
   if i in ids:raise ValueError('spotlight target cannot be among others')
   op(i,'zoom',r['scale'])
   for k in ids:get(k,FLAT);op(k,'fade',at(k,'opacity',start)*dim);op(k,'defocus',blur)
  elif name=='depth_turn':
   get(i,SOLIDS);op(i,'tilt',vec(r['angles']));op(i,'light_sweep',bounded(r['light'],0,1,'light'));op(i,'zoom',r['scale'])
  elif name=='elastic_settle':
   get(i,SOLIDS);hit=start+d*bounded(r['impact_fraction'],.2,.85,'impact_fraction');op(i,'slide',vec(r['to']),start,hit,'out');a.append(dict(op='elastic',layer=i,start=hit,end=hit,preset=r['preset'],strength=bounded(r['strength'],0,1,'strength'),mode='squash'))
  elif name=='quiet_exit':
   get(i,FLAT|SOLIDS);off=vec(r['offset']);q=coords(i,start);op(i,'slide',[q[0]+off[0],q[1]+off[1]]);op(i,'zoom',r['scale']);op(i,'fade',0,e='smooth')
  elif name=='mask_continue':
   get(i,FLAT|SOLIDS);a.append(dict(op='wipe',layer=i,start=start,end=end,ease=ease,mask=r['mask'],**{'from':at(i,'mask_progress',start),'to':bounded(r['to'],0,1,'mask end')}))
  compile_spec(s,base) # fail on incompatible, overlapping or discontinuous lanes immediately
 p,notes=compile_spec(s,base);final={l['id']:l for l in p['layers']}
 for source,t,q in follow_checks:
  if any(abs(val(final[source].get(k,DEFAULTS[k]),t)-v)>1e-6 for k,v in zip(('x','y'),q)):raise ValueError('follow source changed after sampling: '+source+'; author source path first')
 return p,s,notes

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);sub.add_parser('catalog');c=sub.add_parser('compile');c.add_argument('spec',type=Path);c.add_argument('out',type=Path);x=ap.parse_args()
 if x.mode=='catalog':print(json.dumps({'state_motion':{k:dict(recipe=k,start=1,end=2,**v) for k,v in RECIPES.items()},'units':'seconds; 720x1280 design coordinates; prior compiled state; follow sources must be authored earlier'},indent=2));return
 if x.out.exists() or x.out.with_suffix('.expanded.json').exists():raise ValueError('refuse overwrite')
 p,s,notes=build(json.loads(x.spec.read_text()),x.spec.resolve().parent);x.out.parent.mkdir(parents=True,exist_ok=True);x.out.write_text(json.dumps(p,indent=2)+'\n');x.out.with_suffix('.expanded.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({'actions':len(s['actions']),'diagnostics':diagnose(p),'notes':notes},indent=2))
if __name__=='__main__':main()
