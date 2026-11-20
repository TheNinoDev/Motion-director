#!/usr/bin/env python3
"""Frame-accurate proof board for shot entrances/landings and cut boundaries."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw
import cv2

def main():
 p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('video',type=Path);p.add_argument('out',type=Path);a=p.parse_args();d=json.loads(a.project.read_text());at=0;points={}
 for s in d['shots']:
  at-=s.get('transition_in',{}).get('frames',0);n=s['frames']
  for i in sorted({0,min(n-1,3),n//3,2*n//3,n-1}):points.setdefault(at+i,[]).append(s['id'])
  at+=n
 cap=cv2.VideoCapture(str(a.video));assert cap.isOpened(),'cannot open render';assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==at,'timeline/render frame mismatch';assert abs(cap.get(cv2.CAP_PROP_FPS)-d['fps'])<.01,'fps mismatch'
 w,h=192,342;board=Image.new('RGB',(w*5,(h+43)*math.ceil(len(points)/5)),(17,18,20));draw=ImageDraw.Draw(board)
 for j,(i,ids) in enumerate(sorted(points.items())):
  cap.set(cv2.CAP_PROP_POS_FRAMES,i);ok,fr=cap.read();assert ok,f'cannot decode {i}';im=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB));im.thumbnail((w,h));x=j%5*w;y=j//5*(h+43);board.paste(im,(x+(w-im.width)//2,y));draw.text((x+5,y+h+3),f'{i/d["fps"]:.2f}s  |  frame {i}',fill='white');draw.text((x+5,y+h+20),'/'.join(ids)[:25],fill='#a4a5ac')
 cap.release();board.save(a.out,quality=93);print(f'{len(points)} exact boundary/beat frames; manual visual review required')
if __name__=='__main__':main()
