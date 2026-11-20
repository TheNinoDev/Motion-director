import sys,unittest,copy,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/composite_film'))
from compositor import Engine,validate,val
from refinement import feather_mask,shadow_pass,projected_exposure
from refined_compile import build
from cue_align import align
class V29(unittest.TestCase):
 def plan(self,layers):return dict(width=180,height=320,fps=30,duration=2,background='#ffffff',layers=layers)
 def rect(self,**kw):return dict(id='r',kind='rect',active=[.2,1.8],x=360,y=640,w=200,h=120,color='#000000',**kw)
 def test_rotation_exposure(self):
  l=self.rect(rotate=[[0,-90],[2,90,'linear']]);p=self.plan([l]);a=Engine(validate(p,ROOT),ROOT).frame(1);l['projected_blur']=1.8;b=Engine(validate(p,ROOT),ROOT).frame(1);self.assertGreater(np.abs(a.astype(float)-b).sum(),100)
 def test_scale_exposure(self):
  l=self.rect(scale=[[0,.3],[2,2.5,'linear']]);p=self.plan([l]);a=Engine(validate(p,ROOT),ROOT).frame(1);l['projected_blur']=1.8;b=Engine(validate(p,ROOT),ROOT).frame(1);self.assertGreater(np.abs(a.astype(float)-b).sum(),100)
 def test_shadow(self):
  l=self.rect(shadow=True,shadow_y=32,shadow_blur=16,shadow_opacity=.6);p=self.plan([l]);a=Engine(validate(p,ROOT),ROOT).frame(1);self.assertLess(a[181,90,0],255);self.assertEqual(a[5,5,0],255)
 def test_feather(self):
  a=np.full((1,5),255,np.uint8);b=feather_mask(a,np.linspace(0,1,5),.5,.5);self.assertEqual(b[0,0],255);self.assertTrue(100<b[0,2]<150);self.assertEqual(b[0,-1],0)
 def test_spring(self):self.assertGreater(val([[0,0],[1,1,'spring']],.25),1);self.assertEqual(val([[0,0],[1,1,'spring']],1),1)
 def test_thin(self):
  l=self.rect();l['h']=1;Engine(validate(self.plan([l]),ROOT),ROOT).frame(1)
 def test_align(self):
  l=self.rect(rotate=[[.2,0],[1,90,'linear']]);p=self.plan([l]);q,r=align(p,[dict(time=1.06,strength=.8)],[dict(layers=['r'],anchor=1)]);self.assertAlmostEqual(q['layers'][0]['active'][0],.266667);self.assertEqual(p['layers'][0]['active'][0],.2);self.assertAlmostEqual(q['layers'][0]['rotate'][1][0],1.066667)
 def test_align_dependency(self):
  l=self.rect();l['parent']='g';p=self.plan([dict(id='g',kind='group',active=[0,2]),l]);self.assertRaises(ValueError,align,p,[],[dict(layers=['r'],anchor=1)])
 def test_plan(self):
  p=build(json.loads((ROOT/'starter/composite_film/premium-timing.json').read_text()),ROOT/'examples/assets/v15-workspace.png');validate(p,ROOT);self.assertEqual(p['duration'],24.1);self.assertGreater(len(p['layers']),70)
if __name__=='__main__':unittest.main()
