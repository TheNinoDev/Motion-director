#!/usr/bin/env python3
"""V41 production entry point; existing gated render pipeline plus hierarchy audit."""
import argparse,json
from pathlib import Path
from director_v41 import build
from production_v40 import start as start40,render,checked,gate,review_template,evidence
from scene_audit_v41 import audit
from agent_session import write

def start(spec,creative,work,audio=None):
 r=start40(spec,creative,work,audio,builder=build);p=json.loads((work/'plan.json').read_text());write(work/'scene-audit.json',audit(p));return {**r,'scene_audit':str(work/'scene-audit.json'),'component_map':json.loads((work/'expanded.json').read_text())['component_map']}

def next_step(work):
 """One next action, not a claim of creative approval or a background job."""
 state=checked(work);prefix=['python','scripts/production_v41.py'];w=str(work.resolve())
 if not (work/'preview'/'evidence.json').is_file():
  if (work/'preview').exists():return {'stage':'blocked','action':'Preview folder is incomplete. Preserve logs; start a fresh revision directory.'}
  return {'stage':'preview','argv':prefix+['preview',w,'--backend','auto','--size','540']}
 _,errors=evidence(work)
 if errors:return {'stage':'blocked','errors':errors,'action':'Preserve files; start a new revision and render.'}
 if not (work/'review.json').is_file():return {'stage':'review','argv':prefix+['review-template',w],'action':'Inspect complete preview and audio where present. Review template starts pending.'}
 g=gate(work)
 if not g['ready']:return {'stage':'blocked_review','errors':g['errors'],'action':'Resolve real issues or missing audio in a new revision; never fill passes automatically.'}
 if not (work/'upload'/'evidence.json').is_file():
  if (work/'upload').exists():return {'stage':'blocked','action':'Upload folder incomplete; use a fresh revision.'}
  return {'stage':'upload','argv':prefix+['upload',w,'--backend','auto'],'action':'Review final picture and audio after rendering.'}
 return {'stage':'verify','argv':prefix+['verify-export',w],'action':'Verify exports, then personally inspect final video and audio before claiming completion. Master is optional.'}

def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);b=s.add_parser('start');b.add_argument('spec',type=Path);b.add_argument('creative',type=Path);b.add_argument('work',type=Path);b.add_argument('--audio',type=Path)
 for k in ('preview','upload','master'):
  b=s.add_parser(k);b.add_argument('work',type=Path);b.add_argument('--backend',choices=['auto','cpu','cuda'],default='auto');b.add_argument('--size',type=int)
 for k in ('review-template','gate','verify-export','audit','next'):
  b=s.add_parser(k);b.add_argument('work',type=Path)
 z=a.parse_args()
 if z.cmd=='start':r=start(z.spec,z.creative,z.work,z.audio)
 elif z.cmd in ('preview','upload','master'):r=render(z.work,z.cmd,z.backend,z.size)
 elif z.cmd=='review-template':r=review_template(z.work)
 elif z.cmd=='gate':r=gate(z.work)
 elif z.cmd=='next':r=next_step(z.work)
 elif z.cmd=='audit':checked(z.work);r=audit(json.loads((z.work/'plan.json').read_text()))
 else:
  r={}
  for stage in ('upload','master'):
   if (z.work/stage/'evidence.json').is_file():_,err=evidence(z.work,stage);r[stage]={'valid':not err,'errors':err}
 print(json.dumps(r,indent=2));raise SystemExit(2 if (z.cmd=='gate' and not r['ready']) or (z.cmd=='verify-export' and (not r or any(not x['valid'] for x in r.values()))) else 0)
if __name__=='__main__':main()
