#!/usr/bin/env python3
"""Gesture-aware production with full-preview cadence evidence in addition to V44 gates."""
import argparse,json,sys
from pathlib import Path
import production_v44 as old
from director_v45 import build
from agent_session import write,sha
from cadence_review_v45 import create,verify

def start(spec,creative,w,audio=None):
 p,_,_=build(json.loads(spec.read_text()),spec.resolve().parent);c=json.loads(creative.read_text());r=old.old.requests(p,c)
 s=old.old.start40(spec,creative,w,audio,builder=build);write(w/'pixel-requests.json',r);write(w/'scene-audit.json',old.old.audit(p));return {**s,'next':'run next'}

def cadence(w):
 v,c,_,fps,n=old.old.context(w);return create(v,c,w/'cadence',fps,n)
def check(w):
 try:
  v,c,_,fps,n=old.old.context(w);return verify(v,c,w/'cadence',fps,n)
 except (OSError,ValueError,TypeError,KeyError) as e:return {'valid':False,'errors':[str(e)]}

def template(w):
 f=check(w)
 if not f['valid']:raise ValueError('; '.join(f['errors']))
 r=old.template(w);report=w/'cadence'/'report.json';data=json.loads(report.read_text());r['cadence_report_sha256']=sha(report);r['cadence_reviews']=[{'beat':x['beat'],'decision':'pending','observation':'','reason':''} for x in data['results']];(w/'review.json').write_text(json.dumps(r,indent=2)+'\n');return r

def gate(w):
 a=old.gate(w);f=check(w);errors=a['errors']+f['errors']
 if f['valid']:
  try:
   r=json.loads((w/'review.json').read_text());report=w/'cadence'/'report.json';data=json.loads(report.read_text());d=r['cadence_reviews']
   if r.get('cadence_report_sha256')!=sha(report):errors.append('stale cadence review')
   if not isinstance(d,list) or len(d)!=len(data['results']):errors.append('review every cadence beat')
   else:
    for x,y in zip(d,data['results']):
     if x.get('beat')!=y['beat'] or x.get('decision')!='pass' or not isinstance(x.get('observation'),str) or not x['observation'].strip() or (y['flags'] and not str(x.get('reason','')).strip()):errors.append(f'cadence beat {y["beat"]}: unresolved')
  except (OSError,ValueError,KeyError,TypeError,AttributeError):errors.append('cadence decisions missing/invalid')
 return {'ready':not errors,'errors':errors,'note':'Evidence and self-attestation. No aesthetic certification.'}

def next_step(w):
 r=old.next_step(w);prefix=[sys.executable,'scripts/production_v45.py'];path=str(w.resolve())
 if r['stage'] not in ('preview','pixel','transitions','flow','blocked'):
  if not (w/'cadence'/'report.json').is_file():return {'stage':'blocked','action':'incomplete cadence folder; new revision required'} if (w/'cadence').exists() else {'stage':'cadence','argv':prefix+['cadence',path]}
  f=check(w)
  if not f['valid']:return {'stage':'blocked','errors':f['errors']}
  if not (w/'review.json').exists():return {'stage':'review','argv':prefix+['review-template',path],'action':'Watch complete preview, listen if audio; inspect every evidence sheet. No auto-approval.'}
  g=gate(w)
  if not g['ready']:return {'stage':'blocked_review','errors':g['errors'],'action':'Inspect and fix real defects; use advice and new revision. Never auto-approve.'}
 if 'argv' in r:r['argv']=prefix+r['argv'][2:]
 return r

def advice(w):
 r=old.advice(w)
 if check(w)['valid']:
  data=json.loads((w/'cadence'/'report.json').read_text());c=json.loads((w/'creative.json').read_text())
  for x in data['results']:
   for flag in x['flags']:r['suggestions'].append({'category':'cadence','time':x['start_frame']/data['fps'],'layer_ids':c['beats'][x['beat']]['layer_ids'],'evidence':str(w/'cadence'/x['file']),'observation':flag,'inspect_fields':['active','opacity','x','y','scale','mask_progress'],'action':'Watch entire beat, preserve deliberate holds; repair absent action or unintended blank, not every quiet frame.'})
 return r

def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);a=s.add_parser('start');a.add_argument('spec',type=Path);a.add_argument('creative',type=Path);a.add_argument('work',type=Path);a.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  a=s.add_parser(k);a.add_argument('work',type=Path);a.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');a.add_argument('--size',type=int)
 for k in ('next','pixels','transitions','flow','cadence','review-template','gate','advice','verify-export'):s.add_parser(k).add_argument('work',type=Path)
 z=p.parse_args();w=z.work
 if z.cmd=='start':r=start(z.spec,z.creative,w,z.audio)
 elif z.cmd in ('preview','upload','master'):
  if z.cmd!='preview' and not gate(w)['ready']:raise ValueError('V45 gate failed; run gate')
  r=old.old.render(w,z.cmd,z.backend,z.size)
 elif z.cmd=='verify-export':
  r={k:{'valid':not old.old.evidence(w,k)[1]} for k in ('upload','master') if (w/k/'evidence.json').is_file()}
 else:r={'next':next_step,'pixels':old.old.pixels,'transitions':old.old.transitions,'flow':old.flow,'cadence':cadence,'review-template':template,'gate':gate,'advice':advice}[z.cmd](w)
 print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or not all(x['valid'] for x in r.values()))) else 0)
if __name__=='__main__':main()
