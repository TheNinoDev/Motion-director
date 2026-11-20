#!/usr/bin/env python3
"""Mix selected visual accents at actual frame positions after picture lock."""
import argparse,json,sys,wave,subprocess
from pathlib import Path
import numpy as np
from importlib.util import spec_from_file_location,module_from_spec
_spec=spec_from_file_location('md25_sfx',Path(__file__).resolve().parents[1]/'sound_design'/'render.py');_module=module_from_spec(_spec);_spec.loader.exec_module(_module);sfx=_module.render
# Selected motion-related accents; no blanket impact on every cut.
DEFAULT={'tabs':('click',5,-23),'counter':('impact',11,-22),'tunnel':('whoosh',12,-24),'cascade':('click',4,-26),'field':('riser',22,-25),'mesh':('whoosh',17,-19),'reveal':('chime',15,-25),'duo':('whoosh',10,-25),'lockup':('chime',18,-24)}
def finish(build,fps,output=None):
 build=Path(build);shots=json.loads((build/'visual-timeline.json').read_text());frames=shots[-1]['start']+shots[-1]['frames'];events=[]
 for i,s in enumerate(shots):
  val=s.get('sfx',DEFAULT.get(s['kind']));
  if not val:continue
  k,n,g=val;f=s['start']+min(4,s['frames']//4);n=min(n,frames-f)
  if i and n>0:events.append({'frame':f,'duration_frames':n,'gain_db':g,'kind':k,'pan':0})
 plan={'fps':fps,'frames':frames,'events':events};(build/'sound-cues.json').write_text(json.dumps(plan,indent=2));a=sfx(plan)
 with wave.open(str(build/'mix.wav')) as w:assert w.getframerate()==48000 and w.getnchannels()==2 and w.getsampwidth()==2;orig=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2).astype(np.float32)/32768
 n=min(len(orig),len(a));orig[:n]+=a[:n];orig*=min(1,.92/max(.001,float(np.max(np.abs(orig)))))
 for name,data in [('picture-sfx.wav',a),('final-mix.wav',orig)]:
  with wave.open(str(build/name),'wb') as w:w.setnchannels(2);w.setframerate(48000);w.setsampwidth(2);w.writeframes((np.clip(data,-1,1)*32767).astype('<i2').tobytes())
 output=Path(output or build/'finished.mp4');subprocess.run(['ffmpeg','-v','error','-y','-i',str(build/'film.mp4'),'-i',str(build/'final-mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(output)],check=True)
 return len(events)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--fps',type=int,default=30);p.add_argument('--output',type=Path);a=p.parse_args();print('mixed',finish(a.build,a.fps,a.output),'visual cues')
