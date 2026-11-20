import unittest,sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'starter/composite_film'))
from director_v47 import build,resolve_markers
from production_v47 import start,next_step,gate
from compositor import val
from cue_review_v47 import targets,create,verify
from agent_session import sha
import subprocess

class V47(unittest.TestCase):
 def spec(self):return json.loads((ROOT/'examples/director-v47.json').read_text())
 def compile(self,s=None):return build(s if s is not None else self.spec(),ROOT/'examples')
 def test_markers(self):
  self.assertEqual(resolve_markers([{'id':'b','after':'a','offset':.2},{'id':'a','time':1}],[],30,90),{'b':36,'a':30})
 def test_cycle(self):self.assertRaisesRegex(ValueError,'cycle',resolve_markers,[{'id':'a','after':'b','offset':0},{'id':'b','after':'a','offset':0}],[],30,90)
 def test_unknown(self):self.assertRaisesRegex(ValueError,'unknown',resolve_markers,[{'id':'a','after':'none','offset':0}],[],30,90)
 def test_duplicate(self):self.assertRaises(ValueError,resolve_markers,[{'id':'a','time':1},{'id':'a','time':2}],[],30,90)
 def test_out_of_bounds(self):self.assertRaises(ValueError,resolve_markers,[{'id':'a','time':3}],[],30,90)
 def test_repeat_pulse(self):
  p,e,_=self.compile();h=next(x for x in p['layers'] if x['id']=='halo1')['opacity'];m=e['named_markers'];fps=p['fps'];self.assertAlmostEqual(val(h,(m['select']+7)/fps),.8);self.assertAlmostEqual(val(h,3),0);self.assertAlmostEqual(val(h,(m['plan_ready']+7)/fps),.8)
 def test_independent_lanes(self):
  p,e,_=self.compile();x=next(x for x in p['layers'] if x['id']=='status1');f=e['named_markers']['finish'];self.assertAlmostEqual(val(x['opacity'],f/30),1);self.assertAlmostEqual(val(x['scale'],(f+6)/30),1.08)
 def test_retime(self):
  s=self.spec();_,e,_=self.compile(s);s['gestures'][0]['steps'][2]['end']=3.7;p,f,_=self.compile(s);delta=f['named_markers']['plan_ready']-e['named_markers']['plan_ready'];self.assertGreater(delta,0);self.assertEqual(f['named_markers']['plan_status']-e['named_markers']['plan_status'],delta);self.assertEqual(f['named_sound_cues'][2]['frame']-e['named_sound_cues'][2]['frame'],delta)
 def test_identity(self):
  s=self.spec();s['markers'][2]['gesture']['expect_target']='card2';self.assertRaises(ValueError,self.compile,s)
 def test_overlap(self):
  s=self.spec();r=copy.deepcopy(s['cue_actions'][0]);r['offset']=.1;s['cue_actions'].append(r);self.assertRaisesRegex(ValueError,'overlap',self.compile,s)
 def test_occupied_lane(self):
  s=self.spec();s['cue_actions'][0]['layer']='card1';s['cue_actions'][0]['values']={'scale':.1};self.assertRaises(ValueError,self.compile,s)
 def test_relative_state(self):
  s=self.spec();s['cue_actions'].append({'marker':'plan_status','layer':'status1','offset':0,'duration':.2,'op':'relative','values':{'x':10},'ease':'smooth'});s['cue_actions'].append({'marker':'finish','layer':'status1','offset':0,'duration':.2,'op':'relative','values':{'x':15},'ease':'smooth'});p,e,_=self.compile(s);x=next(x for x in p['layers'] if x['id']=='status1')['x'];self.assertAlmostEqual(val(x,9),292)
 def test_bad_duration(self):
  s=self.spec();s['cue_actions'][0]['duration']=.001;self.assertRaises(ValueError,self.compile,s)
 def test_immutability(self):
  s=self.spec();old=copy.deepcopy(s);self.compile(s);self.assertEqual(s,old)
 def test_targets(self):
  p,e,_=self.compile();t=targets(e,p['fps'],270);self.assertEqual(len(t),9);self.assertTrue(all(x['frame'] in x['frames'] for x in t))
 def test_session(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'work';start(ROOT/'examples/director-v47.json',ROOT/'examples/creative-v47.json',w);self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready']);state=json.loads((w/'production.json').read_text());self.assertEqual(state['inputs'][str((w/'expanded.json').resolve())],sha(w/'expanded.json'))
 def test_actual_evidence(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);v=d/'sample.mp4';subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=64x112:r=30:d=1','-c:v','libx264',str(v)],check=True);e={'named_markers':{'a':9},'cue_actions':[{'marker':'a','start_frame':9,'end_frame':15}],'named_sound_cues':[]};out=d/'review';create(v,e,out,30,30);self.assertTrue(verify(v,e,out,30,30)['valid']);(out/'cue-000.png').write_bytes(b'tampered');self.assertFalse(verify(v,e,out,30,30)['valid'])
if __name__=='__main__':unittest.main()
