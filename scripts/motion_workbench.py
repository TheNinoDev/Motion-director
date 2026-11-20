#!/usr/bin/env python3
"""Compile small, composable motion actions into the existing global timeline.
No network, no new renderer, no implicit overwrites of authored tracks.
"""
import argparse, copy, json, math, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import validate, KEYS, val
from review_targets import targets
from PIL import ImageColor
SOLIDS={'object3d','glass_object','text3d'}
FLAT={'rect','ellipse','line','image','text','path','gradient','mesh'}
COMMON={'id','kind','active','parent','x','y','scale','scale_x','scale_y','rotate','opacity'}
FX={'pitch','yaw','blur','glow','glow_color','reveal','mask','mask_progress','mask_feather','matte','matte_only','matte_mode','blend','shadow','shadow_x','shadow_y','shadow_blur','shadow_opacity','shadow_color','projected_blur','velocity_blur'}
FIELDS={
 'group':set(), 'text':{'text','size','font','maxw','color','material','light','bevel','outline'},
 'text3d':{'text','size','font','maxw','color','material','light','quality','antialias','atlas_resolution','depth','bevel3d','size_x','size_y','scale_z','bend3d','twist3d','roughness','softbody','pitch','yaw','mask','mask_progress','mask_feather','reveal','shadow','shadow_x','shadow_y','shadow_blur','shadow_opacity','shadow_color'},
 'image':{'src','w','h','crop'},'rect':{'w','h','radius','stroke','color'},'ellipse':{'w','h','stroke','color'},'line':{'w','h','radius','stroke','color'},'path':{'w','h','points','points_keyframes','stroke','color','trim'},'gradient':{'w','h','stops','angle'},'mesh':{'w','h','mesh'},
 'lens':{'w','h','shape','strength','dispersion','radius','color','shine','light','frost','tint_mix','edge_feather'},
}
FIELDS['object3d']=FIELDS['glass_object']={'w','h','geometry','material','color','depth','bevel3d','size_x','size_y','scale_z','phase3d','twist3d','bend3d','ior','roughness','transmission','absorption','dispersion','background_gap','reflection','quality','antialias','light','pitch','yaw','softbody','mask','mask_progress','mask_feather','reveal','shadow','shadow_x','shadow_y','shadow_blur','shadow_opacity','shadow_color'}
DEFAULTS={'x':360,'y':640,'scale':1,'scale_x':1,'scale_y':1,'rotate':0,'opacity':1,'reveal':1,'yaw':0,'pitch':0,'light':.5,'mask_progress':1,'trim':1,'phase3d':0}
OPS={
 'fade':('opacity',),'slide':('x','y'),'zoom':('scale',),'turn':('rotate',),'tilt':('yaw','pitch'),'reveal':('reveal',),'wipe':('mask_progress',),'trace':('trim',),'morph':('phase3d',),'light_sweep':('light',),'pulse':('scale',),'orbit':('x','y'),'elastic':(),'handoff':('opacity',),'curve':('x','y'),'stretch':('scale_x','scale_y'),'bend':('bend3d',),'twist':('twist3d',),'refraction':('ior',),'roughness':('roughness',)
}
EXTRA_OPS={
 'lens_strength':('strength',),'dispersion':('dispersion',),'defocus':('blur',),'shadow_strength':('shadow_opacity',),'glow_strength':('glow',),'transmission':('transmission',),'extrusion':('depth',),'bevel_depth':('bevel3d',)
}
ALL_OPS={**OPS,**EXTRA_OPS}
EASE={'linear','smooth','in','out','sine','quint','hold','back','spring'}
ACTION_FIELDS={'op','layer','start','end','ease','from','to','amount','center','radius','degrees','preset','mode','strength','target','mask','samples'}

def fail(msg):raise ValueError(msg)
def number(x,name):
 if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):fail(name+' must be finite number')
 return float(x)
def allowed(l):return COMMON|FIELDS.get(l['kind'],set())|(FX if l['kind'] in FLAT else set())
def audit(p):
 issues=[]
 for l in p['layers']:
  i=l['id'];k=l['kind'];bad=set(l)-allowed(l)
  for key in sorted(bad):issues.append({'layer':i,'field':key,'message':'not supported for '+k})
  if k in ('text','text3d') and (not isinstance(l.get('text'),str) or not l['text'].strip()):issues.append({'layer':i,'field':'text','message':'nonempty text required'})
  if k in ('rect','ellipse','line','gradient','mesh','lens','object3d','glass_object'):
   for key in ('w','h'):
    v=l.get(key);
    if not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0:issues.append({'layer':i,'field':key,'message':'positive finite static dimension required'})
  if k=='text' and l.get('material') not in (None,'metal'):issues.append({'layer':i,'field':'material','message':'2D text supports metal only; ordinary text omit material'})
  if k not in ('lens',) and 'radius' in l and isinstance(l['radius'],list):issues.append({'layer':i,'field':'radius','message':'static corner radius for flat geometry'})
  if l.get('matte_only') and l.get('matte'):issues.append({'layer':i,'field':'matte','message':'nested matte unsupported'})
  if k=='lens' and not l.get('shape') and any(x in l for x in ('rotate','frost','tint_mix','edge_feather')):issues.append({'layer':i,'field':'shape','message':'set shape for flexible lens controls'})
  if k=='text' and any(x in l for x in ('light','bevel')) and l.get('material')!='metal':issues.append({'layer':i,'field':'material','message':'2D light/bevel require metal'})
 return issues

