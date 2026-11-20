import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v38 import build,diagnose,RECIPES
from motion_workbench import compile_spec,EXTRA_OPS
from agent_session import start,review,verify
from compositor import val
from creative_gate import assess
class V38(unittest.TestCase):
 def spec(self):
  return {'version':1,'width':180,'duration':3,'layers':[{'id':i,'kind':'rect','w':120,'h':100,'shadow':True} for i in ('card','card1','card2','card3')]+[{'id':'lens','kind':'lens','w':120,'h':100,'shape':'ellipse'},{'id':'solid','kind':'object3d','w':120,'h':100,'material':'chrome'},{'id':'type','kind':'text3d','text':'OK','material':'chrome'}]}
 def test_all_recipes(self):
  for name,params in RECIPES.items():
   with self.subTest(recipe=name):
    s=self.spec();s['choreography']=[dict(recipe=name,start=.1,end=1,**params)];p,plain,_=build(s,ROOT);self.assertGreater(len(plain['actions']),0)
 def test_extra_primitives(self):
  cases={'lens_strength':('lens',.1,.3),'dispersion':('lens',.01,.02),'defocus':('card',0,3),'shadow_strength':('card',.1,.4),'glow_strength':('card',0,.3),'transmission':('solid',0,.3),'extrusion':('solid',30,45),'bevel_depth':('type',1,4)}
  self.assertEqual(set(cases),set(EXTRA_OPS))
  for op,(layer,a,b) in cases.items():
   with self.subTest(op=op):
    s=self.spec();s['actions']=[dict(op=op,layer=layer,start=0,end=1,**{'from':a,'to':b})];p,_=compile_spec(s,ROOT);l=next(l for l in p['layers'] if l['id']==layer);self.assertEqual(val(l[EXTRA_OPS[op][0]],1),b)
 def test_example_and_endpoint(self):
  s=json.loads((ROOT/'examples/director-v38.json').read_text());original=copy.deepcopy(s);p,e,_=build(s,ROOT/'examples');self.assertEqual(s,original);self.assertEqual(len(e['actions']),31);l=next(l for l in p['layers'] if l['id']=='card1');self.assertEqual(val(l['x'],2.89),228);self.assertEqual(val(l['y'],3.65),688);self.assertFalse(any(x['code']=='subframe_change' for x in diagnose(p)))
 def test_invalid_recipe(self):
  s=self.spec();s['choreography']=[dict(recipe='arc_arrival',start=0,end=1,**RECIPES['arc_arrival'],typo=1)]
  with self.assertRaises(ValueError):build(s,ROOT)
 def test_lens_requires_shape(self):
  s=self.spec();next(l for l in s['layers'] if l['id']=='lens').pop('shape');s['choreography']=[dict(recipe='lens_pass',start=0,end=1,**RECIPES['lens_pass'])]
  with self.assertRaises(ValueError):build(s,ROOT)
 def test_gap(self):
  s=self.spec();s['layers']=[{'id':'x','kind':'text','text':'Hi','active':[0,1]}];p,_,_=build(s,ROOT);self.assertTrue(any(x['code']=='foreground_gap' for x in diagnose(p)))
 def test_creative_gate(self):
  s=json.loads((ROOT/'examples/creative-v38.json').read_text());self.assertTrue(assess(s)['structure_valid']);s['mode']='advertisement';self.assertFalse(assess(s)['structure_valid']);s['beats'][1]['start']=1.9;self.assertTrue(any('gap or overlap' in x for x in assess(s)['errors']))
 def test_session_and_review(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);s=self.spec();s['layers']=s['layers'][:1];sp=d/'spec.json';sp.write_text(json.dumps(s));w=d/'session';r=start(sp,w);self.assertEqual(r['phase'],'compiled');self.assertTrue((w/'plan.json').is_file())
   with self.assertRaises(ValueError):start(sp,w)
   p=w/'plan.json';out=w/'review';m=review(p,out,'cpu',180,3);self.assertTrue(verify(p,out)['provenance_valid']);(out/m['frames'][0]['file']).write_bytes(b'changed');self.assertFalse(verify(p,out)['provenance_valid'])
if __name__=='__main__':unittest.main()
