import sys,json,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import Engine,validate
from continuity_compile import build
from optics import shaped_lens
class V30(unittest.TestCase):
 def test_shapes(self):
  y,x=np.indices((100,160));src=np.uint8(np.stack([(x*9)%255,(y*13)%255,((x+y)*8)%255],2));results=[]
  for s in ['roundrect','ellipse','diamond','squircle','capsule']:
   a=src.copy();shaped_lens(a,[[1,0,80],[0,1,50],[0,0,1]],80,48,shape=s);self.assertGreater(np.abs(a.astype(float)-src).sum(),100);self.assertTrue(np.array_equal(a[0],src[0]));results.append(a)
  self.assertEqual(len({a.tobytes() for a in results}),5)
 def test_rotation(self):
  a=np.full((100,100,3),100,np.uint8);b=a.copy();shaped_lens(a,[[1,0,50],[0,1,50],[0,0,1]],70,24,shape='capsule',tint_mix=.6);shaped_lens(b,[[0,-1,50],[1,0,50],[0,0,1]],70,24,shape='capsule',tint_mix=.6);self.assertFalse(np.array_equal(a,b));self.assertTrue(a[50,75,0]>b[50,75,0])
 def test_zero_alpha(self):
  a=np.full((30,30,3),80,np.uint8);b=a.copy();shaped_lens(a,np.eye(3),30,30,shape='ellipse',opacity=0);self.assertTrue(np.array_equal(a,b))
 def test_plan(self):
  p=build(json.loads((ROOT/'starter/composite_film/premium-timing.json').read_text()),ROOT/'examples/assets/v15-workspace.png');validate(p,ROOT);d={l['id']:l for l in p['layers']};self.assertLess(d['hero']['active'][0],d['story']['active'][1]);self.assertGreaterEqual(d['hero']['active'][1],d['proof']['mask_progress'][-1][0]);self.assertEqual(p['duration'],24.1)
 def test_parent(self):
  p=dict(width=180,height=320,fps=30,duration=2,background='#303030',layers=[dict(id='g',kind='group',active=[0,2],x=360,y=640,rotate=[[0,0],[2,90,'linear']]),dict(id='glass',kind='lens',active=[0,2],parent='g',x=0,y=0,w=400,h=100,shape='capsule',tint_mix=.5)])
  e=Engine(validate(p,ROOT),ROOT);self.assertFalse(np.array_equal(e.frame(0),e.frame(1)))
if __name__=='__main__':unittest.main()
