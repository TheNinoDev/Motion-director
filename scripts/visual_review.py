#!/usr/bin/env python3
"""Sample-based technical visual diagnostics. Never certifies taste or release readiness."""
import argparse,json,math
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw

def review(path,out,step=3):
    out.mkdir(parents=True,exist_ok=True);cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS);w=int(cap.get(3));h=int(cap.get(4));reported=int(cap.get(7));assert fps>0 and w>0 and h>0
    samples=[];thumb=[];prev=None;index=0;still=[];black=[];cuts=[];deltas=[];mov=[]
    while True:
        ok,frame=cap.read()
        if not ok:break
        if index%step==0:
            small=cv2.resize(frame,(180,320),interpolation=cv2.INTER_AREA);g=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY);edge=cv2.Laplacian(g,cv2.CV_32F);lit=float(np.mean(g>24));clipped=float(np.mean(g>=250));mean=float(g.mean());delta=None;changed=None
            if prev is not None:
                diff=cv2.absdiff(g,prev);delta=float(diff.mean());changed=float(np.mean(diff>12));deltas.append(delta);mov.append(changed)
                if delta<.35 and changed<.005:still.append(index)
                if delta>25 and changed>.42:cuts.append(index)
            if mean<3 and lit<.01:black.append(index)
            samples.append(dict(frame=index,seconds=round(index/fps,3),mean_luma=round(mean,2),lit_fraction=round(lit,4),highlight_fraction=round(clipped,4),edge_variance=round(float(edge.var()),2),delta=round(delta,3) if delta is not None else None,changed_fraction=round(changed,4) if changed is not None else None));prev=g
            if index%max(step,round(fps/step)*step//2)==0:thumb.append((index,Image.fromarray(cv2.cvtColor(small,cv2.COLOR_BGR2RGB))))
        index+=1
    cap.release();assert samples,'no decoded frames'
    def ranges(a):
        seq=[]
        for f in a:
            if seq and f-seq[-1][-1]<=step:seq[-1].append(f)
            else:seq.append([f])
        return [dict(start=round(max(0,x[0]-step)/fps,2),end=round((x[-1]+step)/fps,2),samples=len(x)) for x in seq if len(x)*step/fps>=.25]
    board=Image.new('RGB',(4*190,math.ceil(len(thumb)/4)*342),(16,17,21));draw=ImageDraw.Draw(board)
    for j,(i,img) in enumerate(thumb):x=j%4*190;y=j//4*342;board.paste(img,(x+5,y));draw.text((x+5,y+322),f'{i/fps:.2f}s  f{i}',fill='white')
    board.save(out/'contact-sheet.jpg',quality=92)
    report=dict(source=str(path),width=w,height=h,fps=fps,decoded_frames=index,reported_frames=reported,duration=index/fps,sample_stride=step,mean_frame_delta=round(float(np.mean(deltas)),3) if deltas else None,mean_changed_fraction=round(float(np.mean(mov)),4) if mov else None,low_motion_ranges=ranges(still),near_black_ranges=ranges(black),possible_hard_cuts=[round(i/fps,2) for i in cuts],samples=samples,manual_review=['Check opening at 0.2 and 0.8 seconds for meaningful composition and hook.','Review every change of focal point, intentional holds, clipping, UI fidelity, text size, contrast and continuity at full and phone size.','Inspect contact sheet and playback: high motion score is not quality. Do not optimize score; fix actual issue.','Review real VO/music audibly; no evidence of creative quality or release approval is inferred.'])
    (out/'visual-review.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('output',type=Path);p.add_argument('--step',type=int,default=3);a=p.parse_args();assert 1<=a.step<=30;d=review(a.video,a.output,a.step);print(json.dumps({k:v for k,v in d.items() if k!='samples'},indent=2))
