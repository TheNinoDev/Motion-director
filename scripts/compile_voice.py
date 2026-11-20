#!/usr/bin/env python3
"""Compile clean phrase text and acting intents into provider-ready text; no TTS."""
import argparse,json,re,sys
from pathlib import Path
CUES={
 'elevenlabs':{'neutral':'','curious':'curious','dry':'sarcastic','mischief':'mischievously','quiet':'whispers','sigh':'sighs','chuckle':'chuckles','excited':'excited','reflective':'thoughtful','pause':'short pause'},
 'fish':{'neutral':'','curious':'curious, rising tone','dry':'slightly sarcastic','mischief':'playful, sly tone','quiet':'whispering','sigh':'sigh','chuckle':'chuckling','excited':'excited','reflective':'thoughtful, measured tone','pause':'short pause'},
 'plain':{'neutral':''}}
MODELS={'elevenlabs':{'eleven_v3','eleven_v4'},'fish':{'s2-pro','s2.1-pro'},'plain':{'plain'}}
def compile_plan(p):
 provider=p['provider'];model=p['model'];beats=p['beats']; sep=p.get('separator','\n\n')
 if provider not in MODELS or model not in MODELS[provider]: raise ValueError('Unsupported route; verify provider documentation or use plain.')
 if sep not in ['\n\n','\n',' ']: raise ValueError('Unsupported separator')
 if not isinstance(beats,list) or not beats:raise ValueError('beats must be nonempty')
 plain=[]; tagged=[]
 for beat in beats:
  t=beat['text'];cue=beat.get('cue','neutral')
  if not isinstance(t,str) or not t.strip() or t!=t.strip(): raise ValueError('Text must be nonempty with no boundary whitespace')
  if re.search(r'\[[^\]]*\]|</?[^>]+>|\((?:happy|sad|whispering|laughing|excited)\)',t,re.I):raise ValueError('Inline tags in clean text; move into cue field')
  if cue not in CUES[provider]:raise ValueError(f'Unsupported cue: {cue}')
  tag=CUES[provider][cue];plain.append(t);tagged.append(f'[{tag}] {t}' if tag else t)
 clean=sep.join(plain); output=sep.join(tagged)
 if 'locked_text' in p and p['locked_text']!=clean:raise ValueError('Narration mismatch; preserve exact wording, punctuation and separators')
 return clean,output

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('plan',type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
 try:
  p=json.loads(a.plan.read_text(encoding='utf-8'));clean,tagged=compile_plan(p)
  a.out.mkdir(parents=True,exist_ok=True)
  for name,txt in [('narration.txt',clean),('provider-input.txt',tagged),('caption-source.txt',clean)]: (a.out/name).write_text(txt,encoding='utf-8')
  (a.out/'performance.json').write_text(json.dumps({'provider':p['provider'],'model':p['model'],'beats':p['beats'],'audio_generated':False,'timing_verified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 except (KeyError,TypeError,ValueError,OSError) as e:ap.exit(1,f'{e}\n')
 print('Compiled text only; generate and validate audio separately.')
if __name__=='__main__':main()
