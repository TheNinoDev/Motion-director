import unittest,sys,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fusion20_render',ROOT/'starter/fusion/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FONT=next((str(p) for p in (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')) if p.is_file()),None)
class FusionTest(unittest.TestCase):
 def test_invalid(self):
  for c in [dict(material='invalid'),dict(phase=2),dict(samples=0),dict(phase=[[0,0],[0,1],[1,0]]),dict(zoom=[[0,2],[1,3,'bad']]),dict(exposure=float('nan')),dict(floor='yes'),dict(quality=.1)]:
   with self.assertRaises(ValueError):m.validate(dict(kind='morph',frames=20,**c))
 def test_key(self):
  self.assertEqual(m.key(dict(phase=[[0,0],[1,1,'linear']]),'phase',.5,0),.5)
  self.assertAlmostEqual(m.key(dict(phase=[[0,0],[1,1,'out']]),'phase',.5,0),.875)
 @unittest.skipUnless(FONT,'font unavailable')
 def test_type_and_lockup(self):
  for c in [dict(kind='type',words=['LESS','NOISE'],layout=x) for x in ('stack','mono','stripe')]+[dict(kind='lockup',brand='FORM',sub='Make it yours.')]:
   z=m.Fusion(180,320,dict(c,frames=20),FONT);a=z.frame(0);b=z.frame(18);self.assertEqual(b.shape,(320,180,3));self.assertGreater(b.std(),3);self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(b,z.frame(18)))
 @unittest.skipUnless(FONT and importlib.util.find_spec('numba'),'font or numba unavailable')
 def test_geometry_and_materials(self):
  # Module name optics is shared by legacy studio; isolate runtime import for unit tests.
  old=sys.modules.pop('optics',None);sys.path.insert(0,str(ROOT/'starter/fusion'))
  try:
   for shape,material in zip(m.SHAPES,m.MATS):
    z=m.Fusion(180,320,dict(kind='morph',frames=20,shape=shape,material=material,quality=.5,phase=[[0,0],[1,1]],zoom=1.8,grain=0,samples=2),FONT)
    a=z.frame(0);b=z.frame(19);self.assertGreater(a.std(),5);self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(a,z.frame(0)))
   for mask in ('rounded','split','iris','diagonal'):
    z=m.Fusion(180,320,dict(kind='bridge',frames=20,src=str(ROOT/'examples/assets/v15-workspace.png'),shape='tiles',mask=mask,quality=.4,grain=0,phase=1),FONT)
    a=z.frame(0);b=z.frame(9);c=z.frame(19);self.assertFalse(np.array_equal(a,b));self.assertFalse(np.array_equal(b,c));self.assertGreater(c.std(),8)
  finally:
   sys.path.pop(0);sys.modules.pop('optics',None)
   if old is not None:sys.modules['optics']=old
 def test_invalid_bridge(self):
  with self.assertRaises(ValueError):m.validate(dict(kind='bridge',frames=20,src='missing.png'))
if __name__=='__main__':unittest.main()
