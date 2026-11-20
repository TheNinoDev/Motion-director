#!/usr/bin/env python3
"""Glyph-aware geometric layout checks and conservative static text repair.
Checks fully visible text, not decorative elements or intentionally moving masks.
Never certifies readability, occlusion, contrast, or creative quality.
"""
import argparse,copy,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'starter/unified'))
from production import validate,resolve_assets
sys.path.insert(0,str(ROOT/'starter/layer_motion'))
from render import sprite,value

def boxes(l,raw,cam,f):
    yy,xx=np.where(raw[:,:,3]>96)
    if not len(xx):return None
    H,W=raw.shape[:2];v=lambda k,d:value(l.get(k,d),f);dep=v('depth',1);z=1+(value(cam.get('zoom',1),f)-1)*dep
    X=540+(v('x',540)-540+value(cam.get('x',0),f)*dep)*z;Y=960+(v('y',960)-960+value(cam.get('y',0),f)*dep)*z
    p=np.array([[xx.min()-W/2,yy.min()-H/2],[xx.max()-W/2,yy.min()-H/2],[xx.max()-W/2,yy.max()-H/2],[xx.min()-W/2,yy.max()-H/2]],float)*2
    p[:,0]*=v('scale',1)*z*v('sx',1);p[:,1]*=v('scale',1)*z*v('sy',1)
    tilt=math.radians(np.clip(v('tilt',0),-75,75));x=p[:,0].copy();pers=1/(1+np.sin(tilt)*x/(1920*1.7));p[:,0]=x*np.cos(tilt)*pers;p[:,1]*=pers
    pitch=math.radians(np.clip(v('pitch',0),-70,70));y=p[:,1].copy();pers2=1/(1+np.sin(pitch)*y/(1920*1.7));p[:,1]=y*np.cos(pitch)*pers2;p[:,0]*=pers2
    a=math.radians(v('rotation',0));p=p@np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])+[X,Y]
    return tuple(p.min(0))+tuple(p.max(0))

def overlap(a,b):
    w=max(0,min(a[2],b[2])-max(a[0],b[0]));h=max(0,min(a[3],b[3])-max(a[1],b[1]));return w*h/max(1,min((a[2]-a[0])*(a[3]-a[1]),(b[2]-b[0])*(b[3]-b[1])))

def inspect(path,fix=False):
    pr,project,fp,_=validate(path);d=copy.deepcopy(project);issues=[];repairs=[]
    for shot in d['shots']:
        if shot['engine']!='layers':continue
        c=shot['content'];n=shot['frames'];cam=c.get('camera',{});ls=[]
        for l in c['layers']:
            if l['kind'] not in ('text','image') or l.get('decorative',False):continue
            raw=sprite(resolve_assets(l,pr.parent),.5,str(fp));ls.append((l,raw))
        frames=range(0,n,max(1,round(d['fps']/10)))
        bounds={};collisions={}
        for f in frames:
            active={}
            for l,raw in ls:
                v=lambda k,default:value(l.get(k,default),f)
                if not l.get('start',0)<=f<l.get('end',n) or v('opacity',1)<.85 or v('reveal',1)<.98:continue
                b=boxes(l,raw,cam,f)
                if b is None:continue
                active[l['id']]=(l,b)
                if l['kind']=='text' and (b[0]<65 or b[2]>1015 or b[1]<175 or b[3]>1690):bounds.setdefault(l['id'],[]).append((f,b))
            items=list(active.items())
            for i,(aid,(a,ab)) in enumerate(items):
                for bid,(b,bb) in items[i+1:]:
                    if a['kind']==b['kind']=='image' or a.get('allow_overlap') or b.get('allow_overlap'):continue
                    if overlap(ab,bb)>.18:collisions.setdefault((aid,bid),[]).append(f)
        for lid,points in bounds.items():
            l=next(x for x,_ in ls if x['id']==lid)
            issues.append(dict(shot=shot['id'],layer=lid,kind='safe_area',frames=[x[0] for x in points],suggestion='Check the glyph pixels. Move or resize the readable hold; intentional offscreen animation is not automatically a failure.'))
            # Conservative repair only for a fully static text transform and static camera.
            if fix and not any(isinstance(l.get(k),list) for k in ('x','y','scale','sx','sy','rotation','tilt','pitch')) and not any(isinstance(v,list) for v in cam.values()) and not l.get('allow_overlap'):
                b=points[0][1];bw=b[2]-b[0];bh=b[3]-b[1];factor=min(1,940/max(bw,1),1500/max(bh,1));x=l.get('x',540);y=l.get('y',960)
                # Only repair a simple unrotated, non-camera-transformed text layer.
                if not cam and l.get('rotation',0)==0 and l.get('tilt',0)==0 and l.get('pitch',0)==0:
                    targetx=np.clip((b[0]+b[2])/2,70+bw*factor/2,1010-bw*factor/2);targety=np.clip((b[1]+b[3])/2,180+bh*factor/2,1680-bh*factor/2)
                    l['scale']=round(l.get('scale',1)*factor,5);l['x']=round(x+targetx-(b[0]+b[2])/2,3);l['y']=round(y+targety-(b[1]+b[3])/2,3);repairs.append(dict(shot=shot['id'],layer=lid,reason='simple static glyph box fit'))
        for pair,fs in collisions.items():
            if len(fs)>=2:issues.append(dict(shot=shot['id'],layers=pair,kind='possible_readable_overlap',frames=fs,suggestion='Review actual composite. Shift the text or time its exit before the other focal layer enters. Intentional overlays may be marked allow_overlap after review.'))
    return dict(status='advisory_only',issues=issues,repairs=repairs,limits='Projected nontransparent sprite bounding boxes; ignores exact occlusion and contrast. A repair requires visual recheck.'),d

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('report',type=Path);p.add_argument('--repair',type=Path,help='write new plan in same project folder; original never overwritten');a=p.parse_args()
    if a.repair and (a.repair.resolve().parent!=a.project.resolve().parent or a.repair.resolve()==a.project.resolve()):p.error('repair project must be a different file in the same folder (asset paths)')
    r,d=inspect(a.project,fix=bool(a.repair));a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,indent=2));
    if a.repair:a.repair.write_text(json.dumps(d,indent=2,ensure_ascii=False));validate(a.repair)
    print(json.dumps({'issues':len(r['issues']),'repairs':len(r['repairs'])}))
