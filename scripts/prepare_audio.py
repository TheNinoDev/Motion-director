#!/usr/bin/env python3
"""Offline SCRATCH TTS, measured phrase offsets, optional music mix. Not premium TTS or ASR."""
import argparse,json,re,shutil,subprocess,tempfile,wave
from pathlib import Path

def run(args):subprocess.run([str(x) for x in args],check=True)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('script',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--music',type=Path);p.add_argument('--waive-music',action='store_true');p.add_argument('--voice',default='en-us');p.add_argument('--rate',type=int,default=155);p.add_argument('--lead',type=float,default=.15);p.add_argument('--tail',type=float,default=1.8);p.add_argument('--scratch-approved',action='store_true');a=p.parse_args()
 if not a.scratch_approved:p.error('Local espeak is robotic scratch only; explicitly approve --scratch-approved')
 if bool(a.music)==bool(a.waive_music):p.error('Provide exactly one --music or --waive-music')
 if not 80<=a.rate<=250 or not 0<=a.lead<=5 or not 0<=a.tail<=10:p.error('invalid rate or lead/tail')
 tts=shutil.which('espeak-ng') or shutil.which('espeak');ff=shutil.which('ffmpeg')
 if not tts or not ff:p.error('Need espeak(-ng) and ffmpeg installed')
 text=a.script.read_text(encoding='utf8').strip();phrases=[s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+',text) if s.strip()]
 if not phrases:p.error('empty script')
 a.out.mkdir(parents=True,exist_ok=True);voice=a.out/'voiceover.wav';mix=a.out/'mix.wav';timings=[];rate=48000;pos=round(a.lead*rate)
 with tempfile.TemporaryDirectory() as td, wave.open(str(voice),'wb') as dest:
  dest.setparams((1,2,rate,0,'NONE','not compressed'));dest.writeframes(b'\0\0'*pos)
  for i,phrase in enumerate(phrases):
   inp=Path(td)/'phrase.txt';raw=Path(td)/'raw.wav';norm=Path(td)/'norm.wav';inp.write_text(phrase,encoding='utf8')
   run([tts,'-v',a.voice,'-s',a.rate,'-w',raw,'-f',inp]);run([ff,'-y','-v','error','-i',raw,'-ar',rate,'-ac','1','-c:a','pcm_s16le',norm])
   with wave.open(str(norm),'rb') as src:n=src.getnframes();data=src.readframes(n)
   timings.append({'id':f'p{i+1}','text':phrase,'start':pos/rate,'end':(pos+n)/rate});dest.writeframes(data);pos+=n
  tail=round(a.tail*rate);dest.writeframes(b'\0\0'*tail);pos+=tail
 dur=pos/rate
 if a.music:
  music=a.out/'music-edit.wav';run([ff,'-y','-v','error','-i',a.music,'-t',str(dur),'-af',f'apad,afade=t=out:st={max(0,dur-.8)}:d={min(.8,dur)}','-ar',rate,'-ac','2','-c:a','pcm_s16le',music]);run([ff,'-y','-v','error','-i',voice,'-i',music,'-filter_complex','[0:a]aformat=channel_layouts=stereo,asplit[v][key];[1:a]volume=-15dB[m];[m][key]sidechaincompress=threshold=0.035:ratio=5:attack=30:release=300[d];[v][d]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=0','-ar',rate,'-ac','2','-c:a','pcm_s16le',mix])
 else:run([ff,'-y','-v','error','-i',voice,'-ac','2','-af','alimiter=limit=0.89:level=0','-c:a','pcm_s16le',mix])
 def ts(s):
  ms=round(s*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{sec:02},{ms:03}'
 (a.out/'phrases.srt').write_text('\n\n'.join(f'{i+1}\n{ts(q["start"])} --> {ts(q["end"])}\n{q["text"]}' for i,q in enumerate(timings))+'\n',encoding='utf8')
 (a.out/'alignment.json').write_text(json.dumps({'method':'espeak per phrase PCM boundaries (including synthesis silence); no word alignment','quality':'scratch only','duration':dur,'music_waived':a.waive_music,'phrases':timings},indent=2),encoding='utf8');print(f'Scratch audio: {dur:.3f}s; audition and measure before release: {mix}')
if __name__=='__main__':main()
