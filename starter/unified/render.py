#!/usr/bin/env python3
"""One explicit timeline, existing headless engines, exact-frame output and per-shot logs."""
import argparse, copy, json, os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ENGINES={'ui':'starter/ui_engine/render.py','type':'starter/type_motion/render.py','expressive':'starter/expressive_motion/render.py','material':'starter/material_motion/render.py','scene3d':'starter/scene3d/render.py','brand':'starter/brand_motion/render.py','data':'starter/data_motion.py'}
def require(x,m):
    if not x:raise ValueError(m)
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def run(cmd,log=None):
    p=subprocess.run([str(x) for x in cmd],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    if log:log.write_text(p.stdout,encoding='utf-8')
    if p.returncode:raise RuntimeError(f'Command failed ({p.returncode}): {cmd[1]}\n{p.stdout[-4000:]}')
    return p.stdout

def media(path):
    return json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',path]))
def video(path,n,fps):
    m=media(path);v=next((s for s in m['streams'] if s['codec_type']=='video'),None);require(v is not None,'no video stream');require(int(v.get('nb_read_frames',-1))==n,f'{path.name}: expected {n} frames, got {v.get("nb_read_frames")}'); a,b=map(int,v['avg_frame_rate'].split('/'));require(b and a==fps*b,'fps mismatch');return m

def absolute_assets(x,base):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in ('src','font','logo') and isinstance(v,str):
                p=(base/v).resolve();require(p.is_file(),f'missing asset {p}');x[k]=str(p)
            else:absolute_assets(v,base)
    elif isinstance(x,list):
        for v in x:absolute_assets(v,base)

def prepare(p,base,preview=False):
    require(p.get('schema')==1,'schema must be 1'); w,h,fps=(p[k] for k in ('width','height','fps'));require(all(type(v)==int for v in (w,h,fps)) and 160<=w<=2160 and 160<=h<=3840 and w%2==h%2==0 and 1<=fps<=60,'invalid raster/fps')
    require(p.get('mode') in ('demo','production'),'mode demo or production required');require(isinstance(p.get('shots'),list) and p['shots'],'no shots');require(not(p['mode']=='production' and not p.get('audio')),'production requires locked mix, use demo for silent proof')
    if p.get('audio'):require((base/p['audio']).is_file(),'audio missing')
    out=[];ids=set();at=0
    for s in p['shots']:
        sid=s['id'];require(isinstance(sid,str) and 1<=len(sid)<=80 and sid not in ids,'duplicate or invalid shot id');ids.add(sid);eng=s['engine'];n=s['frames'];require(eng in ENGINES,'unknown engine '+eng);require(type(n)==int and 1<=n<=3600,'bad frame count');require(s.get('start_frame',at)==at,'timeline gap/overlap');require(isinstance(s.get('reason'),str) and s['reason'].strip(),'motion purpose required')
        c=copy.deepcopy(s['config']);require(isinstance(c,dict),'config object required');absolute_assets(c,base)
        if eng=='scene3d':
            require('start' not in c and 'end' not in c,'scene start/end auto');doc={'width':w,'height':h,'fps':fps,'scenes':[dict(c,start=0,end=n)]}
        elif eng=='data':
            require(n==fps*6,'legacy data demo exactly six seconds');require(p['mode']=='demo','legacy illustrative data renderer demo only');doc=dict(c,fps=fps)
        else:
            require('frames' not in c,'frames supplied by central shot');doc={'width':w,'height':h,'fps':fps,'shots':[dict(c,frames=n)]}
            if eng=='type' and c.get('kind')=='words':require(p['mode']=='demo' or c.get('timing_source') in ('verified_alignment','manual_verified'),'unverified word timestamps')
        if eng=='brand' and c.get('kind')=='endcard' and p['mode']=='production':require(n>=round(fps*1.5),'endcard must hold at least 1.5s')
        out.append((s,doc,at));at+=n
    require(at<=18000,'timeline too long');return out,at

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('output',type=Path,nargs='?');ap.add_argument('--font',type=Path);ap.add_argument('--work',type=Path);ap.add_argument('--validate',action='store_true');ap.add_argument('--preview',action='store_true');ap.add_argument('--shot',help='Render one named shot, no audio');a=ap.parse_args();p=read(a.plan);base=a.plan.resolve().parent;plans,total=prepare(p,base,a.preview)
    if a.validate:print(json.dumps({'status':'structural_valid','frames':total,'shots':len(plans),'note':'Backend render checks not yet run'}));return
    require(a.output and a.font and a.font.is_file() and a.work,'output, --font and --work required');a.output=a.output.resolve();work=a.work.resolve();work.mkdir(parents=True,exist_ok=True);a.output.parent.mkdir(parents=True,exist_ok=True);font=a.font.resolve();fps=p['fps']; w,h=p['width'],p['height'];audio=None
    if p.get('audio') and not a.shot:
        audio=(base/p['audio']).resolve();require(audio.is_file(),'audio missing');m=media(audio);stream=next((x for x in m['streams'] if x['codec_type']=='audio'),None);require(stream,'audio stream missing');duration=float(stream.get('duration',m['format']['duration']));require(abs(duration-total/fps)<=max(.1,2/fps),'locked mix duration mismatch; align first')
        run(['ffmpeg','-v','error','-xerror','-i',audio,'-map','0:a:0','-f','null','-'])
    chosen=[x for x in plans if not a.shot or x[0]['id']==a.shot];require(chosen,'unknown shot id');clips=[];report={'status':'rendering','plan':str(a.plan.resolve()),'mode':p['mode'],'shots':[],'preview':a.preview,'single_shot':a.shot,'qa':'technical only, no creative or rights certification'};dump(work/'report.json',report)
    try:
        for j,(s,doc,at) in enumerate(chosen):
            eng=s['engine']; stem=f'{j:03d}'; cfg=work/(stem+'.json'); clip=work/(stem+'.mp4');dump(cfg,doc);cmd=[sys.executable,ROOT/ENGINES[eng],cfg,clip]
            if eng!='data':cmd+=['--font',font]
            if eng=='material':cmd+=['--samples','1' if a.preview else '3']
            if eng=='type' and p['mode']=='demo':cmd+=['--allow-synthetic-timing']
            log=work/(stem+'.log');report['active_shot']=s['id'];dump(work/'report.json',report);run(cmd,log);video(clip,s['frames'],fps);clips.append({'src':str(clip),'frames':s['frames']});report['shots'].append({'id':s['id'],'engine':eng,'start_frame':at,'frames':s['frames'],'clip':str(clip),'log':str(log)});dump(work/'report.json',report)
        stitch=work/'stitch.json';dump(stitch,{'width':w,'height':h,'fps':fps,'clips':clips});temp=work/'assembled.mp4';require(a.output!=temp,'output cannot be internal assembled.mp4');cmd=[sys.executable,ROOT/'starter/ui_engine/stitch.py',stitch,temp];
        if audio:cmd+=['--audio',audio]
        run(cmd,work/'stitch.log');expected=sum(c['frames'] for c in clips);m=video(temp,expected,fps);require(any(s['codec_type']=='audio' for s in m['streams'])==bool(audio),'unexpected audio stream');run(['ffmpeg','-v','error','-xerror','-i',temp,'-f','null','-'],work/'decode.log');shutil.copyfile(temp,a.output.with_suffix('.tmp.mp4'));os.replace(a.output.with_suffix('.tmp.mp4'),a.output);report.update(status='technical_pass',frames=expected,output=str(a.output),audio=bool(audio));report.pop('active_shot',None);dump(work/'report.json',report);print(f'{expected} frames, {expected/fps:.3f}s; technical pass only: {a.output}')
    except Exception as e:
        report.update(status='failed',error=str(e));dump(work/'report.json',report);raise
if __name__=='__main__':main()
