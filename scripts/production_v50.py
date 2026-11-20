#!/usr/bin/env python3
"""Ad-first orchestration: enforce preproduction before the legacy compositor workflow."""
import argparse, json, sys, subprocess
from pathlib import Path
import production_v49 as old
from production_v43 import pixels,transitions
from production_v44 import flow
from production_v45 import cadence
from production_v46 import audio_review
import preproduction_v50 as pre
from director_v49 import build
from production_v40 import checked,render,evidence
from agent_session import sha,write
from compositor import val


def coverage(p,c):
 """Conservative heuristic: proof of nontrivial changes on named visible layers, not visual quality."""
 fps=p['fps'];by={l['id']:l for l in p['layers']};rows=[];errors=[]
 if c['mode']!='advertisement':return {'errors':[], 'beats':[]}
 for i,b in enumerate(c['beats']):
  event=b.get('direction',{});a,z=b['start'],b['end'];active=[]
  for k in ('subject_layer','operation','before','after','why','transition'):
   if not pre.text(event.get(k)):errors.append(f'beat {i}: direction.{k} missing')
  subject=event.get('subject_layer')
  if subject not in b.get('layer_ids',[]):errors.append(f'beat {i}: dominant subject must link to actual layer')
  for key in b.get('layer_ids',[]):
   if key not in by:continue
   l=by[key];lo=max(a,l['active'][0]);hi=min(z,l['active'][1]);times=[lo+(hi-lo)*j/12 for j in range(13)] if hi>lo else []
   if not times:continue
   tracks=[]
   for prop,v in l.items():
    if prop not in ('x','y','scale','sx','sy','rotate','yaw','pitch','reveal','mask_progress','light','morph','bend','twist','refraction','crop_x','crop_y','blur'):continue
    if isinstance(v,list):
     try:
      vv=[val(v,t) for t in times]
      if max(vv)-min(vv)>.001:tracks.append(prop)
     except (ValueError,TypeError,IndexError):pass
   if tracks:active.append({'layer':key,'kind':l['kind'],'changing':tracks})
  if not active and not pre.text(event.get('intentional_hold')):errors.append(f'beat {i}: no measured linked motion except opacity; create a meaningful action or document intentional hold')
  rows.append({'beat':i,'active_motion':active})
 if len(rows)>=4 and sum(not x['active_motion'] for x in rows)>len(rows)//2:errors.append('More than half of beats have no measured motion. Not a motion-led advertisement; redesign or use a different renderer with equivalent evidence.')
 layouts=[b.get('layout') for b in c['beats']]
 if len(layouts)>=4 and len(set(layouts))<3:errors.append('Repeated slideshow layout: use at least three distinct compositional treatments, not merely different names.')
 return {'errors':errors,'beats':rows,'limitations':'Track sampling, not rendered aesthetics; custom renderer motion may need a separate documented route.'}

def start(spec,creative,w,manifest=None):
 c=pre.read(creative);bed=None;record=None
 if c['mode']!='fictional_study':
  if manifest is None:raise ValueError('No preproduction manifest. Run preproduction_v50.py next first. Do not downgrade ad to study.')
  r=pre.check(manifest,release=True)
  if not r['ready']:raise ValueError('Preproduction blocked: '+r['stage']+' '+str(r['errors']))
  p,_,_=build(pre.read(spec),spec.resolve().parent);report=coverage(p,c)
  if report['errors']:raise ValueError('; '.join(report['errors']))
  d=pre.read(manifest);b=d['brief']
  if c['audience']!=b['audience'] or c['product']!=b['product_name'] or c['central_idea']!=b['focus']:raise ValueError('Creative brief differs from locked product/audience/focus; revise explicitly.')
  if w.exists():raise ValueError('Choose fresh production directory.')
  bed=w.parent/(w.name+'-bed.wav');bed.parent.mkdir(parents=True,exist_ok=True)
  record=pre.mix(manifest,bed,p['duration']);record['coverage']=report
 result=old.start(spec,creative,w,bed);s=checked(w)
 if record:
  f=w/'preproduction.json';write(f,record);s['inputs'].update(record['inputs']);s['inputs'][str(f.resolve())]=sha(f);s['inputs'][str(bed.with_suffix('.mix.json').resolve())]=sha(bed.with_suffix('.mix.json'));old.old.replace_json(w/'production.json',s)
 return {**result,'preproduction_locked':bool(record)}

def ensure(w):
 s=checked(w)
 if s['mode']!='fictional_study' and not (w/'preproduction.json').is_file():raise ValueError('V50 preproduction missing; migrate real ad to new session.')
 return s

def gate(w):
 try:ensure(w);return old.gate(w)
 except (ValueError,OSError,KeyError) as e:return {'ready':False,'errors':[str(e)]}

def next_step(w):
 ensure(w);r=old.next_step(w)
 if 'argv' in r:r['argv']=[sys.executable,'scripts/production_v50.py']+r['argv'][2:]
 return r

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);s=sub.add_parser('start');s.add_argument('spec',type=Path);s.add_argument('creative',type=Path);s.add_argument('work',type=Path);s.add_argument('--manifest',type=Path)
 for k in ('preview','upload','master'):
  a=sub.add_parser(k);a.add_argument('work',type=Path);a.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');a.add_argument('--size',type=int)
 for k in ('next','pixels','transitions','flow','cadence','audio-review','cue-review','review-template','gate','advice','verify-export'):sub.add_parser(k).add_argument('work',type=Path)
 z=ap.parse_args();w=z.work
 try:
  if z.cmd=='start':r=start(z.spec,z.creative,w,z.manifest)
  elif z.cmd=='gate':r=gate(w)
  else:
   ensure(w)
   if z.cmd in ('preview','upload','master'):
    if z.cmd!='preview' and not gate(w)['ready']:raise ValueError('V50 gate failed; run gate')
    r=render(w,z.cmd,z.backend,z.size)
   elif z.cmd=='verify-export':r={k:{'valid':not evidence(w,k)[1]} for k in ('upload','master') if (w/k/'evidence.json').is_file()}
   else:r={'next':next_step,'pixels':old.old.old.old.old.pixels,'transitions':old.old.old.old.old.transitions,'flow':old.old.old.old.flow,'cadence':old.old.old.cadence,'audio-review':old.old.audio_review,'cue-review':old.cues,'review-template':old.template,'advice':old.advice}[z.cmd](w)
  print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or not all(x['valid'] for x in r.values()))) else 0)
 except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as e:ap.exit(2,str(e)+'\n')
if __name__=='__main__':main()
