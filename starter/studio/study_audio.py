"""Original synthetic study bed, never a replacement for commissioned music or VO."""
import argparse,wave
import numpy as np

def create(out,duration=8.7):
    sr=48000;n=round(duration*sr);t=np.arange(n)/sr;rng=np.random.default_rng(91);mix=np.zeros(n)
    for f,amp in [(65.406,.058),(98,.021),(130.812,.018),(196,.012)]:
        mix+=amp*np.sin(2*np.pi*f*t+.25*np.sin(2*np.pi*.27*t))*(.75+.25*np.sin(t*.8))
    for start,f in [(0,261.626),(1.5,293.665),(2.8,220),(5.3,329.628),(6.7,261.626)]:
        i=round(start*sr)
        if i>=n:continue
        x=np.arange(n-i)/sr;env=(1-np.exp(-x*30))*np.exp(-x*3.5);mix[i:]+=.05*env*(np.sin(2*np.pi*f*x)+.22*np.sin(2*np.pi*2.01*f*x))
    for start in [0,1.5,1.94,2.36,2.8,5.3,6.7]:
        i=round(start*sr)
        if i>=n:continue
        size=min(round(.24*sr),n-i);x=np.arange(size)/sr;env=np.exp(-x*24)*(1-np.exp(-x*600));mix[i:i+size]+=.12*env*np.sin(2*np.pi*(50*x+37*(1-np.exp(-x*32))/32))
    for start in [1.29,2.59,5.09,6.49]:
        i=round(start*sr)
        if i>=n:continue
        size=min(round(.21*sr),n-i);x=np.arange(size)/sr;noise=rng.normal(0,1,size);f=np.fft.rfftfreq(size,1/sr);noise=np.fft.irfft(np.fft.rfft(noise)*np.exp(-((f-2100)/1000)**2),size);mix[i:i+size]+=.16*noise*np.sin(np.pi*x/.21)**2
    envelope=np.minimum(1,t/.08)*np.minimum(1,(duration-t)/.4);mix*=envelope
    stereo=np.column_stack([mix,np.roll(mix,12)]);stereo[:12,1]=0
    with wave.open(str(out),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(np.int16(np.clip(stereo,-1,1)*32767).tobytes())
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--duration',type=float,default=8.7);a=p.parse_args();create(a.output,a.duration)
