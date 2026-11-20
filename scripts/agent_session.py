#!/usr/bin/env python3
"""One low-context entry point: compile a spec, give runnable next commands,
render exact review stills, verify provenance. Never declares aesthetic approval."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from director_v38 import build, diagnose
from review_targets import targets
from compositor import validate
ROOT=Path(__file__).resolve().parents[1]

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def inputs(plan,p):
 base=plan.resolve().parent;paths={plan.resolve()}
 for l in p['layers']:
  if l['kind']=='image':paths.add((base/l['src']).resolve())
 for v in p.get('fonts',{}).values():paths.add((base/v).resolve())
 # Default font aliases and nested mesh resources are not fully fingerprinted here.
 return {str(x):sha(x) for x in sorted(paths)}

def write(path,data):
 with path.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2);f.write('\n')

def start(spec,work):
 p,expanded,notes=build(json.loads(spec.read_text()),spec.resolve().parent)
 if work.exists():raise ValueError('work directory already exists; choose a new revision directory')
 work.mkdir(parents=True);plan=work/'plan.json';write(plan,p);write(work/'expanded.json',expanded)
 # Expanded JSON preserves source asset paths; source spec remains canonical.
 cmds={k:[sys.executable,str(ROOT/'starter/composite_film/compositor.py'),str(plan.resolve()),str((work/k).resolve()),*args] for k,args in {'preview':['--size','540','--backend','auto'],'master_picture':['--size','1080','--profile','lossless','--backend','auto'],'upload_picture':['--size','1080','--profile','high','--backend','auto']}.items()}
 cmds['native_review']=[sys.executable,str(Path(__file__).resolve()),'review',str(plan.resolve()),str((work/'native_review').resolve())]
 cmds['verify_review']=[sys.executable,str(Path(__file__).resolve()),'verify',str(plan.resolve()),str((work/'native_review').resolve())]
 state={'source_spec':str(spec.resolve()),'source_sha256':sha(spec),'inputs':inputs(plan,p),'phase':'compiled','diagnostics':diagnose(p),'notes':notes,'commands_argv':cmds,'next':'Run native_review, inspect stills, then preview and listen to real audio where required. If changing source, start a new revision directory. No quality approval yet.'};write(work/'session.json',state);return state

def review(plan,out,backend='auto',size=1080,limit=12):
 p=json.loads(plan.read_text());validate(p,plan.resolve().parent)
 if out.exists():raise ValueError('review output already exists')
 if not 2<=limit<=60:raise ValueError('limit 2–60')
 initial=inputs(plan,p);tt=targets(p,limit);cmd=[sys.executable,str(ROOT/'starter/composite_film/compositor.py'),str(plan.resolve()),str(out.resolve()),'--size',str(size),'--profile','high','--backend',backend]
 for x in tt:cmd+=['--at',str(x['time'])]
 subprocess.run(cmd,check=True)
 if inputs(plan,p)!=initial:raise ValueError('inputs changed during render')
 from PIL import Image
 frames=[]
 for i,x in enumerate(tt):
  f=out/f"still-{i:03d}-{x['time']:.3f}s.png"
  with Image.open(f) as im:im.verify()
  frames.append({**x,'file':f.name,'sha256':sha(f)})
 m={'inputs':initial,'size':size,'frames':frames,'backend_sha256':sha(out/'render-backend.json'),'limitations':'Provenance of render files only; default fonts and nested mesh resources are not fully fingerprinted; visual review still required.'};write(out/'provenance.json',m);return m

def verify(plan,out):
 from PIL import Image
 p=json.loads(plan.read_text());validate(p,plan.resolve().parent);m=json.loads((out/'provenance.json').read_text());errors=[]
 if m['inputs']!=inputs(plan,p):errors.append('plan or explicit input files changed')
 expected=targets(p,len(m['frames']))
 if len(expected)!=len(m['frames']):errors.append('review target count mismatch')
 for i,(x,e) in enumerate(zip(m['frames'],expected)):
  filename=f"still-{i:03d}-{e['time']:.3f}s.png";f=out/filename
  if any(x.get(k)!=e[k] for k in ('time','frame','reasons')) or x.get('file')!=filename:errors.append('review target mismatch '+filename);continue
  if not f.is_file() or sha(f)!=x.get('sha256'):errors.append('missing/changed '+filename);continue
  try:
   with Image.open(f) as im:
    if im.size!=(m['size'],round(m['size']*16/9/2)*2):errors.append('wrong resolution '+filename)
    im.verify()
  except Exception:errors.append('invalid PNG '+filename)
 if not (out/'render-backend.json').is_file() or sha(out/'render-backend.json')!=m['backend_sha256']:errors.append('backend report changed')
 return {'provenance_valid':not errors,'errors':errors,'note':'This is not creative approval or evidence of playback.'}

def main():
 ap=argparse.ArgumentParser();s=ap.add_subparsers(dest='mode',required=True);a=s.add_parser('start');a.add_argument('spec',type=Path);a.add_argument('work',type=Path);a=s.add_parser('review');a.add_argument('plan',type=Path);a.add_argument('out',type=Path);a.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');a.add_argument('--size',type=int,default=1080);a.add_argument('--limit',type=int,default=12);a=s.add_parser('verify');a.add_argument('plan',type=Path);a.add_argument('out',type=Path);a=ap.parse_args()
 r=start(a.spec,a.work) if a.mode=='start' else review(a.plan,a.out,a.backend,a.size,a.limit) if a.mode=='review' else verify(a.plan,a.out);print(json.dumps(r,indent=2));raise SystemExit(2 if a.mode=='verify' and not r['provenance_valid'] else 0)
if __name__=='__main__':main()
