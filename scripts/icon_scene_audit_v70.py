#!/usr/bin/env python3
"""Editorial icon-shot check. Warnings are for review, never a creativity score."""
import argparse,json
from pathlib import Path

ROLES={'hero','cause','target','consequence','context','bridge','decoration'}
def audit(doc):
    issues=[];facts=[];solo=[]
    shots=doc.get('shots',[])
    if not shots:return {'errors':['shot plan needs shots'],'warnings':[],'facts':[]}
    prev=None
    for i,s in enumerate(shots):
        sid=s.get('id',f'shot-{i}');actors=s.get('assets',[]);rels=s.get('relationships',[])
        ids={a.get('id') for a in actors}
        meaningful=[a for a in actors if a.get('role')!='decoration']
        if any(a.get('role') not in ROLES for a in actors):issues.append(sid+': invalid role')
        if len(ids)!=len(actors):issues.append(sid+': duplicate ids')
        if not any(a.get('role')=='hero' for a in meaningful):issues.append(sid+': missing hero')
        if any(r.get('from') not in ids or r.get('to') not in ids or r.get('from')==r.get('to') or not r.get('verb') for r in rels):issues.append(sid+': invalid interaction')
        if len(meaningful)>=2 and not rels:issues.append(sid+': multiple unrelated icons — possible sticker row')
        if len(meaningful)==1 and not rels:solo.append(sid)
        else:
            if len(solo)>=3:issues.append('three isolated-icon shots in sequence: '+', '.join(solo))
            solo=[]
        if prev and prev.get('bridge_actor') and prev['bridge_actor'] not in ids:issues.append(sid+': preceding bridge actor absent — check if deliberate cut')
        facts.append({'shot':sid,'actors':len(meaningful),'relations':len(rels)})
        prev=s
    if len(solo)>=3:issues.append('three isolated-icon shots in sequence: '+', '.join(solo))
    return {'errors':[],'warnings':issues,'facts':facts}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('plan');a=p.parse_args()
    print(json.dumps(audit(json.loads(Path(a.plan).read_text(encoding='utf-8'))),indent=2))
