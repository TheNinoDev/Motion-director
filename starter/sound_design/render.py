#!/usr/bin/env python3
"""Frame-accurate synthetic SFX stem; no borrowed samples, no narration or song replacement."""
import argparse,json,math,wave
from pathlib import Path
import numpy as np
SR=48000
KINDS={'click','impact','whoosh','chime','riser','drop',
       'snap','paper','brush','tick','rattle','glint','glitch','sweep','pulse'}

def sound(kind,n,rng):
    t=np.arange(n)/SR;u=np.arange(n)/max(1,n-1);noise=rng.normal(0,1,n)
    # Filter noise via FFT with gradual band limiting; fades below prevent clicks.
    f=np.fft.rfftfreq(n,1/SR);N=np.fft.rfft(noise)
    band=(1-np.exp(-(f/250)**2))*np.exp(-(f/6500)**2)
    filtered=np.fft.irfft(N*band,n);filtered/=max(.01,np.max(np.abs(filtered)))
    if kind=='click':x=(.55*np.sin(2*math.pi*1700*t)+.45*filtered)*np.exp(-u*9)
    elif kind=='impact':x=.8*np.sin(2*np.pi*(45*t+24*(1-np.exp(-t*24))/24))*np.exp(-u*5)+.2*filtered*np.exp(-u*16)
    elif kind=='drop':x=.85*np.sin(2*np.pi*(38*t+80*(1-np.exp(-t*12))/12))*np.exp(-u*4)
    elif kind in ('whoosh','riser'):
        env=np.sin(np.pi*u)**1.7 if kind=='whoosh' else u**1.8*(1-u**18)
        x=(.7*filtered+.25*np.sin(2*np.pi*(170*t+500*t*t/max(.01,t[-1]))))*env
    elif kind=='chime':x=(.55*np.sin(2*np.pi*740*t)+.28*np.sin(2*np.pi*1109*t)+.12*np.sin(2*np.pi*1480*t))*np.exp(-u*5)
    elif kind=='snap':
        # Dry contact: broadband initial crack, quick pitched wood/body resonance.
        x=(.78*filtered*np.exp(-u*19)+.24*np.sin(2*np.pi*210*t)*np.exp(-u*14))
    elif kind=='paper':
        # Soft layered rustle with uneven pressure and subtle stereo pan handled in render().
        breath=(np.sin(2*np.pi*(3.1*t+0.2*np.sin(2*np.pi*1.3*t)))**2)*.5+.30
        x=filtered*breath*np.sin(np.pi*u)**.35
    elif kind=='brush':
        # Brief directional friction/sweep; smooth attack, soft release.
        x=filtered*(np.sin(np.pi*u)**1.2)*(0.52+0.32*u)
    elif kind=='tick':
        # Tiny electronic/mechanical accent rather than a full-length chime.
        x=(.62*filtered+.40*np.sin(2*np.pi*2250*t))*np.exp(-u*24)
    elif kind=='rattle':
        # A short accelerating cascade of micro-contacts, not uniform white noise.
        phases=np.cumsum(7+19*u)/SR
        gate=(np.sin(2*np.pi*phases*SR/1000)>0.72).astype(float)
        x=filtered*gate*(np.sin(np.pi*u)**.7)
    elif kind=='glint':
        # Thin bright sparkle with two decays; not a high-energy impact.
        x=(.57*np.sin(2*np.pi*(1250*t+450*t*t/max(.01,t[-1])))
           +.23*np.sin(2*np.pi*1810*t))*np.exp(-u*6)
    elif kind=='glitch':
        # Distinct short chopped digital movement; no copyrighted sample.
        freq=220+310*(np.floor(u*11)%4)
        phase=2*np.pi*np.cumsum(freq)/SR
        gate=(np.mod(u*14,1)<.57).astype(float)
        x=(.72*np.sin(phase)+.31*filtered)*gate*(1-.32*u)
    elif kind=='sweep':
        # Thin tonal whoosh with a moving spectral center.
        phase=2*np.pi*(290*t+570*t*t/max(.01,t[-1]))
        x=(.42*filtered+.56*np.sin(phase))*np.sin(np.pi*u)**1.15
    elif kind=='pulse':
        # Controlled bass and soft transient for low-weight confirmations.
        phase=2*np.pi*(86*t+18*t*t/max(.01,t[-1]))
        x=(.90*np.sin(phase)+.12*filtered)*np.exp(-u*6)
    else:raise ValueError('unknown SFX '+kind)
    fade=min(n//3,round(SR*.006));x[:fade]*=np.linspace(0,1,fade);x[-fade:]*=np.linspace(1,0,fade);return x/ max(.1,np.max(np.abs(x)))

def render(d):
    fps=d['fps'];frames=d['frames']
    if type(fps) is not int or not 1<=fps<=60 or type(frames) is not int or not 1<=frames<=72000:raise ValueError('invalid timeline')
    if len(d['events'])>200:raise ValueError('too many events')
    n=round(frames*SR/fps);mix=np.zeros((n,2),np.float32);rng=np.random.default_rng(d.get('seed',111))
    for e in d['events']:
        fr=e['frame'];dur=e['duration_frames'];gain=e.get('gain_db',-16);pan=e.get('pan',0)
        if type(fr) is not int or not 0<=fr<frames or type(dur) is not int or not 1<=dur<=fps*4 or fr+dur>frames:raise ValueError('event outside timeline: '+str(e))
        if e['kind'] not in KINDS or not -45<=gain<=-3 or not -1<=pan<=1:raise ValueError('invalid effect, gain or pan')
        a=round(fr*SR/fps);b=round((fr+dur)*SR/fps);x=sound(e['kind'],b-a,rng)*10**(gain/20)
        angle=(pan+1)*math.pi/4;mix[a:b,0]+=x*math.cos(angle);mix[a:b,1]+=x*math.sin(angle)
    peak=float(np.max(np.abs(mix)));mix*=min(1,.75/max(peak,1e-8));return mix

def write(d,out):
    mix=render(d);out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(out),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(np.int16(np.clip(mix,-1,1)*32767).tobytes())
    return dict(samples=len(mix),peak=float(np.max(np.abs(mix))),duration=len(mix)/SR)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('output',type=Path);a=p.parse_args();print(json.dumps(write(json.loads(a.plan.read_text()),a.output)))
