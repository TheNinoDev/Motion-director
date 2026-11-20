#!/usr/bin/env python3
"""Mandatory ad intake, script, audio handoff and locked stem mix. No TTS generation."""
import argparse, hashlib, json, math, re, subprocess, sys
from pathlib import Path
from compile_voice import compile_plan
from audio_intake import probe

ROOT=Path(__file__).resolve().parents[1]
QUESTIONS={
 'product_name':'What is the exact product or brand name?',
 'product_source':'What product should I inspect? Send a URL, local project, HTML, screenshots, or description (one source is enough).',
 'focus':'Which ONE feature or outcome should this video sell? Or say choose for me.',
 'audience':'Who should watch this, and what should they do afterwards?',
 'language':'Which spoken language should I use?',
 'platforms':'Where will this be posted (TikTok, Shorts, Reels, etc.)?',
 'use_scope':'Is it public promotion or a private preview? Public product marketing is commercial by default.',
 'voice_route':'Do you have narration already, want to record it, want me to use an authorized voice tool, or prefer a supported TTS provider?',
 'music_route':'Do you have music already, want me to research tracks, want original/licensed music, or explicitly want no music?'}
CUE_ROUTES={'elevenlabs','fish'}

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def put(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(x):return isinstance(x,str) and bool(x.strip())
def path(base,p):return (base/p).resolve()
def valid_num(x):return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x)
def questions(b):
 return [{'key':k,'question':v} for k,v in QUESTIONS.items() if not (b.get(k) if k=='platforms' else text(b.get(k)))]

def script_review(p,brief):
 errors=[];warnings=[]
 try:clean,tagged=compile_plan(p)
 except (KeyError,TypeError,ValueError) as e:return {'errors':[str(e)],'warnings':[]}
 beats=p['beats'];cues=[b.get('cue','neutral') for b in beats];provider=p['provider'];route=brief.get('voice_route');qa=p.get('copy_review',{})
 if route in CUE_ROUTES and provider!=route:errors.append('Provider must match selected voice route.')
 if provider in CUE_ROUTES:
  if len(set(cues)-{'neutral'})<2 or sum(c!='neutral' for c in cues)<min(2,len(beats)) or tagged==clean:errors.append('Expressive narration needs at least two distinct motivated non-neutral delivery cues; not all neutral.')
  for i,b in enumerate(beats):
   if b.get('cue','neutral')!='neutral' and not text(b.get('note')):errors.append(f'Beat {i}: explain acting intent.')
 elif route in CUE_ROUTES:errors.append('Do not downgrade to plain to bypass tags.')
 elif not text(p.get('plain_reason')):errors.append('Plain narration needs a reason (human recording, supplied VO, unsupported model). Give separate acting direction.')
 for k in ('hook_reason','single_story','payoff','claim_check','read_aloud_review','rewrite_reason'):
  if not text(qa.get(k)):errors.append('Missing copy review: '+k)
 hooks=p.get('hook_candidates',[])
 if not isinstance(hooks,list) or len(hooks)<3 or len({str(x).strip().lower() for x in hooks})<3 or not all(text(x) for x in hooks):errors.append('Write three distinct hook candidates and select one.')
 elif beats[0]['text'] not in hooks:errors.append('Opening phrase must match selected hook candidate.')
 if len(beats)<3:errors.append('Provide at least three purposeful phrase beats (short formats may use script-only route).')
 if any(len(b['text'].split())>34 for b in beats):warnings.append('Long phrase: split at natural emotional pivot if needed.')
 if re.search(r'\b(game changer|revolutioniz\w*|unlock your potential|seamless experience|next level|one stop shop)\b',clean,re.I):warnings.append('Generic marketing phrase detected: rewrite in natural speech.')
 if not text(p.get('locked_text')) or p['locked_text']!=clean:errors.append('Exact clean narration must be locked; captions must not include acting tags.')
 return {'errors':errors,'warnings':warnings,'clean':clean,'tagged':tagged,'word_count':len(clean.split()),'tags':sum(c!='neutral' for c in cues),'cue_types':sorted(set(cues)-{'neutral'})}

