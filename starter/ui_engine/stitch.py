#!/usr/bin/env python3
"""Normalize silent rendered shots to exact frame counts then concatenate; optional pre-aligned audio."""
import argparse,json,pathlib,subprocess,tempfile
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('plan',type=P);p.add_argument('output',type=P);p.add_argument('--audio',type=P);a=p.parse_args();d=json.loads(a.plan.read_text());root=a.plan.resolve().parent;w,h,fps=(d[k] for k in ('width','height','fps'));assert all(isinstance(v,int) and v>0 for v in (w,h,fps)) and w%2==h%2==0
assert d['clips'],'no clips'; a.output.parent.mkdir(parents=True,exist_ok=True)
def run(args):subprocess.run(['ffmpeg','-v','error','-y']+args,check=True)
def dur(path):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))
with tempfile.TemporaryDirectory() as td:
    t=P(td); total=0; files=[]
    for i,c in enumerate(d['clips']):
        src=root/c['src']; n=c['frames']; start=float(c.get('start',0)); assert isinstance(n,int) and n>0 and start>=0 and src.is_file();assert dur(src)+.01>=start+n/fps,'clip too short; do not silently freeze';out=t/f'{i:04d}.mp4'
        vf=f'fps={fps},scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1'
        run(['-ss',str(start),'-i',str(src),'-an','-vf',vf,'-frames:v',str(n),'-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','fast',str(out)])
        actual=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames','-of','default=nw=1:nk=1',str(out)]));assert actual==n,f'clip {i}: {actual} vs {n} frames'; files.append(out.name);total+=n
    (t/'list.txt').write_text(''.join(f"file '{f}'\n" for f in files));cmd=['-f','concat','-safe','1','-i',str(t/'list.txt')]
    if a.audio:
        assert abs(dur(a.audio)-total/fps)<=max(.1,2/fps),'audio duration mismatch';cmd+=['-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k']
    cmd+=['-c:v','copy','-movflags','+faststart',str(a.output)];run(cmd)
print(f'{total} frames / {total/fps:.3f}s')
