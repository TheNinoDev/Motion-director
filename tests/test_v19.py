import sys,unittest,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('studio19_render',ROOT/'starter/studio/render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
Studio,validate,key,SHAPES,MATS=m.Studio,m.validate,m.key,m.SHAPES,m.MATS
FONT=next((str(p) for p in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')] if p.is_file()),None)
class TestStudio(unittest.TestCase):
    def test_keyframe_validation(self):
        for x in [dict(zoom=[[0,0],[1,2]]),dict(zoom=[[0,2],[.5,3]]),dict(yaw=[[0,0],[0,1],[1,0]]),dict(shape='invalid'),dict(quality=0),dict(roughness=2),dict(floor='yes')]:
            with self.assertRaises(ValueError):validate(dict(kind='hero',frames=20,**x))
        self.assertAlmostEqual(key({'zoom':[[0,2],[1,4]]},'zoom',.5,1),3)
    @unittest.skipUnless(FONT,'font unavailable')
    def test_2d_modes(self):
        for s in [dict(kind='kinetic',words=['NOTES','WORK']),dict(kind='kinetic',words=['NOTES','WORK'],layout='carousel'),dict(kind='kinetic',words=['NOTES','LINKS','WORK'],layout='cascade'),dict(kind='proof',src=str(ROOT/'examples/assets/v15-workspace.png'),text='Together.'),dict(kind='lockup',brand='FORM')]:
            z=Studio(180,320,dict(s,frames=20),FONT);a=z.frame(4);b=z.frame(17)
            self.assertEqual(a.shape,(320,180,3));self.assertGreater(a.std(),3);self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(a,z.frame(4)))
    @unittest.skipUnless(FONT and importlib.util.find_spec('numba'),'font/numba unavailable')
    def test_3d_shapes_materials(self):
        sys.path.insert(0,str(ROOT/'starter/studio'));self.addCleanup(lambda:sys.path.remove(str(ROOT/'starter/studio')))
        for shape in SHAPES:
            for mat in MATS:
                z=Studio(180,320,dict(kind='hero',frames=20,shape=shape,material=mat,quality=.5,floor=True,yaw=[[0,-.5],[1,.4]]),FONT);a=z.frame(4);b=z.frame(17)
                self.assertEqual(a.shape,(320,180,3));self.assertGreater(a.std(),5);self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(a,z.frame(4)))
    def test_story_scaffolds(self):
        sp=importlib.util.spec_from_file_location('studio19_preset',ROOT/'starter/studio/preset.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
        for st in p.STYLES:
            d=p.build(st,'Hook',['WORD'],'Proof','Brand','Visit.',str(ROOT/'examples/assets/v15-workspace.png'),[20]*5)
            self.assertEqual(sum(s['frames'] for s in d['shots']),100)
            for s in d['shots']:validate(dict(s['content'],frames=s['frames']))
    def test_invalid_proof(self):
        with self.assertRaises(ValueError):validate(dict(kind='proof',frames=20,src='missing.png'))
        with self.assertRaises(ValueError):validate(dict(kind='proof',frames=20,src=str(ROOT/'examples/assets/v15-workspace.png'),crop=[.8,.2,.1,.5]))
if __name__=='__main__':unittest.main()
