#!/usr/bin/env python3
"""Executable production contract. Technical gates never imply aesthetic approval."""
import argparse,json,subprocess,sys,math
from pathlib import Path
from fractions import Fraction
from director_v39 import build
from director_v38 import diagnose
from creative_gate import assess
from agent_session import sha,write,inputs,review,verify,ROOT
from compositor import validate,val

def snapshot(plan,p):
 result=inputs(plan,p)
 for l in p['layers']:
  if l['kind']=='mesh' and l.get('mesh',{}).get('src'):
   f=(plan.resolve().parent/l['mesh']['src']).resolve();result[str(f)]=sha(f)
 return result

def bind(creative,p):
 report=assess(creative);errors=list(report['errors']);notes=list(report['advice']);by={l['id']:l for l in p['layers']}
 if isinstance(creative,dict) and isinstance(creative.get('duration'),(int,float)) and abs(creative['duration']-p['duration'])>1/p['fps']/2:errors.append('creative and picture durations differ')
 if report['structure_valid']:
  for i,b in enumerate(creative['beats']):
   ids=b.get('layer_ids',[])
   if not isinstance(ids,list) or not ids or any(not isinstance(k,str) or k not in by for k in ids):errors.append(f'beat {i}: layer_ids must refer to existing layers');continue
   if not any(by[k]['active'][0]<b['end'] and by[k]['active'][1]>b['start'] for k in ids):errors.append(f'beat {i}: no linked layer active during beat')
   if b.get('proof_id') and not any(by[k]['kind'] in ('image','mesh') for k in ids):notes.append(f'beat {i}: verify real evidence rendered; no image or mesh layer linked')
 return {'valid':not errors,'errors':errors,'advice':notes,'note':'Layer/time linkage only, not verification of evidence or visual quality.'}

def start(spec,creative,work,audio=None):
 if work.exists():raise ValueError('choose a new work directory')
 p,s,notes=build(json.loads(spec.read_text()),spec.resolve().parent);c=json.loads(creative.read_text());check=bind(c,p)
 if not check['valid']:raise ValueError('; '.join(check['errors']))
 if audio is not None and not audio.is_file():raise ValueError('audio missing')
 work.mkdir(parents=True);plan=work/'plan.json';write(plan,p);write(work/'expanded.json',s);write(work/'creative.json',c)
 cmd={};renderer=ROOT/'starter/composite_film/compositor.py';mode=c['mode'];auditable=mode!='advertisement' or audio is not None
 for k,size,profile in [('preview',540,'preview'),('upload',1080,'high'),('master',1080,'lossless')]:
  if k!='preview' and not auditable:continue
  cmd[k]=[sys.executable,str(renderer),str(plan.resolve()),str((work/k).resolve()),'--size',str(size),'--profile',profile,'--backend','auto']+(['--audio',str(audio.resolve())] if audio else [])
 cmd['check_inputs']=[sys.executable,str(Path(__file__).resolve()),'verify-inputs',str(work.resolve())]
 cmd['review']=[sys.executable,str(ROOT/'scripts/agent_session.py'),'review',str(plan.resolve()),str((work/'review').resolve())]
 cmd['verify_review']=[sys.executable,str(ROOT/'scripts/agent_session.py'),'verify',str(plan.resolve()),str((work/'review').resolve())]
 for k in ('preview','upload','master'):
  if k in cmd:cmd['check_'+k]=[sys.executable,str(Path(__file__).resolve()),'verify-video',str(plan.resolve()),str((work/k/'film.mp4').resolve()),'--width',str(540 if k=='preview' else 1080),*(['--require-audio'] if audio or mode=='advertisement' else [])]
 state={'mode':mode,'source':str(spec.resolve()),'source_sha256':sha(spec),'creative_sha256':sha(work/'creative.json'),'inputs':snapshot(plan,p),'audio':{'path':str(audio.resolve()),'sha256':sha(audio)} if audio else None,'binding':check,'diagnostics':diagnose(p),'notes':notes,'commands_argv':cmd,'blocked':['Final export needs authorized actual audio'] if not auditable else [],'next':'Render review, personally inspect and repair, render preview, inspect playback/audio, verify final export visually and technically. Automatic gates are not aesthetic approval.'};write(work/'production.json',state);return state

def verify_inputs(work):
 state=json.loads((work/'production.json').read_text());errs=[]
 checks={**state['inputs'],state['source']:state['source_sha256'],str((work/'creative.json').resolve()):state['creative_sha256']}
 if state['audio']:checks[state['audio']['path']]=state['audio']['sha256']
 for name,digest in checks.items():
  f=Path(name)
  if not f.is_file() or sha(f)!=digest:errs.append('missing or changed: '+name)
 return {'inputs_valid':not errs,'errors':errs,'files_checked':len(checks),'note':'Recorded explicit inputs only; does not fingerprint system fonts or renderer code.'}

def verify_video(plan,video,width,require_audio=False):
 p=json.loads(plan.read_text());validate(p,plan.resolve().parent)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],text=True));v=[s for s in probe['streams'] if s['codec_type']=='video'];a=[s for s in probe['streams'] if s['codec_type']=='audio'];err=[]
 if len(v)!=1:err.append('expected exactly one video track')
 else:
  s=v[0];n=round(p['duration']*p['fps']);height=round(width*16/9/2)*2
  if (s['width'],s['height'])!=(width,height):err.append('resolution differs')
  if Fraction(s['avg_frame_rate'])!=p['fps']:err.append('fps differs')
  if s.get('nb_read_frames')!=str(n):err.append('decoded frame count differs')
  if abs(float(s.get('duration',0))-n/p['fps'])>1/p['fps']+.001:err.append('picture duration differs')
 if require_audio and not a:err.append('missing audio stream')
 if require_audio and a and abs(float(a[0].get('duration',0))-round(p['duration']*p['fps'])/p['fps'])>.15:err.append('audio duration differs')
 dec=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-map','0:v:0','-map','0:a?','-f','null','-'],capture_output=True)
 if dec.returncode:err.append('decode error')
 return {'technical_valid':not err,'errors':err,'video_sha256':sha(video),'video_tracks':len(v),'audio_tracks':len(a),'frames':v[0].get('nb_read_frames') if v else None,'note':'No proof of audio intelligibility, music rights, creative quality, or connection to a particular rendered plan.'}

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);c=sub.add_parser('start');c.add_argument('spec',type=Path);c.add_argument('creative',type=Path);c.add_argument('work',type=Path);c.add_argument('--audio',type=Path);c=sub.add_parser('verify-video');c.add_argument('plan',type=Path);c.add_argument('video',type=Path);c.add_argument('--width',type=int,default=1080);c.add_argument('--require-audio',action='store_true');c=sub.add_parser('verify-inputs');c.add_argument('work',type=Path);x=ap.parse_args();r=start(x.spec,x.creative,x.work,x.audio) if x.cmd=='start' else verify_inputs(x.work) if x.cmd=='verify-inputs' else verify_video(x.plan,x.video,x.width,x.require_audio);print(json.dumps(r,indent=2));raise SystemExit(2 if x.cmd!='start' and not r.get('technical_valid',r.get('inputs_valid',False)) else 0)
if __name__=='__main__':main()
