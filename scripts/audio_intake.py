#!/usr/bin/env python3
"""Check audio input files and declared permission state. Does not authenticate licenses or audition speech."""
import argparse,json,subprocess,sys,math
from pathlib import Path

def probe(path):
    r=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True,timeout=60,check=True)
    d=json.loads(r.stdout); a=next((s for s in d.get('streams',[]) if s.get('codec_type')=='audio'),None)
    if not a: raise ValueError('no audio stream')
    dur=float(a.get('duration') or d.get('format',{}).get('duration') or 0)
    if not math.isfinite(dur) or dur<=0: raise ValueError('invalid duration')
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-map','0:a:0','-f','null','-'],capture_output=True,check=True,timeout=180)
    return {'duration_seconds':dur,'codec':a.get('codec_name'),'sample_rate':a.get('sample_rate')}

def validate(data, root, stage):
    errors=[]; warnings=[]; reports={}; scope=data.get('use_scope')
    if scope not in {'commercial','personal-public','private-preview'}: errors.append('Choose use_scope before song research')
    if stage=='release' and scope=='private-preview': errors.append('Private preview is not public-release-ready')
    for kind in ('voice','music'):
        obj=data.get(kind,{})
        if obj.get('waived') is True:
            if not obj.get('waiver_reason'): errors.append(f'{kind}: explicit waiver reason required')
            continue
        p=obj.get('path')
        if not isinstance(p,str) or not p.strip(): errors.append(f'{kind}: actual local audio file required'); continue
        path=(root/p).resolve()
        if not path.is_file(): errors.append(f'{kind}: file not found'); continue
        try: reports[kind]=probe(path)
        except (OSError,ValueError,subprocess.SubprocessError) as e: errors.append(f'{kind}: decode/probe failed: {e}'); continue
        state=obj.get('rights_status')
        if state!='cleared' or not str(obj.get('rights_evidence','')).strip():
            (errors if stage=='release' else warnings).append(f'{kind}: rights unverified; preview only until cleared')
    if stage=='release' and not data.get('platforms'): errors.append('Release destination platforms required')
    return {'ready':not errors,'stage':stage,'errors':errors,'warnings':warnings,'media':reports,'note':'File and declared status checks only; human/agent audio audition and rights review remain necessary.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('--root',type=Path);p.add_argument('--stage',choices=['edit','release'],default='edit');a=p.parse_args()
    try: result=validate(json.loads(a.manifest.read_text(encoding='utf-8')),a.root or a.manifest.parent,a.stage)
    except (OSError,ValueError,TypeError,AttributeError) as e:p.exit(1,str(e)+'\n')
    print(json.dumps(result,indent=2));sys.exit(not result['ready'])
