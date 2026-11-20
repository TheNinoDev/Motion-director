#!/usr/bin/env python3
"""Return task-specific guidance and exact argv without running or guessing inputs."""
import argparse,json,sys
from pathlib import Path
from agent_route import ROUTES,route
ROOT=Path(__file__).resolve().parents[1]
def plan(task,work,source=None,creative=None,audio=None,layer=None):
 r=route(task,work);p=lambda file:str(ROOT/file);exe=sys.executable
 r['read_first']=p('SKILL.md');r['only_needed_guides']=[p('references/86-precise-execution-v49.md')]+r['only_needed_guides']
 # Never offer older session start commands from the historical route.
 commands={k:v for k,v in r['commands_argv'].items() if k in ('doctor','probe','generate_example','render_example_still','catalog','macro_catalog')}
 commands['sequence_catalog']=[exe,p('scripts/director_v49.py'),'catalog']
 if source:
  commands['diagnose']=[exe,p('scripts/director_v49.py'),'diagnose',str(source.resolve())]
  if layer:commands['capabilities']=[exe,p('scripts/director_v49.py'),'capabilities',str(source.resolve()),layer]
  commands['capture_before_edit']=[exe,p('scripts/revision_guard_v49.py'),'capture',str(source.resolve()),str(work.resolve()/'before.json')]+(['--creative',str(creative.resolve())] if creative else [])+(['--audio',str(audio.resolve())] if audio else [])
 if source and creative:
  commands['start']=[exe,p('scripts/production_v49.py'),'start',str(source.resolve()),str(creative.resolve()),str(work.resolve()/'session-v49')]+(['--audio',str(audio.resolve())] if audio else [])
  commands['next']=[exe,p('scripts/production_v49.py'),'next',str(work.resolve()/'session-v49')]
 r['commands_argv']=commands;r['missing_inputs']=[k for k,v in [('source',source),('creative',creative)] if not v] if task in ('advertisement','revision','motion') else [];r['note']='Commands are candidates, not a claim of completion. Execute the applicable route in skill root; create work directory before writing snapshots. Do not start a new session over an existing one. Real ads require verified proof and authorized audio before export.'
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('task',choices=ROUTES);p.add_argument('work',type=Path);p.add_argument('--source',type=Path);p.add_argument('--creative',type=Path);p.add_argument('--audio',type=Path);p.add_argument('--layer');z=p.parse_args();print(json.dumps(plan(z.task,z.work,z.source,z.creative,z.audio,z.layer),indent=2))
