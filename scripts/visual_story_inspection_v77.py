#!/usr/bin/env python3
"""Creates normal and headline-muted filmstrips from an actual MP4; cannot judge aesthetics."""
import argparse, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageStat

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("video",type=Path)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--step",type=float,default=1.0)
    p.add_argument("--width",type=int,default=180)
    args=p.parse_args(argv)
    if not args.video.is_file(): p.error("Missing video file")
    if not .2<=args.step<=10: p.error("Step must be .2 to 10 seconds")
    info=subprocess.run(["ffprobe","-v","error","-show_entries","stream=width,height:format=duration","-select_streams","v:0","-of","json",str(args.video)],capture_output=True,text=True,check=True)
    d=json.loads(info.stdout); w=args.width
    h=round(w*d["streams"][0]["height"]/d["streams"][0]["width"])
    fps=f"1/{args.step:g}" if args.step>=1 else str(1/args.step)
    cmd=["ffmpeg","-v","error","-i",str(args.video),"-vf",f"fps={fps},scale={w}:{h}", "-an","-pix_fmt","rgb24","-f","rawvideo","pipe:1"]
    frames=[]
    with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as process:
        n=w*h*3
        while 1:
            chunk=process.stdout.read(n)
            if not chunk: break
            if len(chunk)!=n: raise RuntimeError("Truncated frame")
            frames.append(Image.frombytes("RGB",(w,h),chunk))
        err=process.stderr.read()
        if process.wait(): raise RuntimeError(err.decode("utf8","replace"))
    if not frames: raise RuntimeError("No frames decoded")
    args.out.mkdir(parents=True,exist_ok=True)
    def write_contact(items,file):
        cols=6; extra=25
        board=Image.new("RGB",(cols*w,((len(items)+cols-1)//cols)*(h+extra)),"#161a20")
        dr=ImageDraw.Draw(board)
        for idx,img in enumerate(items):
            x=(idx%cols)*w; y=(idx//cols)*(h+extra)
            board.paste(img,(x,y));dr.text((x+6,y+h+4),f"{idx*args.step:.1f}s",fill="#ffffff")
        board.save(args.out/file)
    write_contact(frames,"normal-storyboard.png")
    muted=[]
    for fr in frames:
        img=fr.copy();bounds=(0,round(h*.10),w,round(h*.34))
        img.paste(fr.crop(bounds).filter(ImageFilter.GaussianBlur(radius=max(10,w//11))),bounds)
        muted.append(img)
    write_contact(muted,"title-muted-storyboard.png")
    diff=[round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,3) for a,b in zip(frames,frames[1:])]
    report={"source":str(args.video),"count":len(frames),"duration_seconds":float(d["format"]["duration"]),"sample_step":args.step,
    "difference_diagnostic_only":diff,"important":"No automated aesthetic rating. Inspect both sheets and original video at 1x with audio."}
    (args.out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"normal":str(args.out/"normal-storyboard.png"),"muted":str(args.out/"title-muted-storyboard.png"),"count":len(frames)}))
    return 0

if __name__=="__main__":
    try: sys.exit(main())
    except (subprocess.SubprocessError,ValueError,KeyError,RuntimeError) as err:
        print("ERROR",err,file=sys.stderr);sys.exit(2)
