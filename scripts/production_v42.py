#!/usr/bin/env python3
"""V42 production: actual per-beat pixel evidence before existing review gate."""
import argparse,json,sys,math
from pathlib import Path
from director_v42 import build
from production_v40 import start as start40, checked,render,gate as gate40,review_template,evidence
from production_v41 import next_step as next41
from agent_session import write,sha
from pixel_review_v42 import review,verify
from scene_audit_v41 import audit,world

def requests(p,c):
 by={l['id']:l for l in p['layers']};fps=p['fps'];nn=round(p['duration']*fps);out=[]
 for i,b in enumerate(c['beats']):
  choices=[]
  for id in b['layer_ids']:
   l=by[id]
   if l['kind']=='group' or l.get('matte_only'):continue
   lo=max(0,math.ceil(max(b['start'],l['active'][0])*fps-1e-9));hi=min(nn-1,math.ceil(min(b['end'],l['active'][1])*fps-1e-9)-1)
   if lo>hi:continue
   # Pick most visible among five times, prefer near middle on tie.
   mid=(b['start']+b['end'])/2*fps
   f=max({lo,hi,*[round(lo+(hi-lo)*q/4) for q in range(5)]},key=lambda f:(world(l,by,f/fps)[1],-abs(f-mid)))
   choices.append((world(l,by,f/fps)[1],l['kind'] in ('text','text3d'),f,id))
  if not choices:raise ValueError(f'beat {i}: link an actual drawable active on a frame')
  # One principal drawable per beat; add text if distinct and budget permits.
  best=max(choices,key=lambda x:x[0]);out.append({'frame':best[2],'layer':best[3]})
  texts=[x for x in choices if x[1] and x[3]!=best[3]]
  if texts and len(c['beats'])<=16:
   z=max(texts,key=lambda x:x[0]);out.append({'frame':z[2],'layer':z[3]})
 if len(out)>32:raise ValueError('pixel review supports up to 32 targets; split long project into review sections or consolidate beats')
 return [dict(frame=f,layer=l) for f,l in dict.fromkeys((x['frame'],x['layer']) for x in out)]

def start(spec,creative,work,audio=None):
 # Fail before making work if target generation fails.
 p,_,_=build(json.loads(spec.read_text()),spec.resolve().parent);c=json.loads(creative.read_text());r=requests(p,c)
 s=start40(spec,creative,work,audio,builder=build);write(work/'pixel-requests.json',r);write(work/'scene-audit.json',audit(p));return {**s,'pixel_targets':len(r),'next':'run next; preview, pixel review, then explicit review'}

def check_pixels(work):
 checked(work);p=json.loads((work/'plan.json').read_text());c=json.loads((work/'creative.json').read_text());want=requests(p,c)
 try:
  report=json.loads((work/'pixel'/'report.json').read_text());r=verify(work/'plan.json',work/'pixel');got=[{k:x[k] for k in ('frame','layer')} for x in report['results']]
  if got!=want:r['errors'].append('pixel targets differ from current project')
  if json.loads((work/'pixel-requests.json').read_text())!=want:r['errors'].append('pixel request file changed')
  r['valid']=not r['errors'];return r
 except (OSError,KeyError,ValueError,TypeError) as e:return {'valid':False,'errors':['pixel evidence missing/invalid: '+str(e)]}

def pixels(work):
 checked(work);p=json.loads((work/'plan.json').read_text());c=json.loads((work/'creative.json').read_text());r=requests(p,c)
 if json.loads((work/'pixel-requests.json').read_text())!=r:raise ValueError('pixel request file changed')
 return review(work/'plan.json',work/'pixel',r)

