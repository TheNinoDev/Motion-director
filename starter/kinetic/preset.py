#!/usr/bin/env python3
"""Build a portable four-shot kinetic study. Use actual copy, screenshot and audio durations."""
import argparse,json,shutil
from pathlib import Path

def main():
 a=argparse.ArgumentParser(description=__doc__)
 for x in ('hook','glyph','proof','brand','cta','screenshot','out'):a.add_argument('--'+x,required=True)
 a.add_argument('--words',nargs='+',required=True);a.add_argument('--frames',nargs=4,type=int,required=True);a.add_argument('--field',choices=['vortex','wave','burst','helix','grid'],default='vortex');a.add_argument('--layout',choices=['stack','split','track'],default='split');a.add_argument('--mask',choices=['diagonal','iris','split','horizontal'],default='diagonal');a.add_argument('--accent',default='#bdb0ff');a.add_argument('--crop',nargs=4,type=float,default=[0,0,1,1]);a.add_argument('--width',type=int,default=1080);a.add_argument('--height',type=int,default=1920);a.add_argument('--fps',type=int,default=30);a.add_argument('--count',type=int,default=3600);a.add_argument('--samples',type=int,default=2);v=a.parse_args()
 if not 1<=len(v.words)<=5 or min(v.frames)<4 or not 1<=len(v.glyph)<=12:raise ValueError('invalid words, glyph or durations')
 out=Path(v.out).resolve();out.parent.mkdir(parents=True,exist_ok=True);src=Path(v.screenshot).resolve();dst=out.parent/'assets'/src.name;dst.parent.mkdir(exist_ok=True); 
 if src!=dst:shutil.copy2(src,dst)
 common={'accent':v.accent};contents=[dict(common,kind='field',field=v.field,glyph=v.glyph,text=v.hook,count=v.count,samples=v.samples,spread=[[0,0],[.18,0],[.9,1],[1,1]],yaw=[[0,.7],[1,0]],zoom=[[0,1.4],[1,1.05]]),dict(common,kind='type',words=v.words,layout=v.layout),dict(common,kind='proof',src=str(dst.relative_to(out.parent)),crop=v.crop,mask=v.mask,text=v.proof,focus=[[0,0],[.2,0],[.85,1],[1,1]]),dict(common,kind='lockup',brand=v.brand,sub=v.cta)]
 d={'version':1,'width':v.width,'height':v.height,'fps':v.fps,'shots':[{'id':s,'engine':'kinetic','frames':n,'content':c} for s,n,c in zip(('hook','reset','proof','end'),v.frames,contents)]};out.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8');print(out)
if __name__=='__main__':main()
