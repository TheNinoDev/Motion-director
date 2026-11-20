#!/usr/bin/env python3
"""Validate brief structure and explicit production gates, not truth or artistic quality."""
import argparse,json,sys
from pathlib import Path

def validate(b, production=False, root=None):
    errors=[]; warnings=[]
    def need(condition,message):
        if not condition: errors.append(message)
    need(b.get('source_mode') in {'local-project','source-copy','url','html','user-info','mixed','screenshots'},'Choose a supported source mode')
    src=b.get('sources',[]); features=b.get('features',[])
    need(bool(src),'At least one source required')
    source_ids=[s.get('id') for s in src]; feature_ids=[f.get('id') for f in features]
    need(all(source_ids) and len(set(source_ids))==len(source_ids),'Source IDs must be unique/nonempty')
    need(all(feature_ids) and len(set(feature_ids))==len(feature_ids),'Feature IDs must be unique/nonempty')
    for s in src: need(bool(s.get('locator')),f"{s.get('id')}: source locator required")
    by_id={f.get('id'):f for f in features}
    for f in features:
        fid=f.get('id'); state=f.get('state')
        need(bool(f.get('claim')),f'{fid}: claim required')
        need(state in {'live-confirmed','source-only','user-asserted','planned','unknown'},f'{fid}: invalid state')
        need(bool(f.get('source_ids')) and set(f.get('source_ids',[]))<=set(source_ids),f'{fid}: missing/unknown source IDs')
        if state in {'planned','unknown'} and f.get('public_claim_allowed'): errors.append(f'{fid}: planned/unknown feature not allowed as current public claim')
    a=b.get('selected_angle',{}); script=b.get('script',{}); music=b.get('music',{})
    for k in ('title','main_message','cta'): need(bool(a.get(k)),f'Angle missing {k}')
    supporting=a.get('supporting_features',[]); selected=([a['main_feature']] if a.get('main_feature') else [])+supporting
    need(len(supporting)<=2 or bool(a.get('scope_override_reason')),'More than 2 supporting features needs a reason')
    need(len(set(selected))==len(selected),'Duplicate feature in angle')
    need(set(selected)<=set(feature_ids),'Angle uses unknown feature IDs')
    need(set(script.get('claim_ids',[]))<=set(selected),'Script claim IDs outside selected scope')
    if production:
        need(script.get('status') in {'final','waived'},'Final script or explicit no-VO waiver required')
        if script.get('status')=='final':
            need(bool(script.get('path')),'Missing script path')
            if root and script.get('path'): need((root/script['path']).is_file(),'Missing actual script file')
        for fid in script.get('claim_ids',[]): need(by_id.get(fid,{}).get('public_claim_allowed') is True,f'{fid}: not permitted as public claim')
        if not music.get('waived'):
            need(bool(music.get('path')),'Actual soundtrack path required (delegation alone does not mean file exists)')
            if root and music.get('path'): need((root/music['path']).is_file(),'Missing actual soundtrack file')
        if not script.get('claim_ids'): warnings.append('No script claim IDs; confirm no unsupported claims')
    if not b.get('audience'): warnings.append('Audience unspecified')
    return errors,warnings

def main():
    p=argparse.ArgumentParser();p.add_argument('brief',type=Path);p.add_argument('--production',action='store_true');p.add_argument('--root',type=Path);a=p.parse_args()
    try: e,w=validate(json.loads(a.brief.read_text(encoding='utf-8')),a.production,a.root)
    except (OSError,ValueError,TypeError,AttributeError,KeyError) as ex: p.exit(1,f'Invalid brief: {ex}\n')
    print(json.dumps({'valid':not e,'errors':e,'warnings':w},indent=2));sys.exit(bool(e))
if __name__=='__main__': main()
