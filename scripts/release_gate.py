#!/usr/bin/env python3
"""Fail-closed release check. Manual editorial evidence cannot be replaced by this script."""
import argparse,json,sys,math
from pathlib import Path
from check_render import check
REQUIRED=('claims_verified','visual_review','voice_and_mix_audition','script_audio_match','no_placeholders','mobile_readability','rights_review')
def gate(manifest):
    m=json.loads(manifest.read_text(encoding='utf-8')); errors=[];checks=m.get('checks',{});evidence=m.get('evidence',{})
    for k in REQUIRED:
        if checks.get(k)!='pass' or not isinstance(evidence.get(k),str) or not evidence[k].strip():errors.append(f'{k}: missing verified pass and evidence')
    if m.get('blockers'):errors.append('Unresolved blockers')
    try:
        video=(manifest.parent/m['video']).resolve(); dur=float(m['duration_seconds']);fps=float(m['fps']);w=int(m['width']);h=int(m['height'])
        if not math.isfinite(dur) or dur<=0 or not math.isfinite(fps) or fps<=0 or w<=0 or h<=0:raise ValueError('invalid target video properties')
        report=check(video,w,h,fps,dur,m.get('audio_required',True),True,False)
        errors.extend(report.get('errors',[]))
        streams=report.get('metadata',{}).get('streams',[]);v=next((s for s in streams if s.get('codec_type')=='video'),{});a=next((s for s in streams if s.get('codec_type')=='audio'),{})
        if v.get('codec_name')!='h264' or v.get('pix_fmt')!='yuv420p':errors.append('Default release requires H.264 yuv420p')
        if m.get('audio_required',True) and a.get('codec_name')!='aac':errors.append('Default release requires AAC audio')
    except (OSError,KeyError,ValueError) as ex:errors.append(str(ex));report={}
    return {'release_ready':not errors,'errors':errors,'technical_report':report,'note':'Editorial evidence supplied by agent, not independently authenticated. Do not fake evidence.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('-o','--output',type=Path);a=p.parse_args()
    try:r=gate(a.manifest)
    except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')
    s=json.dumps(r,indent=2)+'\n'
    if a.output:a.output.write_text(s,encoding='utf-8')
    else:print(s,end='')
    sys.exit(not r['release_ready'])
