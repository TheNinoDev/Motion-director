import unittest,importlib.util,tempfile
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location('mesh23',R/'starter/mesh_motion/render.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
F=next((str(p) for p in (Path('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')) if p.is_file()),None)
class MeshTest(unittest.TestCase):
 def test_invalid(self):
  for c in [dict(kind='bad'),dict(kind='sheet',material='texture'),dict(kind='ribbon',samples=0),dict(kind='ribbon',zoom=[[0,1],[0,2]]),dict(kind='ribbon',bend=9),dict(kind='obj',src='x.obj')]:
   with self.assertRaises(ValueError):m.validate(dict(frames=12,**c))
 def test_flat(self):
  v,f,n,uv=m.geom(dict(kind='sheet',bend=0,twist=0,resolution=32),1,1.4);self.assertEqual(float(np.ptp(v[:,2])),0);self.assertTrue(np.isfinite(n).all());self.assertEqual(float(uv.max()),1)
 def test_depth(self):
  p=np.array([[1,1,2],[15,1,2],[1,15,2],[1,1,1],[15,1,1],[1,15,1]],float);a=np.array([[0.]]*3+[[1.]]*3);d,b=m.raster(p,np.array([[3,4,5],[0,1,2]],np.int32),a,20,20);self.assertAlmostEqual(float(b[2,2,0]),1);self.assertAlmostEqual(float(d[2,2]),1)
 @unittest.skipUnless(F,'no font')
 def test_materials_and_motion(self):
  for kind,mat in [('ribbon','chrome'),('knot','satin'),('ribbon','ink'),('sheet','ceramic'),('sheet','texture')]:
   c=dict(kind=kind,material=mat,frames=20,resolution=32,src=str(R/'examples/assets/v15-workspace.png'),quality=.65,grain=0,bloom=0);sh=m.MeshMotion(160,284,c,F);a,b=sh.frame(0),sh.frame(19);self.assertEqual(b.shape,(284,160,3));self.assertGreater(b.std(),4);self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(b,sh.frame(19)))
 @unittest.skipUnless(F,'no font')
 def test_obj(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'tri.obj';p.write_text('v -1 -1 0\nv 1 -1 0\nv 0 1 0\nf 1 2 3\n');sh=m.MeshMotion(160,284,dict(kind='obj',material='ceramic',frames=10,src=str(p),grain=0),F);self.assertGreater(sh.frame(9).std(),5)
if __name__=='__main__':unittest.main()
