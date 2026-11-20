#!/usr/bin/env python3
"""Static layer-plan warnings. Approximate projected bounds, not pixel inspection."""
import argparse,importlib.util,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('layer_engine',ROOT/'starter/layer_motion/render.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
def audit(d):
    issues=[]
    for shot in d['shots']:
        if shot['engine']!='layers':continue
        c=shot['content'];n=shot['frames'];cam=c.get('camera',{});fps=d['fps']
        for l in c['layers']:
            if l['kind']!='text' or l.get('decorative',False):continue
            o=[];small=[]
            for f in range(l.get('start',0),l.get('end',n),max(1,round(fps/10))):
                v=lambda key,default:r.value(l.get(key,default),f)
                if v('opacity',1)<.75 or v('reveal',1)<.95:continue
                depth=v('depth',1);z=1+(r.value(cam.get('zoom',1),f)-1)*depth;scale=abs(v('scale',1)*z);x=540+(v('x',540)-540+r.value(cam.get('x',0),f)*depth)*z;y=960+(v('y',960)-960+r.value(cam.get('y',0),f)*depth)*z
                w,h=l['size'];w*=scale*abs(v('sx',1));h*=scale*abs(v('sy',1));ang=math.radians(v('rotation',0));bw=abs(w*math.cos(ang))+abs(h*math.sin(ang));bh=abs(w*math.sin(ang))+abs(h*math.cos(ang));
                if x-bw/2<80 or x+bw/2>1000 or y-bh/2<200 or y+bh/2>1660:o.append(f)
                if l.get('font_size',100)*scale<36:small.append(f)
            for frames,kind,fix in [(o,'possible_safe_area_overlap','Check rendered text pixels; shrink box or shift its anchor only during readable hold. Intentional offscreen travel is allowed.'),(small,'small_type','If this communicates needed information, increase font and simplify copy; mark as decorative only if nonessential.')]:
                if frames:issues.append(dict(shot=shot['id'],layer=l['id'],type=kind,first_frame=frames[0],last_frame=frames[-1],sample_count=len(frames),repair=fix))
    return dict(status='advisory_only',issues=issues,notes=['Bounds use sprite rectangles, not rendered glyphs; false positives possible. Auto-fit may make fonts smaller than configured. Use phone-size render and review actual content.'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('report',type=Path);a=p.parse_args();a.report.parent.mkdir(parents=True,exist_ok=True);d=audit(json.loads(a.project.read_text()));a.report.write_text(json.dumps(d,indent=2));print(f'{len(d["issues"])} advisory warnings')
