"""Transactional canonical-source repairs for simple authored layers; no implicit cascade."""
import argparse,copy,json
from pathlib import Path
from director_v44 import build
from director_v40 import track
from motion_workbench import number,allowed
from agent_session import sha,write

BOUNDS={'x':(-4000,4000),'y':(-4000,4000),'scale':(.01,8),'scale_x':(.01,8),'scale_y':(.01,8),'rotate':(-1440,1440),'opacity':(0,1),'size':(8,1000),'maxw':(16,2000),'blur':(0,80),'glow':(0,80),'w':(1,4000),'h':(1,4000)}
def repair(src,req,out):
 if out.exists() or out.resolve().parent!=src.resolve().parent:raise ValueError('new source alongside original required; preserve relative paths')
 original=sha(src)
 if set(req)!={'source_sha256','reason','changes'} or req['source_sha256']!=original or not isinstance(req['reason'],str) or not req['reason'].strip():raise ValueError('require current fingerprint and concrete reason')
 s=json.loads(src.read_text());before,_,_=build(s,src.resolve().parent);new=copy.deepcopy(s);by={l['id']:l for l in new['layers']};compiled={l['id']:l for l in before['layers']};expected=set();changes=req['changes']
 if not isinstance(changes,list) or not 1<=len(changes)<=32:raise ValueError('1–32 explicit changes required')
 for x in changes:
  if not isinstance(x,dict) or set(x)!={'layer','field','before','after'}:raise ValueError('explicit layer, field, before, after required')
  lid,k=x['layer'],x['field'];l=by.get(lid);c=compiled.get(lid)
  if not l or not c or l['kind']=='group' or k not in BOUNDS or k not in allowed(c) or (lid,k) in expected:raise ValueError('unsupported or duplicate direct-layer repair; edit complex source explicitly')
  if k not in l or track(c.get(k)) or l[k]!=x['before']:raise ValueError('field absent, animated or stale; edit owning motion recipe instead')
  v=number(x['after'],k);lo,hi=BOUNDS[k]
  if not lo<=v<=hi or v==l[k]:raise ValueError('invalid/no-op replacement')
  l[k]=v;expected.add((lid,k))
 after,_,_=build(new,src.resolve().parent);b={l['id']:l for l in before['layers']};a={l['id']:l for l in after['layers']}
 if list(a)!=list(b) or {k:v for k,v in before.items() if k!='layers'}!={k:v for k,v in after.items() if k!='layers'}:raise ValueError('compiled global structure changed')
 diff={(lid,k) for lid in a for k in set(a[lid])|set(b[lid]) if a[lid].get(k)!=b[lid].get(k)}
 if diff!=expected:raise ValueError('compiled change set differs from explicit request; dependent fields must be edited as a full revision')
 if sha(src)!=original:raise ValueError('source changed during repair')
 write(out,new);return {'source_sha256':original,'revision_sha256':sha(out),'changed':[list(x) for x in sorted(diff)],'reason':req['reason'],'next':'Start new session with revised source and unchanged creative/audio; render and compare. No review carried forward.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('request',type=Path);p.add_argument('output',type=Path);z=p.parse_args();print(json.dumps(repair(z.source,json.loads(z.request.read_text()),z.output),indent=2))
if __name__=='__main__':main()
