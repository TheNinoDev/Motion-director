import unittest,importlib.util,copy
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sequence18',ROOT/'starter/sequence/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FONT=next((str(p) for p in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')] if p.is_file()),None)
SRC=str(ROOT/'examples/assets/v15-workspace.png')
BASE=dict(kind='consolidate',frames=90,hook='FIVE TABS.\nONE PROJECT.',turn='Why five?',payoff='One place.',brand='FORM',cta='Open your workspace.',src=SRC,beats=[0,18,35,53,74])
@unittest.skipUnless(FONT,'font unavailable')
class TestSequence(unittest.TestCase):
    def test_all_kinds(self):
        for k in m.KINDS:
            s=m.Sequence(180,320,dict(BASE,kind=k,alternate={'src':str(ROOT/'examples/assets/demo-profile.png')}),FONT)
            for f in (1,19,34,35,44,54,73,80,89):
                a=s.frame(f);self.assertEqual(a.shape,(320,180,3));self.assertGreater(a.std(),4)
            self.assertTrue(np.array_equal(s.frame(44),s.frame(44)))
            self.assertFalse(np.array_equal(s.frame(19),s.frame(32)))
    def test_optics(self):
        for t in ('cut','wipe','iris'):
            for o in ('lens','brackets','none'):
                s=m.Sequence(180,320,dict(BASE,transition=t,focus=o,samples=2),FONT)
                self.assertEqual(s.sample(34).shape,(320,180,3));self.assertEqual(s.sample(44).shape,(320,180,3))
    def test_invalid(self):
        for e in (dict(beats=[0,1,20,30,40]),dict(labels=[]),dict(frames=2),dict(kind='bad'),dict(kind='compare'),dict(focus='bad'),dict(light=2),dict(transition='bad')):
            with self.assertRaises(ValueError):m.validate(dict(BASE,**e))
if __name__=='__main__':unittest.main()
