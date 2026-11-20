#!/usr/bin/env python3
"""One current production route. Picture joins require decoded preview evidence and review."""
import argparse,json,sys,math
from pathlib import Path
from director_v43 import build
from production_v40 import start as start40,checked,render,evidence
from production_v42 import requests,pixels,check_pixels,gate as gate42,template as template42
from scene_audit_v41 import audit
from transition_review_v43 import create,verify
from agent_session import write,sha

def start(spec,creative,work,audio=None):
 p,_,_=build(json.loads(spec.read_text()),spec.resolve().parent);c=json.loads(creative.read_text());r=requests(p,c)
 s=start40(spec,creative,work,audio,builder=build);write(work/'pixel-requests.json',r);write(work/'scene-audit.json',audit(p));return {**s,'pixel_targets':len(r),'next':'run next'}

def context(w):
 checked(w);p=json.loads((w/'plan.json').read_text());c=json.loads((w/'creative.json').read_text());_,err=evidence(w)
 if err:raise ValueError('; '.join(err))
 return w/'preview'/'film.mp4',c,w/'transitions',p['fps'],round(p['duration']*p['fps'])

def transitions(w):return create(*context(w))
def check_transitions(w):
 try:return verify(*context(w))
 except (OSError,KeyError,ValueError,TypeError) as e:return {'valid':False,'errors':['transition evidence missing/invalid: '+str(e)]}

def template(w):
 q=check_transitions(w)
 if not q['valid']:raise ValueError('; '.join(q['errors']))
 r=template42(w);report=json.loads((w/'transitions'/'report.json').read_text());r['transition_report_sha256']=sha(w/'transitions'/'report.json');r['boundary_reviews']=[{'id':x['id'],'decision':'pending','observation':'','reason':''} for x in report['results']]
 # template42 already created the new file; update only this newly created template.
 (w/'review.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');return r

def gate(w):
 a=gate42(w);b=check_transitions(w);errors=a['errors']+b['errors']
 if b['valid']:
  try:
   r=json.loads((w/'review.json').read_text());actual=json.loads((w/'transitions'/'report.json').read_text());d=r['boundary_reviews']
   if r.get('transition_report_sha256')!=sha(w/'transitions'/'report.json'):errors.append('review tied to different boundary report')
   if not isinstance(d,list) or len(d)!=len(actual['results']):errors.append('review every boundary including opening and closing')
   else:
    for x,y in zip(d,actual['results']):
     if x.get('id')!=y['id'] or x.get('decision')!='pass' or not isinstance(x.get('observation'),str) or not x['observation'].strip() or (y['flags'] and not str(x.get('reason','')).strip()):errors.append(f'boundary {y["id"]}: unresolved; inspect actual frames, fix or explain intentional cut')
  except (OSError,ValueError,KeyError,TypeError):errors.append('boundary review missing/invalid')
 return {'ready':not errors,'errors':errors,'note':'Review decisions are self-attestations, not proof of aesthetic quality or audio rights.'}

def advice(w):
 """Map measured review prompts to source-layer owners, never auto-apply a repair."""
 state=checked(w);c=json.loads((w/'creative.json').read_text());p=json.loads((w/'plan.json').read_text());by={l['id']:l for l in p['layers']};issues=[]
 if check_pixels(w)['valid']:
  r=json.loads((w/'pixel'/'report.json').read_text())
  for x in r['results']:
   l=by[x['layer']]
   for flag in x['flags']:
    fields=['x','y','scale','maxw','size','parent'] if 'safe area' in flag else ['active','opacity','parent','mask','mask_progress','matte','reveal','color']
    issues.append({'category':'pixel','time':x['time'],'layer_ids':[l['id']],'evidence':str(w/'pixel'/x['file']),'observation':flag,'inspect_fields':fields,'action':'Inspect actual crop or visible contribution, then edit the canonical authoring spec (or component definition), compile a fresh revision and compare. Intentional crop/occlusion is allowed only with explanation.'})
 if check_transitions(w)['valid']:
  r=json.loads((w/'transitions'/'report.json').read_text())
  for x in r['results']:
   i=x['id'];ids=list(dict.fromkeys(k for b in c['beats'][max(0,i-1):min(len(c['beats']),i+1)] for k in b['layer_ids']))
   for flag in x['flags']:
    issues.append({'category':'boundary','time':x['center']/p['fps'],'layer_ids':ids,'evidence':str(w/'transitions'/x['file']),'observation':flag,'inspect_fields':['active','x','y','scale','rotate','opacity','mask_progress','parent'],'action':'Compare before/after silhouettes, anchor and direction; check velocity separately. Repair motion timing/overlap in a new source revision, or document why a deliberate cut works.'})
 return {'canonical_source':state['source'],'suggestions':issues,'note':'Only measured flags with matching evidence are included. No flags does not prove readability, smoothness or professional quality. Never automatically modify or approve the source.'}

def next_step(w):
 checked(w);prefix=[sys.executable,'scripts/production_v43.py'];path=str(w.resolve())
 def stage(name,cmd,*args):return {'stage':name,'argv':prefix+[cmd,path,*args]}
 for sub,marker,cmd,args in [('preview','evidence.json','preview',['--size','720']),('pixel','report.json','pixels',[]),('transitions','report.json','transitions',[])]:
  if not (w/sub/marker).is_file():return {'stage':'blocked','action':f'Incomplete {sub}; preserve and create fresh revision'} if (w/sub).exists() else stage(sub,cmd,*args)
  try:
   if sub=='preview':_,err=evidence(w)
   else:err=(check_pixels(w) if sub=='pixel' else check_transitions(w))['errors']
  except (OSError,ValueError,KeyError,TypeError) as e:err=[str(e)]
  if err:return {'stage':'blocked','errors':err}
 if not (w/'review.json').is_file():return {**stage('review','review-template'),'action':'Watch actual preview; inspect each pixel/boundary sheet; listen if audio. No automatic passes.'}
 g=gate(w)
 if not g['ready']:return {'stage':'blocked_review','errors':g['errors'],'action':'Repair actual defects in canonical source, rerender new revision; never auto-approve.'}
 if not (w/'upload'/'evidence.json').is_file():return {'stage':'blocked','action':'Incomplete upload; new revision required'} if (w/'upload').exists() else stage('upload','upload')
 return stage('verify','verify-export')

def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);b=s.add_parser('start');b.add_argument('spec',type=Path);b.add_argument('creative',type=Path);b.add_argument('work',type=Path);b.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  b=s.add_parser(k);b.add_argument('work',type=Path);b.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');b.add_argument('--size',type=int)
 for k in ('next','pixels','transitions','review-template','gate','verify-export','advice'):s.add_parser(k).add_argument('work',type=Path)
 z=a.parse_args();w=z.work
 if z.cmd=='start':r=start(z.spec,z.creative,w,z.audio)
 elif z.cmd in ('preview','upload','master'):
  if z.cmd!='preview' and not gate(w)['ready']:raise ValueError('V43 gate failed; run gate')
  r=render(w,z.cmd,z.backend,z.size)
 elif z.cmd=='next':r=next_step(w)
 elif z.cmd=='pixels':r=pixels(w)
 elif z.cmd=='transitions':r=transitions(w)
 elif z.cmd=='review-template':r=template(w)
 elif z.cmd=='gate':r=gate(w)
 elif z.cmd=='advice':r=advice(w)
 else:
  r={}
  for k in ('upload','master'):
   if (w/k/'evidence.json').is_file():_,err=evidence(w,k);r[k]={'valid':not err,'errors':err}
 print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or any(not x['valid'] for x in r.values()))) else 0)
if __name__=='__main__':main()
