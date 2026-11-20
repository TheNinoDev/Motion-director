#!/usr/bin/env python3
"""Low-context dispatcher: only the applicable handbooks and next executable command.
Prints commands; does not run them or declare a production complete.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROUTES={
 'advertisement':(['references/01-product-intake.md','references/02-human-copywriting.md','references/03-hook-lab.md','references/25-voice-acting-and-tagging.md','references/20-audio-first.md'], 'Collect verified product evidence, choose central promise, lock real audio before editing.', 'Full release gate, actual playback and sound review.'),
 'revision':(['starter/composite_film/README-v36.md','references/66-continuous-handoffs-and-glass.md'], 'Use latest source and actual review issue, fingerprint and patch only affected layers.', 'Review old and new actual interval, then full export.'),
 'motion':(['starter/composite_film/README-v36.md'], 'Choose subject and action; compile compact spec to editable timeline.', 'Render and inspect motion excerpt.'),
 'glass':(['starter/composite_film/README-v31.md','starter/composite_film/README-v36.md'], 'Use solid shape for a physical-looking object; local lens only for optical adjustments.', 'Inspect edges, grazing angle and live background.'),
 'type3d':(['starter/composite_film/README-v32.md','references/69-weak-agent-execution-and-render-quality.md'], 'Resolve licensed font locally, use short text and true depth/bevel.', 'Inspect native face and both sides; no blur to conceal geometry defects.'),
 'jelly':(['references/70-elastic-motion-and-type-selection.md','starter/composite_film/README-v36.md'], 'Choose a motivated impulse and independently choose geometry, material and preset.', 'Check compression, recovery and visual silhouette; stylized, not collision solver.'),
 'collision':(['starter/contact3d/README.md','references/70-elastic-motion-and-type-selection.md'], 'Use wall-contact solver, not an authored impulse masquerading as physics.', 'Review contact, no excessive intersection, rebound and actual backend.'),
 'audio':(['references/20-audio-first.md','references/22-music-research-and-acquisition.md','references/25-voice-acting-and-tagging.md'], 'Verify rights and actual voice/music, measure cues.', 'Listen to mix and check claims and timing.'),
 'gpu':(['references/71-gpu-and-agent-execution.md','starter/composite_film/README-v35.md'], 'Probe hardware; strict CUDA only on compatible actual GPU.', 'Inspect actual backend report; simulator is not a real GPU benchmark.'),
}
def route(task,work):
 docs,next_action,finish=ROUTES[task];p=lambda x:str(ROOT/x);out=str(work.resolve());cmd=[sys.executable,p('scripts/doctor.py')]
 commands={'doctor':cmd}
 if task in ('motion','glass','type3d','jelly','revision','advertisement'):
  commands['catalog']=[sys.executable,p('scripts/motion_workbench.py'),'catalog']
  commands['v38_catalog']=[sys.executable,p('scripts/director_v38.py'),'catalog']
  commands['start_v38_session']=[sys.executable,p('scripts/agent_session.py'),'start',str(work.resolve()/'spec.json'),str(work.resolve()/'session-v38')]
  commands['macro_catalog']=[sys.executable,p('scripts/director_v37.py'),'catalog']
  commands['diagnose_existing_plan']=[sys.executable,p('scripts/director_v37.py'),'diagnose',str(work.resolve()/'plan.json')]
  commands['create_review_record']=[sys.executable,p('scripts/review_ledger.py'),'create',str(work.resolve()/'plan.json'),str(work.resolve()/'review-ledger.json')]
  commands['preflight_existing_plan']=[sys.executable,p('scripts/agent_preflight.py'),str(work.resolve()/'plan.json'),str(work.resolve()/'review'),'--backend','auto']
 if task=='gpu':commands['probe']=[sys.executable,p('scripts/gpu_doctor.py')]
 if task=='jelly':commands['generate_example']=[sys.executable,p('scripts/elastic_recipe.py'),str(work.resolve()/'elastic.json'),'--recipe','wobble','--preset','jelly_soft']
 if task=='collision':commands['render_example_still']=[sys.executable,p('starter/contact3d/render.py'),p('examples/jelly-v34.json'),str(work.resolve()/'contact'),'--backend','auto','--still','2.0']
 return {'task':task,'read_first':p('references/74-executable-production-v38.md'),'only_needed_guides':[p(x) for x in docs],'next_action':next_action,'commands_argv':commands,'finish_requires':finish,'status':'not started; inspect needed inputs first'}
def main():
 a=argparse.ArgumentParser();a.add_argument('task',choices=ROUTES);a.add_argument('work',type=Path);p=a.parse_args();print(json.dumps(route(p.task,p.work),indent=2))
if __name__=='__main__':main()
