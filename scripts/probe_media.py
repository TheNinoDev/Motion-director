#!/usr/bin/env python3
"""Probe media and optionally estimate audio onset candidates; no third-party Python packages."""
import argparse, array, json, math, statistics, subprocess, sys
from pathlib import Path

def run(args):
    return subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def analyze(path, audio=False):
    result = json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
    if not audio: return result
    rate=16000; hop=320
    pcm=array.array('h'); pcm.frombytes(run(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar',str(rate),'-f','s16le','-']))
    if sys.byteorder != 'little': pcm.byteswap()
    rms=[]
    for i in range(0,len(pcm),hop):
        chunk=pcm[i:i+hop]
        if len(chunk): rms.append(math.sqrt(sum(x*x for x in chunk)/len(chunk))/32768)
    # Simple positive log-energy changes; not a spectral onset detector or BPM estimator.
    flux=[0.0]+[max(0,math.log1p(100*rms[i])-math.log1p(100*rms[i-1])) for i in range(1,len(rms))] if rms else []
    candidates=[]
    for i in range(1,len(flux)-1):
        window=flux[max(0,i-25):i+26]; med=statistics.median(window)
        mad=statistics.median(abs(x-med) for x in window)
        if flux[i]>max(0.12,med+3*mad) and flux[i]>=flux[i-1] and flux[i]>flux[i+1] and (not candidates or i*hop/rate-candidates[-1]['time']>=0.12):
            candidates.append({'time':round(i*hop/rate,3),'strength':round(flux[i],4)})
    result['audio_analysis']={'method':'20 ms mono log RMS energy change; unverified onset candidates, not beats or speech alignment','duration_seconds':len(pcm)/rate,'sample_peak_dbfs':round(20*math.log10(max(max(map(abs,pcm),default=0)/32768,1e-9)),2),'onset_candidates':candidates}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('media',type=Path);p.add_argument('--audio',action='store_true');p.add_argument('-o','--output',type=Path);a=p.parse_args()
    try: data=json.dumps(analyze(a.media,a.audio),indent=2)
    except (OSError,subprocess.CalledProcessError,ValueError) as e: p.exit(1,f'Probe failed: {e}\n')
    if a.output: a.output.write_text(data+'\n',encoding='utf-8')
    else: print(data)
if __name__=='__main__': main()
