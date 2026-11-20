#!/usr/bin/env python3
"""Create editable five-shot editorial scaffold; no new copy or claims inferred."""
import argparse,json,shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--hook',required=True);p.add_argument('--tension',required=True);p.add_argument('--reveal',required=True);p.add_argument('--proof',required=True);p.add_argument('--brand',required=True);p.add_argument('--cta',required=True);p.add_argument('--screenshot',type=Path,required=True);p.add_argument('--crop',type=float,nargs=4,required=True);p.add_argument('--crop2',type=float,nargs=4,required=True);p.add_argument('--frames',type=int,nargs=5,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--bg',default='#101110');p.add_argument('--fg',default='#f0eee7');p.add_argument('--accent',default='#d8e986');p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920);p.add_argument('--fps',type=int,default=30);a=p.parse_args()
 if not a.screenshot.is_file():p.error('Actual screenshot required')
 if min(a.frames)<4 or max(a.frames)>3600:p.error('invalid frames')
 if any(not(0<=r[0]<r[2]<=1 and 0<=r[1]<r[3]<=1) for r in (a.crop,a.crop2)):p.error('invalid crop')
 if a.width%2 or a.height%2 or not(160<=a.width<=2160 and 160<=a.height<=3840 and 1<=a.fps<=60):p.error('invalid render dimensions or fps')
 if any(not t.strip() or len(t)>40 for t in (a.hook,a.tension)) or any(not t.strip() or len(t)>100 for t in (a.reveal,a.proof,a.brand,a.cta)):p.error('empty or excessive copy')
 a.out.parent.mkdir(parents=True,exist_ok=True);assets=a.out.parent/'assets';assets.mkdir(exist_ok=True);dst=assets/(a.out.stem+'-product'+a.screenshot.suffix);src=a.screenshot.resolve()
 if dst.resolve()!=src:
  if dst.exists() and dst.read_bytes()!=src.read_bytes():p.error('asset destination exists with different bytes; choose new output')
  if not dst.exists():shutil.copy2(src,dst)
 path=dst.relative_to(a.out.parent).as_posix();common=dict(bg=a.bg,fg=a.fg,accent=a.accent,grain=.4)
 def shot(id,n,kind,**kw):return dict(id=id,frames=n,engine='editorial',content=dict(common,kind=kind,**kw))
 shots=[shot('hook',a.frames[0],'wall',lines=[a.hook,a.tension],repeat=a.hook+' / ',reveal='glyph',label=a.brand),shot('reveal',a.frames[1],'shutter',src=path,crop=a.crop,text=a.reveal),shot('detail',a.frames[2],'macro',src=path,crop=a.crop2,crop2=a.crop2,text=a.proof),shot('proof',a.frames[3],'folio',src=path,crop=a.crop,crop2=a.crop2,text=a.proof),shot('cta',a.frames[4],'signature',brand=a.brand,sub=a.cta)]
 a.out.write_text(json.dumps(dict(version=1,width=a.width,height=a.height,fps=a.fps,shots=shots),indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()
