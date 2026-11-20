import importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('layer_renderer',ROOT/'starter/layer_motion/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FONTS=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf']
FONT=next((x for x in FONTS if Path(x).exists()),None)
class LayerTests(unittest.TestCase):
    def test_keys(self):
        self.assertAlmostEqual(m.value([[0,0],[10,100,'inout']],5),50)
        self.assertEqual(m.value([[0,0],[10,100,'hold']],9),0)
    @unittest.skipUnless(FONT,'system font required')
    def test_masks(self):
        for axis in ('x','y','radial','diagonal','dissolve'):
            layer=dict(id='a',kind='rect',size=[450,450],color='#ffffff',reveal=[[0,0],[5,1]],reveal_axis=axis)
            sc=m.Scene(180,320,dict(frames=6,layers=[layer]),FONT)
            a,b,c=[sc.frame(i) for i in (0,2,5)]
            self.assertTrue(a.mean()<b.mean()<c.mean(),axis)
    @unittest.skipUnless(FONT,'system font required')
    def test_particles_and_gradient(self):
        s=dict(frames=10,layers=[dict(id='g',kind='gradient',size=[800,900],color='#77aaff80'),dict(id='p',kind='particles',size=[800,900],count=64,seed=3,rotation=[[0,0],[9,90]])])
        a=m.Scene(180,320,s,FONT);b=m.Scene(180,320,s,FONT)
        self.assertTrue(np.array_equal(a.frame(5),b.frame(5)));self.assertFalse(np.array_equal(a.frame(0),a.frame(9)))
    def test_invalid(self):
        l=dict(id='x',kind='rect',size=[120,120],x=[[0,1],[0,2]])
        with self.assertRaises(ValueError):m.validate(dict(frames=10,layers=[l]))
        with self.assertRaises(ValueError):m.validate(dict(frames=10,layers=[dict(l,x=0,reveal_axis='madeup')]))
if __name__=='__main__':unittest.main()
