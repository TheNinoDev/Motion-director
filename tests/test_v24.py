import unittest,json,copy,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'starter/story_film'))
import film
class StoryTest(unittest.TestCase):
 def setUp(self):
  self.base=ROOT/'starter/story_film';self.p=json.loads((self.base/'demo.json').read_text());self.p.update(width=360,height=640)
 def test_validation(self):self.assertEqual(film.validate(self.p,self.base),self.p)
 def test_bad_kind(self):
  self.p['beats'][0]['kind']='not-an-engine'
  with self.assertRaises(AssertionError):film.validate(self.p,self.base)
 def test_bad_crop(self):
  self.p['beats'][6]['crop']=[.8,0,.1,1]
  with self.assertRaises(AssertionError):film.validate(self.p,self.base)
 def test_stills(self):
  c=film.Canvas(self.p,self.base)
  for i,b in enumerate(self.p['beats']):
   if b['kind']=='fold':continue
   for phase in (0,.25,.5,.75,.99):
    a=c.frame(b,b['min']*phase,b['min'],i);self.assertEqual(a.size,(360,640));self.assertEqual(a.mode,'RGB')
if __name__=='__main__':unittest.main()
