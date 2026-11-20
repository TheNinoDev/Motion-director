import unittest,sys,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'starter/contact3d'),str(ROOT/'starter/composite_film'),str(ROOT/'starter'),str(ROOT/'scripts')]
from render import simulate,sample,bake_layer,camera,raster
from compositor import Engine,validate,val
from agent_preflight import inspect
import softbody,text3d
class V33(unittest.TestCase):
 def setUp(self):self.p=json.loads((ROOT/'examples/contact-v33.json').read_text())
 def test_contact(self):
  for b in self.p['bodies']:
   r=b['radius'];a,ev=simulate(b,1.85);self.assertEqual(len(ev),1);self.assertAlmostEqual(ev[0],(b['position'][0]-r)/abs(b['velocity'][0]),delta=.002);self.assertGreater(a[-1,6],0);self.assertLess(a[:,3].min(),r*.8);self.assertTrue(np.all(a[:,0]-a[:,3]>=-1e-8));np.testing.assert_allclose(np.prod(a[:,3:6],1),r**3);np.testing.assert_allclose(a[:,8],b['velocity'][2])
 def test_independent_lanes(self):
  a,b=[simulate(q,1.85)[0] for q in self.p['bodies']];self.assertTrue(np.all(np.linalg.norm(a[:,:3]-b[:,:3],axis=1)>a[:,3:6].max(1)+b[:,3:6].max(1)))
 def test_bake(self):
  b=self.p['bodies'][0];a,_=simulate(b,1.85);l=bake_layer(b,a,5,60,rate=.37);t=3.1;self.assertAlmostEqual(val(l['x'],t),160+sample(a,t*.37)[0]*100);self.assertEqual(l['geometry'],'ellipsoid');self.assertLess(min(x[1] for x in l['size_x']),.8)
 def test_invalid(self):
  with self.assertRaises(ValueError):simulate(dict(self.p['bodies'][0],position=[0,1,0]),1)
 def test_raster(self):
  o,r=camera(160,90);a=np.array([simulate(b,1.85)[0][0] for b in self.p['bodies']]);im=raster(o,r,a,np.ones((2,3),np.float32)*.5);self.assertEqual(im.shape,(90,160,3));self.assertGreater(im.std(),5)
 def test_preflight(self):
  p=json.loads((ROOT/'examples/type-v33.json').read_text());self.assertEqual(inspect(p,ROOT/'examples'),[]);p['layers'][2]['antialias']=3
  with self.assertRaises(ValueError):validate(p,ROOT/'examples')
 def test_sphere_softbody(self):
  l=dict(geometry='sphere',w=200,h=200,depth=200,softbody={'events':[{'time':0,'strength':.8}]});q=softbody.solid_layer(l,.06,val);self.assertEqual(q['geometry'],'ellipsoid');self.assertLess(q['size_y'],1);self.assertAlmostEqual(q['size_x']*q['size_y']*q['scale_z'],1)
 def test_text_quality(self):
  p=json.loads((ROOT/'examples/type-v33.json').read_text());p.update(width=180,height=320);a=Engine(validate(p,ROOT/'examples'),ROOT/'examples');self.assertGreater(a.glyphs['type'][0].shape[0],500);im=a.frame(.45);self.assertEqual(im.shape,(320,180,3));self.assertEqual(im.dtype,np.uint8);self.assertFalse(np.array_equal(im,a.frame(1.3)))
if __name__=='__main__':unittest.main()