def compile_spec(spec,base):
 if spec.get('version')!=1:fail('workbench version must be 1')
 unknown=set(spec)-{'version','duration','fps','width','background','grain','fonts','assets','layers','cues','actions','sound_events','shutter_windows','shutter'}
 if unknown:fail('unknown root fields: '+', '.join(sorted(unknown)))
 d=number(spec['duration'],'duration');w=spec.get('width',720)
 if type(w)!=int or not 90<=w<=2160 or w%2:fail('width must be even 90–2160')
 p={'version':1,'width':w,'height':round(w*16/9/2)*2,'duration':d,'fps':spec.get('fps',30),'background':spec.get('background','#101116'),'layers':copy.deepcopy(spec['layers'])}
 for k in ('grain','fonts','sound_events','shutter_windows','shutter'):
  if k in spec:p[k]=copy.deepcopy(spec[k])
 assets=spec.get('assets',{}); cues=spec.get('cues',{})
 def time(t):
  if isinstance(t,str):
   if t not in cues:fail('unknown cue: '+t)
   t=cues[t]
  t=number(t,'time')
  if not 0<=t<=d:fail('time outside timeline')
  return t
 ls={}
 for l in p['layers']:
  i=l['id'];k=l['kind']
  if i in ls:fail('duplicate layer '+i)
  ls[i]=l;l['active']=[time(t) for t in l.get('active',[0,d])]
  if isinstance(l.get('src'),str) and l['src'].startswith('@'):
   name=l['src'][1:]
   if name not in assets:fail('unknown asset '+name)
   l['src']=assets[name]
  if 'src' in l:l['src']=str((base/l['src']).resolve())
  if l['kind']=='mesh' and 'src' in l.get('mesh',{}):l['mesh']['src']=str((base/l['mesh']['src']).resolve())
  if 'color' in l:ImageColor.getrgb(l['color'])
 for name,loc in p.get('fonts',{}).items():p['fonts'][name]=str((base/loc).resolve())
 issues=audit(p)
 if issues:fail(f"{issues[0]['layer']}.{issues[0]['field']}: {issues[0]['message']}")
 lanes={};notes=[]
 def push(l,key,points,ease):
  pair=(l['id'],key); arr=lanes.setdefault(pair,[])
  if key not in allowed(l):fail(l['id']+'.'+key+' unsupported')
  if isinstance(l.get(key),list) and l[key] and isinstance(l[key][0],list):fail('authored track collision: '+'.'.join(pair))
  points=[(number(t,'time'),number(v,key)) for t,v in points]
  if points[0][0]<l['active'][0] or points[-1][0]>l['active'][1]:fail('action outside layer active interval: '+l['id'])
  if arr and points[0][0]<arr[-1][0]-1e-8:fail('overlapping action on '+'.'.join(pair))
  if arr and abs(points[0][1]-arr[-1][1])>1e-6:fail('discontinuous action on '+'.'.join(pair)+'; match prior endpoint')
  if not arr and points[0][0]>l['active'][0]:arr.append([l['active'][0],points[0][1]])
  for t,v in points:
   if key in ('opacity','reveal','mask_progress','trim','phase3d','shadow_opacity','transmission') and not 0<=v<=1:fail(key+' must be 0–1')
   if key in ('blur','glow','strength','dispersion','depth','bevel3d') and v<0:fail(key+' must be nonnegative')
   if key in ('scale','scale_x','scale_y') and not .01<=v<=20:fail(key+' must be .01–20')
   if arr and abs(t-arr[-1][0])<1e-8:
    if abs(v-arr[-1][1])>1e-6:fail('conflicting keyframe '+'.'.join(pair))
    continue
   arr.append([t,v,ease])
  # A gap between adjacent actions holds the same prior endpoint.
 def vector(v,n):
  if not isinstance(v,list) or len(v)!=n:fail('expected '+str(n)+' component vector')
  return [number(x,'vector') for x in v]
 for a in sorted(spec.get('actions',[]),key=lambda a:time(a['start'])):
  op=a['op'];i=a['layer'];l=ls.get(i);s=time(a['start']);e=time(a.get('end',a['start']));ease=a.get('ease','smooth')
  fields={'op','layer','start','end','ease'} | ({'preset','mode','strength'} if op=='elastic' else {'target'} if op=='handoff' else {'center','radius','degrees','samples'} if op=='orbit' else {'points','samples'} if op=='curve' else {'from','amount'} if op=='pulse' else {'from','to','mask'} if op=='wipe' else {'from','to'})
  if set(a)-fields:fail('unknown action fields '+str(sorted(set(a)-fields)))
  if op not in ALL_OPS or l is None or ease not in EASE:fail('unknown action/layer/easing')
  if op!='elastic' and not s<e:fail('action end must exceed start')
  if op=='elastic':
   if l['kind'] not in SOLIDS or not l['active'][0]<=s<l['active'][1]:fail('elastic requires active solid')
   sb=l.setdefault('softbody',{'preset':a.get('preset','jelly'),'events':[]})
   if 'preset' in a and a['preset']!=sb.get('preset','jelly'):fail('one elastic preset per layer')
   sb['events'].append({'time':s,'mode':a.get('mode','squash'),'strength':a.get('strength',.6)});continue
  if op=='handoff':
   t=ls.get(a.get('target'))
   if not t or t is l or l.get('parent')!=t.get('parent'):fail('handoff requires distinct layers in same parent coordinates')
   # No fake geometric matching: require explicit same anchor at midpoint.
   if p['layers'].index(t)<p['layers'].index(l):fail('handoff target must follow source in draw order')
   push(l,'opacity',[(s,1),(e,0)],ease);push(t,'opacity',[(s,0),(e,1)],ease);notes.append('Handoff is a crossfade at a shared anchor, not a 3D morph.');continue
  if op=='curve':
   pts=a.get('points',[]);n=a.get('samples',32)
   if len(pts)!=4 or type(n)!=int or not 8<=n<=120:fail('curve needs four control points and 8–120 samples')
   pts=[vector(v,2) for v in pts]
   # Sample a parametric cubic; the curve follows the chosen time easing.
   from compositor import ease as easing
   samples=[]
   for j in range(n+1):
    v=easing(j/n,ease);u=1-v;weights=(u**3,3*u*u*v,3*u*v*v,v**3)
    samples.append((s+(e-s)*j/n,[sum(w*p[k] for w,p in zip(weights,pts)) for k in (0,1)]))
   for k,axis in enumerate(('x','y')):push(l,axis,[(t,v[k]) for t,v in samples],'linear')
   continue
  if op=='orbit':
   cx,cy=vector(a['center'],2);rx,ry=vector(a['radius'],2);deg=vector(a.get('degrees',[0,360]),2);n=a.get('samples',24)
   if type(n)!=int or not 6<=n<=120:fail('orbit samples 6–120')
   for key,c,r,fn in [('x',cx,rx,math.cos),('y',cy,ry,math.sin)]:push(l,key,[(s+(e-s)*j/n,c+r*fn(math.radians(deg[0]+(deg[1]-deg[0])*j/n))) for j in range(n+1)],'linear')
   continue
  if op=='pulse':
   baseval=number(a.get('from',l.get('scale',1)),'pulse base');peak=baseval*number(a.get('amount',1.12),'pulse amount');push(l,'scale',[(s,baseval),((s+e)/2,peak),(e,baseval)],ease);continue
  if op=='shadow_strength' and not l.get('shadow'):fail('shadow_strength requires shadow:true')
  if op=='lens_strength' and l['kind']!='lens':fail('lens_strength requires lens')
  if op=='wipe':
   mask=a.get('mask','diagonal')
   if l.get('mask',mask)!=mask:fail('only one mask kind per layer')
   l['mask']=mask
  channels=ALL_OPS[op];v0=a['from'];v1=a['to'];v0=[v0] if len(channels)==1 else vector(v0,len(channels));v1=[v1] if len(channels)==1 else vector(v1,len(channels))
  for k,x,y in zip(channels,v0,v1):push(l,k,[(s,x),(e,y)],ease)
 for (i,k),arr in lanes.items():ls[i][k]=arr
 issues=audit(p)
 if issues:fail(f"{issues[0]['layer']}.{issues[0]['field']}: {issues[0]['message']}")
 # Validate handoff anchors against the completed timeline, including later-added motion.
 for a in spec.get('actions',[]):
  if a['op']=='handoff':
   x,y=ls[a['layer']],ls[a['target']];mid=(time(a['start'])+time(a['end']))/2
   for k in ('x','y'):
    if abs(val(x.get(k,DEFAULTS[k]),mid)-val(y.get(k,DEFAULTS[k]),mid))>12:fail('final handoff anchors differ: '+k)
 validate(p,base)
 p['review_times']=[v['time'] for v in targets(p,24)]
 return p,notes

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
 a=sub.add_parser('compile');a.add_argument('spec',type=Path);a.add_argument('out',type=Path)
 a=sub.add_parser('audit');a.add_argument('plan',type=Path)
 sub.add_parser('catalog');a=ap.parse_args()
 if a.cmd=='catalog':print(json.dumps({'actions':ALL_OPS,'allowed_fields':{k:sorted(allowed({'kind':k})) for k in FIELDS}},indent=2));return
 if a.cmd=='audit':p=json.loads(a.plan.read_text());validate(p,a.plan.resolve().parent);print(json.dumps({'advisories':audit(p)},indent=2));return
 p,notes=compile_spec(json.loads(a.spec.read_text()),a.spec.resolve().parent)
 if a.out.exists():fail('refusing to overwrite existing plan')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(p,indent=2)+'\n');print(json.dumps({'plan':str(a.out.resolve()),'layers':len(p['layers']),'notes':notes,'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':main()
