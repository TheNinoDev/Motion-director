import json,sys,tempfile,unittest,copy
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v43 import build,compile_programs
from compositor import val
from transition_review_v43 import targets,metrics,create,verify
from production_v43 import start,next_step,gate

class V43(unittest.TestCase):
 def plan(self):return {'fps':30,'layers':[dict(id='x',kind='rect',active=[0,4],x=110,scale=1)]}
 def prog(self):return [{'layer':'x','start':0,'steps':[{'op':'animate','end':1,'to':{'x':200},'ease':'quint'},{'op':'hold','end':1.5},{'op':'pulse','end':2.5,'offset':{'scale':.2},'ease':'sine'},{'op':'relative','end':3.5,'delta':{'x':50},'ease':'smooth'}]}]
 def test_program(self):
  p=self.plan();compile_programs(p,self.prog());l=p['layers'][0];self.assertEqual(val(l['x'],1.3),200);self.assertEqual(val(l['x'],3.5),250);self.assertAlmostEqual(val(l['scale'],2),1.2);self.assertEqual(val(l['scale'],2.5),1)
 def test_carry(self):
  p=self.plan();compile_programs(p,self.prog());l=p['layers'][0];self.assertEqual(val(l['x'],2.5),200);self.assertTrue(all(a[0]<b[0] for a,b in zip(l['x'],l['x'][1:])))
 def test_conflict(self):
  p=self.plan();p['layers'][0]['x']=[[0,100],[3,300]];self.assertRaises(ValueError,compile_programs,p,self.prog())
 def test_invalid_range(self):
  r=self.prog();r[0]['steps'][2]['offset']['scale']=-2;self.assertRaises(ValueError,compile_programs,self.plan(),r)
 def test_bad_timing(self):
  r=self.prog();r[0]['steps'][1]['end']=.99;self.assertRaises(ValueError,compile_programs,self.plan(),r)
 def test_bad_property(self):
  r=self.prog();r[0]['steps'][0]['to']={'ior':1.4};self.assertRaises(ValueError,compile_programs,self.plan(),r)
 def test_example(self):
  p,e,n=build(json.loads((ROOT/'examples/director-v43.json').read_text()),ROOT/'examples');self.assertEqual(len(e['motion_programs']),17);self.assertEqual(p['duration'],7.2)
 def test_targets(self):
  c=json.loads((ROOT/'examples/creative-v43.json').read_text());t=targets(c,30,216);self.assertEqual(len(t),4);self.assertEqual(t[0]['frames'][0],0);self.assertEqual(t[-1]['frames'][-1],215);self.assertEqual(t[1]['center'],76)
 def test_metrics(self):
  a=np.zeros((20,20,3),np.uint8);b=np.full_like(a,255);self.assertEqual(metrics(a,a)['changed_fraction'],0);self.assertEqual(metrics(a,b)['mean_rgb_delta'],255)
 def test_gate_pending(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'work';start(ROOT/'examples/director-v43.json',ROOT/'examples/creative-v43.json',w);self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready']);self.assertTrue(any('transition' in x for x in gate(w)['errors']))
 def test_decoded_video_tamper(self):
  import cv2
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);v=root/'sample.mp4';writer=cv2.VideoWriter(str(v),cv2.VideoWriter_fourcc(*'mp4v'),30,(64,112));self.assertTrue(writer.isOpened())
   for i in range(30):writer.write(np.full((112,64,3),0 if i<15 else 255,np.uint8))
   writer.release();c={'beats':[{'start':0,'outgoing_anchor':'a','incoming_anchor':'a'},{'start':.5,'outgoing_anchor':'b','incoming_anchor':'b'}]};o=root/'review';r=create(v,c,o,30,30);self.assertTrue(r['results'][1]['flags']);self.assertTrue(verify(v,c,o,30,30)['valid']);(o/r['results'][1]['file']).write_bytes(b'tamper');self.assertFalse(verify(v,c,o,30,30)['valid'])
if __name__=='__main__':unittest.main()
