import sys,unittest,tempfile,json,copy
from pathlib import Path
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'starter/composite_film'))
from director_v44 import build,curve,compile_accents,PROFILES
from source_repair_v44 import repair
from flow_review_v44 import measure,compare,create,verify
from agent_session import sha
from production_v44 import start,gate,next_step
from compositor import val

class V44(unittest.TestCase):
 def spec(self):return json.loads((ROOT/'examples/director-v44.json').read_text())
 def test_profiles(self):
  for n,(t,v) in PROFILES.items():
   self.assertAlmostEqual(curve(n,0),0);self.assertAlmostEqual(curve(n,1),v[-1]);self.assertLess(abs(curve(n,.00001)/.00001),.01);self.assertLess(abs((curve(n,1)-curve(n,.99999))/.00001),.01)
 def test_build(self):
  p,e,n=build(self.spec(),ROOT/'examples');self.assertEqual(len(e['motion_accents']),4);stage=next(l for l in p['layers'] if l['id']=='stage');self.assertAlmostEqual(val(stage['rotate'],2.7),22);self.assertLess(val(stage['rotate'],.8),0)
 def test_conflict(self):
  p=self.spec();p['motion_accents'][0]['delta']={'y':22};self.assertRaises(ValueError,build,p,ROOT/'examples')
 def test_bounds(self):
  p=self.spec();p['motion_accents'][1]['delta']={'scale_x':-10};self.assertRaises(ValueError,build,p,ROOT/'examples')
 def test_flow_translation(self):
  a=np.zeros((160,240,3),np.uint8);rng=np.random.default_rng(7);a[35:125,50:150]=rng.integers(0,255,(90,100,3),dtype=np.uint8);b=np.roll(a,4,axis=1);m,_,_=measure(a,b);self.assertGreater(m['support'],.05);self.assertAlmostEqual(m['dx'],4,delta=.5);self.assertAlmostEqual(m['dy'],0,delta=.5)
 def test_flow_static(self):
  a=np.zeros((80,100,3),np.uint8);m,_,_=measure(a,a);self.assertEqual(m['support'],0);self.assertIsNone(compare(m,m))
 def test_direction(self):
  a=dict(support=.2,coherence=1,speed_px_frame=4,dx=4,dy=0);b={**a,'dx':-4};self.assertAlmostEqual(compare(a,b),180)
 def test_repair(self):
  with tempfile.TemporaryDirectory() as d:
   s=Path(d)/'source.json';s.write_text(json.dumps(self.spec()));out=s.with_name('new.json');r={'source_sha256':sha(s),'reason':'Improve type size','changes':[{'layer':'foot','field':'size','before':19,'after':17}]};x=repair(s,r,out);self.assertEqual(x['changed'],[['foot','size']]);self.assertEqual(sha(s),r['source_sha256']);self.assertRaises(ValueError,repair,s,r,out)
 def test_protected(self):
  with tempfile.TemporaryDirectory() as d:
   s=Path(d)/'source.json';s.write_text(json.dumps(self.spec()));r={'source_sha256':sha(s),'reason':'wrong','changes':[{'layer':'intro','field':'y','before':276,'after':250}]};self.assertRaises(ValueError,repair,s,r,s.with_name('new.json'))
 def test_flow_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);v=r/'v.mp4';w=cv2.VideoWriter(str(v),cv2.VideoWriter_fourcc(*'mp4v'),30,(64,112));self.assertTrue(w.isOpened())
   for i in range(15):
    a=np.zeros((112,64,3),np.uint8);a[25:50,5+i:23+i]=255;w.write(a)
   w.release();c={'beats':[{'start':0,'outgoing_anchor':'a','incoming_anchor':'a'}]};report=create(v,c,r/'flow',30,15);self.assertTrue(verify(v,c,r/'flow',30,15)['valid']);(r/'flow'/report['results'][0]['file']).write_bytes(b'changed');self.assertFalse(verify(v,c,r/'flow',30,15)['valid'])
 def test_gate(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'session';start(ROOT/'examples/director-v44.json',ROOT/'examples/creative-v44.json',w);self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready'])
if __name__=='__main__':unittest.main()
