#!/usr/bin/env python3
"""Report candidate long low-change intervals in real decoded MP4s (FFmpeg + numpy).

An editorial lead generator, not a motion-quality score or a ban on intentional holds.
"""
import argparse, json, math, shutil, subprocess, sys
from pathlib import Path
try:
    import numpy as np
except ImportError:
    raise SystemExit("Install numpy before using hold_audit_v65.py")

def detect(means, regions, fps, max_hold=.85, diff_threshold=2.0, region_threshold=.04):
    spans=[]; start=None
    for i,(mean,region) in enumerate(zip(means,regions)):
        inactive=mean<diff_threshold and region<region_threshold
        if inactive and start is None: start=i
        if not inactive and start is not None:
            if (i-start)/fps>=max_hold:
                spans.append({"start":round(start/fps,3),"end":round(i/fps,3),"duration":round((i-start)/fps,3)})
            start=None
    if start is not None and (len(means)-start)/fps>=max_hold:
        spans.append({"start":round(start/fps,3),"end":round(len(means)/fps,3),"duration":round((len(means)-start)/fps,3)})
    return spans

def measure(video,fps=10,width=160,pixel_cutoff=8):
    if not shutil.which("ffmpeg"): raise RuntimeError("ffmpeg is not on PATH")
    height=round(width*16/9)
    if height%2: height+=1
    size=width*height
    cmd=["ffmpeg","-v","error","-i",str(video),"-an","-vf",f"fps={fps},scale={width}:{height}","-pix_fmt","gray","-f","rawvideo","-"]
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    prev=None;means=[];regions=[];frames=0
    while True:
        buff=p.stdout.read(size)
        if not buff:break
        if len(buff)!=size: raise RuntimeError("incomplete decoded frame")
        frame=np.frombuffer(buff,dtype=np.uint8).astype(np.int16)
        if prev is not None:
            diff=np.abs(frame-prev)
            means.append(float(diff.mean()))
            regions.append(float(np.count_nonzero(diff>pixel_cutoff)/size))
        prev=frame;frames+=1
    p.stdout.close();err=p.stderr.read().decode("utf8",errors="replace")
    if p.wait()!=0:raise RuntimeError("ffmpeg decode failed: "+err[:250])
    if frames<2:raise RuntimeError("not enough decoded frames")
    return means,regions,frames

def apply_allowlist(intervals,data):
    holds=data.get("holds",[])
    if not isinstance(holds,list):raise ValueError("holds must be an array")
    for h in holds:
        if not isinstance(h,dict) or not all(k in h for k in ("start","end","reason")):raise ValueError("hold requires start, end, reason")
        if not isinstance(h["reason"],str) or len(h["reason"].strip())<12:raise ValueError("specific hold justification required")
        if not all(isinstance(h[k],(int,float)) and math.isfinite(h[k]) for k in ("start","end")) or h["start"]<0 or h["end"]<=h["start"]:
            raise ValueError("invalid intentional hold range")
    for s in intervals:
        found=next((h for h in holds if h["start"]<=s["start"]+.12 and h["end"]>=s["end"]-.12),None)
        s["approved_hold"]=bool(found)
        if found:s["reason"]=found["reason"]
    return intervals

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("video",type=Path);p.add_argument("--fps",type=float,default=10.)
    p.add_argument("--width",type=int,default=160);p.add_argument("--max-hold",type=float,default=.85)
    p.add_argument("--diff-threshold",type=float,default=2.0)
    p.add_argument("--region-threshold",type=float,default=.04)
    p.add_argument("--allow",type=Path)
    p.add_argument("--report",type=Path)
    p.add_argument("--strict",action="store_true")
    a=p.parse_args(argv)
    if a.fps<=0 or a.fps>60 or a.width<64 or a.max_hold<=0:p.error("invalid scan options")
    if not a.video.is_file():p.error("video not found")
    means,regions,frames=measure(a.video,a.fps,a.width)
    spans=detect(means,regions,a.fps,a.max_hold,a.diff_threshold,a.region_threshold)
    allow=json.loads(a.allow.read_text(encoding="utf8")) if a.allow else {"holds":[]}
    spans=apply_allowlist(spans,allow)
    outstanding=[s for s in spans if not s["approved_hold"]]
    report={"file":str(a.video),"sample_fps":a.fps,"decoded_samples":frames,
            "estimated_duration":round(frames/a.fps,2),
            "pct_low_change_transitions":round(100*sum(m<a.diff_threshold and r<a.region_threshold for m,r in zip(means,regions))/len(means),1),
            "definition":"low grayscale mean delta and small changed area; subjective film review required",
            "flagged_intervals":spans,"pending_review":len(outstanding),
            "note":"Flagged does not mean bad. Review real playback and actual audio."}
    output=json.dumps(report,indent=2,ensure_ascii=False)
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(output+"\n",encoding="utf8")
    print(output)
    return 2 if a.strict and outstanding else 0

if __name__=="__main__":sys.exit(main())
