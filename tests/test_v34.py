import sys,unittest,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'starter/contact3d'),str(ROOT/'starter/composite_film'),str(ROOT/'starter'),str(ROOT/'scripts')]
from render import simulate
from presets import resolve,PRESETS
import softbody,font_library,elastic_recipe
from compositor import validate
class V34(unittest.TestCase):
 def test_all_contact_presets(self):
  b=dict(id='a',position=[4.4,1.2,0],velocity=[-3.8,0,0],radius=.67,color='#aaccee')
  for p in PRESETS:
   t,e=simulate(dict(b,preset=p),2.3);self.assertEqual(len(e),1,p);self.assertTrue(np.isfinite(t).all());self.assertGreaterEqual(np.min(t[:,0]-t[:,3]),-1e-8);np.testing.assert_allclose(np.prod(t[:,3:6],axis=1),b['radius']**3)
 def test_jelly_vs_rubber(self):
  p=json.loads((ROOT/'examples/jelly-v34.json').read_text());a,b=[simulate(x,2.3)[0] for x in p['bodies']];r=p['bodies'][0]['radius'];self.assertLess(a[:,3].min(),b[:,3].min());self.assertGreater(a[:,3].max(),r*1.04);self.assertGreater(a[:,3].max(),b[:,3].max())
 def test_overrides(self):
  self.assertEqual(resolve(dict(preset='jelly',stiffness=99))['stiffness'],99)
  for b in [dict(preset='bogus'),dict(recovery_frequency=0),dict(recovery_amplitude=.9)]:
   with self.assertRaises(ValueError):resolve(b)
 def test_recipe(self):
  for recipe in elastic_recipe.RECIPES:
   for preset in softbody.PRESETS:
    p=elastic_recipe.build(recipe,preset);validate(p,ROOT);self.assertEqual(p['layers'][0]['softbody']['preset'],preset)
 def test_catalog(self):
  a=font_library.catalog();self.assertEqual(len(a),217);self.assertEqual(len({x['family'].casefold() for x in a}),217);self.assertEqual(len({x['role'] for x in a}),9)
  for mood in font_library.PAIRINGS:
   for a in font_library.pairs(mood,{}):self.assertFalse(a['both_installed']);self.assertTrue({a['hero'],a['support']} <= {x['family'] for x in font_library.catalog()})
if __name__=='__main__':unittest.main()