def handoff(b,p,r,selection=None):
 provider=p['provider'];voice_route=b['voice_route']; lines=['# Audio handoff — send only missing items','', 'Target: '+b['language']+' | '+', '.join(b['platforms'])+' | '+b['use_scope'],'','## Voiceover','']
 if voice_route in ('supplied','recording','authorized_tool'):
  lines+=['Use the already supplied dry narration if available. Otherwise record/generate using the locked script and acting notes below; send original WAV/MP3. Do not mix, trim or time it for the editor.']
 elif provider=='elevenlabs':
  lines+=['Eligibility and commercial rights must be confirmed first: https://elevenlabs.io/terms-of-use-eu . If ineligible or unable to access the service, use recording or an eligible alternative.', '1. Open https://elevenlabs.io/ and select an existing authorized voice. Only if a new voice is needed: Voices > Add/Create Voice > Voice Design; paste the separate voice description, audition and save.', '2. Open Text to Speech: https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech . Select the saved voice and the selected expressive model ('+p['model']+').', '3. Paste only the tagged narration below. Generate, audition brand pronunciation and emotional changes. Regenerate defective phrases only.', '4. Export the original WAV or MP3 via player/history and upload it here. No screen recording, background music, credentials or editing needed.']
  if b.get('voice_design')=='holographic_new':
   original=(ROOT/'references/24-holographic-voice-preset.md').read_text().split('## Exact original',1)[1].split('\n\n',1)[1].split('\n\n## Optional',1)[0].strip()
   lines+=['','### Separate voice design description (not narration)','```',original,'```']
 elif provider=='fish':
  lines+=['Confirm account eligibility and voice/commercial rights: https://fish.audio/terms/ and https://fish.audio/plan/ .', '1. Open https://fish.audio/text-to-speech/ . Select an original or authorized voice; audition it.', '2. Select the supported expressive S2 model ('+p['model']+'); paste the tagged script below. S2 accepts natural-language square-bracket cues.', '3. Generate and audition; export original WAV/MP3 from the player or history and upload. No credentials or editing needed.']
 else:lines+=['Use an eligible authorized provider or record the script; follow the separate acting notes. Upload the original dry audio.']
 lines+=['','### Exact narration to paste','```',r['tagged'],'```','','### Acting notes (not spoken)']+[f"- {x['text']}: {x.get('note','Natural delivery')}" for x in p['beats']]
 lines+=['','## Music']
 m=b['music_route']
 if m=='none':lines+=['No music requested. Editor still handles intentional sound design.']
 elif m=='supplied':lines+=['Use the supplied original authorized music file. If not attached yet, upload WAV/MP3/M4A separately.']
 elif selection and all(text(selection.get(k)) for k in ('track','version','source_url','acquisition_steps')):lines+=['Selected track: '+selection['track']+' — '+selection['version'],selection['source_url'],selection['acquisition_steps'],'Upload the original authorized file separately.']
 else:lines+=['Research and present 2–3 real candidates with exact track/version, listening link, emotional fit, trend date/region/source if called trending, license scope and lawful acquisition steps. Get selection unless delegated. Do not tell the user to find a random song. TikTok-only commercial music: https://ads.tiktok.com/help/article/commercial-music-library?lang=en ; do not assume portability. After selection, send the exact source and instructions for legal export or licensed acquisition.']
 lines+=['','Upload only the missing raw files. I handle alignment, edits, music ducking, SFX, animation and export. If you already sent a file, I will not ask again.']
 return '\n\n'.join(lines)+'\n'

