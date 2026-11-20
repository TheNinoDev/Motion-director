#!/usr/bin/env python3
"""Run staged local production; hash real artifacts and require explicit review decisions."""
import argparse,json,subprocess,sys
from pathlib import Path
from director_v40 import build
from production_v39 import bind,snapshot,verify_inputs,verify_video
from agent_session import sha,write,ROOT
from motion_audit_v40 import audit

def start(spec,creative,work,audio=None,*,builder=build):
 if work.exists():raise ValueError('use a new work directory')
 p,e,notes=builder(json.loads(spec.read_text()),spec.resolve().parent);c=json.loads(creative.read_text());b=bind(c,p)
 if not b['valid']:raise ValueError('; '.join(b['errors']))
 if audio and not audio.is_file():raise ValueError('missing audio')
 work.mkdir(parents=True);plan=work/'plan.json';write(plan,p);write(work/'creative.json',c);write(work/'expanded.json',e);write(work/'motion-audit.json',audit(p,c))
 state={'mode':c['mode'],'source':str(spec.resolve()),'source_sha256':sha(spec),'creative_sha256':sha(work/'creative.json'),'inputs':snapshot(plan,p),'audio':{'path':str(audio.resolve()),'sha256':sha(audio)} if audio else None,'notes':notes,'binding':b}
 write(work/'production.json',state);return {'next':'run preview; watch actual MP4, inspect review sheet, write review decisions, then check/export','audio_blocked':c['mode']!='fictional_study' and not audio,'motion_audit':str(work/'motion-audit.json')}

def checked(work):
 s=json.loads((work/'production.json').read_text());r=verify_inputs(work)
 if not r['inputs_valid']:raise ValueError('; '.join(r['errors'])+'; start a new revision')
 return s

def render(work,stage,backend='auto',size=None):
 s=checked(work);plan=work/'plan.json';p=json.loads(plan.read_text());final=stage!='preview';out=work/stage
 if out.exists():raise ValueError('output exists; retain it and start a new revision for changes')
 if final:
  r=gate(work)
  if not r['ready']:raise ValueError('; '.join(r['errors']))
  if size not in (None,1080):raise ValueError('final export width must be 1080')
 width=size or (1080 if final else 540)
 if width not in (360,540,720,1080):raise ValueError('unsupported render width')
 cmd=[sys.executable,str(ROOT/'starter/composite_film/compositor.py'),str(plan.resolve()),str(out.resolve()),'--size',str(width),'--profile',{'preview':'preview','upload':'high','master':'lossless'}[stage],'--backend',backend]
 if s['audio']:cmd+=['--audio',s['audio']['path']]
 subprocess.run(cmd,check=True);v=verify_video(plan,out/'film.mp4',width,bool(s['audio']));checked(work)
 if not v['technical_valid']:raise ValueError(str(v['errors']))
 evidence={'inputs':s['inputs'],'video':v,'sheet_sha256':sha(out/'contact-sheet.jpg'),'backend_sha256':sha(out/'render-backend.json'),'width':width};write(out/'evidence.json',evidence)
 return evidence

def evidence(work,stage='preview'):
 s=checked(work);out=work/stage;e=json.loads((out/'evidence.json').read_text());errors=[]
 if e['inputs']!=s['inputs']:errors.append('render input mismatch')
 for f,h in [('film.mp4',e['video']['video_sha256']),('contact-sheet.jpg',e['sheet_sha256']),('render-backend.json',e['backend_sha256'])]:
  if not (out/f).is_file() or sha(out/f)!=h:errors.append('missing/changed '+f)
 if not e['video']['technical_valid']:errors.append('technical video check failed')
 return e,errors

def review_template(work):
 e,errors=evidence(work)
 if errors:raise ValueError('; '.join(errors))
 c=json.loads((work/'creative.json').read_text());p=work/'review.json';data={'preview_sha256':e['video']['video_sha256'],'playback_watched':False,'audio_listened':False,'rights_verified':False,'beats':[{'beat':i,'time':round((b['start']+b['end'])/2,3),'decision':'pending','observation':'','repair':''} for i,b in enumerate(c['beats'])],'global_checks':{k:'pending' for k in ('typography','transitions','composition','motion','product_accuracy','audio')},'note':'Inspect actual playback and native stills. Do not mark pass without doing the review. A fix requires a new revision.'};write(p,data);return data

def gate(work):
 s=checked(work);errors=[]
 if s['mode']!='fictional_study' and not s['audio']:errors.append('actual authorized audio required for ad or revision using this route')
 try:e,err=evidence(work);errors+=err
 except (OSError,KeyError,ValueError) as ex:return {'ready':False,'errors':errors+['preview evidence missing/invalid: '+str(ex)]}
 try:r=json.loads((work/'review.json').read_text())
 except (OSError,ValueError):return {'ready':False,'errors':errors+['review.json missing or invalid']}
 if r.get('preview_sha256')!=e['video']['video_sha256']:errors.append('review is for another preview')
 if r.get('playback_watched') is not True:errors.append('watch the complete preview')
 if s['audio'] and (r.get('audio_listened') is not True or r.get('rights_verified') is not True):errors.append('listen and verify audio rights')
 c=json.loads((work/'creative.json').read_text());beats=r.get('beats',[])
 if not isinstance(beats,list) or len(beats)!=len(c['beats']):errors.append('review every beat')
 else:
  for i,(x,b) in enumerate(zip(beats,c['beats'])):
   if x.get('beat')!=i or not isinstance(x.get('time'),(int,float)) or not b['start']<=x['time']<b['end'] or x.get('decision')!='pass' or not str(x.get('observation','')).strip() or x.get('repair'):errors.append(f'beat {i}: unresolved or missing concrete review')
 for k in ('typography','transitions','composition','motion','product_accuracy','audio'):
  v=r.get('global_checks',{}).get(k);allowed=('pass','not_applicable') if (k=='audio' and not s['audio']) or (k=='product_accuracy' and s['mode']=='fictional_study') else ('pass',)
  if v not in allowed:errors.append('global review: '+k)
 return {'ready':not errors,'errors':errors,'note':'Review entries are self-attestations, not proof of viewing, rights, or design quality. Inspect the final export again.'}

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True);a=sub.add_parser('start');a.add_argument('spec',type=Path);a.add_argument('creative',type=Path);a.add_argument('work',type=Path);a.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  a=sub.add_parser(k);a.add_argument('work',type=Path);a.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');a.add_argument('--size',type=int)
 for k in ('review-template','gate','verify-export'):
  a=sub.add_parser(k);a.add_argument('work',type=Path)
 z=p.parse_args()
 if z.cmd=='verify-export':
  results={}
  for stage in ('upload','master'):
   if (z.work/stage/'evidence.json').is_file():
    _,errors=evidence(z.work,stage);results[stage]={'valid':not errors,'errors':errors}
  print(json.dumps({'exports':results,'note':'Hashes and technical evidence only; inspect final picture and sound.'},indent=2));raise SystemExit(0 if results and all(x['valid'] for x in results.values()) else 2)
 r=start(z.spec,z.creative,z.work,z.audio) if z.cmd=='start' else render(z.work,z.cmd,z.backend,z.size) if z.cmd in ('preview','upload','master') else review_template(z.work) if z.cmd=='review-template' else gate(z.work);print(json.dumps(r,indent=2));raise SystemExit(2 if z.cmd=='gate' and not r['ready'] else 0)
if __name__=='__main__':main()
