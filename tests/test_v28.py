import sys, unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import Engine,validate,val
from optics import gradient,lens,directional
from premium_compile import compile_plan
class Test28(unittest.TestCase):
 def test_gradient(self):
  g=gradient(20,10,[[0,'#000000'],[1,'#ffffff']],0);self.assertEqual(g.shape,(10,20,4));self.assertEqual(int(g[0,0,0]),0);self.assertEqual(int(g[0,-1,0]),255)
 def test_lens(self):
  a=np.tile(np.arange(200,dtype=np.uint8),(200,1));im=np.stack([a,a,a],-1);orig=im.copy();lens(im,100,100,80,100);self.assertTrue(np.array_equal(im[0],orig[0]));self.assertGreater(np.abs(im.astype(float)-orig).sum(),10)
 def test_blur(self):
  a=np.zeros((60,60,4),np.uint8);a[20:40,20:40]=255;b=directional(a,18,0);self.assertGreater(b[30,15,3],0);self.assertEqual(b[10,15,3],0)
 def test_back(self):self.assertGreater(val([[0,0],[1,1,'back']],.65),1)
 def test_combined(self):
  p=dict(fps=30,width=180,height=320,duration=2,layers=[dict(kind='gradient',id='g',active=[0,2],w=720,h=1280,stops=[[0,'#151515'],[1,'#bbbbbb']]),dict(kind='lens',id='l',active=[0,2],w=250,h=250,x=[[0,180],[2,540,'linear']],y=640)])
  e=Engine(validate(p,ROOT),ROOT);self.assertFalse(np.array_equal(e.frame(.3),e.frame(1.5)))
 def test_plan(self):
  import json;meta=json.loads((ROOT/'starter/composite_film/premium-timing.json').read_text());p=compile_plan(meta,ROOT/'examples/assets/v15-workspace.png');validate(p,ROOT);self.assertEqual(p['duration'],24.1)
if __name__=='__main__':unittest.main()
