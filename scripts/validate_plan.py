#!/usr/bin/env python3
"""Validate scene coverage and essential inputs. Does not verify artistic quality or semantic accuracy."""
import argparse, json, math, sys
from pathlib import Path

def validate(plan, root=None):
    errors=[]; warnings=[]
    f=plan.get('format',{});fps=f.get('fps',0);duration=plan.get('duration',0)
    if not isinstance(fps,(int,float)) or fps<=0: return ['Invalid fps'],warnings
    if not isinstance(duration,(int,float)) or not math.isfinite(duration) or duration<=0: return ['Invalid duration'],warnings
    for k in ('width','height'):
        if not isinstance(f.get(k),int) or f[k]<=0 or f[k]%2: errors.append(f'Invalid/even-required {k}')
    tol=1/fps+1e-6;inp=plan.get('inputs',{})
    for key,waiver in [('script','voiceover_waived'),('music','music_waived'),('voiceover','voiceover_waived')]:
        if waiver and inp.get(waiver) is True: continue
        value=inp.get(key)
        if not isinstance(value,str) or not value.strip(): errors.append(f'Missing {key}')
        elif root and not (root/value).is_file(): errors.append(f'Missing file: {value}')
    if plan.get('version',1)>=2:
        c=plan.get('concept',{})
        for k in ('main_message','hook_family','payoff','main_cta'):
            if not c.get(k): errors.append(f'Missing concept {k}')
        if len(c.get('supporting_features',[]))>2 and not c.get('scope_override_reason'): errors.append('Feature scope too broad without explicit reason')
    prev=0;ids=set();families=[]
    scenes=plan.get('scenes',[])
    if not scenes: errors.append('No scenes')
    for s in scenes:
        sid=s.get('id')
        if not sid or sid in ids: errors.append(f'Missing or duplicate scene ID: {sid}')
        ids.add(sid);start=s.get('start');end=s.get('end')
        if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in (start,end)) or start<0 or end<=start: errors.append(f'{sid}: invalid interval'); continue
        if abs(start-prev)>tol: errors.append(f'{sid}: scene gap/overlap {start-prev:.3f}s')
        if end>duration+tol: errors.append(f'{sid}: exceeds duration')
        prev=end
        for k in ('family','message','focus','entry','development','exit','bridge','audio_cue'):
            if not s.get(k): errors.append(f'{sid}: missing {k}')
        if plan.get('version',1)>=2:
            for k in ('anchor_in','anchor_out'):
                anchor=s.get(k)
                if not isinstance(anchor,list) or len(anchor)!=2 or not all(isinstance(x,(int,float)) and math.isfinite(x) and 0<=x<=1 for x in anchor): errors.append(f'{sid}: invalid normalized {k}')
            if not s.get('motion_roles',{}).get('primary'): errors.append(f'{sid}: missing primary motion role')
        families.append(s.get('family'))
    if abs(prev-duration)>tol: errors.append('Scene coverage does not match duration')
    if len(families)>=4 and len(set(families))<3: warnings.append('Low scene-family variety; assess creative intent')
    if not plan.get('audio',{}).get('alignment_method'): warnings.append('No documented alignment method')
    if not inp.get('music_waived') and not plan.get('audio',{}).get('music_onsets_verified'): warnings.append('Music onset sync unverified')
    return errors,warnings

def main():
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('--root',type=Path,help='Check input paths relative to project root');a=p.parse_args()
    try: errors,warnings=validate(json.loads(a.plan.read_text(encoding='utf-8')),a.root)
    except (OSError,ValueError,TypeError,AttributeError) as e: p.exit(1,f'Invalid plan: {e}\n')
    print(json.dumps({'valid':not errors,'errors':errors,'warnings':warnings},indent=2));sys.exit(bool(errors))
if __name__=='__main__': main()
