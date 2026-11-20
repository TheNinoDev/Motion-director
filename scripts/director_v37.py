#!/usr/bin/env python3
"""Small-agent choreography compiler: explicit macros -> existing validated actions.
No renderer replacement. All times are absolute seconds; coordinates are 720x1280.
"""
import argparse,copy,json,math,sys
from pathlib import Path
from motion_workbench import compile_spec,allowed,number
from review_targets import targets
from compositor import val,validate

# Required macro options are explicit to prevent guessing geometry or content.
MACROS={
 'masked_arrival':(['at','offset'], 'Flat drawable: slide and mask in together'),
 'focus_pull':(['from','to','scale_from','scale_to'], 'Group or drawable: pan and zoom toward an anchor'),
 'object_turn':(['from','to','angles_from','angles_to'], 'Solid or flat with pitch/yaw: move while rotating in depth'),
 'elastic_land':(['from','to','preset'], 'Solid: approach and trigger a deformation on arrival (not collision physics)'),
 'shape_unfold':(['from','to','angles_from','angles_to'], 'Box or rounded box solid: morph toward ellipsoid, tilt and illumination'),
 'glass_travel':(['from','to','angles_from','angles_to'], 'Solid glass: move and rotate while changing IOR'),
 'orbit_reveal':(['center','radius','degrees'], 'Drawable: orbital motion with fade in'),
 'exit_match':(['from','to','scale_from','scale_to'], 'Drawable: move, expand and fade out'),
 'stagger_reveal':(['layers','offset'], 'Multiple drawables: sequential reveal; each finishes before macro end'),
 'path_draw':(['from','to'], 'Path: trace with progressive reveal only'),
}
OPTIONAL={'masked_arrival':{'mask'},'object_turn':{'light_from','light_to'},'elastic_land':{'strength','mode'},'shape_unfold':{'light_from','light_to'},'glass_travel':{'ior_from','ior_to'},'orbit_reveal':{'samples'},'stagger_reveal':{'stagger'},'path_draw':set()}

def expand(spec):
 s=copy.deepcopy(spec);macros=s.pop('macros',[]);cues=s.get('cues',{});layers={l['id']:l for l in s['layers']};actions=s.setdefault('actions',[])
 def time(v):
  if isinstance(v,str):
   if v not in cues:raise ValueError('unknown cue '+v)
   v=cues[v]
  return number(v,'macro time')
 def vec(v):
  if not isinstance(v,list) or len(v)!=2:raise ValueError('expected 2D vector')
  return [number(x,'vector') for x in v]
 for m in macros:
  name=m['recipe'];req,desc=MACROS[name];required={'recipe','start','end'}|set(req)|({'layer'} if name!='stagger_reveal' else set());extras={'ease'}|OPTIONAL.get(name,set());missing=required-set(m);unknown=set(m)-required-extras
  if missing or unknown:raise ValueError(f'{name}: missing={sorted(missing)} unknown={sorted(unknown)}')
  a,b=time(m['start']),time(m['end']);dt=b-a;ease=m.get('ease','quint');i=m.get('layer')
  if not 0<=a<b<=s['duration']:raise ValueError('macro outside timeline')
  def act(op,**kw):
   j=kw.pop('layer',i);x=kw.pop('start',a);y=kw.pop('end',b);e=kw.pop('ease',ease)
   if j not in layers:raise ValueError('unknown macro layer '+str(j))
   actions.append(dict(op=op,layer=j,start=x,end=y,ease=e,**kw))
  def move(x,y,**kw):act('slide',**{'from':vec(x),'to':vec(y)},**kw)
  def change(op,x,y,**kw):act(op,**{'from':x,'to':y},**kw)
  if name=='masked_arrival':
   if layers[i]['kind'] not in ('rect','ellipse','line','image','text','path','gradient','mesh'):raise ValueError('masked_arrival requires flat drawable')
   x=vec(m['at']);o=vec(m['offset']);move([x[0]+o[0],x[1]+o[1]],x);change('wipe',0,1,mask=m.get('mask','diagonal'))
  elif name in ('focus_pull','exit_match'):
   move(m['from'],m['to']);change('zoom',m['scale_from'],m['scale_to']);
   if name=='exit_match':change('fade',1,0,start=a+dt*.4)
  elif name=='object_turn':
   move(m['from'],m['to']);change('tilt',vec(m['angles_from']),vec(m['angles_to']));
   if 'light_from' in m or 'light_to' in m:change('light_sweep',m.get('light_from',.2),m.get('light_to',.8))
  elif name=='elastic_land':
   stop=a+dt*.65;move(m['from'],m['to'],end=stop);act('elastic',start=stop,end=stop,preset=m['preset'],mode=m.get('mode','squash'),strength=m.get('strength',.5))
  elif name=='shape_unfold':
   if layers[i]['kind'] not in ('object3d','glass_object') or layers[i].get('geometry','rounded_box') not in ('box','rounded_box'):raise ValueError('shape_unfold requires box or rounded_box volume')
   change('morph',m['from'],m['to']);change('tilt',vec(m['angles_from']),vec(m['angles_to']));change('light_sweep',m.get('light_from',.2),m.get('light_to',.8))
  elif name=='glass_travel':
   if layers[i]['kind']!='glass_object':raise ValueError('glass_travel requires glass_object')
   move(m['from'],m['to']);change('tilt',vec(m['angles_from']),vec(m['angles_to']));change('refraction',m.get('ior_from',1.35),m.get('ior_to',1.52))
  elif name=='orbit_reveal':
   act('orbit',center=vec(m['center']),radius=vec(m['radius']),degrees=vec(m['degrees']),samples=m.get('samples',32));change('fade',0,1,end=a+dt*.3)
  elif name=='stagger_reveal':
   ids=m['layers'];o=vec(m['offset']);st=number(m.get('stagger',.45),'stagger fraction')
   if not isinstance(ids,list) or not 1<=len(ids)<=32 or len(set(ids))!=len(ids) or not 0<=st<.85:raise ValueError('stagger layers 1–32 unique, stagger 0–.85')
   for j,k in enumerate(ids):
    l=layers[k];
    if l['kind'] not in ('rect','ellipse','line','image','text','path','gradient','mesh'):raise ValueError('stagger requires flat drawables')
    x=number(l.get('x',360),'static stagger x');y=number(l.get('y',640),'static stagger y');start=a+dt*st*j/max(1,len(ids)-1);end=start+dt*(1-st)
    move([x+o[0],y+o[1]],[x,y],layer=k,start=start,end=end);change('reveal',0,1,layer=k,start=start,end=end)
  elif name=='path_draw':change('trace',m['from'],m['to'])
 return s

