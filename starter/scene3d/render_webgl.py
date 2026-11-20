#!/usr/bin/env python3
"""Render local JSON using headless WebGL, then encode H264. No GUI."""
import argparse,base64,json,math,pathlib,shutil,subprocess
from mesh import glyph
from playwright.sync_api import sync_playwright
P=pathlib.Path;LAYOUTS={'grid','helix','torus','tunnel','sphere','scatter','custom'}
def validate(p):
    for k in ('width','height','fps'):
        if type(p.get(k)) is not int or p[k]<1:raise ValueError('Invalid '+k)
    if p['width']%2 or p['height']%2 or max(p['width'],p['height'])>4096 or p['fps']>120:raise ValueError('Invalid raster/FPS')
    at=0
    for s in p['scenes']:
        if s['start']!=at or type(s['end'])!=int or s['end']<=at:raise ValueError('Frame gap/overlap')
        at=s['end'];n=s['count']
        if type(n)!=int or not 1<=n<=10000 or not s['glyphs'] or any(c.isspace() or ord(c)>126 for c in s['glyphs']):raise ValueError('Invalid count/glyphs (ASCII nonspace)')
        for k in ('layout','to_layout'):
            if k in s and s[k] not in LAYOUTS:raise ValueError('Unknown layout')
            if s.get(k)=='custom' and (len(s.get('points',[]))!=n or any(len(v)!=3 or not all(math.isfinite(x) for x in v) for v in s['points'])):raise ValueError('Bad custom points')
        for k in ('from','to'):
            eye=s['eye_'+k];tar=s.get('target_'+k,[0,0,0]);
            if len(eye)!=3 or len(tar)!=3 or not all(math.isfinite(x) for x in eye+tar) or math.hypot(eye[0]-tar[0],eye[2]-tar[2])<.001:raise ValueError('Bad camera')
        if not 10<=s.get('fov',42)<=110 or not 0<=s.get('roughness',.22)<=1 or not 0<s.get('size',.3)<=10:raise ValueError('Bad optics')
    if not at:raise ValueError('No scenes')
    return at

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('plan',type=P);a.add_argument('output',type=P);a.add_argument('--font',type=P,required=True);a.add_argument('--chromium',default=shutil.which('chromium') or shutil.which('chromium-browser'));a.add_argument('--preview-dir',type=P);args=a.parse_args();p=json.loads(args.plan.read_text());total=validate(p);args.output.parent.mkdir(parents=True,exist_ok=True)
    geo={c:glyph(c,args.font,p.get('depth',.22),p.get('bevel',.02)) for c in sorted(set(''.join(s['glyphs'] for s in p['scenes'])))};print({c:(m['triangles'],m['beveled_components']) for c,m in geo.items()},flush=True)
    tmp=args.output.with_name(args.output.stem+'.tmp.mp4');preview=args.preview_dir;selected={s['start']+(s['end']-s['start'])//2 for s in p['scenes']}
    if preview:preview.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=args.chromium,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(P(__file__).with_name('engine.html').read_text());print(page.evaluate('([p,g])=>setup(p,g)',[p,geo]),flush=True)
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(p['fps']),'-vcodec','png','-i','-','-an','-c:v','libx264','-threads','2','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
        try:
            for i in range(total):
                png=base64.b64decode(page.evaluate('i=>render(i)',i));proc.stdin.write(png)
                if preview and i in selected:(preview/f'frame-{i:05}.png').write_bytes(png)
                if errors:raise RuntimeError(errors)
            proc.stdin.close()
            if proc.wait():raise RuntimeError('FFmpeg failed')
        except BaseException:
            proc.kill();proc.wait();tmp.unlink(missing_ok=True);raise
        finally:browser.close()
    count=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames','-of','default=nw=1:nk=1',str(tmp)]))
    if count!=total:tmp.unlink(missing_ok=True);raise RuntimeError(f'Frame count {count} != {total}')
    tmp.replace(args.output);print(f'{total} frames / {total/p["fps"]:.3f}s')
if __name__=='__main__':main()