def check(manifest,release=False):
 d=read(manifest);base=manifest.resolve().parent;b=d.get('brief',{});q=questions(b);errors=[];warnings=[];files={}
 def result(stage,**extra):return {'stage':stage,'ready':stage=='ready','errors':errors,'warnings':warnings,'questions':q if stage=='briefing' else [],'files':files,**extra}
 if q:return result('briefing')
 if b['use_scope'] not in ('commercial','personal-public','private-preview') or not isinstance(b['platforms'],list) or not all(text(x) for x in b['platforms']):errors.append('Invalid release scope/platforms.')
 if b['voice_route'] not in ('elevenlabs','fish','recording','supplied','authorized_tool'):errors.append('Choose an actual voice route.')
 if b['music_route'] not in ('supplied','research','original','none'):errors.append('Choose actual music route.')
 if errors:return result('briefing_invalid')
 if not text(d.get('performance')):return result('write_script')
 try:
  f=path(base,d['performance']);p=read(f);files[str(f)]=sha(f);r=script_review(p,b)
 except (OSError,ValueError,TypeError,KeyError) as e:errors.append(str(e));return result('write_script')
 errors+=r['errors'];warnings+=r['warnings']
 if errors:return result('rewrite_script',script=r)
 if d.get('script_decision') not in ('approved','delegated'):return result('script_decision',script=r)
 if b['music_route']=='research':
  m=d.get('music_selection',{});required=('track','version','source_url','rights_evidence','acquisition_steps','selection_basis')
  if not all(text(m.get(k)) for k in required):return result('music_selection',script=r)
  if m.get('trending') is True and not all(text(m.get(k)) for k in ('trend_date','trend_region','trend_source','trend_metric')):errors.append('Trending claim needs evidence, date and region.');return result('music_selection',script=r)
 delivery=d.get('audio_delivery',{});mode=delivery.get('mode')
 if mode not in ('user_handoff','agent_acquired','already_supplied') or not text(delivery.get('observation')):return result('prepare_audio_handoff',script=r)
 if mode=='user_handoff':
  try:
   folder=path(base,delivery['handoff_dir']);expected={'handoff.md':handoff(b,p,r,d.get('music_selection')),'provider-input.txt':r['tagged'],'narration.txt':r['clean']}
   for n,want in expected.items():
    f=folder/n
    if f.read_text(encoding='utf8')!=want:raise ValueError('Handoff files stale: regenerate and send updated instructions.')
    files[str(f)]=sha(f)
  except (OSError,ValueError,KeyError,TypeError) as e:errors.append(str(e));return result('prepare_audio_handoff',script=r)
 if mode=='already_supplied' and b['voice_route'] not in ('supplied',):errors.append('Already supplied narration must use supplied route; do not skip manual handoff for a new TTS job.');return result('prepare_audio_handoff',script=r)
 a=d.get('audio',{});media={}
 if release and b['use_scope']=='private-preview':errors.append('Private preview cannot be released.')
 for k in ('voice','music'):
  o=a.get(k,{})
  if k=='music' and b['music_route']=='none':
   if not text(d.get('music_waiver')):errors.append('Record explicit user music waiver.')
   continue
  if not text(o.get('path')):errors.append('Upload missing raw '+k);continue
  try:
   f=path(base,o['path']);media[k]=probe(f);files[str(f)]=sha(f)
  except (OSError,ValueError,subprocess.SubprocessError) as e:errors.append(f'{k}: {e}');continue
  if o.get('rights_status')!='cleared' or not text(o.get('rights_evidence')):errors.append(k+': confirm rights for intended platforms.')
  if not text(o.get('audition_observation')):errors.append(k+': actual listening review missing; do not fabricate.')
 if errors:return result('audio_handoff_or_review',script=r,media=media)
 if a.get('voice',{}).get('scratch') is not False:errors.append('Scratch voice may not pass final ad intake.')
 if b['music_route']!='none' and path(base,a['music']['path'])==path(base,a['voice']['path']):errors.append('Voice and music must be separate raw stems.')
 if not text(d.get('alignment')):errors.append('Measured phrase alignment required.')
 else:
  try:
   f=path(base,d['alignment']);al=read(f);files[str(f)]=sha(f)
   if al.get('voice_sha256')!=files[str(path(base,a['voice']['path']))]:errors.append('Alignment is for another voice file.')
   if al.get('method') not in ('asr_verified','forced_alignment_verified','manual_listen_verified'):errors.append('No predicted or scratch alignment.')
   ph=al['phrases'];prev=0
   if [x['text'] for x in ph]!=[x['text'] for x in p['beats']]:errors.append('Phrase text does not match locked script.')
   for x in ph:
    st,en=x['start'],x['end']
    if not(valid_num(st) and valid_num(en) and prev<=st<en<=media['voice']['duration_seconds']+.03):errors.append('Invalid/overlapping phrase boundaries.');break
    prev=en
  except (OSError,ValueError,KeyError,TypeError) as e:errors.append('Alignment: '+str(e))
 if errors:return result('alignment',script=r,media=media)
 files[str(manifest.resolve())]=sha(manifest)
 return result('ready',script=r,media=media)

