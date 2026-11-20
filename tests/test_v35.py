import unittest,sys,json,warnings
from pathlib import Path
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'starter/composite_film'),str(ROOT/'scripts')]
from render_backend import Backend,probe
from review_targets import targets
from compositor import Engine,validate
class V35(unittest.TestCase):
 def test_cpu_report(self):
  b=Backend('cpu');self.assertEqual(b.run('text',lambda x:x+1,3),4);self.assertEqual(b.report()['kernel_calls'],{'text:cpu':1})
 def test_invalid(self):
  for args in [('bogus',0,64),('cpu',-1,64),('cpu',0,0)]:
   with self.assertRaises(ValueError):Backend(*args)
 def test_auto_fallback(self):
  from numba import cuda
  with patch.object(cuda,'is_available',return_value=False),warnings.catch_warnings():
   warnings.simplefilter('ignore');b=Backend('auto');self.assertEqual(b.selected,'cpu');self.assertIsNotNone(b.reason)
   with self.assertRaises(RuntimeError):Backend('cuda')
 def test_kernel_failure(self):
  b=Backend('cpu');b.cuda=object();b.selected='cuda';b.mode='auto'
  with patch.object(b,'_gpu',side_effect=RuntimeError('test failure')) as f,warnings.catch_warnings():
   warnings.simplefilter('ignore');self.assertEqual(b.run('text',lambda:2),2);self.assertEqual(b.run('text',lambda:3),3);self.assertEqual(f.call_count,1)
  self.assertIn('text',b.report()['fallbacks']);b.mode='cuda';b.failures.clear()
  with patch.object(b,'_gpu',side_effect=RuntimeError('test failure')):
   with self.assertRaises(RuntimeError):b.run('text',lambda:4)
 def test_review(self):
  p=json.loads((ROOT/'examples/elastic-v34.json').read_text());r=targets(p,8);self.assertLessEqual(len(r),8);self.assertEqual(r[0]['frame'],0);self.assertEqual(r[-1]['frame'],round(p['duration']*p['fps'])-1);self.assertTrue(any('elastic event' in y for x in r for y in x['reasons']));self.assertEqual(r,targets(p,8))
 def test_cpu_integrated(self):
  p={'width':90,'height':160,'fps':24,'duration':1,'layers':[{'id':'v','kind':'object3d','geometry':'torus','material':'chrome','w':230,'h':230,'active':[0,1]},{'id':'t','kind':'text3d','text':'3D','size':90,'y':400,'active':[0,1]}]};validate(p,ROOT);b=Backend('cpu');e=Engine(p,ROOT,b);x=e.frame(.2);self.assertTrue(np.array_equal(x,Engine(p,ROOT).frame(.2)));self.assertEqual(b.report()['kernel_calls'],{'volume:cpu':1,'text:cpu':1})
if __name__=='__main__':unittest.main()
