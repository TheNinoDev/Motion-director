import unittest,sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v48 import build,expand,PRESETS,definition
from sequence_audit_v48 import report,compare
from production_v48 import start,next_step,gate
from compositor import val

class V48(unittest.TestCase):
 def setUp(self):self.spec=json.loads((ROOT/'examples/director-v48.json').read_text());self.base=ROOT/'examples'
 def compile(self,s=None):return build(self.spec if s is None else s,self.base)
 def test_catalog(self):
  self.assertEqual(len(PRESETS),8)
  for d in PRESETS.values():definition(d)
 def test_compile(self):
  p,e,_=self.compile();self.assertEqual(len(e['sequences']),16);self.assertEqual(len(e['cue_actions']),16);self.assertEqual(len(e['sound_cues']),7)
 def test_custom_and_state(self):
  p,e,_=self.compile();by={x['id']:x for x in p['layers']};self.assertAlmostEqual(val(by['card1line']['opacity'],8.99),.82);self.assertAlmostEqual(val(by['card2line']['opacity'],6),.28)
 def test_immutable(self):
  b=copy.deepcopy(self.spec);self.compile();self.assertEqual(b,self.spec)
 def test_duration_retime(self):
  a=self.compile();self.spec['sequences'][4]['duration']=.5;b=self.compile();d=compare(a,b);self.assertEqual({x['layer'] for x in d['layer_changes']},{'status1','status1label'});self.assertEqual([x['id'] for x in d['sequence_changes']],['reveal1']);self.assertFalse(d['audio_cues_changed'])
 def test_gesture_retime(self):
  a=self.compile();self.spec['gestures'][0]['steps'][2]['end']=3.7;b=self.compile();self.assertEqual(b[1]['named_markers']['plan_ready']-a[1]['named_markers']['plan_ready'],3);self.assertGreater(len(compare(a,b)['marker_changes']),0)
 def test_missing_slot(self):
  self.spec['sequences'][0]['bind']={};self.assertRaisesRegex(ValueError,'bind',self.compile)
 def test_unknown_param(self):
  self.spec['sequences'][0]['params']={'typo':1};self.assertRaisesRegex(ValueError,'parameter',self.compile)
 def test_short_duration(self):
  self.spec['sequences'][0]['duration']=1/30;self.assertRaisesRegex(ValueError,'too short',self.compile)
 def test_duplicate_instance(self):
  self.spec['sequences'].append(copy.deepcopy(self.spec['sequences'][0]));self.assertRaisesRegex(ValueError,'instance',self.compile)
 def test_overlap(self):
  r=copy.deepcopy(self.spec['sequences'][0]);r['id']='extra';self.spec['sequences'].append(r);self.assertRaisesRegex(ValueError,'overlap',self.compile)
 def test_custom_shadow(self):
  self.spec['sequence_library']['contact_feedback']=PRESETS['contact_feedback'];self.assertRaisesRegex(ValueError,'custom',self.compile)
 def test_bad_parameter_ref(self):
  self.spec['sequence_library']['finish_lines']['actions'][0]['values']['opacity']='$missing';self.assertRaisesRegex(ValueError,'parameter',self.compile)
 def test_schedule_rounding(self):
  p,e,_=self.compile();r=report(p,e);x=next(x for x in r['sequences'] if x['id']=='title1');self.assertEqual(x['duration_frames'],15);self.assertTrue(all(x['start_frame']<=a['start_frame']<a['end_frame']<=x['end_frame'] for a in x['actions']))
 def test_legacy(self):
  p,e,_=self.compile(json.loads((self.base/'director-v47.json').read_text()));self.assertEqual(e['sequences'],[]);self.assertEqual(len(e['sound_cues']),7)
 def test_session(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'work';start(self.base/'director-v48.json',self.base/'creative-v48.json',w);self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready'])
if __name__=='__main__':unittest.main()
