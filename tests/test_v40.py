import json,sys,tempfile,unittest,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v40 import build,hermite
from compositor import val
from motion_audit_v40 import audit
from production_v40 import start,gate,checked
class V40(unittest.TestCase):
 def spec(self):return json.loads((ROOT/'examples/director-v40.json').read_text())
 def test_path_derivative(self):
  f=hermite([[0,0,0],[1,100,150],[2.5,220,0]],.2);eps=1e-5
  self.assertEqual(f(1),[100,150]);self.assertEqual(f(0),[0,0]);self.assertEqual(f(2.5),[220,0]);
  for k in (0,1):self.assertLess(abs((f(1)[k]-f(1-eps)[k])/eps-(f(1+eps)[k]-f(1)[k])/eps),.02)
 def test_four_recipes(self):
  p,_,_=build(self.spec(),ROOT/'examples');l={x['id']:x for x in p['layers']};self.assertAlmostEqual(val(l['hero']['x'],2.15),440);self.assertAlmostEqual(val(l['marker']['x'],2.3),440,places=4);self.assertGreater(abs(val(l['hero']['rotate'],1)),1);self.assertAlmostEqual(val(l['solid']['scale'],6),1)
 def test_bad_path(self):
  s=self.spec();s['continuous_motion'][0]['knots'][0][1]=0;self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_collision(self):
  s=self.spec();s['actions'].append({'op':'slide','layer':'hero','start':0,'end':1,'from':[95,875],'to':[50,60]});self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_forward_dependency(self):
  s=self.spec();s['continuous_motion'][0],s['continuous_motion'][1]=s['continuous_motion'][1],s['continuous_motion'][0];self.assertRaises(ValueError,build,s,ROOT/'examples')
 def test_audit(self):
  p,_,_=build(self.spec(),ROOT/'examples');c=json.loads((ROOT/'examples/creative-v40.json').read_text());r=audit(p,c);self.assertEqual(len(r['beats']),2);self.assertGreater(r['beats'][0]['layers'][0]['local_motion_score'],100)
 def test_gate_missing(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'work';start(ROOT/'examples/director-v40.json',ROOT/'examples/creative-v40.json',w);self.assertFalse(gate(w)['ready']);(w/'creative.json').write_text('{}');self.assertRaises(ValueError,checked,w)
if __name__=='__main__':unittest.main()
