#!/usr/bin/env python3
"""Primary route with named event tracks and rendered cue review, preserving V46 gates."""
import argparse,json,sys
from pathlib import Path
import production_v46 as old
from director_v47 import build
from agent_session import sha
from production_v40 import checked,evidence,render
import cue_review_v47 as cr

def start(spec,creative,w,audio=None):
 result=old.start(spec,creative,w,audio,builder=build);state=checked(w);x=w/'expanded.json';state['inputs'][str(x.resolve())]=sha(x);old.replace_json(w/'production.json',state);return result

def context(w):
 checked(w);_,err=evidence(w)
 if err:raise ValueError('; '.join(err))
 p=json.loads((w/'plan.json').read_text());e=json.loads((w/'expanded.json').read_text());return w/'preview'/'film.mp4',e,w/'cue-review',p['fps'],round(p['duration']*p['fps'])

def cues(w):return cr.create(*context(w))

def check_cues(w):
 try:return cr.verify(*context(w))
 except (OSError,ValueError,TypeError,KeyError) as ex:return {'valid':False,'errors':[str(ex)]}

def template(w):
 a=check_cues(w)
 if not a['valid']:raise ValueError('; '.join(a['errors']))
 r=old.template(w);p=w/'cue-review'/'report.json';q=json.loads(p.read_text());r['cue_review_v47']={'report_sha256':sha(p),'decisions':[{'id':x['id'],'decision':'pending','observation':''} for x in q['results']]};old.replace_json(w/'review.json',r);return r

def gate(w):
 a=old.gate(w);c=check_cues(w);errors=a['errors']+c['errors']
 if c['valid']:
  try:
   p=w/'cue-review'/'report.json';q=json.loads(p.read_text());r=json.loads((w/'review.json').read_text())['cue_review_v47'];ds=r['decisions']
   if r['report_sha256']!=sha(p) or len(ds)!=len(q['results']) or any(x['id']!=y['id'] or x['decision']!='pass' or not isinstance(x['observation'],str) or not x['observation'].strip() for x,y in zip(ds,q['results'])):errors.append('inspect each named cue and document actual timing/result')
  except (OSError,KeyError,ValueError,TypeError,AttributeError):errors.append('cue decisions missing/invalid')
 return {'ready':not errors,'errors':errors,'note':'Recorded evidence and review attestations only; no automatic aesthetic or audio approval.'}

def next_step(w):
 r=old.next_step(w);prefix=[sys.executable,'scripts/production_v47.py'];path=str(w.resolve())
 if r['stage'] not in ('preview','pixel','transitions','flow','cadence','audio-review','blocked'):
  if not (w/'cue-review'/'report.json').is_file():return {'stage':'blocked','action':'incomplete cue review; retain files and create new revision'} if (w/'cue-review').exists() else {'stage':'cue-review','argv':prefix+['cue-review',path]}
  a=check_cues(w)
  if not a['valid']:return {'stage':'blocked','errors':a['errors']}
  if (w/'review.json').exists():
   g=gate(w)
   if not g['ready']:return {'stage':'blocked_review','errors':g['errors'],'action':'Inspect actual media, repair if necessary, never auto-approve.'}
 if 'argv' in r:r['argv']=prefix+r['argv'][2:]
 return r

def advice(w):
 r=old.advice(w);a=check_cues(w)
 if a['valid']:
  q=json.loads((w/'cue-review'/'report.json').read_text())
  for x in q['results']:r['suggestions'].append({'category':'cue timing','time':x['frame']/q['fps'],'layer_ids':sorted({v['layer'] for v in x['actions']}),'evidence':str(w/'cue-review'/x['file']),'inspect_fields':['markers','cue_actions.offset','cue_actions.duration','cue_sounds.offset'],'action':'Compare the trigger, legibility, and outcome in the actual clip. Move a named marker to retime dependent motions and SFX; preserve unrelated lanes.'})
 return r

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);a=sub.add_parser('start');a.add_argument('spec',type=Path);a.add_argument('creative',type=Path);a.add_argument('work',type=Path);a.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  a=sub.add_parser(k);a.add_argument('work',type=Path);a.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');a.add_argument('--size',type=int)
 for k in ('next','pixels','transitions','flow','cadence','audio-review','cue-review','review-template','gate','advice','verify-export'):sub.add_parser(k).add_argument('work',type=Path)
 z=ap.parse_args();w=z.work
 if z.cmd=='start':r=start(z.spec,z.creative,w,z.audio)
 elif z.cmd in ('preview','upload','master'):
  if z.cmd!='preview' and not gate(w)['ready']:raise ValueError('V47 gate failed; run gate')
  r=render(w,z.cmd,z.backend,z.size)
 elif z.cmd=='verify-export':r={k:{'valid':not evidence(w,k)[1]} for k in ('upload','master') if (w/k/'evidence.json').is_file()}
 else:r={'next':next_step,'pixels':old.old.old.old.pixels,'transitions':old.old.old.old.transitions,'flow':old.old.old.flow,'cadence':old.old.cadence,'audio-review':old.audio_review,'cue-review':cues,'review-template':template,'gate':gate,'advice':advice}[z.cmd](w)
 print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or not all(x['valid'] for x in r.values()))) else 0)
if __name__=='__main__':main()
