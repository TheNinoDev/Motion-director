#!/usr/bin/env python3
"""Validated choreography recipes, explicit continuity checks and agent-ready examples."""
import argparse, copy, json, math, sys
from pathlib import Path
from director_v37 import expand as expand37, diagnosis as diagnose37, MACROS as OLD
from motion_workbench import compile_spec, number, FLAT, SOLIDS
from compositor import val, validate

# Each entry includes a fully usable argument example; no guessing property names.
RECIPES={
 'arc_arrival':dict(layer='card',points=[[540,1080],[680,760],[160,680],[360,640]],fade_fraction=.35),
 'card_fan':dict(layers=['card1','card2','card3'],center=[360,660],spacing=[112,36],angle=14,scale_from=.84,scale_to=1),
 'cascade_exit':dict(layers=['card1','card2','card3'],offset=[0,-130],stagger=.4),
 'matched_exchange':dict(layer='card1',target='card2',anchor=[360,640],source_scale=[1,1.15],target_scale=[.85,1]),
 'lens_pass':dict(layer='lens',points=[[-160,650],[160,520],[560,800],[880,650]],strength=[.05,.3],dispersion=[.005,.025]),
 'compression_release':dict(layer='solid',at=[360,640],offset=[0,180],preset='jelly_soft',strength=.45,angles=[-18,22]),
 'metal_reveal':dict(layer='type',angles_from=[-32,12],angles_to=[12,-6],light_from=.1,light_to=.85,scale_from=.75,scale_to=1),
 'focus_transfer':dict(layer='card1',target='card2',blur_from=0,blur_to=12,focus_from=.75,focus_to=1),
}

def expand(spec,base):
 s=copy.deepcopy(spec); recipes=s.pop('choreography',[]);s=expand37(s);a=s.setdefault('actions',[]);layers={l['id']:l for l in s['layers']};cues=s.get('cues',{})
 def t(v):return number(cues[v] if isinstance(v,str) and v in cues else v,'recipe time')
 def vec(v,n=2):
  if not isinstance(v,list) or len(v)!=n:raise ValueError(f'expected {n} components')
  return [number(x,'vector') for x in v]
 def get(i,kinds=None):
  if i not in layers:raise ValueError('unknown layer '+str(i))
  l=layers[i]
  if kinds is not None and l['kind'] not in kinds:raise ValueError(f'{i}: incompatible kind {l["kind"]}')
  return l
 def ids(v):
  if not isinstance(v,list) or not 2<=len(v)<=16 or len(set(v))!=len(v):raise ValueError('2–16 distinct layers required')
  return v
 for r in recipes:
  name=r.get('recipe')
  if name not in RECIPES:raise ValueError('unknown choreography recipe '+str(name))
  expected=set(RECIPES[name])|{'recipe','start','end'}
  if set(r)-expected-{'ease'} or expected-set(r):raise ValueError(f'{name}: missing {sorted(expected-set(r))}; unknown {sorted(set(r)-expected-{"ease"})}')
  start,end=t(r['start']),t(r['end']);dt=end-start;ease=r.get('ease','quint');i=r.get('layer')
  if not 0<=start<end<=s['duration']:raise ValueError('recipe outside timeline')
  def act(op,i=i,lo=start,hi=end,e=ease,**kw):
   get(i);a.append(dict(op=op,layer=i,start=lo,end=hi,ease=e,**kw))
  def change(op,x,y,**kw):act(op,**{'from':x,'to':y},**kw)
  def curve(p,**kw):act('curve',points=[vec(x) for x in vec4(p)],samples=48,**kw)
  def vec4(v):
   if not isinstance(v,list) or len(v)!=4:raise ValueError('curve needs four 2D controls')
   return v
  if name=='arc_arrival':
   get(i,FLAT);f=number(r['fade_fraction'],'fade_fraction')
   if not .1<=f<=1:raise ValueError('fade_fraction .1–1')
   curve(r['points']);change('fade',0,1,hi=start+dt*f,e='smooth')
  elif name=='card_fan':
   ls=ids(r['layers']);c=vec(r['center']);sp=vec(r['spacing']);ang=number(r['angle'],'angle')
   for j,k in enumerate(ls):
    get(k,FLAT);q=j-(len(ls)-1)/2;change('slide',c,[c[0]+q*sp[0],c[1]+abs(q)*sp[1]],i=k);change('turn',0,q*ang,i=k);change('zoom',r['scale_from'],r['scale_to'],i=k)
  elif name=='cascade_exit':
   ls=ids(r['layers']);off=vec(r['offset']);st=number(r['stagger'],'stagger')
   if not 0<=st<=.75:raise ValueError('stagger 0–.75')
   # Use latest prior authored motion as origin. Compile prefix to resolve endpoints, not guess static positions.
   before=copy.deepcopy(s);before['actions']=[x for x in a if t(x['start'])<start or t(x['end'])<=start];p,_=compile_spec(before,base)
   prev={l['id']:l for l in p['layers']}
   for j,k in enumerate(ls):
    get(k,FLAT);lo=start+dt*st*j/(len(ls)-1);hi=lo+dt*(1-st);l=prev[k];x=val(l.get('x',360),lo);y=val(l.get('y',640),lo);op=val(l.get('opacity',1),lo)
    change('slide',[x,y],[x+off[0],y+off[1]],i=k,lo=lo,hi=hi);change('fade',op,0,i=k,lo=lo,hi=hi,e='smooth')
  elif name=='matched_exchange':
   l=get(i,FLAT|SOLIDS);k=r['target'];m=get(k,FLAT|SOLIDS);anchor=vec(r['anchor']);u=vec(r['source_scale']);v=vec(r['target_scale'])
   if l.get('parent')!=m.get('parent'):raise ValueError('exchange requires same parent')
   # Anchor is explicit and the compiler checks continuity with earlier actions.
   change('slide',anchor,anchor);change('slide',anchor,anchor,i=k);change('zoom',u[0],u[1]);change('zoom',v[0],v[1],i=k);act('handoff',target=k,e='smooth')
  elif name=='lens_pass':
   l=get(i,{'lens'})
   if 'shape' not in l:raise ValueError('lens_pass requires explicit shape')
   curve(r['points']);u=vec(r['strength']);v=vec(r['dispersion']);mid=(start+end)/2
   for op,ab in [('lens_strength',u),('dispersion',v)]:
    change(op,ab[0],ab[1],hi=mid);change(op,ab[1],ab[0],lo=mid)
  elif name=='compression_release':
   get(i,SOLIDS);c=vec(r['at']);o=vec(r['offset']);angles=vec(r['angles']);hit=start+dt*.58
   change('slide',[c[0]+o[0],c[1]+o[1]],c,hi=hit,e='out');change('turn',angles[0],angles[1],hi=hit,e='out');change('turn',angles[1],0,lo=hit);act('elastic',lo=hit,hi=hit,preset=r['preset'],mode='squash',strength=r['strength'])
  elif name=='metal_reveal':
   l=get(i,{'text3d','object3d'})
   if l.get('material') not in ('chrome','gold','satin'):raise ValueError('metal_reveal requires metallic material')
   change('tilt',vec(r['angles_from']),vec(r['angles_to']));change('light_sweep',r['light_from'],r['light_to']);change('zoom',r['scale_from'],r['scale_to']);change('fade',0,1,hi=start+dt*.35,e='smooth')
  elif name=='focus_transfer':
   get(i,FLAT);k=r['target'];get(k,FLAT)
   if k==i:raise ValueError('focus transfer needs distinct layers')
   change('defocus',r['blur_from'],r['blur_to']);change('defocus',r['blur_to'],r['blur_from'],i=k);change('fade',1,r['focus_from']);change('fade',r['focus_from'],r['focus_to'],i=k)
 return s

