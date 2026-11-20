#!/usr/bin/env python3
"""Create and validate a review checklist bound to exact plan and evidence files.
A human/agent must inspect images and playback; the checker cannot judge aesthetics.
"""
import argparse,hashlib,json
from pathlib import Path
from director_v37 import diagnosis
from compositor import validate
from review_targets import targets

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def create(plan):
 p=json.loads(plan.read_text());validate(p,plan.resolve().parent)
 items=[]
 for i,x in enumerate(targets(p,18)):items.append({'id':f'frame-{i:02d}','time':x['time'],'task':'; '.join(x['reasons']),'status':'pending','evidence':None,'sha256':None,'observation':'','decision':''})
 for i,x in enumerate(diagnosis(p)):items.append({'id':f'issue-{i:02d}','time':x['time'],'task':x['layer']+': '+x['fix'],'status':'pending','evidence':None,'sha256':None,'observation':'','decision':''})
 items.append({'id':'playback','time':None,'task':'Watch complete preview, checking continuity and actual motion; listen to intended audio if present.','status':'pending','evidence':None,'sha256':None,'observation':'','decision':''})
 return {'plan_sha256':digest(plan),'items':items,'note':'Technical record only. Status reviewed does not prove artistic quality.'}
def check(plan,ledger,base):
 expected=create(plan);errs=[];pending=[]
 if ledger.get('plan_sha256')!=expected['plan_sha256']:errs.append('plan changed; regenerate checklist')
 items=ledger.get('items',[]);ref={x['id']:x for x in expected['items']};seen=set()
 for x in items:
  i=x.get('id')
  if i not in ref or i in seen:errs.append('unknown or duplicate item '+str(i));continue
  seen.add(i)
  if any(x.get(k)!=ref[i][k] for k in ('time','task')):errs.append(i+': changed task or timing')
  if x.get('status')!='reviewed':pending.append(i);continue
  e=x.get('evidence');f=(base/e).resolve() if isinstance(e,str) and e else None
  if not f or not f.is_file() or f.suffix.lower() not in ('.png','.jpg','.jpeg','.mp4','.mov','.mkv','.webm') or (i=='playback' and f.suffix.lower() not in ('.mp4','.mov','.mkv','.webm')):errs.append(i+': missing or wrong evidence type')
  elif x.get('sha256')!=digest(f):errs.append(i+': evidence hash mismatch')
  if not str(x.get('observation','')).strip() or x.get('decision') not in ('keep','fix','intentional','blocked'):errs.append(i+': specific observation and decision required')
  elif x['decision'] in ('fix','blocked'):pending.append(i)
 for i in sorted(set(ref)-seen):errs.append('missing item '+i)
 return {'record_complete':not errs and not pending,'errors':errs,'pending':pending,'note':'Record completeness only; no assertion that evidence was watched or quality approved.'}
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['create','check']);a.add_argument('plan',type=Path);a.add_argument('ledger',type=Path);x=a.parse_args()
 if x.mode=='create':
  if x.ledger.exists():raise ValueError('refuse overwrite')
  x.ledger.parent.mkdir(parents=True,exist_ok=True);x.ledger.write_text(json.dumps(create(x.plan),indent=2)+'\n')
 else:
  r=check(x.plan,json.loads(x.ledger.read_text()),x.ledger.resolve().parent);print(json.dumps(r,indent=2));raise SystemExit(0 if r['record_complete'] else 2)
if __name__=='__main__':main()
