"""Deterministic original sound design, optional supplied bed, and decoded audio review."""
import json,math,subprocess,wave
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import numpy as np
from PIL import Image,ImageDraw
from agent_session import sha,write,ROOT
s=spec_from_file_location('md46sfx',ROOT/'starter/sound_design/render.py');m=module_from_spec(s);s.loader.exec_module(m)
SR=48000

def decode(path):
 b=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-map','0:a:0','-ac','2','-ar',str(SR),'-f','f32le','-'])
 x=np.frombuffer(b,'<f4').reshape(-1,2)
 if not len(x) or not np.isfinite(x).all():raise ValueError('empty or nonfinite audio')
 return x

def wav(path,x):
 with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(np.int16(np.clip(x,-1,1)*32767).tobytes())

def make(plan,cues,out,bed=None):
 if not cues:raise ValueError('no sound cues to synthesize')
 fps=plan['fps'];n=round(plan['duration']*fps);a=m.render({'fps':fps,'frames':n,'events':cues,'seed':46});mix=a.copy()
 if bed:
  x=decode(bed)
  if abs(len(x)-len(a))>SR/fps:raise ValueError('supplied premixed bed must match picture duration within one frame; do not silently truncate narration')
  mix[:min(len(x),len(a))]+=x[:len(a)]
 gain=min(1,.89/max(.001,float(np.max(np.abs(mix)))));mix*=gain
 wav(out/'event-sfx.wav',a);wav(out/'mix-v46.wav',mix)
 return {'bed':str(bed.resolve()) if bed else None,'bed_sha256':sha(bed) if bed else None,'stem_sha256':sha(out/'event-sfx.wav'),'mix_sha256':sha(out/'mix-v46.wav'),'gain':gain,'cues':cues,'duration':n/fps,'note':'Original synthetic accents; provided bed rights and speech remain subject to review. No music or voice substitution.'}

def db(x):return round(20*math.log10(max(1e-8,float(np.sqrt(np.mean(x*x))))),2) if len(x) else -160

def review(video,cues,fps,out):
 out.mkdir(exist_ok=False);x=decode(video);peak=float(np.max(np.abs(x)));duration=len(x)/SR
 flags=[]
 if peak>=.999:flags.append('decoded peak near full scale; inspect clipping')
 if db(x)<-50:flags.append('very quiet decoded mix')
 rows=[]
 for i,c in enumerate(cues):
  a=round(c['frame']*SR/fps);b=round((c['frame']+c['duration_frames'])*SR/fps);r=db(x[a:b]);rows.append({'id':i,'time':c['frame']/fps,'kind':c['kind'],'target':c['target'],'rms_dbfs':r,'flags':['quiet cue window; listen for missing effect'] if r<-45 else []})
 im=Image.new('RGB',(960,260),'#16202b');d=ImageDraw.Draw(im);d.text((18,12),'DECODED AUDIO | waveform and planned cue times',fill='white');d.text((18,232),f'{duration:.2f}s   peak {peak:.3f}   RMS {db(x):.1f} dBFS   (not LUFS)',fill='white')
 for i in range(920):
  seg=x[i*len(x)//920:(i+1)*len(x)//920];v=float(np.max(np.abs(seg))) if len(seg) else 0;d.line((20+i,130-v*85,20+i,130+v*85),fill='#8bd3bc')
 for i,c in enumerate(rows):
  q=20+int(920*c['time']/duration);d.line((q,45,q,216),fill='#f6bc7e');d.text((q+2,34+(i%2)*14),str(i),fill='#ffffff')
 im.save(out/'waveform.png');r={'video_sha256':sha(video),'waveform_sha256':sha(out/'waveform.png'),'duration':duration,'peak':peak,'rms_dbfs':db(x),'flags':flags,'cues':rows,'note':'RMS/peak only. A loud cue window may contain speech or music; not verified sync or listening.'};write(out/'report.json',r);return r
