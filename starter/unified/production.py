#!/usr/bin/env python3
"""Motion Director: one strictly validated frame-timed project -> silent/video/audio output.

Uses bundled renderers through stable JSON contracts; no Blender, GUI or new AI code.
CLI: python starter/unified/production.py examples/brand-story-project.json --build-dir /tmp/md13build --preview
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, os, shutil, subprocess, sys, time
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[2]
ENGINES = {
    'mesh': ROOT/'starter/mesh_motion/render.py',
    'editorial': ROOT/'starter/editorial/render.py',
    'kinetic': ROOT/'starter/kinetic/render.py',
    'fusion': ROOT/'starter/fusion/render.py',
    'studio': ROOT/'starter/studio/render.py',
    'sequence': ROOT/'starter/sequence/render.py',
    'cinematic': ROOT/'starter/cinematic/render.py',
    'layers': ROOT/'starter/layer_motion/render.py',
    'type': ROOT/'starter/type_motion/render.py',
    'data': ROOT/'starter/unified/data_chart.py',
    'brand': ROOT/'starter/brand_motion/render.py',
    'ui': ROOT/'starter/ui_engine/render.py',
    'expressive': ROOT/'starter/expressive_motion/render.py',
    'material': ROOT/'starter/material_motion/render.py',
    'scene3d': ROOT/'starter/scene3d/render.py',
}
TRANSITIONS = {'cut','dissolve','fadeblack','wipeleft','wiperight','smoothleft','smoothright','circleopen','circleclose','radial','diagtl','diagbr','squeezeh','squeezev','zoomin','hblur','slideup','slidedown'}
BUILTIN_FONTS = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                 '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
                 '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                 'C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/segoeuib.ttf']

def err(condition, msg):
    if not condition: raise ValueError(msg)

def run(args, cwd=None):
    print('RUN', ' '.join(str(a) for a in args[:5]),'…',flush=True)
    subprocess.run([str(a) for a in args], cwd=cwd, check=True)

def probe(path, count=False):
    args=['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,avg_frame_rate,nb_frames,nb_read_frames:format=duration','-of','json']
    if count:args.insert(3,'-count_frames')
    args.append(str(path))
    d=json.loads(subprocess.check_output(args))
    v=next((s for s in d.get('streams',[]) if s.get('codec_type')=='video'),None)
    return {'video':v,'audio':any(s.get('codec_type')=='audio' for s in d.get('streams',[])), 'duration':float(d['format']['duration'])}

def sandbox_path(root:Path,value:str,exists=True):
    err(isinstance(value,str) and value.strip(),'empty path')
    p=(root/value).resolve()
    err(p.is_relative_to(root.resolve()), 'Asset outside project folder: '+value)
    if exists:err(p.is_file(), 'Missing asset: '+value)
    return p

def font_path(root, data):
    if 'font' in data:return sandbox_path(root,data['font'])
    candidates=BUILTIN_FONTS
    if any(s.get('engine') in ('editorial','mesh') for s in data.get('shots',[]) if isinstance(s,dict)):
        candidates=['/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf','/usr/share/fonts/opentype/inter/Inter-Bold.otf']+BUILTIN_FONTS
    for p in candidates:
        if Path(p).is_file():return Path(p)
    raise ValueError('Font not found. Set font path in project or install DejaVu Sans.')

def validate(project_path):
    pr=Path(project_path).resolve();base=pr.parent
    d=json.loads(pr.read_text(encoding='utf8'))
    err(d.get('version')==1,'Expected version 1')
    for k,lo,hi in (('width',160,2160),('height',160,3840),('fps',1,60)):
        err(type(d.get(k)) is int and lo<=d[k]<=hi,k+' out of range')
    err(d['width']%2==0 and d['height']%2==0,'Width and height must be even')
    err(isinstance(d.get('shots'),list) and 1<=len(d['shots'])<=60,'Expected 1-60 shots')
    font=font_path(base,d)
    total=0;overlap=0;ids=set()
    for i,s in enumerate(d['shots']):
        err(isinstance(s,dict),f'Shot {i}: expected object')
        sid=s.get('id');err(isinstance(sid,str) and 1<=len(sid)<=60 and sid.replace('-','').replace('_','').isalnum(),f'Shot {i}: invalid id')
        err(sid not in ids,'Duplicate shot ID: '+sid);ids.add(sid)
        n=s.get('frames');err(type(n) is int and 4<=n<=3600, f'{sid}: frames must be 4..3600')
        engine=s.get('engine');err(engine in ENGINES or engine=='clip',f'{sid}: unknown engine {engine}')
        if engine=='clip':sandbox_path(base,s.get('src'))
        else:err(isinstance(s.get('content'),dict),f'{sid}: content must be an object')
        tr=s.get('transition_in',{'kind':'cut','frames':0})
        err(isinstance(tr,dict),'transition_in must be object')
        kind=tr.get('kind','cut');j=tr.get('frames',0)
        err(kind in TRANSITIONS and type(j) is int and 0<=j<=24,f'{sid}: invalid transition')
        err((kind=='cut' and j==0) or (kind!='cut' and 2<=j<=24),f'{sid}: invalid transition length')
        if i==0:err(j==0,f'{sid}: first shot cannot transition in')
        else:err(j<min(n,d['shots'][i-1]['frames'])//2,f'{sid}: transition too long')
        if engine!='clip':
            # Fail fast on missing/escaped assets before spending time rendering earlier shots.
            resolve_assets(s['content'],base)
            if engine in ('cinematic','sequence','studio','fusion','kinetic','editorial','mesh'):
                if engine in ('studio','fusion'):err(abs(d['width']/d['height']-9/16)<=.02,'studio requires 9:16 portrait')
                import importlib.util
                spec=importlib.util.spec_from_file_location('motion_director_'+engine,ENGINES[engine])
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                module.validate(dict(resolve_assets(s['content'],base),frames=n))
            if engine=='layers':
                import importlib.util
                spec=importlib.util.spec_from_file_location('motion_director_layers',ROOT/'starter/layer_motion/render.py')
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                module.validate(dict(resolve_assets(s['content'],base),frames=n))
        total+=n;overlap+=j
    final_frames=total-overlap
    err(final_frames<=60*60*20,'Film exceeds 20 minutes')
    aud=d.get('audio',{})
    err(isinstance(aud,dict),'audio must be object')
    for key in ('voice','music','sfx'):
        if aud.get(key):sandbox_path(base,aud[key])
    if 'sfx_volume' in aud:err(type(aud['sfx_volume']) in (int,float) and 0<aud['sfx_volume']<=1,'sfx_volume must be 0..1')
    if 'music_volume' in aud:err(type(aud['music_volume']) in (int,float) and 0<aud['music_volume']<=.5,'music_volume must be 0..0.5')
    return pr,d,font,final_frames

def resolve_assets(content,base):
    """Rewrite known image sources to absolute paths; never trust arbitrary execution strings."""
    if isinstance(content,list):return [resolve_assets(x,base) for x in content]
    if isinstance(content,dict):
        out={}
        for k,v in content.items():out[k]=str(sandbox_path(base,v)) if k in ('src','font','logo') and isinstance(v,str) else resolve_assets(v,base)
        return out
    return content

def subplan(d,s,base):
    engine=s['engine'];c=resolve_assets(copy.deepcopy(s['content']),base)
    o={'width':d['width'],'height':d['height'],'fps':d['fps']}
    if engine=='scene3d':
        # Either one scene content or multiple nested scenes whose frame counts sum to the shot duration.
        o.update({k:c[k] for k in ('depth','bevel') if k in c})
        scenes=c.get('scenes',[{k:v for k,v in c.items() if k not in ('depth','bevel')}])
        err(isinstance(scenes,list) and scenes,'scene3d requires scenes')
        start=0;normalized=[]
        for scene in scenes:
            t=copy.deepcopy(scene)
            length=t.pop('frames',None)
            if length is None:
                # Existing renderer uses start/end directly, if explicitly supplied.
                length=t.get('end',s['frames'])-t.get('start',0)
            err(type(length) is int and length>0,'scene3d invalid scene frames')
            t['start']=start;t['end']=start+length;start+=length;normalized.append(t)
        err(start==s['frames'],s['id']+': scene3d total duration mismatch')
        o['scenes']=normalized
    else:
        o['shots']=[{'frames':s['frames'],**c}]
        # Avoid allowing conflicting content.frames for a weaker agent.
        o['shots'][0]['frames']=s['frames']
        if engine=='type' and o['shots'][0].get('kind')=='words':
            err(o['shots'][0].get('timing_source')!='synthetic_demo','Synthetic word timing cannot be included in production')
    return o

def filehash(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def key_for(plan,engine,font,asset_files):
    h=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()+str(font).encode()+filehash(font).encode())
    for dep in sorted(ENGINES[engine].parent.glob('*.py')):h.update(filehash(dep).encode())
    if engine=='sequence':h.update(filehash(ENGINES['cinematic']).encode())
    for p in sorted(asset_files):h.update(str(p).encode()+filehash(p).encode())
    return h.hexdigest()

def list_sources(item,acc):
    if isinstance(item,dict):
        for k,v in item.items():
            if k in ('src','font','logo') and isinstance(v,str):acc.add(Path(v))
            else:list_sources(v,acc)
    elif isinstance(item,list):
        for x in item:list_sources(x,acc)

def render_one(root,d,font,s,build,force=False):
    sid=s['id'];path=build/'shots'/f'{sid}.mp4';path.parent.mkdir(parents=True,exist_ok=True)
    if s['engine']=='clip':
        src=sandbox_path(root,s['src']);key=filehash(src)+f':{d["width"]}:{d["height"]}:{d["fps"]}:{s["frames"]}'
        plan=None
    else:
        plan=subplan(d,s,root);assets=set();list_sources(plan,assets)
        key=key_for(plan,s['engine'],font,assets)
    stamp=path.with_suffix('.sha256')
    if not force and path.exists() and stamp.exists() and stamp.read_text()==key:
        meta=probe(path,True);v=meta['video']
        if v and int(v['nb_read_frames'])==s['frames'] and v['width']==d['width'] and v['height']==d['height']:
            print(f'CACHE HIT {sid}',flush=True);return path,True
    if s['engine']=='clip':
        run(['ffmpeg','-v','error','-y','-i',src,'-an','-vf',f'fps={d["fps"]},scale={d["width"]}:{d["height"]}:force_original_aspect_ratio=decrease,pad={d["width"]}:{d["height"]}:(ow-iw)/2:(oh-ih)/2,setsar=1','-frames:v',s['frames'],'-c:v','libx264','-threads','2','-crf','18','-pix_fmt','yuv420p',path])
    else:
        planpath=build/'plans'/f'{sid}.json';planpath.parent.mkdir(parents=True,exist_ok=True)
        planpath.write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf8')
        cmd=[sys.executable,ENGINES[s['engine']],planpath,path]
        if s['engine'] in ('type','material','scene3d','data','brand'):cmd+=['--font',font]
        elif s['engine'] in ('ui','expressive','layers','cinematic','sequence','studio','fusion','kinetic','editorial','mesh'):cmd+=['--font',font]
        if s['engine']=='material':cmd+=['--samples','1']
        run(cmd)
    meta=probe(path,True);v=meta['video']
    err(v is not None and int(v['nb_read_frames'])==s['frames'],f'{sid}: renderer returned wrong frame count')
    err(v['width']==d['width'] and v['height']==d['height'],f'{sid}: wrong dimensions')
    stamp.write_text(key,encoding='ascii')
    return path,False

def compose_video(shots,d,build,frames):
    """Accumulate transitions into verified CFR intermediate files (fixes concat VFR)."""
    w,h,fps=d['width'],d['height'],d['fps']
    current=shots[0];running=d['shots'][0]['frames']
    for i in range(1,len(shots)):
        tr=d['shots'][i].get('transition_in',{'kind':'cut','frames':0})
        kind=tr.get('kind','cut');n=tr.get('frames',0)
        out=build/f'assembled-{i:02d}.mp4';expected=running+d['shots'][i]['frames']-n
        prefix=(f'[0:v]scale={w}:{h},setsar=1,settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p,fps={fps}[a];'
                f'[1:v]scale={w}:{h},setsar=1,settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p,fps={fps}[b];')
        if kind=='cut':
            graph=f'[0:v][1:v]concat=n=2:v=1:a=0,fps={fps},trim=end_frame={expected}[out]'
        else:
            t='fade' if kind=='dissolve' else kind
            offset=Fraction(running-n,fps);dur=Fraction(n,fps)
            graph=prefix+f'[a][b]xfade=transition={t}:duration={float(dur):.8f}:offset={float(offset):.8f},fps={fps},trim=end_frame={expected}[out]'
        cmd=['ffmpeg','-v','error','-y','-filter_complex_threads','1','-i',current,'-i',shots[i],
             '-filter_complex',graph,'-map','[out]','-an','-frames:v',expected,'-c:v','libx264',
             '-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',out]
        run(cmd)
        meta=probe(out,True);count=int(meta['video']['nb_read_frames'])
        err(count==expected, f'Transition {i}: expected {expected} frames, got {count}')
        current=out;running=expected
    err(running==frames,'Internal timeline mismatch')
    picture=build/'picture.mp4'
    if current!=picture:shutil.copy2(current,picture)
    return picture

def mix_voice_music(project,base,build,frames,final):
    a=project.get('audio',{})
    if not a.get('voice'):
        err(not final,'Final export requires a real voiceover file. Preview is silent.')
        return None
    fps=project['fps'];duration=frames/fps;voice=sandbox_path(base,a['voice']);vdur=probe(voice)['duration']
    err(vdur>0 and vdur<=duration+0.12,f'Voiceover {vdur:.2f}s exceeds timeline {duration:.2f}s. Re-time the video; do not truncate speech.')
    level=subprocess.run(['ffmpeg','-v','info','-i',str(voice),'-af','volumedetect','-f','null','-'],capture_output=True,text=True)
    err(level.returncode==0,'Voice audio failed to decode')
    import re
    peak=re.search(r'max_volume:\s*([\-\d.]+|\-inf) dB',level.stderr)
    err(peak is not None and peak.group(1)!='-inf' and float(peak.group(1))>-65,
        'Voiceover appears silent or nearly inaudible; provide a real narration file')
    dest=build/'mix.wav'
    vd=f'[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,apad,atrim=duration={duration:.9f}[voice]'
    if a.get('music'):
        music=sandbox_path(base,a['music']);vol=a.get('music_volume',0.22)
        filter_graph=(vd+';'+f'[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},asetpts=PTS-STARTPTS,atrim=duration={duration:.9f}[music];'
             f'[music][voice]sidechaincompress=threshold=0.03:ratio=7:attack=15:release=300[duck];'
             f'[duck][voice]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:latency=1,apad,atrim=duration={duration:.9f}[out]')
        cmd=['ffmpeg','-v','error','-y','-i',voice,'-stream_loop','-1','-i',music]
    else:
        filter_graph=vd+f';[voice]alimiter=limit=0.95:latency=1,apad,atrim=duration={duration:.9f}[out]';cmd=['ffmpeg','-v','error','-y','-i',voice]
    cmd+=['-filter_complex',filter_graph,'-map','[out]','-t',f'{duration:.9f}','-c:a','pcm_s16le',dest]
    run(cmd);err(abs(probe(dest)['duration']-duration)<.055,'Audio mix duration mismatch')
    return dest

def mix_audio(project,base,build,frames,final):
    main=mix_voice_music(project,base,build,frames,final)
    a=project.get('audio',{})
    if not a.get('sfx'):return main
    duration=frames/project['fps'];sfx=sandbox_path(base,a['sfx']);dest=build/'mix-sfx.wav';volume=a.get('sfx_volume',.65)
    if main:
        cmd=['ffmpeg','-v','error','-y','-i',main,'-i',sfx,'-filter_complex',f'[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={volume},apad,atrim=duration={duration:.9f}[fx];[0:a][fx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:latency=1[out]','-map','[out]']
    else:
        cmd=['ffmpeg','-v','error','-y','-i',sfx,'-af',f'aresample=48000,aformat=channel_layouts=stereo,volume={volume},apad,atrim=duration={duration:.9f}']
    run(cmd+['-t',f'{duration:.9f}','-c:a','pcm_s16le',dest]);err(abs(probe(dest)['duration']-duration)<.055,'SFX mix duration mismatch');return dest

def final_mux(picture,audio,build,frames,d):
    if not audio:return picture
    out=build/'video.mp4'
    run(['ffmpeg','-v','error','-y','-i',picture,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','aresample=async=1:first_pts=0','-movflags','+faststart',out])
    p=probe(out,True);err(p['audio'] and int(p['video']['nb_read_frames'])==frames,'Final mux invalid')
    return out

def sheet(video,d,build):
    from PIL import Image,ImageDraw
    import cv2
    cap=cv2.VideoCapture(str(video));count=cap.get(cv2.CAP_PROP_FRAME_COUNT);fps=cap.get(cv2.CAP_PROP_FPS);n=min(12,max(3,int(math.ceil(count/fps))))
    images=[]
    for i in range(n):
        fi=round((i+.5)*count/n);cap.set(cv2.CAP_PROP_POS_FRAMES,fi);ok,fr=cap.read()
        if not ok:continue
        im=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB));im.thumbnail((192,342));images.append((fi,im.copy()))
    cap.release();board=Image.new('RGB',(4*204,math.ceil(len(images)/4)*370),(15,15,18));draw=ImageDraw.Draw(board)
    for i,(fi,im) in enumerate(images):
        x=i%4*204;y=i//4*370;board.paste(im,(x,y));draw.text((x+8,y+346),f'{fi/fps:.2f}s',fill='white')
    path=build/'contact-sheet.jpg';board.save(path,quality=90);return path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('project',type=Path)
    p.add_argument('--build-dir',type=Path)
    p.add_argument('--check',action='store_true',help='Preflight without rendering')
    p.add_argument('--preview',action='store_true',help='Allow silent/unfinished drafts')
    p.add_argument('--final',action='store_true',help='Require actual voice file')
    p.add_argument('--force',action='store_true')
    args=p.parse_args();err(not(args.preview and args.final),'Use either --preview or --final')
    pr,d,font,frames=validate(args.project);root=pr.parent
    if args.final:err(bool(d.get('audio',{}).get('voice')),'Final rendering requires an actual voiceover path in audio.voice')
    print(f'PROJECT {len(d["shots"])} shots | {frames} frames | {frames/d["fps"]:.3f}s | font {font}',flush=True)
    if args.check:return
    build=(args.build_dir.resolve() if args.build_dir else root/'build'/pr.stem)
    err(not build.is_relative_to(ROOT/'starter'), 'Build outside packaged starter code')
    build.mkdir(parents=True,exist_ok=True)
    started=time.time();clips=[];cached=0
    for i,s in enumerate(d['shots']):
        print(f'[{i+1}/{len(d["shots"])}] {s["id"]} ({s["engine"]})',flush=True)
        path,hit=render_one(root,d,font,s,build,args.force);cached+=hit;clips.append(path)
    picture=compose_video(clips,d,build,frames)
    audio=mix_audio(d,root,build,frames,args.final)
    finalfile=final_mux(picture,audio,build,frames,d)
    run(['ffmpeg','-v','error','-xerror','-i',finalfile,'-f','null','-'])
    thumbnail=sheet(finalfile,d,build)
    report={'project':str(pr),'output':str(finalfile),'contact_sheet':str(thumbnail),'frames':frames,'fps':d['fps'],
            'duration_seconds':frames/d['fps'],'has_audio':bool(audio),'status':'technical_export_complete' if audio and args.final else 'PREVIEW_ONLY',
            'cached_shots':cached,'shot_count':len(clips),'render_seconds':round(time.time()-started,2),
            'visual_review_required':True,'voice_listening_required':bool(audio),'copyright_clearance_not_assessed':True}
    (build/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('RESULT',json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    try:main()
    except (ValueError,FileNotFoundError,subprocess.CalledProcessError,KeyError,TypeError) as e:
        sys.exit('ERROR: '+str(e))
