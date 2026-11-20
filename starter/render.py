#!/usr/bin/env python3
"""Deterministic fictional, SILENT typography/UI technique demo; not a production ad."""
import argparse,math,shutil,subprocess
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920; BG='#0D1015';FG='#F3F2EF';MUT='#8E96A4';ACC='#9DE5BA';FPS=30;N=240

def ease(x):x=max(0,min(1,x));return 1-(1-x)**3
def lerp(a,b,p):return a+(b-a)*p
@lru_cache(None)
def font(size):return ImageFont.truetype(FONT,size)
def label(d,xy,text,size,color=FG,anchor='lt'):
 d.text(xy,text,font=font(size),fill=color,anchor=anchor)
def reveal(im,text,x,y,size,p):
 if p<=0:return
 layer=Image.new('RGB',(W,size+25),BG);d=ImageDraw.Draw(layer);label(d,(x,round(35*(1-p))),text,size);im.paste(layer,(0,y))
def frame(f):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);label(d,(90,155),'FINDNOTE / DESIGN STUDY',34,MUT)
 # persistent line anchor; match title underline to search border.
 if f<60:
  reveal(im,'I know I',90,510,110,ease((f+1)/10));reveal(im,'saved this.',90,640,110,ease((f-9)/10));reveal(im,'Somewhere.',90,790,96,ease((f-24)/10));d=ImageDraw.Draw(im)
  p=ease((f-45)/14);d.rounded_rectangle((90,1000,990,1000+round(lerp(5,8,p))),radius=4,fill=ACC)
 elif f<150:
  q=f-60;p=ease(q/18);top=round(lerp(1000,720,p));d.rounded_rectangle((90,top,990,top+round(lerp(8,160,p))),radius=20,outline=ACC,width=6)
  if q>18:
   label(d,(120,top-75),'DEMO SEARCH',42,MUT);word='project';s=word[:max(0,min(len(word),(q-19)//4+1))];label(d,(130,top+52),s,68)
   x=130+round(d.textlength(s,font=font(68)));d.rectangle((x+6,top+48,x+10,top+120),fill=ACC)
  if q>=54:
   a=ease((q-54)/12);y=round(960+26*(1-a));d.rounded_rectangle((90,y,990,y+225),radius=28,fill='#1B2429');label(d,(125,y+35),'Project notes',65);label(d,(125,y+125),'Illustrative match',40,ACC)
 elif f<195:
  q=f-150;d.rounded_rectangle((90,720,990,880),radius=20,outline=ACC,width=6);label(d,(130,772),'project',68);d.rounded_rectangle((90,960,990,1185),radius=28,fill='#1B2429');label(d,(125,995),'Project notes',65);label(d,(125,1085),'Illustrative match',40,ACC)
  reveal(im,'There it is.',90,480,100,ease((q+1)/12))
 else:
  p=ease((f-195+1)/12);label(d,(540,850+round(15*(1-p))),'FindNote',135,ACC,anchor='mm');label(d,(540,1020),'Fictional technique demo',43,MUT,anchor='mm')
 return im

def main():
 global FONT
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--font',default='DejaVuSans-Bold.ttf');p.add_argument('--preview',action='store_true');p.add_argument('--frame',type=int);a=p.parse_args();FONT=a.font;font(50);a.output.parent.mkdir(parents=True,exist_ok=True)
 if a.frame is not None:
  if not 0<=a.frame<N:p.error('frame out of range')
  frame(a.frame).save(a.output);return
 ff=shutil.which('ffmpeg');
 if not ff:p.error('ffmpeg required')
 size=(540,960) if a.preview else (W,H);cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)]
 with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
  try:
   for f in range(N):
    im=frame(f)
    if a.preview:im=im.resize(size,Image.Resampling.LANCZOS)
    proc.stdin.write(im.tobytes())
  finally:proc.stdin.close()
  if proc.wait()!=0:raise SystemExit('ffmpeg failed')
 print(a.output)
if __name__=='__main__':main()
