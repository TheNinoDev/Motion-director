#!/usr/bin/env python3
"""Validate evidence in a human-authored causal multi-object motion plan.

This cannot judge artistry or infer that a storyboard was actually rendered.
"""
import argparse
import json
from pathlib import Path


def validate(plan):
    scenes=plan.get('scenes')
    if not isinstance(scenes,list) or not scenes:
        raise ValueError('scenes must be a nonempty list')
    errors=[]
    previous_end=0.
    previous_received=None
    for i,s in enumerate(scenes):
        name=s.get('id') or f'scene {i+1}'
        a,b=s.get('start'),s.get('end')
        if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or a<0 or b<=a:
            errors.append(f'{name}: valid numeric start/end required')
            continue
        if abs(a-previous_end)>0.11:errors.append(f'{name}: timeline gap/overlap from previous scene')
        previous_end=b
        for k in ['visual_cause','primary_action','secondary_reaction','result','text_role']:
            if not isinstance(s.get(k),str) or len(s[k].strip())<12:
                errors.append(f'{name}: explain {k}, not a generic label')
        elements=s.get('elements',[])
        if not isinstance(elements,list) or not elements:
            errors.append(f'{name}: element relationships missing')
        else:
            ids=[x.get('id') for x in elements]
            if len(ids)!=len(set(ids)):
                errors.append(f'{name}: duplicate element IDs')
            if not any(x.get('role')=='actor' for x in elements):
                errors.append(f'{name}: no driving actor')
            if not any(x.get('responds_to') in ids and x.get('responds_to')!=x.get('id') for x in elements):
                errors.append(f'{name}: no related responding element; scene may be a single isolated slide')
        bridge=s.get('handoff',{})
        if i<len(scenes)-1:
            anchor=bridge.get('anchor')
            if not isinstance(anchor,str) or len(anchor.strip())<3:
                errors.append(f'{name}: successor has no handoff anchor')
            prep=bridge.get('preparation_start')
            if not isinstance(prep,(int,float)) or not a<=prep<b:
                errors.append(f'{name}: successor not prepared before end')
            if not isinstance(bridge.get('forward_action'),str) or len(bridge['forward_action'].strip())<12:
                errors.append(f'{name}: handoff has no forward action')
        if i>0 and (not isinstance(s.get('receives'),str) or s['receives']!=previous_received):
            # Stored value is a plan-level link to the earlier anchor, not visual proof.
            errors.append(f'{name}: does not explicitly receive previous handoff anchor')
        previous_received=bridge.get('anchor')
    return {'ok':not errors,'scenes':len(scenes),'errors':errors,
            'warning':'Schema checks narrative metadata only. Inspect actual moving film and transitions.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan',type=Path)
    args=p.parse_args()
    result=validate(json.loads(args.plan.read_text(encoding='utf8')))
    print(json.dumps(result,indent=2))
    if not result['ok']:
        raise SystemExit(2)


if __name__=='__main__': main()
