#!/usr/bin/env python3
"""Measured soundtrack transients. These are onset candidates, not certified beats."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks

def analyze(path):
 sr=22050; hop=220; win=1024
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar',str(sr),'-f','f32le','-']);y=np.frombuffer(raw,'<f4');
 if len(y)<win*2:raise ValueError('soundtrack too short')
 blocks=np.lib.stride_tricks.sliding_window_view(y,win)[::hop];sp=np.log1p(50*np.abs(np.fft.rfft(blocks*np.hanning(win),axis=1))/(win/2));flux=np.maximum(0,np.diff(sp,axis=0)).mean(axis=1);median=float(np.median(flux));mad=float(np.median(abs(flux-median)))
 peaks,_=find_peaks(flux,height=median+max(2.5*mad,1e-5),distance=round(.13*sr/hop),prominence=max(mad,1e-5)); strength=flux[peaks];q=float(np.percentile(strength,90)) if len(strength) else 1
 return {'source':str(path),'method':'positive log spectral flux / onset candidates, not verified beats','duration':len(y)/sr,'cues':[{'time':round(float((i+1)*hop+win/2)/sr,4),'strength':round(min(1,float(v)/max(q,1e-9)),3)} for i,v in zip(peaks,strength)]}
def snap(t,cues,window=.10):
 matches=[v for v in cues if abs(v['time']-t)<=window];return min(matches,key=lambda v:abs(v['time']-t)-.035*v['strength'])['time'] if matches else t
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('song',type=Path);p.add_argument('output',type=Path);a=p.parse_args();a.output.write_text(json.dumps(analyze(a.song),indent=2))
