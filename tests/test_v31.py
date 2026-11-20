import sys,unittest,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import Engine,validate
from volume import SHAPES,PRESETS
from volume_compile import showcase,build
class V31(unittest.TestCase):
 def make(self,**kw):
  l=dict(id='v',kind='glass_object',active=[0,2],x=360,y=640,w=280,h=270,depth=190,geometry='rounded_box',quality=.6);l.update(kw)
  return dict(width=180,height=320,fps=30,duration=2,background='#203246',layers=[dict(id='bg',kind='text',active=[0,2],text='GLASS',size=118,x=360,y=640,color='#ffffff'),l])
 def render(self,p,t=0):return Engine(validate(p,ROOT),ROOT).frame(t)
 def test_all_shapes(self):
  hashes=set()
  for shape in SHAPES:
   p=self.make(geometry=shape,pitch=21,yaw=38);a=self.render(p);b=self.render(dict(p,layers=p['layers'][:1]));self.assertGreater(np.abs(a.astype(float)-b).sum(),500,shape);hashes.add(a.tobytes())
  self.assertEqual(len(hashes),len(SHAPES))
 def test_all_materials(self):
  self.assertEqual(len({self.render(self.make(material=m)).tobytes() for m in PRESETS}),len(PRESETS))
 def test_rotation_depth_morph(self):
  p=self.make(yaw=[[0,0],[2,80]],pitch=21,depth=[[0,90],[2,240]],phase3d=[[0,0],[2,1]]);e=Engine(validate(p,ROOT),ROOT);self.assertFalse(np.array_equal(e.frame(0),e.frame(1)));self.assertTrue(np.array_equal(e.frame(1),e.frame(1)))
 def test_opacity_mask(self):
  p=self.make(mask='iris',mask_progress=0);self.assertTrue(np.array_equal(self.render(p),self.render(dict(p,layers=p['layers'][:1]))));p=self.make(opacity=0);self.assertTrue(np.array_equal(self.render(p),self.render(dict(p,layers=p['layers'][:1]))))
 def test_order_parent(self):
  p=showcase();p.update(width=180,height=320);e=Engine(validate(p,ROOT),ROOT);self.assertFalse(np.array_equal(e.frame(0),e.frame(3)))
 def test_reject(self):
  for kw in [dict(ior=.5),dict(geometry='mesh'),dict(depth=0),dict(material='unknown'),dict(matte='bg')]:
   with self.assertRaises(ValueError):validate(self.make(**kw),ROOT)
 def test_full_plan(self):
  p=build(json.loads((ROOT/'starter/composite_film/premium-timing.json').read_text()),ROOT/'examples/assets/v15-workspace.png');validate(p,ROOT);self.assertEqual(p['duration'],24.1);self.assertEqual(next(l for l in p['layers'] if l['id']=='proof-lens')['kind'],'glass_object')
if __name__=='__main__':unittest.main()
