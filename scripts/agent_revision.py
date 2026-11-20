#!/usr/bin/env python3
"""Non-destructive, fingerprinted layer-only revisions. No automatic aesthetic scoring."""
import argparse, copy, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import validate
from motion_workbench import allowed, audit
from review_targets import targets

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def revise(plan,request,base):
 if set(request)-{'source_sha256','reason','changes'}:raise ValueError('unknown revision keys')
 if not str(request.get('reason','')).strip():raise ValueError('reason required')
 out=copy.deepcopy(plan); layers={l['id']:l for l in out['layers']}; seen=set();report=[]
 for op in request['changes']:
  if set(op)-{'layer','set','remove'}:raise ValueError('unknown change keys')
  name=op['layer'];l=layers[name];fields=op.get('set',{});remove=op.get('remove',[])
  if set(fields)&set(remove):raise ValueError('same field set and removed')
  for k in list(fields)+list(remove):
   if k in ('id','kind','src','parent','active','font','text','crop') or k not in allowed(l):raise ValueError('protected or unsupported field: '+k)
   if (name,k) in seen:raise ValueError('duplicate field change')
   seen.add((name,k))
  before=copy.deepcopy(l)
  for k in remove:
   if k not in l:raise ValueError('cannot remove absent field '+k)
   del l[k]
  l.update(copy.deepcopy(fields));report.append({'layer':name,'changed':sorted(k for k in set(before)|set(l) if before.get(k)!=l.get(k)),'review_interval':l['active']})
 if not report:raise ValueError('empty revision')
 validate(out,base)
 old={(x['layer'],x['field'],x['message']) for x in audit(plan)}
 new=[x for x in audit(out) if (x['layer'],x['field'],x['message']) not in old]
 if new:raise ValueError('new unsupported options: '+str(new))
 return out,report

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('request',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
 if a.output.exists():raise ValueError('refuse overwrite')
 # Same directory preserves existing relative asset paths without altering unrelated fields.
 if a.plan.resolve().parent!=a.output.resolve().parent:raise ValueError('output must be alongside source plan')
 req=json.loads(a.request.read_text());original=digest(a.plan)
 if req.get('source_sha256')!=original:raise ValueError('source fingerprint mismatch; inspect latest plan first')
 p,r=revise(json.loads(a.plan.read_text()),req,a.plan.resolve().parent)
 a.output.write_text(json.dumps(p,indent=2)+'\n');print(json.dumps({'source_sha256':original,'output_sha256':digest(a.output),'reason':req['reason'],'changes':r,'review_targets':targets(p,24),'approval':'not reviewed'},indent=2))
if __name__=='__main__':main()
