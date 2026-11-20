#!/usr/bin/env python3
"""Reusable, namespaced local-time compositions compiled into the existing renderer."""
import argparse,copy,json,re,math
from pathlib import Path
from director_v40 import build as build40
from motion_workbench import number,KEYS
from compositor import validate

IDENT=re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
def ident(n):
 if not isinstance(n,str) or not IDENT.fullmatch(n):raise ValueError('invalid component identifier: '+str(n))
 return n

def layout_instances(layouts):
 """Expand placement only; no hidden keyframes or effects."""
 if not isinstance(layouts,list):raise ValueError('instance_layouts must be array')
 result=[]
 for l in layouts:
  typ=l.get('layout');allowed={'layout','component','center','start','stagger','scale','items'}|({'columns','spacing'} if typ=='grid' else {'radius','angle','spread'} if typ in ('arc','radial') else set())
  if typ not in ('grid','arc','radial') or set(l)-allowed:raise ValueError('unknown layout or fields')
  cx,cy=[number(v,'center') for v in l['center']];items=l['items'];n=len(items)
  if not 1<=n<=32:raise ValueError('layout needs 1–32 items')
  start=number(l.get('start',0),'start');step=number(l.get('stagger',0),'stagger');scale=number(l.get('scale',1),'scale')
  if step<0:raise ValueError('negative stagger')
  if typ=='grid':
   cols=l['columns'];dx,dy=[number(v,'spacing') for v in l['spacing']]
   if type(cols)!=int or not 1<=cols<=n or dx<0 or dy<0:raise ValueError('invalid grid columns or spacing')
   rows=math.ceil(n/cols)
  else:
   rx,ry=[number(v,'radius') for v in l['radius']];angle=number(l.get('angle',-90),'angle');spread=number(l.get('spread',120 if typ=='arc' else 360),'spread')
   if rx<0 or ry<0 or not 0<=spread<=360:raise ValueError('invalid radius or spread')
  for i,item in enumerate(items):
   if not isinstance(item,dict) or set(item)-{'id','overrides','rotate'}:raise ValueError('unknown layout item field')
   if typ=='grid':
    row,col=divmod(i,cols);nrow=min(cols,n-row*cols);x=cx+(col-(nrow-1)/2)*dx;y=cy+(row-(rows-1)/2)*dy
   else:
    t=math.radians(angle+spread*(i/n if typ=='radial' else i/max(1,n-1)-.5 if n>1 else 0));x=cx+rx*math.cos(t);y=cy+ry*math.sin(t)
   result.append(dict(id=item['id'],component=l['component'],start=start+i*step,x=x,y=y,scale=scale,rotate=item.get('rotate',0),overrides=item.get('overrides',{})))
 return result

def expand(spec):
 s=copy.deepcopy(spec);defs=s.pop('components',{});instances=s.pop('instances',[]);layouts=s.pop('instance_layouts',[]);d=number(s['duration'],'duration')
 if not isinstance(defs,dict) or not isinstance(instances,list):raise ValueError('components object and instances array required')
 instances+=layout_instances(layouts)
 if len(instances)>64:raise ValueError('at most 64 instances')
 layers=s['layers']; existing={l['id'] for l in layers};mapping={}
 for ins in instances:
  if set(ins)-{'id','component','start','x','y','scale','rotate','opacity','overrides'}:raise ValueError('unknown instance field')
  name=ident(ins['id']); kind=ident(ins['component']); c=defs.get(kind)
  if not isinstance(c,dict) or set(c)-{'duration','layers'}:raise ValueError('unknown or invalid component '+kind)
  start=number(ins['start'],'start');duration=number(c['duration'],'component duration')
  if not 0<=start<start+duration<=d+1e-9:raise ValueError('component interval outside timeline')
  local=c['layers']; ids={ident(l['id']) for l in local}
  if not local or len(ids)!=len(local):raise ValueError('empty or duplicate component layers')
  group=name; m={k:name+'__'+k for k in sorted(ids)};newids={group,*m.values()}
  if existing&newids:raise ValueError('component ID collision '+name)
  existing|=newids
  root={'id':group,'kind':'group','active':[start,start+duration]}
  for k,default in [('x',360),('y',640),('scale',1),('rotate',0),('opacity',1)]:root[k]=number(ins.get(k,default),k)
  if root['scale']<=0 or not 0<=root['opacity']<=1:raise ValueError('invalid group scale or opacity')
  layers.append(root); overrides=ins.get('overrides',{})
  if not isinstance(overrides,dict) or set(overrides)-ids:raise ValueError('unknown override layer')
  for raw in local:
   l=copy.deepcopy(raw);i=l['id'];o=overrides.get(i,{})
   if not isinstance(o,dict) or set(o)-{'text','color','src','material','font'}:raise ValueError('overrides limited to media, text, color, material, font')
   l.update(o);l['id']=m[i]
   a,b=l.get('active',[0,duration]);a=number(a,'active start');b=number(b,'active end')
   if not 0<=a<b<=duration:raise ValueError('local active interval outside component')
   l['active']=[start+a,start+b]
   for k in ('parent','matte'):
    if k in l:
     if l[k] not in m:raise ValueError('component reference must be internal: '+k)
     l[k]=m[l[k]]
   l.setdefault('parent',group)
   l.setdefault('x',0);l.setdefault('y',0)
   for k,v in list(l.items()):
    if k in KEYS and isinstance(v,list) and v and isinstance(v[0],list):
     for row in v:
      t=number(row[0],'local key time')
      if not 0<=t<=duration:raise ValueError('component key outside interval')
      row[0]=t+start
    if k=='points_keyframes':
     for row in v:
      t=number(row[0],'local path time');
      if not 0<=t<=duration:raise ValueError('component path key outside interval')
      row[0]=t+start
   if 'softbody' in l or 'softbody' in l.get('mesh',{}):raise ValueError('component softbody not supported: event clocks differ; apply to expanded object instead')
   layers.append(l)
  mapping[name]={'group':group,'layers':m,'interval':[start,start+duration]}
 if len(layers)>512:raise ValueError('expanded layer limit 512')
 return s,mapping

def build(spec,base):
 s,m=expand(spec);p,e,n=build40(s,base);validate(p,base);e['component_map']=m;return p,e,n+[f'Expanded {len(m)} reusable component instances. Local child coordinates and time converted to global clock.']

def main():
 a=argparse.ArgumentParser();sub=a.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog');b=sub.add_parser('compile');b.add_argument('spec',type=Path);b.add_argument('output',type=Path);z=a.parse_args()
 if z.cmd=='catalog':print(json.dumps({'component_example':'examples/director-v41.json','other_recipes':['scripts/director_v40.py catalog','scripts/director_v39.py catalog','scripts/director_v38.py catalog','scripts/director_v37.py catalog','scripts/motion_workbench.py catalog'],'layouts':['grid','arc','radial'],'instance_overrides':['text','color','material','src','font']},indent=2));return
 p,e,n=build(json.loads(z.spec.read_text()),z.spec.resolve().parent);z.output.parent.mkdir(parents=True,exist_ok=True)
 with z.output.open('x') as f:json.dump(p,f,indent=2)
 print(json.dumps({'layers':len(p['layers']),'component_map':e['component_map'],'notes':n},indent=2))
if __name__=='__main__':main()