def build(spec,base):
 plain=expand(spec);p,notes=compile_spec(plain,base);return p,plain,notes

def diagnosis(p):
 """Deterministic advisory checks only; no score or creative approval."""
 out=[];fps=p['fps'];ls={l['id']:l for l in p['layers']}
 def issue(code,l,t,fix):out.append(dict(code=code,layer=l['id'],time=round(t,4),fix=fix))
 for l in p['layers']:
  a,b=l['active'];kind=l['kind'];mid=(a+b)/2
  if kind=='group':continue
  if l.get('parent'):
   pa,pb=ls[l['parent']]['active'];
   if a<pa or b>pb:issue('parent_interval',l,mid,'Extend group or shorten child to avoid abrupt disappearance.')
  if kind in ('text','text3d') and not l.get('matte_only'):
   if b-a<.45:issue('brief_text',l,mid,'Verify intentional flash; if information, extend hold after reveal.')
   if kind=='text3d' and (l.get('quality',.7)<.8 or l.get('antialias',1)<1.5):issue('hero_sampling',l,mid,'Render native closeup; use quality >= .8 and antialias >= 1.5 for hero.')
   if not l.get('parent') and not l.get('matte'):
    x=val(l.get('x',360),mid);y=val(l.get('y',640),mid)
    if not 58<=x<=662 or not 96<=y<=1100:issue('text_anchor',l,mid,'Check platform-safe crop; intentional edge typography is allowed.')
  for prop in ('x','y','scale','rotate','opacity','yaw','pitch'):
   track=l.get(prop)
   if isinstance(track,list) and track and isinstance(track[0],list):
    for u,v in zip(track,track[1:]):
     if v[0]-u[0]<1/fps-.00001 and u[1]!=v[1]:issue('subframe_change',l,v[0],f'{prop}: confirm intentional cut or lengthen movement.')
  if kind in ('glass_object','object3d','text3d') and any(k in l for k in ('mask','reveal','shadow')):issue('solid_effect_route',l,mid,'Inspect solid mask, reveal and shadow on an actual render; their local projected bounds differ from flat texture bounds.')
 return out

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog');c=sub.add_parser('compile');c.add_argument('spec',type=Path);c.add_argument('out',type=Path);d=sub.add_parser('diagnose');d.add_argument('plan',type=Path);a=ap.parse_args()
 if a.cmd=='catalog':print(json.dumps({k:{'required':v[0],'purpose':v[1],'optional':sorted(OPTIONAL.get(k,[]))} for k,v in MACROS.items()},indent=2));return
 if a.cmd=='diagnose':
  p=json.loads(a.plan.read_text());validate(p,a.plan.resolve().parent);print(json.dumps({'issues':diagnosis(p),'review':targets(p,24),'status':'advisory only; actual visual inspection required'},indent=2));return
 p,s,n=build(json.loads(a.spec.read_text()),a.spec.resolve().parent);out=a.out;expanded=out.with_suffix('.expanded.json')
 if out.exists() or expanded.exists():raise ValueError('refuse overwrite')
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(p,indent=2)+'\n');expanded.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({'plan':str(out),'expanded_spec':str(expanded),'actions':len(s['actions']),'issues':diagnosis(p),'notes':n},indent=2))
if __name__=='__main__':main()