def mix(manifest,out,duration):
 r=check(manifest,release=True)
 if not r['ready']:raise ValueError(str(r['stage'])+': '+str(r['errors']))
 d=read(manifest);a=d['audio'];base=manifest.resolve().parent;v=path(base,a['voice']['path'])
 if not valid_num(duration) or not r['media']['voice']['duration_seconds']<=duration<=180:raise ValueError('Film duration must cover actual voice, max 180s.')
 if out.exists():raise ValueError('Choose new mix output; preserve raw stems.')
 cmd=['ffmpeg','-v','error','-n','-i',str(v)]
 if d['brief']['music_route']!='none':
  m=path(base,a['music']['path']);offset=d.get('music_offset',0);gain=d.get('music_gain_db',-16)
  if not valid_num(offset) or offset<0 or offset>=r['media']['music']['duration_seconds'] or not valid_num(gain) or not -40<=gain<=-8:raise ValueError('Music offset/gain out of range.')
  cmd+=['-ss',str(offset),'-i',str(m),'-filter_complex',f'[0:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={duration},asplit[v][key];[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,apad,atrim=duration={duration},afade=t=out:st={max(0,duration-.6)}:d={min(.6,duration)}[m];[m][key]sidechaincompress=threshold=0.035:ratio=5:attack=30:release=300[duck];[v][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=.89:level=0[out]','-map','[out]']
 else:cmd+=['-af',f'aresample=48000,apad,atrim=duration={duration},alimiter=limit=.89:level=0','-ac','2']
 subprocess.run(cmd+['-ar','48000','-c:a','pcm_s16le',str(out)],check=True);probe(out)
 meta={'manifest':str(manifest.resolve()),'inputs':r['files'],'mix_sha256':sha(out),'duration':duration,'note':'Actual stem mix; listen before approving. Rights and audition records are attestations.'};put(out.with_suffix('.mix.json'),meta);return meta

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True)
 for k in ('next','handoff','mix'):
  s=sp.add_parser(k);s.add_argument('manifest',type=Path)
  if k!='next':s.add_argument('out',type=Path)
  if k=='mix':s.add_argument('--duration',type=float,required=True)
 x=ap.parse_args()
 try:
  if x.cmd=='next':r=check(x.manifest);print(json.dumps(r,indent=2,ensure_ascii=False))
  elif x.cmd=='handoff':
   d=read(x.manifest);b=d['brief'];p=read(path(x.manifest.resolve().parent,d['performance']));r=script_review(p,b)
   if questions(b) or r['errors']:raise ValueError('Complete briefing and rewrite script: '+str(r['errors']))
   x.out.mkdir(parents=True,exist_ok=False);(x.out/'handoff.md').write_text(handoff(b,p,r,d.get("music_selection")),encoding='utf8');(x.out/'provider-input.txt').write_text(r['tagged'],encoding='utf8');(x.out/'narration.txt').write_text(r['clean'],encoding='utf8');print(x.out/'handoff.md')
  else:print(json.dumps(mix(x.manifest,x.out,x.duration),indent=2))
 except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as e:ap.exit(2,str(e)+'\n')
if __name__=='__main__':main()
