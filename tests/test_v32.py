import sys,unittest,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'));sys.path.insert(0,str(ROOT/'starter'));sys.path.insert(0,str(ROOT/'scripts'))
from compositor import Engine,validate
import softbody,font_library,text3d
from softbody_compile import showcase,recut
class V32(unittest.TestCase):
 def test_response(self):
  self.assertEqual(softbody.response(-1,3,.6),0);self.assertAlmostEqual(softbody.response(0,3,.6),0);self.assertLess(abs(softbody.response(8,3,.6)),1e-7)
 def test_squash_volume(self):
  v=np.array([[x,y,z] for x in (-1,1) for y in (-1,1) for z in (-1,1)],float);q={'events':[{'time':1,'strength':.8,'mode':'squash'}]};self.assertTrue(np.array_equal(v,softbody.deform(v,q,.9)));a=softbody.deform(v,q,1.07);self.assertAlmostEqual(np.prod(np.ptp(a,axis=0)),8);self.assertFalse(np.array_equal(v,a));self.assertTrue(np.array_equal(a,softbody.deform(v,q,1.07)))
 def test_all_modes(self):
  v=np.random.default_rng(7).normal(size=(30,3))
  for m in softbody.MODES:
   q={'events':[{'time':0,'strength':.8,'mode':m}]};a=softbody.deform(v,softbody.validate(q),.08);self.assertGreater(np.linalg.norm(a-v),.01,m)
 def test_bad(self):
  for q in [{'frequency':0},{'damping':1},{'events':[{'time':-1,'strength':1}]},{'events':[{'time':0,'strength':2}]}]:
   with self.assertRaises(ValueError):softbody.validate(q)
 def test_text(self):
  p=showcase();p.update(width=180,height=320);e=Engine(validate(p,ROOT),ROOT);a=e.frame(.5);self.assertEqual(a.shape,(320,180,3));self.assertTrue(np.array_equal(a,e.frame(.5)));self.assertFalse(np.array_equal(a,e.frame(1.5)));q=dict(p,layers=[l for l in p['layers'] if l['id']!='type']);b=Engine(validate(q,ROOT),ROOT).frame(.5);self.assertGreater(np.abs(a.astype(float)-b).sum(),1000)
 def test_materials(self):
  p=showcase();p.update(width=180,height=320);hashes=set()
  for mat in text3d.MATERIALS:
   next(l for l in p['layers'] if l['id']=='type')['material']=mat;hashes.add(Engine(validate(p,ROOT),ROOT).frame(.6).tobytes())
  self.assertEqual(len(hashes),len(text3d.MATERIALS))
 def test_solid_compat(self):
  p=showcase();p.update(width=180,height=320);e=Engine(validate(p,ROOT),ROOT);a=e.frame(3.28);del next(l for l in p['layers'] if l['id']=='glass')['softbody'];b=Engine(validate(p,ROOT),ROOT).frame(3.28);self.assertFalse(np.array_equal(a,b))
 def test_catalog(self):
  a=font_library.catalog();self.assertGreaterEqual(len(a),91);self.assertEqual(len({x['family'] for x in a}),len(a));self.assertGreaterEqual(len({x['role'] for x in a}),6);self.assertTrue({x['family'] for x in json.loads((ROOT/'assets/font-catalog-v32.json').read_text())['families']} <= {x['family'] for x in a});self.assertEqual(font_library.resolve('Test','Bold',{'test':[('Bold','test.otf')]}),'test.otf');
  with self.assertRaises(ValueError):font_library.resolve('Test','Regular',{'test':[('Bold','test.otf')]})
 def test_font_alias(self):
  p=showcase();p.update(width=180,height=320);e=Engine(validate(p,ROOT),ROOT);p['fonts']={'custom':e.fonts['heavy']};next(l for l in p['layers'] if l['id']=='type')['font']='custom';self.assertTrue(np.array_equal(e.frame(.5),Engine(validate(p,ROOT),ROOT).frame(.5)))
 def test_recut(self):
  p=recut(json.loads((ROOT/'starter/composite_film/premium-timing.json').read_text()),ROOT/'examples/assets/v15-workspace.png');validate(p,ROOT);self.assertEqual(p['duration'],24.1);self.assertEqual(next(l for l in p['layers'] if l['id']=='count-face')['kind'],'text3d');self.assertIn('softbody',next(l for l in p['layers'] if l['id']=='hero')['mesh'])
if __name__=='__main__':unittest.main()
