#!/usr/bin/env python3
"""Event-aware primary production route, with all V45 quality gates retained."""
import argparse,json,sys
from pathlib import Path
import production_v45 as old
from director_v46 import build
from production_v40 import start as start40,checked,render,evidence
from production_v43 import requests,audit
from agent_session import write,sha
import event_audio_v46 as audio

def replace_json(path,data):
 tmp=path.with_suffix('.v46.tmp');write(tmp,data);tmp.replace(path)

def start(spec,creative,w,bed=None,*,builder=build):
 p,e,_=builder(json.loads(spec.read_text()),spec.resolve().parent);c=json.loads(creative.read_text());r=requests(p,c);cues=e['sound_cues']
 if cues and c['mode']!='fictional_study' and bed is None:raise ValueError('real production needs actual authorized premixed audio; SFX do not replace narration/music')
 if bed and not bed.is_file():raise ValueError('supplied audio missing')
 # Check mix length before creating a session, so a failed intake leaves no partial directory.
 if bed and cues and abs(len(audio.decode(bed))-round(p['duration']*p['fps'])*audio.SR/p['fps'])>audio.SR/p['fps']:raise ValueError('bed duration differs; align actual narration first')
 s=start40(spec,creative,w,bed,builder=builder);write(w/'pixel-requests.json',r);write(w/'scene-audit.json',audit(p))
 state=checked(w);meta={'cues':cues,'bed':str(bed.resolve()) if bed else None,'bed_sha256':sha(bed) if bed else None}
 if cues:
  meta=audio.make(p,cues,w,bed);mix=w/'mix-v46.wav';state['audio']={'path':str(mix.resolve()),'sha256':sha(mix)};state['inputs'][str((w/'event-sfx.wav').resolve())]=meta['stem_sha256']
 if bed:state['inputs'][str(bed.resolve())]=sha(bed)
 write(w/'event-audio.json',meta);state['inputs'][str((w/'event-audio.json').resolve())]=sha(w/'event-audio.json');replace_json(w/'production.json',state)
 return {**s,'audio_blocked':c['mode']!='fictional_study' and not state['audio'],'event_cues':len(cues),'next':'run next'}

def audio_review(w):
 s=checked(w);_,err=evidence(w)
 if err:raise ValueError('; '.join(err))
 if not s['audio']:raise ValueError('silent study has no audio review')
 p=json.loads((w/'plan.json').read_text());m=json.loads((w/'event-audio.json').read_text());return audio.review(w/'preview'/'film.mp4',m['cues'],p['fps'],w/'audio-review')

def check_audio(w):
 try:
  state=checked(w)
  if not state['audio']:return {'valid':True,'required':False,'errors':[]}
  _,err=evidence(w);p=json.loads((w/'plan.json').read_text());m=json.loads((w/'event-audio.json').read_text());out=w/'audio-review';r=json.loads((out/'report.json').read_text())
  if r['video_sha256']!=sha(w/'preview'/'film.mp4') or r['waveform_sha256']!=sha(out/'waveform.png'):err.append('stale/changed audio evidence')
  if abs(r['duration']-round(p['duration']*p['fps'])/p['fps'])>.15:err.append('audio duration differs')
  if [(x['id'],x['time'],x['kind'],x['target']) for x in r['cues']]!=[(i,x['frame']/p['fps'],x['kind'],x['target']) for i,x in enumerate(m['cues'])]:err.append('audio cue evidence mismatch')
  return {'valid':not err,'required':True,'errors':err}
 except (OSError,ValueError,KeyError,TypeError) as ex:return {'valid':False,'required':True,'errors':[str(ex)]}

def template(w):
 a=check_audio(w)
 if not a['valid']:raise ValueError('; '.join(a['errors']))
 r=old.template(w)
 if a['required']:
  out=w/'audio-review';q=json.loads((out/'report.json').read_text());r['audio_v46']={'report_sha256':sha(out/'report.json'),'mix_observation':'','decisions':[{'id':x['id'],'decision':'pending','observation':''} for x in q['cues']]};replace_json(w/'review.json',r)
 return r

