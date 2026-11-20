import unittest,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cinematic17',ROOT/'starter/cinematic/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FONT=next((p for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf'] if Path(p).is_file()),None)
class TestCinematic(unittest.TestCase):
    @unittest.skipUnless(FONT,'font unavailable')
    def test_presets(self):
        for kind in m.KINDS:
            with self.subTest(kind=kind):
                x=m.Scene(180,320,dict(kind=kind,frames=26,headline='ONE\nSPACE',brand='FORM',label='DEMO',sub='Selected work',src=str(ROOT/'examples/assets/v15-workspace.png')),FONT)
                a,b=x.frame(4),x.frame(22);self.assertEqual(a.shape,(320,180,3));self.assertGreater(a.std(),5);self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(b,x.frame(22)))
    @unittest.skipUnless(FONT,'font unavailable')
    def test_materials(self):
        for shape in ('ring','sphere','disc'):
            for material in ('chrome','glass','ceramic'):
                s=m.Scene(180,320,dict(kind='artifact',frames=24,shape=shape,material=material),FONT);self.assertGreater(s.frame(12).std(),3)
    def test_limits(self):
        for extra in (dict(grain=-1),dict(material='bad'),dict(camera_strength=3),dict(crop=[0,.9,1,.1]),dict(text_scale=4)):
            with self.assertRaises(ValueError):m.validate(dict(kind='artifact',frames=12,**extra))
        with self.assertRaises(ValueError):m.validate(dict(kind='detail',frames=20))
if __name__=='__main__':unittest.main()