def build(spec,base):
 plain=expand(spec,base);p,notes=compile_spec(plain,base);return p,plain,notes

def diagnose(p):
 # Dense sampled curves are not one-frame cuts. Keep short-track warnings, but suppress
 # regular sampled linear tracks (actual velocity is inspected separately).
 result=diagnose37(p);by={l['id']:l for l in p['layers']}
 def false_curve(x):
  if x['code']!='subframe_change':return False
  track=by[x['layer']].get(x['fix'].split(':')[0],[])
  return len(track)>=9 and sum(len(k)==3 and k[2]=='linear' for k in track)>=len(track)-2
 result=[x for x in result if not false_curve(x)];fps=p['fps'];n=round(p['duration']*fps);ls={l['id']:l for l in p['layers']}
 def visible(l,t):
  if not l['active'][0]<=t<l['active'][1] or val(l.get('opacity',1),t)<.02:return False
  if l.get('parent'):return visible(ls[l['parent']],t)
  return True
 def report(code,l,t,fix):result.append(dict(code=code,layer=l,time=round(t,4),fix=fix))
 foreground=[l for l in ls.values() if l['kind'] not in ('group','gradient','lens') and not l.get('matte_only') and not (l['kind']=='rect' and l.get('w',0)>=720 and l.get('h',0)>=1280)]
 # Sample complete timeline; blank candidate is not a pixel-based verdict.
 gap=None
 for f in range(n+1):
  empty=f<n and not any(visible(l,f/fps) for l in foreground)
  if empty and gap is None:gap=f
  if not empty and gap is not None:
   if f-gap>=max(2,round(.15*fps)):report('foreground_gap','timeline',gap/fps,f'No nominal foreground for {(f-gap)/fps:.2f}s; inspect intentional pause vs missing reveal.')
   gap=None
 for l in ls.values():
  if l['kind']=='group' or l.get('matte_only'):continue
  start,end=l['active'];
  for edge,t in [('in',start),('out',end-1/fps)]:
   if 0<t<p['duration']-1/fps and visible(l,t) and l['kind'] in ('text3d','glass_object','object3d'):
    report('solid_boundary',l['id'],t,f'Check {edge} boundary: ordered solid is visible; use motivated cut or an overlap/match, not blind fade.')
 return result

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog');c=sub.add_parser('compile');c.add_argument('spec',type=Path);c.add_argument('out',type=Path);d=sub.add_parser('diagnose');d.add_argument('plan',type=Path);x=ap.parse_args()
 if x.cmd=='catalog':print(json.dumps({'recipes':{k:dict(recipe=k,start=0,end=1,**v) for k,v in RECIPES.items()},'v37_macros':list(OLD),'units':'seconds, 720x1280 design coordinates'},indent=2));return
 if x.cmd=='diagnose':p=json.loads(x.plan.read_text());validate(p,x.plan.resolve().parent);print(json.dumps({'issues':diagnose(p),'status':'advisory'},indent=2));return
 out=x.out;expanded=out.with_suffix('.expanded.json');
 if out.exists() or expanded.exists():raise ValueError('refuse overwrite')
 p,s,notes=build(json.loads(x.spec.read_text()),x.spec.resolve().parent);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(p,indent=2)+'\n');expanded.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({'plan':str(out),'actions':len(s['actions']),'issues':diagnose(p),'notes':notes},indent=2))
if __name__=='__main__':main()
