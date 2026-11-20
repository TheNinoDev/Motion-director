#!/usr/bin/env python3
"""Decode actual frames, flag near-duplicates and abrupt motion changes. No aesthetic scoring."""
import argparse,json,math
from pathlib import Path
import cv2,numpy as np

def scan(path):
 cap=cv2.VideoCapture(str(path)); fps=cap.get(cv2.CAP_PROP_FPS)
 if not cap.isOpened() or not math.isfinite(fps) or fps<=0:raise ValueError('cannot decode video / fps')
 prev=None; rows=[];i=0;cv2.setNumThreads(1)
 while True:
  ok,frame=cap.read()
  if not ok:break
  cur=cv2.resize(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(144,256),interpolation=cv2.INTER_AREA)
  if prev is not None:
   delta=float(np.abs(cur.astype(np.float32)-prev).mean()); flow=cv2.calcOpticalFlowFarneback(prev,cur,None,.5,2,13,2,5,1.1,0); mag=np.linalg.norm(flow,axis=2); rows.append({'frame':i,'seconds':round(i/fps,4),'delta':round(delta,4),'flow_p90':round(float(np.percentile(mag,90)),4)})
  prev=cur;i+=1
 cap.release()
 if i<2:raise ValueError('video has fewer than two frames')
 cuts=[r for r in rows if r['delta']>=21]; spikes=[]
 for a,b,c in zip(rows,rows[1:],rows[2:]):
  if b['delta']<21 and b['flow_p90']>2.5 and b['flow_p90']>3*max(.2,a['flow_p90'],c['flow_p90']):spikes.append(b)
 holds=[];start=None
 for k,r in enumerate(rows+[{'delta':999}]):
  if r['delta']<.15:
   if start is None:start=k
  elif start is not None:
   if k-start>=max(3,round(.25*fps)):holds.append({'start':rows[start]['seconds'],'end':rows[k-1]['seconds'],'frames':k-start})
   start=None
 return {'fps':fps,'decoded_frames':i,'duration_seconds':i/fps,'cuts_or_large_changes':cuts,'isolated_flow_spikes':spikes,'near_static_intervals':holds,'note':'heuristic inspection cues, not aesthetic judgments; intentional cuts and holds are allowed; low-detail scenes and motion blur can distort optical flow.'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('video',type=Path);ap.add_argument('report',type=Path);a=ap.parse_args();a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(scan(a.video),indent=2))
