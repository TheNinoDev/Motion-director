#!/usr/bin/env python3
"""Deterministic, silent chart/metric/reset demonstration; not a finished ad."""
import argparse,json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W,H=540,960

def font(size,mono=False):
 name='DejaVuSansMono.ttf' if mono else 'DejaVuSans-Bold.ttf'
 try:return ImageFont.truetype(name,size)
 except OSError:raise RuntimeError('Install DejaVu fonts or explicitly adapt font loader; no tiny fallback.')
def ease(p):return 1-(1-max(0,min(1,p)))**3

def frame(values,label,unit,t):
 im=Image.new('RGB',(W,H),(12,14,17));d=ImageDraw.Draw(im); white=(240,241,243); muted=(153,161,172); accent=(116,221,195)
 d.text((45,65),'MOTION LAB / DEMO',font=font(15,True),fill=muted);d.line((45,94,495,94),fill=(49,55,62),width=1)
 d.text((45,862),'ILLUSTRATIVE DATA',font=font(20,True),fill=muted)
 maxv=max(values);base=740;left=55;right=485;top=425
 pts=[(left+(right-left)*i/(len(values)-1),base-(base-top)*v/maxv) for i,v in enumerate(values)]
 if t<2.5:
  d.text((45,175),label,font=font(34),fill=white)
  p=ease((t-.15)/1.75)*(len(values)-1);idx=min(int(p),len(values)-2);q=p-idx
  end=tuple(pts[idx][j]+(pts[idx+1][j]-pts[idx][j])*q for j in (0,1));v=values[idx]+(values[idx+1]-values[idx])*q
  path=pts[:idx+1]+[end]
  d.text((45,250),f'{v:.1f} {unit}',font=font(45,True),fill=white)
  for y in range(top,base+1,63):d.line((left,y,right,y),fill=(35,42,47))
  d.polygon([(left,base)]+path+[(end[0],base)], fill=(25,51,49));d.line(path,fill=accent,width=3);d.ellipse((end[0]-4,end[1]-4,end[0]+4,end[1]+4),fill=white)
 elif t<4.5:
  d.text((45,175),'Same series',font=font(40),fill=white);d.text((45,245),f'{unit} per sample',font=font(20),fill=muted)
  gap=(right-left)/len(values)
  for i,v in enumerate(values):
   y=base-(base-top)*v/maxv*ease((t-2.5-i*.065)/.45);x=left+i*gap
   d.rectangle((x,y,x+gap*.66,base),fill=accent if i==len(values)-1 else (110,126,139))
 else:
  d.text((W/2,380),'Final sample',font=font(31),fill=muted,anchor='mm');d.text((W/2,475),str(values[-1]),font=font(112,True),fill=white,anchor='mm');d.text((W/2,559),unit,font=font(25),fill=muted,anchor='mm')
 return im

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('config',type=Path);p.add_argument('output',type=Path);a=p.parse_args();c=json.loads(a.config.read_text());v=c['values'];fps=c.get('fps',30)
 if c.get('illustrative') is not True:raise SystemExit('Demo accepts illustrative data only; adapt explicitly for evidence-backed use.')
 if not isinstance(fps,int) or not 1<=fps<=60 or not 2<=len(v)<=12 or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in v) or max(v)<=0:raise SystemExit('Invalid series or fps')
 if len(c['label'])>23 or len(c['unit'])>12:raise SystemExit('Demo label/unit too wide')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],stdin=subprocess.PIPE)
 try:
  for i in range(fps*6):proc.stdin.write(frame(v,c['label'],c['unit'],i/fps).tobytes())
 finally:
  proc.stdin.close();rc=proc.wait()
 if rc:raise SystemExit(rc)
if __name__=='__main__':main()
