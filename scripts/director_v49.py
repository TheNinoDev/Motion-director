#!/usr/bin/env python3
"""Small, composable staging recipes and actionable compiler diagnostics."""
import argparse, copy, json
from pathlib import Path
import director_v48 as old
from agent_session import write
from motion_workbench import allowed
from director_v40 import track
A=old.action
S=old.sound
EXTRA={
 'masked_handoff':dict(slots=['outgoing','incoming'],params={'exit_x':-80,'entry_x':360},actions=[A('incoming',0,.8,{'opacity':1,'x':'$entry_x','reveal':1},ease='quint'),A('outgoing',.2,1,{'opacity':0,'x':'$exit_x'},ease='smooth')],sounds=[]),
 'press_release':dict(slots=['object'],params={'compression':-.09,'lift':.035},actions=[A('object',0,.42,{'scale':'$compression'},'pulse','sine'),A('object',.42,1,{'scale':'$lift'},'pulse','sine')],sounds=[S(.2,.48,'click',-25)]),
 'light_answer':dict(slots=['hero','label'],params={'light':.8},actions=[A('hero',0,.65,{'light':'$light'}),A('label',.25,1,{'opacity':1,'blur':0})],sounds=[]),
 'depth_handoff':dict(slots=['outgoing','incoming'],params={'exit_yaw':-32,'entry_scale':1},actions=[A('outgoing',.15,1,{'yaw':'$exit_yaw','opacity':0}),A('incoming',0,.85,{'yaw':0,'scale':'$entry_scale','opacity':1})],sounds=[]),
 'proof_detail':dict(slots=['product','annotation'],params={'zoom':1.2,'target_x':360,'target_y':640},actions=[A('product',0,.8,{'scale':'$zoom','x':'$target_x','y':'$target_y'},ease='quint'),A('annotation',.35,1,{'opacity':1,'reveal':1})],sounds=[]),
 'settle_pair':dict(slots=['primary','secondary'],params={'primary_delta':.07,'secondary_delta':.04},actions=[A('primary',0,.7,{'scale':'$primary_delta'},'pulse','sine'),A('secondary',.25,1,{'scale':'$secondary_delta'},'pulse','sine')],sounds=[]),
 'trace_then_label':dict(slots=['trace','label'],params={},actions=[A('trace',0,.72,{'reveal':1},ease='quint'),A('label',.48,1,{'opacity':1,'blur':0})],sounds=[]),
 'quiet_recede':dict(slots=['object'],params={'scale':.92,'opacity':.2,'blur':4},actions=[A('object',0,1,{'scale':'$scale','opacity':'$opacity','blur':'$blur'})],sounds=[]),
}

def build(spec,base):
 s=copy.deepcopy(spec)
 custom=s.get('sequence_library',{})
 if not isinstance(custom,dict):raise ValueError('sequence_library must be an object')
 # V48 projects may already use these names as custom definitions; preserve their meaning.
 used={x.get('recipe') for x in s.get('sequences',[]) if isinstance(x,dict) and isinstance(x.get('recipe'),str)}
 s['sequence_library']={**{k:v for k,v in EXTRA.items() if k in used and k not in custom},**custom}
 return old.build(s,base)

REMEDIES=[
 ('overlapping cue','Inspect all owners of the named layer/property. Move or shorten only the conflicting cue; use another lane if simultaneous motion is intentional.'),
 ('already animated','Do not remove approved keyframes. Put the new movement on a compatible parent or unused property, or revise the same original track deliberately.'),
 ('outside picture','Inspect the resolved marker and total duration. Move or shorten the intended instance. Recheck adjacent cues and sound timing.'),
 ('too short','Increase duration or adjust normalized phase lengths. A pulse needs at least two frames; never silently clamp.'),
 ('rounds to zero','Increase the duration at the actual picture FPS. Do not change FPS merely to hide invalid timing.'),
 ('unknown sequence','Run catalog; use exact recipe, slot and parameter names. Do not invent properties.'),
 ('bind every','Bind every declared slot to a different existing layer ID; the slot is a role, not a new layer.'),
 ('missing asset','Locate the authorized original asset or correct its path. Do not substitute fake UI or a placeholder in a final ad.'),
 ('cycle','Remove unintended circular marker dependency. Prefer one absolute or gesture-rooted marker and dependent offsets.'),
 ('outside range','Read the property range; change the requested target or delta, not the validator.'),
 ('active interval','Extend an active interval only if visibility is intended, or move the cue into its existing interval.'),
]
def diagnose(spec,base):
 try:
  p,e,n=build(spec,base);return {'valid':True,'layers':len(p['layers']),'markers':e['named_markers'],'sequences':len(e['sequences']),'next':'start a fresh production directory; inspect actual playback and evidence','notes':n}
 except (ValueError,KeyError,TypeError,OSError,AttributeError) as ex:
  msg=str(ex);return {'valid':False,'error':msg,'repair':next((v for k,v in REMEDIES if k in msg.lower()),'Read exact compiler error and relevant schema; change only the invalid source property. Do not bypass validation.'),'next':'edit canonical source into a new revision and rerun diagnose'}

def capabilities(spec,base,layer):
 p,e,_=build(spec,base)
 l=next((l for l in p['layers'] if l['id']==layer),None)
 if l is None:raise ValueError('unknown compiled layer '+layer)
 props=set(allowed(l)) & set(old.RANGES)
 if l['kind']=='text' and l.get('material')!='metal':props.discard('light')
 if not l.get('mask'):props.discard('mask_progress')
 if not l.get('shadow'):props.discard('shadow_opacity')
 occupied={k for k in props if track(l.get(k))}
 matches=[]
 for name,d in {**old.PRESETS,**EXTRA,**spec.get('sequence_library',{})}.items():
  for slot in d['slots']:
   needed={k for a in d['actions'] if a['slot']==slot for k in a['values']}
   if needed<=props:matches.append({'recipe':name,'slot':slot,'properties':sorted(needed),'already_animated':sorted(needed&occupied)})
 return {'layer':layer,'kind':l['kind'],'active':l['active'],'supported':sorted(props),'occupied':sorted(occupied),'compatible_roles':matches,'note':'Property compatibility only. For occupied properties, check source ownership and overlapping timing; valid sequential cue lanes may be reused. Compile final bindings.'}

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True);sub.add_parser('catalog')
 for name in ('diagnose','inspect','compile','capabilities'):
  a=sub.add_parser(name);a.add_argument('source',type=Path)
  if name=='compile':a.add_argument('output',type=Path)
  if name=='capabilities':a.add_argument('layer')
 z=p.parse_args()
 if z.cmd=='catalog':r={'recipes':{**old.PRESETS,**EXTRA},'instance':{'id':'accent','recipe':'press_release','marker':'press','offset':0,'duration':.6,'bind':{'object':'existing_layer'},'params':{}},'note':'Read role prerequisites and actual property support. Custom V48 names retain precedence.'}
 else:
  spec=json.loads(z.source.read_text());base=z.source.resolve().parent
  if z.cmd=='diagnose':r=diagnose(spec,base)
  elif z.cmd=='capabilities':r=capabilities(spec,base,z.layer)
  else:
   plan,e,n=build(spec,base)
   if z.cmd=='compile':write(z.output,plan)
   r={'markers':e['named_markers'],'sequences':e['sequences'],'actions':e['cue_actions'],'sounds':e['sound_cues'],'notes':n}
 print(json.dumps(r,indent=2));raise SystemExit(2 if r.get('valid') is False else 0)
if __name__=='__main__':main()
