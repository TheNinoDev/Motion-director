import copy,json,sys,tempfile,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v42 import build,compile_choreography,CATALOG
from compositor import val,Engine
from pixel_review_v42 import measure,review,verify
from production_v42 import start,next_step,gate,requests
class V42(unittest.TestCase):
 def spec(self):return json.loads((ROOT/'examples/director-v42.json').read_text())
 def plan(self):return build(self.spec(),ROOT/'examples')[0]
 def test_fan(self):
  p=self.plan();by={x['id']:x for x in p['layers']};self.assertEqual(val(by['module0']['x'],0),-150);self.assertAlmostEqual(val(by['module0']['x'],2.3),-172);self.assertAlmostEqual(val(by['module2']['rotate'],2.3),14);self.assertEqual(val(by['mark0']['y'],4.3),970)
 def simple(self):return {'width':360,'height':640,'fps':30,'duration':2,'layers':[dict(id=i,kind='rect',w=30,h=30,x=x,y=640,active=[0,2],color='#ffffff') for i,x in [('a',200),('b',520)]]}
 def test_gather(self):
  p=self.simple();r=dict(recipe='gather',layers=['a','b'],start=0,end=2,center=[360,640],spacing=30,stagger=.1,scale=.5);compile_choreography(p,[r]);self.assertEqual(val(p['layers'][0]['x'],2),345);self.assertEqual(val(p['layers'][1]['scale'],2),.5);self.assertRaises(ValueError,compile_choreography,p,[r])
 def test_orbit(self):
  p=self.simple();compile_choreography(p,[dict(recipe='orbit_exchange',layers=['a','b'],start=0,end=2,center=[360,640],radius=[160,80],degrees=180)]);self.assertAlmostEqual(val(p['layers'][0]['x'],2),520);self.assertAlmostEqual(val(p['layers'][1]['x'],2),200)
 def test_bad_parent(self):
  p=self.simple();p['layers'][0]['parent']='x';r=dict(recipe='wave',layers=['a','b'],start=0,end=2,amplitude=20,cycles=1,stagger=0);self.assertRaises(ValueError,compile_choreography,p,[r])
 def test_pixel_math(self):
  a=np.zeros((100,100,3),np.uint8);b=a.copy();b[:5,:5]=255;m,_=measure(a,b);self.assertEqual(m['changed_pixels'],25);self.assertEqual(m['outside_default_safe_fraction'],1)
 def test_actual_occlusion(self):
  p=self.simple();p['layers'][1]['x']=200;p['layers'][1]['color']='#0000ff';p['background']='#000000'
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'p.json';a.write_text(json.dumps(p));o=Path(d)/'pixel';r=review(a,o,[{'frame':5,'layer':'a'},{'frame':5,'layer':'b'}]);self.assertEqual(r['results'][0]['changed_pixels'],0);self.assertTrue(r['results'][0]['flags']);self.assertGreater(r['results'][1]['changed_pixels'],0);self.assertTrue(verify(a,o)['valid']);(o/r['results'][0]['file']).write_bytes(b'changed');self.assertFalse(verify(a,o)['valid'])
 def test_requests(self):
  r=requests(self.plan(),json.loads((ROOT/'examples/creative-v42.json').read_text()));self.assertEqual(len(r),4);self.assertTrue(any(x['layer']=='end' for x in r))
 def test_multiline(self):
  p=self.simple();p['layers']=[dict(id='title',kind='text',text='HELLO\nWORLD',size=76,font='heavy',x=360,y=640,active=[0,2],color='#ffffff',maxw=550)];e=Engine(p,ROOT);tex,w,h=e.textures['title'];rows=np.where(tex[:,:,3].max(axis=1)>0)[0];self.assertTrue(any(np.diff(rows)>1));self.assertGreater(h,90)
 def test_gate(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'work';start(ROOT/'examples/director-v42.json',ROOT/'examples/creative-v42.json',w);self.assertEqual(next_step(w)['stage'],'preview');self.assertFalse(gate(w)['ready']);self.assertTrue(any('pixel' in x for x in gate(w)['errors']))
if __name__=='__main__':unittest.main()
