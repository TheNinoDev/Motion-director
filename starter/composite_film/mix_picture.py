#!/usr/bin/env python3
"""Picture-locked SFX on a premixed VO and music bed; original stems preserved."""
import argparse,json,wave
from pathlib import Path
import numpy as np
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('md27sfx',Path(__file__).resolve().parents[1]/'sound_design'/'render.py');m=module_from_spec(spec);spec.loader.exec_module(m)
def mix_picture(src,plan,dst):
 fps=plan['fps'];n=round(plan['duration']*fps);events=[];length={'click':.10,'whoosh':.36,'chime':.48,'riser':.65,'impact':.40,'drop':.40}
 for e in plan.get('sound_events',[]):
  start=round(e['time']*fps);dur=min(n-start,max(1,round(e.get('duration',length[e['kind']])*fps)))
  if not 0<=start<n or dur<1:raise ValueError('sound event outside picture')
  events.append({'frame':start,'duration_frames':dur,'kind':e['kind'],'gain_db':e['gain_db'],'pan':e.get('pan',0)})
 s=m.render({'fps':fps,'frames':n,'events':events})
 with wave.open(str(src)) as f:
  if (f.getframerate(),f.getsampwidth(),f.getnchannels())!=(48000,2,2):raise ValueError('expected 48kHz stereo PCM16 bed')
  x=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).astype(np.float32)/32768
 if abs(len(x)-len(s))>1600:raise ValueError('bed duration differs from picture')
 mix=np.zeros_like(s);mix[:min(len(x),len(s))]=x[:len(s)];mix+=s;mix*=min(1,.89/max(.001,float(abs(mix).max())))
 for path,arr in [(dst,mix),(Path(dst).with_name('picture-sfx.wav'),s)]:
  with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes((np.clip(arr,-1,1)*32767).astype('<i2').tobytes())
 return events
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('bed',type=Path);p.add_argument('plan',type=Path);p.add_argument('output',type=Path);a=p.parse_args();print(len(mix_picture(a.bed,json.loads(a.plan.read_text()),a.output)))
