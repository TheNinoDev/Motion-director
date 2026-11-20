"""Small-model entry point: validate actual compositor plan, recommend exact commands.
Does not award creative quality or mark a scratch preview ready for release.
"""
import argparse,json,sys,shutil,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import validate,Engine
from render_backend import probe
from review_targets import targets
from motion_workbench import audit

def inspect(plan,base):
    validate(plan,base);p=dict(plan,width=180,height=320);e=Engine(p,base)
    missing=[];warnings=[f"{x['layer']}.{x['field']}: {x['message']} (inspect legacy compatibility)" for x in audit(plan)]
    for l in plan['layers']:
        if l['kind'] in ('text','text3d') and not e.fonts.get(l.get('font','heavy' if l['kind']=='text3d' else 'bold')):missing.append(l['id'])
        if l['kind']=='text3d' and (l.get('quality',.7)<1 or l.get('antialias',1)<1.5):warnings.append(l['id']+': use high/lossless for closeups; review face and both side angles')
        if l['kind']=='text3d' and len(l['text'])>12:warnings.append(l['id']+': dimensional type is long; prefer 2D for sentence text')
        if l['kind'] in ('glass_object','object3d') and l.get('quality',.55)<.8:warnings.append(l['id']+': low internal resolution; high/lossless profile recommended for hero objects')
    if missing:raise ValueError('unknown font aliases: '+', '.join(missing))
    if not shutil.which('ffmpeg'):raise ValueError('ffmpeg not in PATH')
    return warnings

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--backend',choices=('auto','cpu','cuda'),default='auto');ap.add_argument('--device',type=int,default=0);a=ap.parse_args();p=json.loads(a.plan.read_text());warnings=inspect(p,a.plan.resolve().parent)
    c=str(ROOT/'starter/composite_film/compositor.py');base=[sys.executable,c,str(a.plan.resolve()),str(a.out.resolve()),'--backend',a.backend,'--device',str(a.device)]
    gpu=probe();target=targets(p)
    def stage(name):
        b=base.copy();b[3]=str(a.out.resolve()/name);return b
    native=stage('native-review')+['--size','1080','--profile','high']
    for x in target:native+=['--at',str(x['time'])]
    if a.backend=='cuda' and not gpu['available']:warnings.append('Explicit CUDA will fail on this machine; choose auto or install compatible driver/runtime.')
    print(json.dumps({'valid':True,'warnings':warnings,'gpu':gpu,'review_targets':target,'commands_argv':{'native_review':native,'styleframes':stage('styleframes')+['--size','720','--stills'],'preview':stage('preview')+['--size','540'],'master_picture_only':stage('master-picture')+['--size','1080','--profile','lossless'],'delivery_picture_only':stage('delivery-picture')+['--size','1080','--profile','high']},'required_review':['Inspect actual hero closeups at front and side angles.','Check every transition at before/during/after.','Check actual text safe area and no clipping.','For commercial output verify claims, rights, audio mix and release gate.','Never call a silent master a finished voiced ad.']},indent=2))
if __name__=='__main__':main()
