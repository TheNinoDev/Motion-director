#!/usr/bin/env python3
"""Current production route with decoded motion review; previous gates remain mandatory."""
import argparse,json,sys
from pathlib import Path
import production_v43 as old
from director_v44 import build
from agent_session import write,sha
from flow_review_v44 import create,verify

def start(spec,creative,w,audio=None):
 p,_,_=build(json.loads(spec.read_text()),spec.resolve().parent);c=json.loads(creative.read_text());r=old.requests(p,c)
 s=old.start40(spec,creative,w,audio,builder=build);write(w/'pixel-requests.json',r);write(w/'scene-audit.json',old.audit(p));return {**s,'next':'run next'}

def flow(w):
 v,c,_,fps,n=old.context(w);return create(v,c,w/'flow',fps,n)
def check(w):
 try:
  v,c,_,fps,n=old.context(w);return verify(v,c,w/'flow',fps,n)
 except (OSError,ValueError,TypeError,KeyError) as e:return {'valid':False,'errors':['flow unavailable: '+str(e)]}

def template(w):
 f=check(w)
 if not f['valid']:raise ValueError('; '.join(f['errors']))
 r=old.template(w);data=json.loads((w/'flow'/'report.json').read_text());r['flow_report_sha256']=sha(w/'flow'/'report.json');r['flow_reviews']=[{'id':x['id'],'decision':'pending','observation':'','reason':''} for x in data['results']];(w/'review.json').write_text(json.dumps(r,indent=2)+'\n');return r

def gate(w):
 a=old.gate(w);f=check(w);errors=a['errors']+f['errors']
 if f['valid']:
  try:
   r=json.loads((w/'review.json').read_text());data=json.loads((w/'flow'/'report.json').read_text());d=r['flow_reviews']
   if r.get('flow_report_sha256')!=sha(w/'flow'/'report.json'):errors.append('stale flow review')
   if not isinstance(d,list) or len(d)!=len(data['results']):errors.append('review each flow boundary')
   else:
    for x,y in zip(d,data['results']):
     if x.get('id')!=y['id'] or x.get('decision')!='pass' or not str(x.get('observation','')).strip() or (y['flags'] and not str(x.get('reason','')).strip()):errors.append(f'flow boundary {y["id"]}: unresolved')
  except (OSError,ValueError,KeyError,TypeError,AttributeError):errors.append('flow decisions missing or invalid')
 return {'ready':not errors,'errors':errors,'note':'Evidence and self-attestation. Not aesthetic certification.'}

def next_step(w):
 old.checked(w);r=old.next_step(w);prefix=[sys.executable,'scripts/production_v44.py'];path=str(w.resolve())
 if r['stage'] in ('preview','pixel','transitions','blocked'): 
  if 'argv' in r:r['argv']=prefix+r['argv'][2:]
  return r
 if not (w/'flow'/'report.json').is_file():return {'stage':'blocked','action':'incomplete flow folder; new revision required'} if (w/'flow').exists() else {'stage':'flow','argv':prefix+['flow',path]}
 f=check(w)
 if not f['valid']:return {'stage':'blocked','errors':f['errors']}
 if not (w/'review.json').exists():return {'stage':'review','argv':prefix+['review-template',path],'action':'Inspect flow, pixels, boundary sheets and entire video. Never auto-approve.'}
 g=gate(w)
 if not g['ready']:return {'stage':'blocked_review','errors':g['errors'],'action':'Use advice, inspect evidence; repair canonical source and start new revision if needed.'}
 if 'argv' in r:r['argv']=prefix+r['argv'][2:]
 return r

def advice(w):
 r=old.advice(w)
 if check(w)['valid']:
  data=json.loads((w/'flow'/'report.json').read_text());c=json.loads((w/'creative.json').read_text())
  for x in data['results']:
   i=x['id'];ids=list(dict.fromkeys(k for b in c['beats'][max(0,i-1):min(len(c['beats']),i+1)] for k in b['layer_ids']))
   for flag in x['flags']:r['suggestions'].append({'category':'flow','time':x['center']/data['fps'],'layer_ids':ids,'evidence':str(w/'flow'/x['file']),'observation':flag,'inspect_fields':['x','y','rotate','active','opacity','mask_progress'],'action':'Watch frame sequence and actual speed. If unintentional change, use a common path or extend overlap; insufficient flow is not an error by itself.'})
 return r

def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);a=s.add_parser('start');a.add_argument('spec',type=Path);a.add_argument('creative',type=Path);a.add_argument('work',type=Path);a.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  a=s.add_parser(k);a.add_argument('work',type=Path);a.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');a.add_argument('--size',type=int)
 for k in ('next','pixels','transitions','flow','review-template','gate','advice','verify-export'):s.add_parser(k).add_argument('work',type=Path)
 z=p.parse_args();w=z.work
 if z.cmd=='start':r=start(z.spec,z.creative,w,z.audio)
 elif z.cmd in ('preview','upload','master'):
  if z.cmd!='preview' and not gate(w)['ready']:raise ValueError('V44 gate failed; run gate')
  r=old.render(w,z.cmd,z.backend,z.size)
 elif z.cmd=='verify-export':
  r={k:{'valid':not old.evidence(w,k)[1]} for k in ('upload','master') if (w/k/'evidence.json').is_file()}
 else:r={'next':next_step,'pixels':old.pixels,'transitions':old.transitions,'flow':flow,'review-template':template,'gate':gate,'advice':advice}[z.cmd](w)
 print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or not all(x['valid'] for x in r.values()))) else 0)
if __name__=='__main__':main()
