#!/usr/bin/env python3
"""Create review-only before/mid/after and cross-seam contact sheets for an actual film.

No automated score claims that high pixel activity implies good editing.
Usage: python scripts/film_rehearsal_v73.py film.mp4 --plan plan.json --out review
Requires ffmpeg, ffprobe and Pillow. Safe to run on user-provided media; no network.
"""
import argparse
import io
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont


def validate_plan(plan, duration):
    shots=plan.get('shots',[])
    if not isinstance(shots,list) or not shots:raise ValueError('plan must have at least one shot')
    prev=0.
    for i,s in enumerate(shots):
        a,b=s.get('start'),s.get('end')
        if not isinstance(a,(float,int)) or isinstance(a,bool) or not isinstance(b,(float,int)) or isinstance(b,bool):
            raise ValueError(f'shot {i}: start/end must be numbers')
        if a<0 or b<=a or b>duration+0.15:raise ValueError(f'shot {i}: invalid time interval {a}..{b}')
        if a<prev-0.05:raise ValueError(f'shot {i}: intervals out of order or overlapping')
        if a>prev+.10:raise ValueError(f'shot {i}: unexplained timeline gap of {a-prev:.2f}s')
        prev=b
    return shots


def ffprobe_duration(video):
    cmd=['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(video)]
    r=subprocess.run(cmd,check=True,capture_output=True,text=True)
    return float(r.stdout.strip())


def get_frame(video,secs,width=200):
    cmd=['ffmpeg','-nostdin','-v','error','-ss',f'{secs:.3f}','-i',str(video),'-frames:v','1',
         '-vf',f'scale={width}:-1','-f','image2pipe','-c:v','mjpeg','-']
    r=subprocess.run(cmd,check=True,capture_output=True)
    im=Image.open(io.BytesIO(r.stdout)).convert('RGB')
    return im.copy()


def font(size=18):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf']:
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()


def build_sheet(video,times,labels,dest,cols=3,width=200):
    frames=[get_frame(video,t,width=width) for t in times]
    height=max(im.height for im in frames); rows=(len(frames)+cols-1)//cols
    sheet=Image.new('RGB',(cols*width,rows*(height+28)),(15,16,23));d=ImageDraw.Draw(sheet);f=font(14)
    for i,im in enumerate(frames):
        x=(i%cols)*width;y=(i//cols)*(height+28)
        sheet.paste(im,(x,y));d.text((x+5,y+height+3),labels[i][:26],font=f,fill=(245,245,245))
    dest.parent.mkdir(parents=True,exist_ok=True);sheet.save(dest,quality=92)
    return str(dest)


def generate(video,plan,out):
    if not Path(video).is_file():raise FileNotFoundError(video)
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise RuntimeError('ffmpeg and ffprobe required')
    dur=ffprobe_duration(video);shots=validate_plan(plan,dur)
    triples=[];labels=[]
    for i,s in enumerate(shots):
        a,b=float(s['start']),float(s['end']);delta=min(.25,(b-a)*.15)
        for position,t in [('before',a+delta),('middle',(a+b)/2),('after',b-delta)]:
            triples.append(t);labels.append(f'{i+1}:{position} {t:.2f}s')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    f1=build_sheet(video,triples,labels,out/'shot-triptychs.jpg',cols=3)
    seam_times=[];seam_labels=[]
    for i in range(len(shots)-1):
        t=float(shots[i]['end'])
        for offset in [-.30,-.08,.08,.30]:
            z=max(0,min(dur-.02,t+offset));seam_times.append(z);seam_labels.append(f'seam {i+1} {offset:+.2f}s')
    f2=None
    if seam_times:f2=build_sheet(video,seam_times,seam_labels,out/'scene-seams.jpg',cols=4)
    report={'duration':dur,'shots':len(shots),'seams':max(0,len(shots)-1),'triptych':f1,'seam_sheet':f2,
       'decision':'Manual real-time editorial acceptance required. These sheets do not rate creativity.',
       'questions':['Does each subject visibly change state?','Does each scene hand something meaningful to the next?',
       'Can the film be understood without small labels/icons?','Is the weakest shot revised, not decorated?']}
    (out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('film',type=Path);p.add_argument('--plan',required=True,type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();res=generate(a.film,json.loads(a.plan.read_text(encoding='utf8')),a.out)
    print(json.dumps(res,indent=2))

if __name__=='__main__':main()