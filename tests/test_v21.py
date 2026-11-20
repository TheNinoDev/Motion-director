import unittest,importlib.util,json,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('kinetic21',ROOT/'starter/kinetic/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FONT=next((str(p) for p in (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')) if p.is_file()),None)
class KineticTest(unittest.TestCase):
 def test_bad_tracks(self):
  for c in [dict(spread=2),dict(yaw=float('nan')),dict(spread=[[0,0],[0,1]]),dict(zoom=[[0,1],[1,2,'bad']]),dict(samples=0),dict(count=6001),dict(seed=-1),dict(field='invalid')]:
   with self.assertRaises(ValueError):m.validate(dict(kind='field',frames=20,**c))
 def test_asset_and_type(self):
  for c in [dict(kind='proof',src='missing.png'),dict(kind='type',words=[]),dict(kind='lockup',brand=''),dict(kind='field',glyph='    ')]:
   with self.assertRaises(ValueError):m.validate(dict(frames=20,**c))
 def test_interpolation(self):
  self.assertAlmostEqual(m.track(dict(spread=[[0,0],[1,1,'linear']]),'spread',.5,0),.5)
  self.assertAlmostEqual(m.track(dict(spread=[[0,0],[1,1,'out']]),'spread',.5,0),.875)
 @unittest.skipUnless(FONT,'no font')
 def test_fields(self):
  for field in m.FIELDS:
   z=m.Kinetic(180,320,dict(kind='field',frames=24,field=field,count=400,glyph='F',samples=2,grain=.4),FONT);a=z.frame(0);b=z.frame(23);self.assertEqual(b.shape,(320,180,3));self.assertGreater(b.std(),4);self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(b,z.frame(23)))
 @unittest.skipUnless(FONT,'no font')
 def test_proof_and_types(self):
  cs=[dict(kind='proof',src=str(ROOT/'examples/assets/v15-workspace.png'),crop=[.1,.2,.6,.7],mask=k) for k in ('diagonal','iris','split','horizontal')]+[dict(kind='type',words=['LOW','HIGH'],layout=k) for k in ('stack','split','track')]+[dict(kind='lockup',brand='FORM',sub='Keep it simple.')]
  for c in cs:
   z=m.Kinetic(180,320,dict(c,frames=24),FONT);a=z.frame(0);b=z.frame(23);self.assertEqual(b.shape,(320,180,3));self.assertGreater(b.std(),4);self.assertFalse(np.array_equal(a,b))
 def test_example_contract(self):
  p=ROOT/'examples/kinetic-v21.json';d=json.loads(p.read_text());self.assertEqual(sum(s['frames'] for s in d['shots']),237)
if __name__=='__main__':unittest.main()
