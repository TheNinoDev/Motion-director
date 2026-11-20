import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'starter/composite_film')]
from director_v39 import build,RECIPES
from production_v39 import bind,start,snapshot,verify_inputs
from compositor import val
class V39(unittest.TestCase):
 def spec(self):
  return {'version':1,'width':180,'duration':3,'layers':[{'id':i,'kind':'rect','w':120,'h':100,'x':100,'y':200,'mask_progress':0} for i in ('card','card1','card2','card3','marker')]+[{'id':'solid','kind':'object3d','w':120,'h':120,'material':'chrome'}]}
 def test_recipes(self):
  for name,args in RECIPES.items():
   with self.subTest(recipe=name):
    s=self.spec();s['state_motion']=[dict(recipe=name,start=1,end=2,**args)];p,e,_=build(s,ROOT);self.assertTrue(e['actions'])
 def test_state(self):
  s=self.spec();s['state_motion']=[dict(recipe='glide_to',layer='card',start=.2,end=1,to=[205,400],scale=.8,rotation=35),dict(recipe='glide_to',layer='card',start=1.1,end=2,to=[300,500],scale=1,rotation=0)];p,_,_=build(s,ROOT);l=p['layers'][0];self.assertEqual(val(l['x'],.2),100);self.assertEqual(val(l['x'],1.1),205);self.assertEqual(val(l['rotate'],1.1),35);self.assertEqual(val(l['x'],2),300)
 def test_follow(self):
  s=self.spec();s['actions']=[dict(op='slide',layer='card',start=0,end=3,**{'from':[100,200],'to':[400,500]},ease='linear')];s['state_motion']=[dict(recipe='follow_offset',layer='marker',source='card',offset=[10,-100],delay=.1,blend_in=.2,samples=24,start=.3,end=2.7)];p,_,_=build(s,ROOT);m=next(l for l in p['layers'] if l['id']=='marker');self.assertAlmostEqual(val(m['x'],2.7),370); self.assertAlmostEqual(val(m['y'],2.7),360)
 def test_no_overlap(self):
  s=self.spec();s['state_motion']=[dict(recipe='glide_to',layer='card',start=.2,end=1,to=[205,400],scale=.8,rotation=35),dict(recipe='quiet_exit',layer='card',start=.8,end=2,offset=[0,-100],scale=.5)];self.assertRaises(ValueError,build,s,ROOT)
 def test_bad_params(self):
  s=self.spec();s['state_motion']=[dict(recipe='glide_to',layer='card',start=.2,end=1,to=[205,400],scale=.8,rotation=35,typo=True)];self.assertRaises(ValueError,build,s,ROOT)
 def test_binding(self):
  s=json.loads((ROOT/'examples/director-v39.json').read_text());p,_,_=build(s,ROOT/'examples');c=json.loads((ROOT/'examples/creative-v39.json').read_text());self.assertTrue(bind(c,p)['valid']);c['beats'][0]['layer_ids']=['unknown'];self.assertFalse(bind(c,p)['valid'])
 def test_session(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/'project';r=start(ROOT/'examples/director-v39.json',ROOT/'examples/creative-v39.json',w);self.assertTrue((w/'production.json').is_file());self.assertTrue(r['binding']['valid']);self.assertIn('check_upload',r['commands_argv']);self.assertRaises(ValueError,start,ROOT/'examples/director-v39.json',ROOT/'examples/creative-v39.json',w)
 def test_inputs(self):
  with tempfile.TemporaryDirectory() as d:
   w=Path(d)/"project";start(ROOT/"examples/director-v39.json",ROOT/"examples/creative-v39.json",w);self.assertTrue(verify_inputs(w)["inputs_valid"]);(w/"creative.json").write_text("{}");self.assertFalse(verify_inputs(w)["inputs_valid"])
 def test_nested_asset(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);asset=base/'mesh.obj';asset.write_text('dummy');s=self.spec();s['layers'].append({'id':'m','kind':'mesh','w':100,'h':100,'mesh':{'kind':'obj','src':'mesh.obj'}});p,_,_=build(s,base);self.assertEqual(p['layers'][-1]['mesh']['src'],str(asset));plan=base/'plan.json';plan.write_text(json.dumps(p));self.assertIn(str(asset),snapshot(plan,p))
if __name__=='__main__':unittest.main()
