import sys,unittest,json,tempfile,copy
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'starter/composite_film'))
from director_v45 import build
from compositor import val
from cadence_review_v45 import create,verify,metrics
from production_v45 import start,next_step,gate

class V45(unittest.TestCase):
 def spec(self):return json.loads((ROOT/'examples/director-v45.json').read_text())
 def compiled(self):return build(self.spec(),ROOT/'examples')
 def test_drag_lock(self):
  p,e,_=self.compiled();by={l['id']:l for l in p['layers']}
  for a,b in [(1.7,3.6),(3.9,6.5)]:
   for t in np.linspace(a+(b-a)*.53,a+(b-a)*.88,15):
    for k in ('x','y'):self.assertAlmostEqual(val(by['cursor'][k],t),val(by['card1' if a<2 else 'card2'][k],t),places=7)
  self.assertEqual(val(by['card1']['x'],8),-156);self.assertEqual(val(by['card2']['y'],8),125);self.assertEqual(len(e['gesture_events']),6)
 def test_tap_restore(self):
  p,e,_=self.compiled();by={l['id']:l for l in p['layers']};self.assertAlmostEqual(val(by['card1']['scale'],.85+.75*.62),.89);self.assertEqual(val(by['card1']['scale'],2),1)
 def test_original_immutable(self):
  s=self.spec();before=copy.deepcopy(s);build(s,ROOT/'examples');self.assertEqual(s,before)
 def test_parent_mismatch(self):
  s=self.spec();s['gestures'][0]['steps'][0]['target']='confirm';self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_lane_conflict(self):
  s=self.spec();next(l for l in s['layers'] if l['id']=='cursor')['x']=[[0,0],[1,2]];self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_duration_conflict(self):
  s=self.spec();s['gestures'][0]['steps'][1]['start']=.5;self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_inactive_parent(self):
  s=self.spec();next(l for l in s['layers'] if l['id']=='board')['active']=[0,7];self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_invalid_press(self):
  s=self.spec();s['gestures'][0]['steps'][1]['press']=.3;self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_static_metrics(self):
  self.assertTrue(metrics([0]*30,0,30)['flags']);self.assertFalse(metrics([1]*12,0,30)['flags']);self.assertTrue(metrics([1,50],0,30)['flags'])
 def test_cadence_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);v=d/'video.mp4';out=d/'review';w=cv2.VideoWriter(str(v),cv2.VideoWriter_fourcc(*'mp4v'),30,(64,112));self.assertTrue(w.isOpened())
   for i in range(60):w.write(np.full((112,64,3),20 if i<30 else 160,np.uint8))
   w.release();c={'beats':[{'start':0,'end':1},{'start':1,'end':2}]};r=create(v,c,out,30,60);self.assertEqual(len(r['results']),2);self.assertTrue(r['results'][0]['flags']);self.assertTrue(verify(v,c,out,30,60)['valid']);(out/'beat-000.png').write_bytes(b'bad');self.assertFalse(verify(v,c,out,30,60)['valid'])
 def test_new_session(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'w';start(ROOT/'examples/director-v45.json',ROOT/'examples/creative-v45.json',path);self.assertEqual(next_step(path)['stage'],'preview');self.assertFalse(gate(path)['ready'])
if __name__=='__main__':unittest.main()
