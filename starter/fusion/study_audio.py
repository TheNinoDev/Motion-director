"""Original synthetic demonstration bed locked to the film's cut frames. Not licensed track/VO."""
import argparse,json,wave
from pathlib import Path
import numpy as np

def make(project,out):
    fps=project['fps'];frames=[x['frames'] for x in project['shots']];cuts=np.r_[0,np.cumsum(frames[:-1])]/fps;dur=sum(frames)/fps;sr=48000;n=round(dur*sr);t=np.arange(n)/sr;rng=np.random.default_rng(210);a=np.zeros(n)
    # Soft two-note evolving pad, subdued high stereo pluck, no copyrighted melody.
    for f,gain in ((55,.044),(82.407,.020),(110,.020),(164.814,.012)):
        a+=gain*np.sin(2*np.pi*f*t+.23*np.sin(2*np.pi*.3*t))*(.7+.3*np.sin(t*.72+.3))
    for j,c in enumerate(cuts):
        i=round(c*sr);x=np.arange(n-i)/sr
        freq=(220,261.626,293.665,329.628,220)[j%5];env=(1-np.exp(-x*38))*np.exp(-x*4.2)
        a[i:]+=.048*env*(np.sin(2*np.pi*freq*x)+.16*np.sin(2*np.pi*2.01*freq*x))
        k=min(round(.22*sr),n-i);x=np.arange(k)/sr
        a[i:i+k]+=.13*(1-np.exp(-x*700))*np.exp(-x*24)*np.sin(2*np.pi*(49*x+32*(1-np.exp(-30*x))/30))
        if j:
            k=min(round(.23*sr),i);x=np.arange(k)/sr;noise=rng.normal(0,1,k);bins=np.fft.rfftfreq(k,1/sr);noise=np.fft.irfft(np.fft.rfft(noise)*np.exp(-((bins-2300)/1150)**2),k)
            a[i-k:i]+=.14*noise*np.sin(np.pi*x/max(.001,k/sr))**2
    a*=np.minimum(1,t/.08)*np.minimum(1,(dur-t)/.35);stereo=np.column_stack([a,np.roll(a,13)]);stereo[:13,1]=0
    with wave.open(str(out),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(np.int16(np.clip(stereo,-1,1)*32767).tobytes())
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('output',type=Path);a=p.parse_args();make(json.loads(a.project.read_text()),a.output)
