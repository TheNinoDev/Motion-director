#!/usr/bin/env python3
"""V75: validate declared scene-layer ownership & layout before render.

No OCR, no false claims about actual pixels. Input uses normalized 0..1 boxes.
Keeps legitimate designed overlaps by requiring a scoped per-pair justification.
"""
import argparse
import json
import math
from pathlib import Path
from itertools import combinations

TEXT_ROLES={'headline','title','caption','label','button-label'}
IMPORTANT_ROLES=TEXT_ROLES|{'connector','control','key-ui','foreground'}

def _num(x):return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x)
def _box(obj,t):
    frames=obj.get('boxes',[])
    if frames:
        if not isinstance(frames,list):return None
        frames=sorted(frames,key=lambda f:f.get('t',0))
        if t<=frames[0].get('t',0):return frames[0].get('box')
        if t>=frames[-1].get('t',0):return frames[-1].get('box')
        for a,b in zip(frames,frames[1:]):
            if a['t']<=t<=b['t']:
                u=(t-a['t'])/(b['t']-a['t']) if b['t']!=a['t'] else 0
                return [x+(y-x)*u for x,y in zip(a['box'],b['box'])]
    return obj.get('box')

def _collides(a,b,pad=.002):
    if not a or not b:return False
    x,y,w,h=a;X,Y,W,H=b
    return min(x+w,X+W)-max(x,X)>pad and min(y+h,Y+H)-max(y,Y)>pad

def analyze(plan,dt=.1):
    errors=[];warnings=[];summary={'pair_checks':0,'scene_count':0,'layer_count':0}
    scenes=plan.get('scenes',[]); layers=plan.get('layers',[])
    if not scenes or not layers:return {'errors':['Scenes and layers required.'],'warnings':[],**summary}
    if not _num(plan.get('duration')) or plan['duration']<=0:
        errors.append('Invalid duration.');return {'errors':errors,'warnings':[],**summary}
    duration=plan['duration']; summary['scene_count']=len(scenes);summary['layer_count']=len(layers)
    scene_by_id={s.get('id'):s for s in scenes}
    layer_by_id={x.get('id'):x for x in layers}
    if len(scene_by_id)!=len(scenes) or len(layer_by_id)!=len(layers):errors.append('Duplicate scene/layer ID.')
    for s in scenes:
        if not all(_num(s.get(k)) for k in ('start','end')) or not (0<=s['start']<s['end']<=duration):errors.append('Invalid scene interval '+str(s.get('id')))
    for l in layers:
        lid=l.get('id')
        if not all(_num(l.get(k)) for k in ('start','end')) or not (0<=l['start']<l['end']<=duration):
            errors.append('Invalid layer interval '+str(lid));continue
        if l.get('owner') not in scene_by_id:errors.append('Unknown owner for '+str(lid))
        if l.get('role') not in (TEXT_ROLES|IMPORTANT_ROLES|{'hero','support','background','effect','bridge','annotation'}):warnings.append('Unrecognized role '+str(lid))
        if not l.get('exit'):
            errors.append('Missing explicit exit for '+str(lid))
        elif l['exit'] not in ('remove','transform','handoff','mask','dissolve','despawn'):
            errors.append('Invalid exit for '+str(lid))
        for b in [l.get('box')]+[f.get('box') for f in l.get('boxes',[])]:
            if b is None:continue
            if len(b)!=4 or not all(_num(v) for v in b) or b[2]<=0 or b[3]<=0:
                errors.append('Invalid box for '+str(lid));continue
            if (l.get('role') in IMPORTANT_ROLES) and (min(b[:2])<-.02 or b[0]+b[2]>1.02 or b[1]+b[3]>1.02):
                warnings.append('Important layer off-canvas: '+str(lid))
        for f in l.get('boxes',[]):
            if not _num(f.get('t')) or f['t']<l['start']-.0001 or f['t']>l['end']+.0001:errors.append('Invalid keyframe for '+str(lid))
        owner=scene_by_id.get(l.get('owner'))
        if owner and l['end']>owner['end']+.12:
            if l.get('exit')!='handoff' or not l.get('handoff_to'):
                errors.append(f'Stale cross-scene layer: {lid} persists past {l["owner"]} without handoff')
            elif l['handoff_to'] not in scene_by_id:
                errors.append(f'Unknown handoff scene for {lid}')
        if l.get('exit')=='handoff' and not l.get('handoff_to'):
            errors.append(f'Handoff requires destination: {lid}')
    allow={tuple(sorted([a.get('a'),a.get('b')])):a for a in plan.get('intentional_overlaps',[])}
    for pair, rule in allow.items():
        if len(pair)!=2 or any(x not in layer_by_id for x in pair):errors.append('Invalid overlap rule '+str(pair))
        if not rule.get('reason') or len(rule['reason'].strip())<12:errors.append('Overlap must explain purpose '+str(pair))
        if not all(_num(rule.get(k)) for k in ('start','end')) or rule['start']>=rule['end']:errors.append('Overlap rule missing valid time '+str(pair))
    flagged_pairs=set()
    n=int(math.ceil(duration/dt))
    for i in range(n+1):
        t=min(duration,round(i*dt,6));active=[l for l in layers if l.get('box') or l.get('boxes') if isinstance(l.get('start'),(int,float)) and l['start']<=t<l.get('end',0)]
        # Only critical pair combinations should be promoted; background/hero occlusion is not automatically wrong.
        for a,b in combinations(active,2):
            pair=tuple(sorted([a['id'],b['id']]))
            kinds={a.get('role'),b.get('role')}
            if not (kinds & TEXT_ROLES and (kinds & {'connector','title','headline','caption','label','button-label','control','key-ui'})):
                continue
            summary['pair_checks']+=1
            if not _collides(_box(a,t),_box(b,t)):continue
            allowed=allow.get(pair)
            if allowed and allowed.get('start',duration+1)<=t<=allowed.get('end',-1):continue
            if pair not in flagged_pairs:
                flagged_pairs.add(pair)
                errors.append(f'Unjustified text/UI collision at {t:.2f}s: {pair[0]} vs {pair[1]}')
    for triple in zip(scenes,scenes[1:],scenes[2:]):
        vals=[x.get('composition_signature','') for x in triple]
        if vals[0] and len(set(vals))==1:warnings.append(f'Repeated scene composition through {triple[0]["id"]}..{triple[2]["id"]}')
    return {'errors':list(dict.fromkeys(errors)),'warnings':list(dict.fromkeys(warnings)),**summary}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan');p.add_argument('--report');p.add_argument('--sample-step',type=float,default=.1)
    args=p.parse_args()
    if not 0<args.sample_step<=.5:p.error('sample step must be (0,0.5]')
    result=analyze(json.loads(Path(args.plan).read_text('utf-8')),args.sample_step)
    payload=json.dumps(result,indent=2,ensure_ascii=False)
    print(payload)
    if args.report:Path(args.report).write_text(payload+'\n',encoding='utf-8')
    raise SystemExit(1 if result['errors'] else 0)
if __name__=='__main__': main()
