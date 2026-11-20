#!/usr/bin/env python3
"""Waveform and candidate onset inspection. No ASR, BPM, speech-tone or verified beat inference."""
import argparse,json,subprocess,math
from array import array
from pathlib import Path

def probe(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','16000','-f','f32le','-'])
    samples=array('f');samples.frombytes(raw)
    if not samples: raise ValueError('No decoded audio')
    db=lambda v:round(20*math.log10(max(v,1e-9)),2)
    hop=320; windows=[samples[i:i+hop] for i in range(0,len(samples),hop)]
    levels=[math.sqrt(sum(v*v for v in w)/len(w)) for w in windows]
    rises=[max(0,db(levels[i])-db(levels[i-1])) for i in range(1,len(levels))]
    peaks=[]
    for i in sorted(range(len(rises)),key=lambda i:rises[i],reverse=True):
        if rises[i]<4 or db(levels[i+1])<-38:continue
        t=(i+1)*hop/16000
        if all(abs(t-p['seconds'])>=.14 for p in peaks):peaks.append({'seconds':round(t,3),'rise_db':round(rises[i],2)})
        if len(peaks)>=80:break
    return {'file':str(path),'duration_seconds':len(samples)/16000,'peak_sample_dbfs':db(max(abs(v) for v in samples)),'rms_dbfs':db(math.sqrt(sum(v*v for v in samples)/len(samples))),'quiet_window_fraction':round(sum(v<.01 for v in levels)/len(levels),4),'transient_candidates':sorted(peaks,key=lambda p:p['seconds']),'method':'20ms RMS rise, mono 16k decode; audition required; not musical beat or speech timing','verified_beats':[]}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('audio',type=Path);p.add_argument('-o','--output',type=Path);a=p.parse_args()
    try:s=json.dumps(probe(a.audio),indent=2)+'\n'
    except (OSError,ValueError,subprocess.CalledProcessError) as e:p.exit(1,str(e)+'\n')
    if a.output:a.output.write_text(s,encoding='utf-8')
    else:print(s,end='')
