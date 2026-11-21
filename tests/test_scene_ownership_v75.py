import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from scene_ownership_audit_v75 import analyze

SCENE={"duration":5,"scenes":[{"id":"source","start":0,"end":2.5,"composition_signature":"code"},{"id":"success","start":2.5,"end":5,"composition_signature":"brand"}],"layers":[
 {"id":"title","owner":"source","role":"title","start":0,"end":2.5,"exit":"remove","box":[.10,.25,.45,.14]},
 {"id":"connector","owner":"source","role":"connector","start":0,"end":2.4,"exit":"remove","box":[.1,.60,.5,.02]},
 {"id":"tagline","owner":"success","role":"headline","start":2.5,"end":5,"exit":"despawn","box":[.1,.25,.65,.2]}]}

class Tests(unittest.TestCase):
 def test_safe(self):self.assertFalse(analyze(SCENE)['errors'])
 def test_connector_title_collision(self):
  d=copy.deepcopy(SCENE);d['layers'][1]['box']=[.12,.30,.4,.05]
  self.assertTrue(any('collision' in x for x in analyze(d)['errors']))
 def test_stale_layer(self):
  d=copy.deepcopy(SCENE);d['layers'][0]['end']=3
  self.assertTrue(any('Stale' in x for x in analyze(d)['errors']))
 def test_handoff_without_target(self):
  d=copy.deepcopy(SCENE);d['layers'][0]['exit']='handoff'
  self.assertTrue(any('Handoff' in x for x in analyze(d)['errors']))
 def test_good_handoff(self):
  d=copy.deepcopy(SCENE);d['layers'][0].update(end=3,exit='handoff',handoff_to='success',box=[.10,.75,.45,.14])
  self.assertFalse(analyze(d)['errors'])
 def test_intentional_overlap_scoped(self):
  d=copy.deepcopy(SCENE);d['layers'][1]['box']=[.12,.30,.4,.05]
  d['intentional_overlaps']=[{"a":"title","b":"connector","start":0,"end":2.4,"reason":"Connector intentionally masks and reveals title glyphs"}]
  self.assertFalse(analyze(d)['errors'])
 def test_no_global_exception(self):
  d=copy.deepcopy(SCENE);d['layers'][1]['box']=[.12,.30,.4,.05]
  d['intentional_overlaps']=[{"a":"title","b":"connector","start":1,"end":2.4,"reason":"Connector masks title only after one second"}]
  self.assertTrue(any('collision' in x for x in analyze(d)['errors']))
 def test_keyframe_sweep_detected(self):
  d=copy.deepcopy(SCENE);d['layers'][1].pop('box')
  d['layers'][1]['boxes']=[{'t':0,'box':[.1,.6,.4,.04]},{'t':1,'box':[.1,.3,.4,.04]},{'t':2.4,'box':[.1,.6,.4,.04]}]
  self.assertTrue(any('collision' in x for x in analyze(d)['errors']))
 def test_no_false_collision_at_edge(self):
  d=copy.deepcopy(SCENE);d['layers'][1]['box']=[.1,.39,.4,.01]
  self.assertFalse(analyze(d)['errors'])
 def test_repetition_warn(self):
  d=copy.deepcopy(SCENE);d['scenes']=[{'id':str(i),'start':i,'end':i+1,'composition_signature':'all-centered'} for i in range(5)]
  d['layers']=[]
  d['layers']=[{'id':'bg','owner':'0','role':'background','start':0,'end':1,'exit':'remove','box':[0,0,1,1]}]
  self.assertTrue(any('Repeated' in x for x in analyze(d)['warnings']))
 def test_invalid_layer_id(self):
  d=copy.deepcopy(SCENE);d['layers'][1]['id']='title'
  self.assertTrue(any('Duplicate' in x for x in analyze(d)['errors']))
 def test_valid_example(self):
  import json
  p=Path(__file__).resolve().parents[1]/'examples'/'scene-ownership-v75.json'
  self.assertFalse(analyze(json.loads(p.read_text('utf8')))['errors'])

if __name__=='__main__':unittest.main()
