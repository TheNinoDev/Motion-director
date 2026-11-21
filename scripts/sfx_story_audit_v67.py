#!/usr/bin/env python3
"""Review intended visual-event / SFX correspondence; optionally export native renderer cues.

This is a PLAN audit, not a perceptual audio assessment. Does not count SFX from mixed video.
"""
import argparse
import json
import math
from pathlib import Path

KINDS={'click','impact','whoosh','chime','riser','drop','snap','paper','brush','tick','rattle','glint','glitch','sweep','pulse'}
ROLES={'accent','prelap','tail','silence'}
KINDS_OF_EVENT={'contact','change','bridge','build','payoff','read','hold'}

def finite_num(value):
    return type(value) in (float,int) and math.isfinite(value)

def audit(doc):
    errors=[];warnings=[];events=doc.get('visual_events')
    duration=doc.get('duration');fps=doc.get('fps',30)
    if not finite_num(duration) or not .5<=duration<=600:
        errors.append('duration must be between 0.5 and 600 seconds')
        return {'ok':False,'errors':errors,'warnings':warnings,'render_plan':None}
    if type(fps)!=int or not 1<=fps<=60:
        errors.append('fps must be integer 1–60')
        return {'ok':False,'errors':errors,'warnings':warnings,'render_plan':None}
    if not isinstance(events,list) or not events:
        errors.append('visual_events must be a nonempty list')
        return {'ok':False,'errors':errors,'warnings':warnings,'render_plan':None}
    timeline=round(duration*fps)
    ids=set();cues=[];used={};counts={'scored':0,'silent':0,'unscored':0}
    for i,e in enumerate(events):
        at=e.get('at');id=str(e.get('id','')).strip();kind=e.get('event');role=e.get('audio_role')
        if not id or id in ids:errors.append(f'event {i}: missing/duplicate id')
        ids.add(id)
        if not finite_num(at) or not 0<=at<duration:
            errors.append(f'{id}: invalid at');continue
        if kind not in KINDS_OF_EVENT:errors.append(f'{id}: invalid event type')
        if role not in ROLES:errors.append(f'{id}: invalid audio_role')
        if not str(e.get('visual_change','')).strip():errors.append(f'{id}: visual_change required')
        sounds=e.get('sounds',[])
        if role=='silence':
            counts['silent']+=1
            if sounds:errors.append(f'{id}: silence must not include sounds')
            if len(str(e.get('reason','')).strip())<12:errors.append(f'{id}: intentional silence requires reason')
            continue
        if not isinstance(sounds,list) or (role in ROLES-{'silence'} and not sounds):
            counts['unscored']+=1;errors.append(f'{id}: scored events need sounds');continue
        if len(sounds)>4:warnings.append(f'{id}: more than 4 layered sounds; inspect masking/clutter')
        counts['scored']+=1
        for j,s in enumerate(sounds):
            which=s.get('kind'); t=s.get('at',at); dur=s.get('duration',.2);gain=s.get('gain_db',-19);pan=s.get('pan',0)
            if which not in KINDS:errors.append(f'{id}: unknown sound kind {which!r}');continue
            if any(not finite_num(v) for v in (t,dur,gain,pan)):
                errors.append(f'{id}: sound values must be finite numbers');continue
            if not 0<=t<duration or not .01<=dur<=4 or t+dur>duration+.001:
                errors.append(f'{id}: sound outside timeline');continue
            if not -45<=gain<=-3 or not -1<=pan<=1:errors.append(f'{id}: gain/pan out of bounds');continue
            frame=round(t*fps);frame=min(frame,timeline-1)
            n=max(1,round(dur*fps));n=min(n,timeline-frame)
            if n>fps*4:n=fps*4
            cues.append({'frame':frame,'duration_frames':n,'kind':which,'gain_db':gain,'pan':pan})
            used[which]=used.get(which,0)+1
            if gain>-11:warnings.append(f'{id}: loud synthetic accent ({gain} dB); check VO/headroom')
            # Score each *event* prelap/tail below, not every individual layered cue.
        if role=='prelap' and sounds and all(finite_num(s.get('at',at)) and s.get('at',at)>=at for s in sounds):
            warnings.append(f'{id}: prelap cue should normally begin before visual cut')
        if role=='tail' and sounds and all(finite_num(s.get('at',at)) and finite_num(s.get('duration',.2)) and s.get('at',at)+s.get('duration',.2)<=at for s in sounds):
            warnings.append(f'{id}: tail cue should normally ring after visual change')
    if len(events)>=7 and len(used)<3:warnings.append('few sonic materials across many visual events: audition whether variety is warranted')
    if used and max(used.values())>=max(5,int(len(cues)*.70)):
        warnings.append('same sound kind dominates cue map: check for generic template SFX')
    # Intended silence counts and report do not mandate effect quantity.
    cues.sort(key=lambda x:x['frame'])
    return {'ok':not errors,'errors':errors,'warnings':warnings,'summary':{
        'visual_events':len(events),'scored_events':counts['scored'],'intentional_silences':counts['silent'],
        'unscored_events':counts['unscored'],'sound_cues':len(cues),'different_families':len(used),
        'family_counts':used,'note':'Planning metadata only; never evidence of actual audible SFX or quality.'},
        'render_plan':{'fps':fps,'frames':timeline,'seed':doc.get('seed',671),'events':cues}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan',type=Path)
    p.add_argument('--report',type=Path)
    p.add_argument('--render-plan',type=Path,help='Write compatible starter/sound_design/render.py JSON')
    a=p.parse_args();r=audit(json.loads(a.plan.read_text(encoding='utf-8')))
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps({k:v for k,v in r.items() if k!='render_plan'},indent=2)+'\n',encoding='utf8')
    if a.render_plan and r['ok']:
        a.render_plan.parent.mkdir(parents=True,exist_ok=True)
        a.render_plan.write_text(json.dumps(r['render_plan'],indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in r.items() if k!='render_plan'},indent=2))
    return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