def gate(work):
 a=gate40(work);b=check_pixels(work);errors=a['errors']+b['errors']
 if b['valid']:
  try:
   r=json.loads((work/'review.json').read_text());report=json.loads((work/'pixel'/'report.json').read_text());flags=[x for x in report['results'] if x['flags']]
   if r.get('pixel_report_sha256')!=sha(work/'pixel'/'report.json'):errors.append('review not bound to pixel report')
   if r.get('pixel_reviewed') is not True:errors.append('inspect actual pixel comparisons')
   dec=r.get('pixel_flags',[])
   if not isinstance(dec,list) or len(dec)!=len(flags):errors.append('address each measured pixel warning')
   else:
    for x,y in zip(dec,flags):
     if x.get('file')!=y['file'] or x.get('decision')!='intentional' or not isinstance(x.get('reason'),str) or not x['reason'].strip():errors.append('unresolved pixel warning: '+y['file'])
  except (OSError,ValueError,KeyError,TypeError):errors.append('pixel review decisions missing/invalid')
 return {'ready':not errors,'errors':errors,'note':'Technical evidence + explicit self-attestation; warnings may be intentional. Repair real defects in a new source revision.'}

def template(work):
 q=check_pixels(work)
 if not q['valid']:raise ValueError('; '.join(q['errors']))
 # Build same review structure without temporary overwrite.
 e,err=evidence(work)
 if err:raise ValueError('; '.join(err))
 c=json.loads((work/'creative.json').read_text());report=json.loads((work/'pixel'/'report.json').read_text());r={'preview_sha256':e['video']['video_sha256'],'playback_watched':False,'audio_listened':False,'rights_verified':False,'beats':[{'beat':i,'time':round((b['start']+b['end'])/2,3),'decision':'pending','observation':'','repair':''} for i,b in enumerate(c['beats'])],'global_checks':{k:'pending' for k in ('typography','transitions','composition','motion','product_accuracy','audio')},'pixel_report_sha256':sha(work/'pixel'/'report.json'),'pixel_reviewed':False,'pixel_flags':[{'file':x['file'],'decision':'pending','reason':''} for x in report['results'] if x['flags']],'note':'View all actual comparisons, full preview and audio. Never auto-approve. If warning is a defect, revise and render again.'};write(work/'review.json',r);return r

def next_step(work):
 checked(work);prefix=[sys.executable,'scripts/production_v42.py'];w=str(work.resolve());base=next41(work)
 if base['stage']=='preview':return {'stage':'preview','argv':prefix+['preview',w,'--size','720']}
 if base['stage']=='blocked':return base
 if not (work/'pixel'/'report.json').is_file():return {'stage':'blocked','action':'Incomplete pixel folder; preserve and use new revision'} if (work/'pixel').exists() else {'stage':'pixel','argv':prefix+['pixels',w]}
 q=check_pixels(work)
 if not q['valid']:return {'stage':'blocked','errors':q['errors']}
 if not (work/'review.json').is_file():return {'stage':'review','argv':prefix+['review-template',w],'action':'Watch preview and inspect pixel images before editing pending decisions.'}
 g=gate(work)
 if not g['ready']:return {'stage':'blocked_review','errors':g['errors'],'action':'Inspect and address real problems, never auto-mark pass.'}
 if base['stage'] in ('upload','verify'):base['argv']=prefix+base['argv'][2:]
 return base

def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);b=s.add_parser('start');b.add_argument('spec',type=Path);b.add_argument('creative',type=Path);b.add_argument('work',type=Path);b.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  b=s.add_parser(k);b.add_argument('work',type=Path);b.add_argument('--backend',choices=('auto','cpu','cuda'),default='auto');b.add_argument('--size',type=int)
 for k in ('next','pixels','review-template','gate','verify-export'):s.add_parser(k).add_argument('work',type=Path)
 z=a.parse_args();w=z.work
 if z.cmd=='start':r=start(z.spec,z.creative,w,z.audio)
 elif z.cmd in ('preview','upload','master'):
  if z.cmd!='preview' and not gate(w)['ready']:raise ValueError('V42 gate failed; run gate')
  r=render(w,z.cmd,z.backend,z.size)
 elif z.cmd=='next':r=next_step(w)
 elif z.cmd=='pixels':r=pixels(w)
 elif z.cmd=='review-template':r=template(w)
 elif z.cmd=='gate':r=gate(w)
 else:
  r={}
  for k in ('upload','master'):
   if (w/k/'evidence.json').is_file():_,err=evidence(w,k);r[k]={'valid':not err,'errors':err}
 print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or any(not x['valid'] for x in r.values()))) else 0)
if __name__=='__main__':main()