def gate(w):
 r=old.gate(w);a=check_audio(w);errors=r['errors']+a['errors']
 if a['valid'] and a['required']:
  try:
   out=w/'audio-review';q=json.loads((out/'report.json').read_text());v=json.loads((w/'review.json').read_text())['audio_v46'];ds=v['decisions']
   if v['report_sha256']!=sha(out/'report.json') or not str(v['mix_observation']).strip():errors.append('listen to decoded mix, record observation and bind report')
   if len(ds)!=len(q['cues']) or any(x['id']!=y['id'] or x['decision']!='pass' or not str(x['observation']).strip() for x,y in zip(ds,q['cues'])):errors.append('review every audible cue; repair or explain actual sound')
  except (OSError,KeyError,TypeError,ValueError):errors.append('audio review missing/invalid')
 return {'ready':not errors,'errors':errors,'note':'Technical evidence and explicit self-attestation; not aesthetic or rights certification.'}

def next_step(w):
 r=old.next_step(w);prefix=[sys.executable,'scripts/production_v46.py'];state=checked(w)
 if r['stage'] not in ('preview','pixel','transitions','flow','cadence','blocked'):
  if state['audio'] and not (w/'audio-review'/'report.json').is_file():return {'stage':'blocked','action':'incomplete audio review; new revision required'} if (w/'audio-review').exists() else {'stage':'audio-review','argv':prefix+['audio-review',str(w.resolve())]}
  a=check_audio(w)
  if not a['valid']:return {'stage':'blocked','errors':a['errors']}
  if (w/'review.json').exists():
   g=gate(w)
   if not g['ready']:return {'stage':'blocked_review','errors':g['errors'],'action':'Use advice; inspect and repair before release. Never auto-approve.'}
 if 'argv' in r:r['argv']=prefix+r['argv'][2:]
 return r

def advice(w):
 r=old.advice(w);a=check_audio(w)
 if a['valid'] and a['required']:
  out=w/'audio-review';q=json.loads((out/'report.json').read_text())
  for x in q['cues']:
   for f in x['flags']:r['suggestions'].append({'category':'audio','time':x['time'],'layer_ids':[x['target']],'evidence':str(out/'waveform.png'),'observation':f,'inspect_fields':['event_sounds.gain_db','event_sounds.offset','event_sounds.kind'],'action':'Listen to the isolated stem and full mix; adjust only cue or edit the bed if necessary. Do not move picture to hide a bad cue.'})
  for f in q['flags']:r['suggestions'].append({'category':'audio','observation':f,'evidence':str(out/'waveform.png'),'action':'Listen and check actual levels; peak/RMS are not loudness or speech clarity.'})
 return r

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);a=sub.add_parser('start');a.add_argument('spec',type=Path);a.add_argument('creative',type=Path);a.add_argument('work',type=Path);a.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  a=sub.add_parser(k);a.add_argument('work',type=Path);a.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');a.add_argument('--size',type=int)
 for k in ('next','pixels','transitions','flow','cadence','audio-review','review-template','gate','advice','verify-export'):sub.add_parser(k).add_argument('work',type=Path)
 z=ap.parse_args();w=z.work
 if z.cmd=='start':r=start(z.spec,z.creative,w,z.audio)
 elif z.cmd in ('preview','upload','master'):
  if z.cmd!='preview' and not gate(w)['ready']:raise ValueError('V46 gate failed; run gate')
  r=render(w,z.cmd,z.backend,z.size)
 elif z.cmd=='verify-export':r={k:{'valid':not evidence(w,k)[1]} for k in ('upload','master') if (w/k/'evidence.json').is_file()}
 else:r={'next':next_step,'pixels':old.old.old.pixels,'transitions':old.old.old.transitions,'flow':old.old.flow,'cadence':old.cadence,'audio-review':audio_review,'review-template':template,'gate':gate,'advice':advice}[z.cmd](w)
 print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or not all(x['valid'] for x in r.values()))) else 0)
if __name__=='__main__':main()
