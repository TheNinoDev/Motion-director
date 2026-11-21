#!/usr/bin/env python3
"""Editorial WARNINGS for v71 shot-plans; never a replacement for video review.

JSON schema: {"shots":[{"id","start","end","layout","primary_action",
"components":[{"id","type","role"}],"assets":[{"id","type","role",
"attached_to"?}],"handoff"}]}.

Use component anchors for tiny support icons; standalone hero art is allowed only
when justified as the actual subject, but flagged for manual editorial review.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ICON_TYPES={'icon','svg-icon','emoji','pictogram','illustration','png-icon'}
PRIMARY_ROLES={'hero','main','subject','centerpiece','standalone','floating','independent'}
SUPPORT_ROLES={'button-icon','card-icon','badge-icon','toolbar-icon','tab-icon',
               'status-icon','inline-icon','secondary-icon','component-polish'}
GENERIC_LAYOUTS={'title-icon','headline-icon','icon-hero','center-sticker','icon-card','asset-slide'}
GENERIC_ACTIONS={'show','display','appear','fade-in','fade-out','hold','idle','float','pulse','zoom'}

def review(plan:dict)->dict:
    if not isinstance(plan,dict):raise ValueError('plan must be an object')
    shots=plan.get('shots')
    if not isinstance(shots,list) or not shots: raise ValueError('shots must be nonempty array')
    warnings=[]
    previous=None
    for i,shot in enumerate(shots):
        ident=str(shot.get('id') or f'shot-{i+1}')
        def warn(code,msg):warnings.append({'shot':ident,'code':code,'message':msg})
        if not isinstance(shot,dict): raise ValueError(f'shot {i+1} must be an object')
        comps=shot.get('components',[]);assets=shot.get('assets',[])
        if not isinstance(comps,list) or not isinstance(assets,list):raise ValueError('components/assets must be arrays')
        component_ids={str(c.get('id')) for c in comps if isinstance(c,dict)}
        support=0;standalone=0
        for asset in assets:
            if not isinstance(asset,dict):raise ValueError('assets must contain objects')
            if str(asset.get('type','')).lower() not in ICON_TYPES:continue
            role=str(asset.get('role','')).lower()
            anchor=asset.get('attached_to')
            if role in SUPPORT_ROLES:
                support+=1
                if not anchor or str(anchor) not in component_ids:
                    warn('orphan-polish',f"icon {asset.get('id','?')} is described as UI polish but is not attached to a real component")
            if role in PRIMARY_ROLES or (not anchor and role not in SUPPORT_ROLES):
                standalone+=1
                warn('standalone-icon',f"icon {asset.get('id','?')} acts as an independent subject; justify as story or make it a small attached UI detail")
        action=str(shot.get('primary_action','')).strip()
        tokens=re.findall(r'[a-zA-Z-]+',action.lower())
        if not action or tokens and tokens[0] in GENERIC_ACTIONS and len(tokens)<4:
            warn('weak-main-action','describe a visible edit action between components rather than merely displaying an icon')
        layout=str(shot.get('layout','')).lower().strip()
        if layout in GENERIC_LAYOUTS:
            warn('asset-slide-layout','layout is dominated by icon+headline instead of authored edit/composition')
        if previous:
            if layout in GENERIC_LAYOUTS and previous['layout'] in GENERIC_LAYOUTS:
                warn('repeated-asset-slides',f"adjacent scenes {previous['id']} and {ident} use the same asset-slide grammar")
            handoff=str(previous.get('handoff','')).strip().lower()
            if handoff in ('','none','instant switch','hard cut with no reason'):
                warn('unplanned-seam',f"previous shot {previous['id']} has no described transition or motivated direct cut")
        previous={'id':ident,'layout':layout,'handoff':shot.get('handoff','')}
    return {'shots_reviewed':len(shots),'warnings':warnings,'warning_count':len(warnings)}

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('plan',type=Path)
    ap.add_argument('--report',type=Path)
    args=ap.parse_args()
    result=review(json.loads(args.plan.read_text(encoding='utf8')))
    report=json.dumps(result,indent=2,ensure_ascii=False)
    print(report)
    if args.report:args.report.write_text(report+'\n',encoding='utf8')
if __name__=='__main__': main()
