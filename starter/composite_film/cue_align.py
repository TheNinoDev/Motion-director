"""Non-destructive retiming of explicitly selected independent visual accents.
Measured peaks are candidates, not certified musical beats. Never moves speech.
"""
import argparse, copy, json, math
from pathlib import Path
from compositor import validate, KEYS

def align(plan,cues,bindings,window=.09):
    if not 0<=window<=.2:raise ValueError('window must be 0..0.2 seconds')
    p=copy.deepcopy(plan);lookup={x['id']:x for x in p['layers']}; report=[];used=set();fps=p['fps']
    for b in bindings:
        ids=b['layers'];t=float(b['anchor']); members=set(ids)
        if not ids or len(ids)!=len(members) or used & members:raise ValueError('binding layers must be unique')
        if not all(i in lookup for i in ids):raise ValueError('unknown layer')
        for l in p['layers']:
            if l['id'] not in members and (l.get('parent') in members or l.get('matte') in members):raise ValueError('include dependent layers')
            if l['id'] in members and (l.get('parent') and l['parent'] not in members or l.get('matte') and l['matte'] not in members):raise ValueError('include parent and matte in binding')
        used.update(members)
        candidates=[x for x in cues if abs(x['time']-t)<=window and x.get('strength',0)>=.35]
        chosen=min(candidates,key=lambda x:abs(x['time']-t)-.035*x['strength']) if candidates else None
        a=round(t*fps)/fps; target=round(chosen['time']*fps)/fps if chosen else a; dt=target-a
        if abs(dt)>window or any(lookup[i]['active'][0]+dt<0 or lookup[i]['active'][1]+dt>p['duration']+.000001 for i in ids):dt=0
        for i in ids:
            l=lookup[i];l['active']=[round(v+dt,6) for v in l['active']]
            for k,v in l.items():
                if (k in KEYS or k=='points_keyframes') and isinstance(v,list) and v and isinstance(v[0],list):
                    for item in v:item[0]=round(item[0]+dt,6)
        # Existing sound events remain locked, unless explicitly named by index.
        for idx in b.get('sound_indices',[]):
            if not 0<=idx<len(p.get('sound_events',[])):raise ValueError('bad sound index')
            e=p['sound_events'][idx];q=e['time']+dt
            if not 0<=q<p['duration']:raise ValueError('sound outside picture')
            e['time']=round(q,6)
        report.append({'layers':ids,'anchor':t,'candidate':chosen,'shift_seconds':round(dt,6)})
    return p,report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('plan',type=Path);a.add_argument('cues',type=Path);a.add_argument('bindings',type=Path);a.add_argument('output',type=Path);a.add_argument('--window',type=float,default=.09);args=a.parse_args()
    if args.output.resolve()==args.plan.resolve() or args.output.resolve().parent!=args.plan.resolve().parent:raise ValueError('write a new plan beside original to keep asset paths valid')
    p,r=align(json.loads(args.plan.read_text()),json.loads(args.cues.read_text())['cues'],json.loads(args.bindings.read_text()),args.window);validate(p,args.plan.parent);args.output.write_text(json.dumps(p,indent=2));args.output.with_suffix('.alignment.json').write_text(json.dumps(r,indent=2))
